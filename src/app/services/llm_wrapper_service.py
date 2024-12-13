from typing import Dict
import app.clients.wrapper_client as wrapper_client
from app.utils.logger import console_logger

'''
This module manages the interaction between the LLM Wrapper and the LLM Registry. Its resonsible for starting and stopping the LLMs in the Wrapper.
Therefore it provides the following functions:
- the service deploys an LLM instance into an LLM Wrapper
- the service can stop an LLM instance if it is no longer needed
- more function will be added in the future
'''

def deploy_llm(llm_address: str,llm_config_json: Dict):
    response = wrapper_client.deploy_llm(llm_address, llm_config_json)
    if response == "ready":
        console_logger.info(f"LLM deployed successfully: {response}")
        return True
    else:
        console_logger.error(f"Failed to deploy LLM: {response}")
        return False

def stop_llm(lm_address: str):
    response = wrapper_client.stop_llm(lm_address)
    if response == "stopped":
        console_logger.info(f"LLM stopped successfully: {response}")
        return True
    else:
        console_logger.error(f"Failed to stop LLM: {response}")
        return False