import pytest
import time
from unittest.mock import MagicMock, patch
from app.clients.wrapper_client import deploy_llm, stop_llm

@patch("app.clients.wrapper_client.requests")
def test_deploy_llm(mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "ready"}
    mock_requests.post.return_value = mock_response
    llm_address = "http://localhost:5000"
    llm_config_json = {
        "model": "test_model",
        "model_type": "test_model_type"
    }
    assert deploy_llm(llm_address, llm_config_json) == "ready"

    mock_response.status_code = 400
    mock_response.json.return_value = {"status": "not ready"}
    assert deploy_llm(llm_address, llm_config_json) == "failure"
    
@patch("app.clients.wrapper_client.requests")
def test_stop_llm(mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "stopped"}
    mock_requests.post.return_value = mock_response
    llm_address = "http://localhost:5000"
    assert stop_llm(llm_address) == "stopped"

    mock_response.status_code = 400
    mock_response.json.return_value = {"status": "not stopped"}
    assert stop_llm(llm_address) == "failure"
    
    