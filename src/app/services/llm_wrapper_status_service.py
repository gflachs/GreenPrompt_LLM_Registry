'''
This service is responsible for checkinf the status of the LLM Wrapper
'''
from typing import Dict
import app.clients.wrapper_client as wrapper_client
from app.utils.logger import console_logger
from app.controller.db_controller import LLMRegistryDbController
import threading
import time

queue_lock = threading.Lock()

running_threads = []

running = True

def is_running():
    global running
    return running

def check_status():
    #get all wrapper
    global queue_lock
    while is_running():
        with queue_lock:
            db_controller = LLMRegistryDbController.get_instance()
            wrappers = db_controller.get_all_wrappers()

            for wrapper in wrappers:
                if wrapper["status"] == "failure":
                    #we need to restart the wrapper
                    console_logger.info(f"Restarting wrapper {wrapper['address']}")
                    db_controller.change_llm_wrapper_status_by_id(wrapper["id"], "restarting")
                    restart_wrapper_in_background(wrapper["id"], wrapper["address"], wrapper["password"], wrapper["username"])
                    continue
                if wrapper["status"] == "prompting" or wrapper["status"] == "stopping" or wrapper["status"] == "restarting" or wrapper["status"] == "deploying" or wrapper["status"] == "unresponsive" or wrapper["status"] == "installing":
                    continue
                if wrapper["status"] == "not_installed":
                    #we need to install the wrapper
                    console_logger.info(f"Installing wrapper {wrapper['address']} with user {wrapper['username']} and password {wrapper['password']}")
                    db_controller.change_llm_wrapper_status_by_id(wrapper["id"], "installing")
                    install_wrapper_in_background(wrapper["address"], wrapper["password"], wrapper["username"])
                    continue
                    
                response = wrapper_client.check_status(wrapper["address"])
                db_controller.change_llm_wrapper_status_by_id(wrapper["id"], response)
                
        time.sleep(60)
        
def restart_wrapper_in_background(wrapper_id: int, address: str, password: str, username: str):
    """
    Führt den eigentlichen Neustart in einem eigenen Thread durch.
    """
    def _restart_logic():
        db_controller = LLMRegistryDbController.get_instance()
        console_logger.info(f"Neustart im Hintergrund für Wrapper {address}")

        response = wrapper_client.restart_llm_wrapper(address, password, username)

        if response:
            db_controller.change_llm_wrapper_status_by_id(wrapper_id, "not_ready")
        else:
            db_controller.change_llm_wrapper_status_by_id(wrapper_id, "unresponsive")

    # Starte das obige _restart_logic in einem neuen Thread
    t = threading.Thread(target=_restart_logic, daemon=True)
    t.start()
    running_threads.append(t)
    
def install_wrapper_in_background(address: str, password: str, username: str):
    """
    Führt die Installation in einem eigenen Thread durch.
    """
    def _install_logic():
        db_controller = LLMRegistryDbController.get_instance()
        console_logger.info(f"Installation im Hintergrund für Wrapper {address} with user {username} and password {password}")

        response = wrapper_client.deploy_fastapi_service(address,username,password)

        if response:
            db_controller.change_llm_wrapper_status_by_address(address, "not_ready")
        else:
            db_controller.change_llm_wrapper_status_by_address(address, "unresponsive")

    # Starte das obige _install_logic in einem neuen Thread
    t = threading.Thread(target=_install_logic, daemon=True)
    t.start()
    running_threads.append(t)
  
thread = threading.Thread(target=check_status, daemon=True)
      
def start_check_status():
    global running
    running = True
    thread.start()
    return thread

def stop_check_status():
    global running
    running = False
    thread.join()
    for t in running_threads:
        #kill the thread
        t.join()
        t = None

    return True

