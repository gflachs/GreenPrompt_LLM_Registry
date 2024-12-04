from typing import Dict
import app.clients.wrapper_client as wrapper_client

'''
This module manages the interaction between the LLM Wrapper and the LLM Registry. Its resonsible for starting and stopping the LLMs in the Wrapper.
Therefore it provides the following functions:
- you can request an LLM instance for a specific model configuration
- the service deploys an LLM instance into an LLM Wrapper
- the service can stop an LLM instance if it is no longer needed
- more function will be added in the future
'''

def deploy_llm(llm_address: str,llm_config_json: Dict):
    result = wrapper_client.deploy_llm(llm_address, llm_config_json)
    if result is None:
        return False
    if result.status_code == 200:
        return True
    return False
    

def stop_llm(lm_address: str):
    result = wrapper_client.stop_llm(lm_address)
    if result is None:
        return False
    if result.status_code == 200:
        return True
    return False