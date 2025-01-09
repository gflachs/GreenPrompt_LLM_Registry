import pytest
import time
from unittest.mock import MagicMock, patch
from app.services.llm_wrapper_status_service import check_status
from app.controller.db_controller import LLMRegistryDbController

@pytest.fixture(autouse=True)
def reset_singleton():
    # Vor jedem Test das Singleton zurücksetzen
    LLMRegistryDbController._instance = None
    yield
    # Nach dem Test kannst du es optional auch wieder auf None setzen
    LLMRegistryDbController._instance = None

def test_status_check(mocker):
    running_values = iter([True, False])  # Erst True, dann False
    mock_db_controller = mocker.patch("app.services.llm_wrapper_status_service.LLMRegistryDbController")
    mock_db_controller.get_instance.return_value = mock_db_controller
    mock_db_controller.get_all_wrappers.return_value = [{"address": "http://localhost:5000", "id": 1, "status": "ready"}]
    mock_db_controller.change_llm_wrapper_status_by_id.return_value = "ready"
    
    mock_wrapper_client = mocker.patch("app.services.llm_wrapper_status_service.wrapper_client")
    mock_wrapper_client.check_status.return_value = "ready"
    mocker.patch("app.services.llm_wrapper_status_service.is_running", side_effect=lambda: next(running_values))
    mocker.patch("app.services.llm_wrapper_status_service.time.sleep", side_effect=lambda x: None)

    check_status()
    mock_db_controller.get_all_wrappers.assert_called()
    mock_wrapper_client.check_status.assert_called_with("http://localhost:5000")
    mock_db_controller.change_llm_wrapper_status_by_id.assert_called_with(1, "ready")
    
def test_status_not_checked_if_deployment(mocker):
    running_values = iter([True, False])  # Erst True, dann False
    mock_db_controller = mocker.patch("app.services.llm_wrapper_status_service.LLMRegistryDbController")
    mock_db_controller.get_instance.return_value = mock_db_controller
    mock_db_controller.get_all_wrappers.return_value = [{"address": "http://localhost:5000", "id": 1, "status": "deploying"}]
    mock_db_controller.change_llm_wrapper_status_by_id.return_value = "deploying"
    
    mock_wrapper_client = mocker.patch("app.services.llm_wrapper_status_service.wrapper_client")
    mock_wrapper_client.check_status.return_value = "deploying"
    mocker.patch("app.services.llm_wrapper_status_service.is_running", side_effect=lambda: next(running_values))
    mocker.patch("app.services.llm_wrapper_status_service.time.sleep", side_effect=lambda x: None)

    check_status()
    mock_db_controller.get_all_wrappers.assert_called()
    mock_wrapper_client.check_status.assert_not_called()
    mock_db_controller.change_llm_wrapper_status_by_id.assert_not_called()
    
def test_status_not_checked_if_stopping(mocker):
    running_values = iter([True, False])  # Erst True, dann False
    mock_db_controller = mocker.patch("app.services.llm_wrapper_status_service.LLMRegistryDbController")
    mock_db_controller.get_instance.return_value = mock_db_controller
    mock_db_controller.get_all_wrappers.return_value = [{"address": "http://localhost:5000", "id": 1, "status": "stopping"}]
    mock_db_controller.change_llm_wrapper_status_by_id.return_value = "stopping"
    
    mock_wrapper_client = mocker.patch("app.services.llm_wrapper_status_service.wrapper_client")
    mock_wrapper_client.check_status.return_value = "stopping"
    mocker.patch("app.services.llm_wrapper_status_service.is_running", side_effect=lambda: next(running_values))
    mocker.patch("app.services.llm_wrapper_status_service.time.sleep", side_effect=lambda x: None)

    check_status()
    mock_db_controller.get_all_wrappers.assert_called()
    mock_wrapper_client.check_status.assert_not_called()
    mock_db_controller.change_llm_wrapper_status_by_id.assert_not_called()
    
def test_status_not_checked_if_restarting(mocker):
    running_values = iter([True, False])  # Erst True, dann False
    mock_db_controller = mocker.patch("app.services.llm_wrapper_status_service.LLMRegistryDbController")
    mock_db_controller.get_instance.return_value = mock_db_controller
    mock_db_controller.get_all_wrappers.return_value = [{"address": "http://localhost:5000", "id": 1, "status": "restarting"}]
    mock_db_controller.change_llm_wrapper_status_by_id.return_value = "restarting"
    
    mock_wrapper_client = mocker.patch("app.services.llm_wrapper_status_service.wrapper_client")
    mock_wrapper_client.check_status.return_value = "restarting"
    mocker.patch("app.services.llm_wrapper_status_service.is_running", side_effect=lambda: next(running_values))
    mocker.patch("app.services.llm_wrapper_status_service.time.sleep", side_effect=lambda x: None)

    check_status()
    mock_db_controller.get_all_wrappers.assert_called()
    mock_wrapper_client.check_status.assert_not_called()
    mock_db_controller.change_llm_wrapper_status_by_id.assert_not_called()
    
import pytest
from unittest.mock import patch

def test_redeployment_when_status_failure(mocker):
    # Immitiere, dass die Schleife 1-mal durchläuft (True) und dann stoppt (False).
    running_values = iter([True, False])
    
    # Patch DB-Controller
    mock_db_controller = mocker.patch("app.services.llm_wrapper_status_service.LLMRegistryDbController")
    mock_db_controller.get_instance.return_value = mock_db_controller
    mock_db_controller.get_all_wrappers.return_value = [{
        "address": "http://localhost:5000",
        "id": 1,
        "status": "failure",
        "username": "root",
        "password": "secret"
    }]
    
    # Patch `is_running` damit die while-Schleife nur einmal durchläuft
    mocker.patch("app.services.llm_wrapper_status_service.is_running", side_effect=lambda: next(running_values))
    # Zeitpatch, damit kein echtes Sleep passiert
    mocker.patch("app.services.llm_wrapper_status_service.time.sleep", side_effect=lambda x: None)
    
    # **Wichtig**: Patch die Funktion, die den Thread startet:
    with patch("app.services.llm_wrapper_status_service.restart_wrapper_in_background") as mock_restart_bg:
        from app.services.llm_wrapper_status_service import check_status
        check_status()

        # 1) Wurde "get_all_wrappers" aufgerufen?
        mock_db_controller.get_all_wrappers.assert_called_once()

        # 2) Status muss auf "restarting" gesetzt werden
        mock_db_controller.change_llm_wrapper_status_by_id.assert_any_call(1, "restarting")
        
        # 3) Wurde die „Hintergrund-Neustart“-Funktion aufgerufen?
        mock_restart_bg.assert_called_once_with(
            1,
            "http://localhost:5000",
            "secret",
            "root"
        )

