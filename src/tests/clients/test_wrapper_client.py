import pytest
from unittest.mock import MagicMock, patch
from app.clients.wrapper_client import (
    deploy_llm, stop_llm, check_status, stop_wrapper, restart_llm_wrapper, deploy_fastapi_service
)


@patch("app.clients.wrapper_client.requests")
def test_deploy_llm(mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "ready"}
    mock_requests.post.return_value = mock_response

    llm_address = "localhost"
    llm_config_json = {
        "model": "test_model",
        "model_type": "test_model_type"
    }

    # Test successful deployment
    assert deploy_llm(llm_address, llm_config_json) == "ready"

    # Test failed deployment
    mock_response.status_code = 400
    mock_response.json.return_value = {"status": "not ready"}
    assert deploy_llm(llm_address, llm_config_json) == "failure"


@patch("app.clients.wrapper_client.requests")
def test_stop_llm(mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "stopped"}
    mock_requests.post.return_value = mock_response

    llm_address = "localhost"

    # Test successful stop
    assert stop_llm(llm_address) == "stopped"

    # Test failed stop
    mock_response.status_code = 400
    mock_response.json.return_value = {"status": "not stopped"}
    assert stop_llm(llm_address) == "failure"


@patch("app.clients.wrapper_client.requests")
def test_check_status(mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": "running"}
    mock_requests.get.return_value = mock_response

    llm_address = "localhost"

    # Test successful status check
    assert check_status(llm_address) == "running"

    # Test failed status check
    mock_response.status_code = 400
    mock_response.json.return_value = {"message": "unknown"}
    assert check_status(llm_address) == "failure"


@patch("app.clients.wrapper_client.paramiko.SSHClient")
def test_stop_wrapper(mock_ssh_client):
    mock_ssh = MagicMock()
    mock_ssh_client.return_value = mock_ssh

    # Mock successful SSH execution
    mock_stdout = MagicMock()
    mock_stdout.read.return_value = b"Service stopped"
    mock_stderr = MagicMock()
    mock_stderr.read.return_value = b""

    mock_ssh.exec_command.return_value = (None, mock_stdout, mock_stderr)

    wrapper_ip = "127.0.0.1"
    wrapper_username = "user"
    wrapper_password = "pass"

    assert stop_wrapper(wrapper_ip, wrapper_password, wrapper_username) is True

    # Mock SSH error
    mock_stderr.read.return_value = b"Error stopping service"
    assert stop_wrapper(wrapper_ip, wrapper_password, wrapper_username) is False


@patch("app.clients.wrapper_client.paramiko.SSHClient")
def test_restart_llm_wrapper(mock_ssh_client):
    mock_ssh = MagicMock()
    mock_ssh_client.return_value = mock_ssh

    # Mock successful SSH execution
    mock_stdout = MagicMock()
    mock_stdout.read.return_value = b"Service restarted"
    mock_stderr = MagicMock()
    mock_stderr.read.return_value = b""

    mock_ssh.exec_command.return_value = (None, mock_stdout, mock_stderr)

    wrapper_ip = "127.0.0.1"
    wrapper_username = "user"
    wrapper_password = "pass"

    assert restart_llm_wrapper(wrapper_ip, wrapper_password, wrapper_username) is True

    # Mock SSH error
    mock_stderr.read.return_value = b"Error restarting service"
    assert restart_llm_wrapper(wrapper_ip, wrapper_password, wrapper_username) is False


@patch("app.clients.wrapper_client.execute_ssh_command")
def test_deploy_fastapi_service(mock_execute_ssh_command):
    mock_execute_ssh_command.return_value = ("Success", "", 0)

    wrapper_ip = "127.0.0.1"
    username = "user"
    password = "pass"

    # Test successful deployment
    assert deploy_fastapi_service(wrapper_ip, username, password) is True

    # Mock a failing command
    mock_execute_ssh_command.return_value = ("", "Error during deployment", 1)
    assert deploy_fastapi_service(wrapper_ip, username, password) is False
