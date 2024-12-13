import pytest
import time
from unittest.mock import MagicMock, patch
from app.services.llm_wrapper_status_service import check_status

def test_status_check(mocker):
    running_values = iter([True, False])  # Erst True, dann False
    mock_db_controller = mocker.patch("app.services.llm_wrapper_status_service.LLMRegistryDbController")
    mock_db_controller.get_instance.return_value = mock_db_controller
    mock_db_controller.get_all_wrappers.return_value = [{"address": "http://localhost:5000", "id": 1}]
    mock_db_controller.change_llm_wrapper_status_by_id.return_value = "ready"
    
    mock_wrapper_client = mocker.patch("app.services.llm_wrapper_status_service.wrapper_client")
    mock_wrapper_client.check_status.return_value = "ready"
    mocker.patch("app.services.llm_wrapper_status_service.is_running", side_effect=lambda: next(running_values))
    mocker.patch("app.services.llm_wrapper_status_service.time.sleep", side_effect=lambda x: None)

    check_status()
    mock_db_controller.get_all_wrappers.assert_called()
    mock_wrapper_client.check_status.assert_called_with("http://localhost:5000")
    mock_db_controller.change_llm_wrapper_status_by_id.assert_called_with(1, "ready")