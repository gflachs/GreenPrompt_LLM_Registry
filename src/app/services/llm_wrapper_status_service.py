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
                if wrapper["status"] == "prompting" or wrapper["status"] == "stopping" or wrapper["status"] == "restarting" or wrapper["status"] == "deploying" or wrapper["status"] == "unresponsive":
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
            db_controller.change_llm_wrapper_status_by_id(wrapper_id, "idle")
        else:
            db_controller.change_llm_wrapper_status_by_id(wrapper_id, "unresponsive")

    # Starte das obige _restart_logic in einem neuen Thread
    t = threading.Thread(target=_restart_logic, daemon=True)
    t.start()
    
  
  
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
    return True

