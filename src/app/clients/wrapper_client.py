'''
This webclient is responsible for sending requests to the LLM Wrapper.
'''

from typing import Dict
import requests
import json

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
        return response

    except Exception as e:
        print(f"Failed to deploy LLM: {e}")
        return None
    