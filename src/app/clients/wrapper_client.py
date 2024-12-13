'''
This webclient is responsible for sending requests to the LLM Wrapper.
'''

from typing import Dict
import requests
import json
from app.utils.logger import console_logger

def deploy_llm(llm_address: str, llm_config: Dict):
    '''
    Sends a POST request to the LLM Wrapper to deploy a new LLM instance.
    :param llm_address: Address of the LLM Wrapper
    :param llm_config_json: JSON configuration of the LLM
    :return: Response from the LLM Wrapper
    '''
    try:
        llm_config_json = json.dumps(llm_config)
        response = requests.post(f"http://{llm_address}/deploy", json=llm_config_json)
        if response.status_code == 200:
            console_logger.info(f"LLM deployed successfully: {response.json()}")
            return response.json()["status"]
        else:
            console_logger.error(f"Failed to deploy LLM: {response.json()}")
            return "failure"

    except Exception as e:
        console_logger.error(f"An exception occurred: {e}")
        return None
    
def stop_llm(llm_address: str):
    '''
    Sends a POST request to the LLM Wrapper to stop the LLM instance.
    :param llm_address: Address of the LLM Wrapper
    :return: Response from the LLM Wrapper
    '''
    try:
        response = requests.post(f"http://{llm_address}/stop")
        if response.status_code == 200:
            console_logger.info(f"LLM stopped successfully: {response.json()}")
            return response.json()["status"]
        else:
            console_logger.error(f"Failed to stop LLM: {response.json()}")
            return "failure"

    except Exception as e:
        console_logger.error(f"An exception occurred: {e}")
        return None

def check_status(llm_address: str):
    '''
    Sends a GET request to the LLM Wrapper to check the status of the LLM instance.
    :param llm_address: Address of the LLM Wrapper
    :return: Response from the LLM Wrapper
    '''
    try:
        response = requests.get(f"http://{llm_address}/status")
        if response.status_code == 200:
            console_logger.info(f"LLM status: {response.json()}")
            return response.json()["status"]
        else:
            console_logger.error(f"Failed to get LLM status: {response.json()}")
            return "failure"

    except Exception as e:
        console_logger.error(f"An exception occurred: {e}")
        return None