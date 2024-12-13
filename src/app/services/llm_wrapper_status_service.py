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
                response = wrapper_client.check_status(wrapper["address"])
                db_controller.change_llm_wrapper_status_by_id(wrapper["id"], response)
                
        time.sleep(60)
  
  
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

