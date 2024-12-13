import pytest
import time
from unittest.mock import MagicMock, patch
from app.services.llm_wrapper_service import deploy_llm, stop_llm

@patch("app.services.llm_wrapper_service.wrapper_client")
def test_deploy_llm(mock_wrapper_client):
    mock_wrapper_client.deploy_llm.return_value = "ready"
    llm_address = "http://localhost:5000"
    llm_config_json = {
        "model": "test_model",
        "model_type": "test_model_type"
    }
    assert deploy_llm(llm_address, llm_config_json) == True

    mock_wrapper_client.deploy_llm.return_value = "not ready"
    assert deploy_llm(llm_address, llm_config_json) == False
    
@patch("app.services.llm_wrapper_service.wrapper_client")
def test_stop_llm(mock_wrapper_client):
    mock_wrapper_client.stop_llm.return_value = "stopped"
    llm_address = "http://localhost:5000"
    assert stop_llm(llm_address) == True

    mock_wrapper_client.stop_llm.return_value = "not stopped"
    assert stop_llm(llm_address) == False