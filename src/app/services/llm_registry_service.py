from typing import Dict, List
from app.controller.db_controller import LLMRegistryDbController
from app.utils.logger import console_logger
import app.services.llm_wrapper_service as lms
import threading
import time
import uuid
from app.models.request import RequestPayload, RequestResponse, RequestStatus, RequestSingleResponse, LLMConfig, Args

# Initialize the database controller

# Deployment queue and lock for thread safety
queue_lock = threading.Lock()

running = True

def is_running():
    global running
    return running

def process_queue():
    """Processes the deployment queue."""
    wait_time = 5
    llm_registry_db_controller = LLMRegistryDbController.get_instance()

    while is_running():
        console_logger.info("Processing deployment queue...")
        try:
            with queue_lock:
                
                #find best deployments
                try:
                    best_deployments = llm_registry_db_controller.find_best_deployments()
                    console_logger.info(best_deployments)
                    console_logger.info(f"Found {len(best_deployments)} best deployments")
                    for deployment in best_deployments:
                        success = deploy_llm(deployment["llm_config"], deployment["address"])
                        if success:
                            llm_registry_db_controller.set_request_address(deployment["request_id"], deployment["address"])
                            llm_registry_db_controller.change_llm_wrapper_status_by_id(deployment["wrapper_id"], "prompting")
                            llm_registry_db_controller.update_measurement_wrapper_id(deployment["measurementId"], deployment["wrapper_id"])
                        else:
                            llm_registry_db_controller.change_llm_wrapper_status_by_id(deployment["wrapper_id"], "failure")
                            llm_registry_db_controller.update_request_status("queued", deployment["request_id"])
                except Exception as e:
                    console_logger.error(f"Error processing best deployments: {e}")
                
                #get all wrappers with the status "ready"
                measurements = llm_registry_db_controller.get_measurements_waiting_for_deployment()
            
                for measurement in measurements:
                    console_logger.info(f"Processing measurement {measurement['id']}")
                    try:
                        deployment_wrappers = []
                        if measurement.get("wrapper_id", None) is not None:
                            wrapper = llm_registry_db_controller.get_wrapper_by_id(measurement["wrapper_id"])
                            if wrapper:
                                #check if wrapper is either idle or ready
                                if wrapper["status"] == "idle" or wrapper["status"] == "ready":
                                    deployment_wrappers.append(wrapper)
                                else:
                                    continue
                        queued_request = llm_registry_db_controller.get_next_undeployed_request(measurement["id"])
                        console_logger.info(f"Found queued request: {queued_request}")
                        
                        if not queued_request:
                            llm_registry_db_controller.update_measurement_status("finished", measurement["wrapper_id"])
                            continue
                        
                        
                        llm_config = queued_request["config"]
                        request_id = queued_request["id"]

                        #if address is None, find the next idle wrapper
                        if len(deployment_wrappers) == 0:
                            # Fetch all idle wrappers
                            idle_wrappers = llm_registry_db_controller.get_all_wrapper_with_status("idle")
                            if idle_wrappers:
                                for wrapper in idle_wrappers:
                                    deployment_wrappers.append(wrapper)
                            else:
                                console_logger.info("No idle wrappers found")
                                #find the next wrapper with the status "deployed"
                        
                        #if no idle wrapper is found, find the next deployed, which is not prompting
                        if len(deployment_wrappers) == 0:
                            # Fetch all deployed wrappers
                            deployed_wrappers = llm_registry_db_controller.get_all_wrapper_with_status("ready")
                            if deployed_wrappers:
                                for wrapper in deployed_wrappers:
                                    deployment_wrappers.append(wrapper)
                            else:
                                console_logger.info("No deployed wrappers found")
                                #find the next wrapper with the status "deployed"

                        for wrapper in deployment_wrappers:
                            console_logger.info(f"Found wrapper {wrapper['id']} with status {wrapper['status']}")
                            if wrapper["status"] == "ready":
                                try:
                                    success = stop_llm(wrapper["id"])
                                    if success:
                                        llm_registry_db_controller.change_llm_wrapper_status_by_id(wrapper["id"], "idle")
                                    else:
                                        llm_registry_db_controller.change_llm_wrapper_status_by_id(wrapper["id"], "failure")
                                except Exception as e:
                                    console_logger.error(e)
                                    console_logger.error(f"Error stopping LLM: {e}")
                                    llm_registry_db_controller.change_llm_wrapper_status_by_id(wrapper["id"], "failure")
                                    continue
                            success = deploy_llm(llm_config, wrapper["address"])
                            if success:
                                llm_registry_db_controller.set_request_address(request_id, wrapper["address"])
                                llm_registry_db_controller.change_llm_wrapper_status_by_id(wrapper["id"], "prompting")
                                llm_registry_db_controller.change_llm_wrapper_config_by_id(wrapper["id"], llm_config)
                                #check if measurement has a wrapper assigned
                                if measurement.get("wrapper_id", None) is None:
                                    llm_registry_db_controller.update_measurement_wrapper_id(measurement["id"], wrapper["id"])
                                    #update the status of the measurement to "prompting"
                                llm_registry_db_controller.update_measurement_status(measurement["id"], "prompting")
                            else:
                                llm_registry_db_controller.change_llm_wrapper_status_by_id(wrapper["id"], "failure")
                    except Exception as e:
                        console_logger.error(e)
                        console_logger.error(f"Error processing measurement: {e}")
                                
            if len(best_deployments) == 0 and len(measurements) == 0:
                wait_time = min(wait_time + 1, 10)  # Bis max. 10 Sekunden erhöhen
                console_logger.info(f"No work to do. Sleeping for {wait_time} seconds.")
            else:
                wait_time = 5  # Zurücksetzen, wenn Arbeit gefunden wird
                
        except Exception as e:
            console_logger.error(f"Error processing deployment queue: {e}")
        time.sleep(wait_time)


def deploy_llm(llm_config: Dict, address: str) -> str:
    """Deploys an LLM to a wrapper.

    Args:
        llm_config (Dict): The configuration for the LLM to be deployed.
        address (str): The address of the wrapper to deploy the LLM to.

    Returns:
        str: The unique ID for the request.
    """
    console_logger.info(f"Deploying LLM to address {address}")
    llm_registry_db_controller = LLMRegistryDbController.get_instance()
    llm_registry_db_controller.change_llm_wrapper_status_by_address(address, "deploying")
    # Deploy the LLM to the wrapper
    try:
        return lms.deploy_llm(llm_config, address)
    except Exception as e:
        llm_registry_db_controller.change_llm_wrapper_status_by_address(address, "failure")
        console_logger.error(f"Error deploying LLM to address {address}: {e}")
        return False

def request_llm(llm_config: RequestPayload) -> RequestResponse:
    """Handles LLM deployment requests.

    Args:
        llm_config (Dict): The configuration for the LLM to be deployed.
        measurementId (int): The ID of the measurement from the promptingservice.

    Returns:
        str: The unique ID for the request.
    """
    console_logger.info(f"Received LLM deployment request for measurement ID: {llm_config.measurementId}")
    llm_registry_db_controller = LLMRegistryDbController.get_instance()

    llm_registry_db_controller.add_measurement(llm_config.measurementId)
    request_ids = RequestResponse(requests=[])
    for config in llm_config.llms:
        # Generate a unique request ID
        request_id = str(uuid.uuid4())
        # Add the request to the database with status "queued"
        llm_registry_db_controller.add_request(request_id, config.model_dump_json(), llm_config.measurementId)
        console_logger.info(f"Added request ID {request_id} to the deployment queue for measurement ID: {llm_config.measurementId}")
        request = RequestSingleResponse(requestId=request_id, llmconfig=config)
        request_ids.requests.append(request)
        
    return request_ids

def stop_llm(id: str) -> bool:
    """Stops an LLM on a wrapper.

    Args:
        id (str): The unique ID of the LLM to stop.

    Returns:
        bool: True if the LLM was stopped successfully, False otherwise.
    """
    console_logger.info(f"Stopping LLM on id {id}")
    llm_registry_db_controller = LLMRegistryDbController.get_instance()
    llm_registry_db_controller.change_llm_wrapper_status_by_id(id, "stopping")
    # Stop the LLM on the wrapper
    try:
        return lms.stop_llm(id)
    except Exception as e:
        llm_registry_db_controller.change_llm_wrapper_status_by_id(id, "failure")
        console_logger.error(f"Error stopping LLM on address {id}: {e}")
        return False

def release_llm(request_id: str) -> bool:
    """Releases an LLM Wrapper, which is currently in the "prompting" state.

    Args:
        request_id (str): The unique ID of the request.

    Returns:
        bool: True if the request was released successfully, False otherwise.
    """
    try: 
        llm_registry_db_controller = LLMRegistryDbController.get_instance()
        request = llm_registry_db_controller.get_request(request_id)
        if request is None:
            console_logger.error(f"Request with ID {request_id} not found.")
            return False
        wrapper = llm_registry_db_controller.get_wrapper_by_address(request["address"])
        if wrapper is None:
            console_logger.error(f"Wrapper with address {request['address']} not found.")
            return False
        if wrapper["status"] != "prompting":
            console_logger.error(f"Wrapper with address {request['address']} is not in the 'prompting' state.")
            return False
        llm_registry_db_controller.change_llm_wrapper_status_by_id(wrapper["id"], "not_ready")
        llm_registry_db_controller.update_measurement_status(request["measurementId"], "deployments_pending")
        return True
    except Exception as e:
        console_logger.error(f"Error releasing LLM: {e}")
        return False
    
    


def get_request(request_id: str) -> Dict:
    """Gets the request

    Args:
        request_id (str): The unique ID of the request.

    Returns:
        Dict: The status of the request.
    """
    llm_registry_db_controller = LLMRegistryDbController.get_instance()
    request_status_dict = llm_registry_db_controller.get_request(request_id)
    if request_status_dict is None:
        return None
    llm_config = request_status_dict["config"]
    #ll_config is a json string, convert it to a dict
    llm_config = LLMConfig.model_validate_json(llm_config)
    status = request_status_dict["status"]
    measurementId = request_status_dict["measurementId"]
    address = request_status_dict["address"]
    
    return RequestStatus(requestId=request_id, llmconfig=llm_config, status=status, measurementId=measurementId, address=address)


def shutdown():
    global running
    if running:
        running = False
        console_logger.info("Stopping queue processing thread...")
        queue_thread.join(timeout=10)  # Maximal 10 Sekunden warten
        if queue_thread.is_alive():
            console_logger.error("Queue processing thread did not stop in time.")
        else:
            console_logger.info("Queue processing thread has been stopped.")
    else:
        console_logger.warning("Queue processing thread is not running.")



# Start the queue processing in a background thread
queue_thread = threading.Thread(target=process_queue, daemon=True)

def start():
    global running, queue_thread
    if running and queue_thread.is_alive():
        console_logger.warning("Queue processing thread is already running.")
        return
    running = True
    if not queue_thread.is_alive():
        queue_thread = threading.Thread(target=process_queue, daemon=True)
        queue_thread.start()
        console_logger.info("Queue processing thread has been started.")
