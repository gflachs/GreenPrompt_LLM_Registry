import pytest
import time
from unittest.mock import MagicMock, patch
from app.controller.db_controller import LLMRegistryDbController
import app.services.llm_wrapper_service as lms
from app.models.request import RequestPayload, RequestResponse, RequestStatus, Args, LLMConfig, RequestSingleResponse
from app.services.llm_registry_service import (
    start,
    shutdown,
    request_llm,
    get_request,
    deploy_llm,
    queue_thread,
    process_queue,
    stop_llm,
    release_llm,
    running,
)

@pytest.fixture
def mock_environment(mocker):
    """Fixture to set up mock environment."""
    # Mock deploy_llm
    deploy_llm = mocker.patch("app.services.llm_wrapper_service.deploy_llm")
    stop_llm = mocker.patch("app.services.llm_wrapper_service.stop_llm")


    # Mock LLMRegistryDbController.get_instance
    mocker.patch("app.controller.db_controller.LLMRegistryDbController.get_instance")
    db = MagicMock()
    LLMRegistryDbController.get_instance.return_value = db
    
    #mock uuid.uuid4
    uuid4_mock = mocker.patch("uuid.uuid4")

    return {
        "db": db,
        "deploy_llm": deploy_llm,
        "uuid4_mock": uuid4_mock,
        "stop_llm": stop_llm
    }

def test_deploy_llm_when_deployment_success(mock_environment):
    db = mock_environment["db"]
    deploy_llm_mock = mock_environment["deploy_llm"]
    deploy_llm_mock.return_value = True
    
    
    result = deploy_llm("localhost:5000", {"model": "model", "model_type": "model_type"})
    assert result == True
    assert lms.deploy_llm.called

def test_deploy_llm_when_deployment_failure(mock_environment):
    db = mock_environment["db"]
    deploy_llm_mock = mock_environment["deploy_llm"]
    deploy_llm_mock.return_value = False

    result = deploy_llm("localhost:5000", {"model": "model", "model_type": "model_type"})
    assert result == False
    assert lms.deploy_llm.called
    
def test_request_llm(mock_environment):
    db = mock_environment["db"]

    args1 = Args(prompting={"temperature": 0.7, "user": "test_user"}, deployment={"gpu_enabled": True, "batch_size": 8})
    args2 = Args(prompting={"temperature": 0.7, "user": "test_user"}, deployment={"gpu_enabled": True, "batch_size": 8})
    
    llm_config1 = LLMConfig(modeltyp="https://example.com/model", uses_chat_template=True, model="example-model", args=args1)
    llm_config2 = LLMConfig(modeltyp="https://example.com/model2", uses_chat_template=False,   model="example-model2", args=args2)
    
    request_payload = RequestPayload(llms=[llm_config1, llm_config2], measurementId=1234)
    
    single_request_response1 = RequestSingleResponse(llmconfig=llm_config1, requestId="mocked-uuid-1")
    single_request_response2 = RequestSingleResponse(llmconfig=llm_config2, requestId="mocked-uuid-2")
    
    # Mock UUIDs
    with patch("uuid.uuid4", side_effect=["mocked-uuid-1", "mocked-uuid-2"]):
        request_ids = request_llm(
            request_payload
        )
    
    request_json_llms_0 = request_payload.llms[0].model_dump_json()
    request_json_llms_1 = request_payload.llms[1].model_dump_json()
    # Assertions for add_request calls
    expected_calls = [
        (
            "mocked-uuid-1",
            request_json_llms_0,
            1234
        ),
        (
            "mocked-uuid-2",
            request_json_llms_1,
            1234
        )
    ]
    actual_calls = [
        (
            args[0],  # request_id
            args[1],  # JSON-String aus model_dump_json
            args[2]   # measurementId
        )
        for args, _ in db.add_request.call_args_list
    ]

        
    assert actual_calls == expected_calls

    # Assertions for return values
    assert request_ids.requests == [single_request_response1, single_request_response2]

def test_process_queue(mocker, mock_environment):
    # Mock für is_running mit einer Liste von Werten
    running_values = iter([True, False])  # Erst True, dann False
    
    # Mock is_running-Funktion
    mocker.patch("app.services.llm_registry_service.is_running", side_effect=lambda: next(running_values))
    
    # Mock Abhängigkeiten
    db = mock_environment["db"]
    deploy_llm_mock = mock_environment["deploy_llm"]
    
    # Mock die Datenbank-Rückgabewerte
    db.find_best_deployments.return_value = [
        {"llm_config": {"model": "best_model"}, "address": "localhost:5000", "llm_request_id": "request-1", "wrapper_id": 1, "measurementId": 1000}
    ]
    
    db.get_measurements_waiting_for_deployment.return_value = [
        {"id": 1001, "wrapper_id": None},  # Erstes Measurement (findet einen idle Wrapper)
        {"id": 1002, "wrapper_id": None},  # Zweites Measurement (findet einen ready Wrapper)
        {"id": 1003, "wrapper_id": None},  # Drittes Measurement (kein Wrapper gefunden)
    ]
    
    # Mock für get_next_undeployed_request
    db.get_next_undeployed_request.side_effect = lambda measurementId: {
        1001: {"id": "request-2", "llm_config": {"model": "model2"}, "measurementId": 1001},
        1002: {"id": "request-3", "llm_config": {"model": "model3"}, "measurementId": 1002},
        1003: {"id": "request-4", "llm_config": {"model": "model4"}, "measurementId": 1003},
    }.get(measurementId, None)
    
    idle_wrapper_responses = iter([
        [{"id": "idle_wrapper", "address": "localhost:8080", "status" : "idle"}],  # Erstes Mal gibt es einen Wrapper
        [],
        []
    ])

    # Iterator für "ready" Status
    ready_wrapper_responses = iter([
        [{"id": "ready_wrapper", "address": "localhost:8081", "status" : "ready"}],  # Erstes Mal gibt es einen Wrapper
        [],
        []
    ])
    
    # Mock für Wrapper-Status
    db.get_all_wrapper_with_status.side_effect = lambda status: (
        next(idle_wrapper_responses) if status == "idle" else
        next(ready_wrapper_responses) if status == "ready" else
        []
    )
    
    deploy_llm_mock.side_effect = lambda config, wrapper: wrapper != "no_wrapper"
    
    # Patch time.sleep, um Verzögerungen zu vermeiden
    mocker.patch("app.services.llm_registry_service.time.sleep", return_value=None)
    
    # Teste die Prozess-Schleife
    process_queue()
    
    # Assertions für die besten Deployments
    db.find_best_deployments.assert_called_once()
    #deploy_llm_mock.assert_any_call({"model": "best_model"}, "localhost:5000")
    db.set_request_address.assert_any_call("request-1", "localhost:5000")
    db.change_llm_wrapper_status_by_id.assert_any_call(1, "prompting")
    db.update_measurement_wrapper_id.assert_any_call(1000, 1)
    db.update_measurement_status(1000, "prompting")
    unwanted_call = (1, {"model": "best_model"})

    # Überprüfe, ob der unerwünschte Call in der Aufrufliste enthalten ist
    assert unwanted_call not in db.change_llm_wrapper_config_by_id.call_args_list, \
        f"change_llm_wrapper_config_by_id wurde unerwartet mit {unwanted_call} aufgerufen."

    
    # Assertions für Measurements
    db.get_measurements_waiting_for_deployment.assert_called_once()
    
    # Measurement 1: Idle Wrapper gefunden
    db.get_next_undeployed_request.assert_any_call(1001)
    deploy_llm_mock.assert_any_call("localhost:8080", {"model": "model2"})
    db.set_request_address.assert_any_call("request-2", "localhost:8080")
    db.change_llm_wrapper_status_by_id.assert_any_call("idle_wrapper", "prompting")
    db.update_measurement_wrapper_id.assert_any_call(1001, "idle_wrapper")
    db.update_measurement_status(1001, "prompting")
    db.change_llm_wrapper_config_by_id.assert_any_call("idle_wrapper", {"model": "model2"})
    db.change_llm_wrapper_status_by_address("localhost:8080", "deploying")

    
    # Measurement 2: Ready Wrapper gefunden
    db.get_next_undeployed_request.assert_any_call(1002)
    deploy_llm_mock.assert_any_call("localhost:8081", {"model": "model3"})
    db.set_request_address.assert_any_call("request-3", "localhost:8081")
    db.change_llm_wrapper_status_by_id.assert_any_call("ready_wrapper", "prompting")
    db.update_measurement_wrapper_id.assert_any_call(1002, "ready_wrapper")
    db.update_measurement_status(1002, "prompting")
    db.change_llm_wrapper_config_by_id.assert_any_call("ready_wrapper", {"model": "model3"})
    db.change_llm_wrapper_status_by_address("localhost:8081", "deploying")
    db.change_llm_wrapper_status_by_id(1, "idle")

    
    # Measurement 3: Kein Wrapper gefunden
    db.get_next_undeployed_request.assert_any_call(1003)


# test queue processing, when a measurement has already a wrapper assigned
def test_process_queue_with_wrapper_assigned(mocker, mock_environment):
    # Mock für is_running mit einer Liste von Werten
    running_values = iter([True, False])  # Erst True, dann False
    
    # Mock is_running-Funktion
    mocker.patch("app.services.llm_registry_service.is_running", side_effect=lambda: next(running_values))
    
    # Mock Abhängigkeiten
    db = mock_environment["db"]
    deploy_llm_mock = mock_environment["deploy_llm"]
    
    # Mock die Datenbank-Rückgabewerte
    db.find_best_deployments.return_value = []
    
    db.get_measurements_waiting_for_deployment.return_value = [
        {"id": 1001, "wrapper_id": "assigned_wrapper"},  # Erstes Measurement (findet einen idle Wrapper)
    ]
    
    # Mock für get_next_undeployed_request
    db.get_wrapper_by_id.return_value = {"id": "assigned_wrapper", "address": "localhost:8080", "status" : "idle"}
    
    db.get_next_undeployed_request.return_value = {"id": "request-2", "llm_config": {"model": "model2"}, "measurementId": 1001}
    
    # Patch time.sleep, um Verzögerungen zu vermeiden
    mocker.patch("app.services.llm_registry_service.time.sleep", return_value=None)
    
    # Teste die Prozess-Schleife
    process_queue()
    
    # Assertions für die besten Deployments
    db.find_best_deployments.assert_called_once()
    db.get_wrapper_by_id.assert_called_once()
    deploy_llm_mock.assert_any_call("localhost:8080",{"model": "model2"})
    db.set_request_address.assert_any_call("request-2", "localhost:8080")
    db.change_llm_wrapper_status_by_id.assert_any_call("assigned_wrapper", "prompting")
    db.update_measurement_status.assert_any_call(1001, "prompting")
    db.change_llm_wrapper_config_by_id.assert_any_call("assigned_wrapper", {"model": "model2"})
    db.change_llm_wrapper_status_by_address("localhost:8080", "deploying")
    
    #make sure that no other functions are called
    db.get_wrapper_by_status.assert_not_called()
    db.update_measurement_wrapper_id.assert_not_called()
    
# test queue processing, when a measurement has already a wrapper assigned, but the wrapper is prompting
def test_process_queue_with_prompting_wrapper_assigned(mocker, mock_environment):
    # Mock für is_running mit einer Liste von Werten
    running_values = iter([True, False])  # Erst True, dann False
    
    # Mock is_running-Funktion
    mocker.patch("app.services.llm_registry_service.is_running", side_effect=lambda: next(running_values))
    
    # Mock Abhängigkeiten
    db = mock_environment["db"]
    deploy_llm_mock = mock_environment["deploy_llm"]
    
    # Mock die Datenbank-Rückgabewerte
    db.find_best_deployments.return_value = []
    
    db.get_measurements_waiting_for_deployment.return_value = [
        {"id": 1001, "wrapper_id": "assigned_wrapper"},  # Erstes Measurement (findet einen idle Wrapper)
    ]
    
    # Mock für get_next_undeployed_request
    db.get_wrapper_by_id.return_value = {"id": "assigned_wrapper", "address": "localhost:8080", "status" : "prompting"}
    
    db.get_next_undeployed_request.return_value = {"id": "request-2", "config": {"model": "model2"}, "measurementId": 1001}
    
    # Patch time.sleep, um Verzögerungen zu vermeiden
    mocker.patch("app.services.llm_registry_service.time.sleep", return_value=None)
    
    # Teste die Prozess-Schleife
    process_queue()
    
    # Assertions für die besten Deployments
    db.find_best_deployments.assert_called_once()
    db.get_wrapper_by_id.assert_called_once_with("assigned_wrapper")

    
    #make sure that no other functions are called
    db.get_wrapper_by_status.assert_not_called()
    db.update_measurement_wrapper_id.assert_not_called()
    deploy_llm_mock.assert_not_called()
    db.set_request_address.assert_not_called()
    db.change_llm_wrapper_status_by_id.assert_not_called()
    db.update_measurement_status.assert_not_called()
    db.change_llm_wrapper_config_by_id.assert_not_called()
    
# test queue processing, when no measurement is waiting for deployment
def test_process_queue_no_measurement_waiting(mocker, mock_environment):
    # Mock für is_running mit einer Liste von Werten
    running_values = iter([True, False])  # Erst True, dann False
    
    # Mock is_running-Funktion
    mocker.patch("app.services.llm_registry_service.is_running", side_effect=lambda: next(running_values))
    
    # Mock Abhängigkeiten
    db = mock_environment["db"]
    deploy_llm_mock = mock_environment["deploy_llm"]
    
    # Mock die Datenbank-Rückgabewerte
    db.find_best_deployments.return_value = []
    
    db.get_measurements_waiting_for_deployment.return_value = []
    
    # Patch time.sleep, um Verzögerungen zu vermeiden
    mocker.patch("app.services.llm_registry_service.time.sleep", return_value=None)
    
    # Teste die Prozess-Schleife
    process_queue()
    
    # Assertions für die besten Deployments
    db.find_best_deployments.assert_called_once()
    
    #make sure that no other functions are called
    db.get_wrapper_by_status.assert_not_called()
    db.get_next_undeployed_request.assert_not_called()
    deploy_llm_mock.assert_not_called()
    db.set_request_address.assert_not_called()
    db.change_llm_wrapper_status_by_id.assert_not_called()
    db.update_measurement_status.assert_not_called()
    db.update_measurement_wrapper_id.assert_not_called()
    db.change_llm_wrapper_config_by_id.assert_not_called()
    
def test_get_request(mock_environment):
    db = mock_environment["db"]
    
    llm_config = LLMConfig(modeltyp="https://example.com/model", model="example-model", uses_chat_template=True, args=Args(prompting={"temperature": 0.7, "user": "test_user"}, deployment={"gpu_enabled": True, "batch_size": 8}))
    
    
    db.get_request.return_value = {"id": "request-1", "llm_config": llm_config.model_dump_json(), "status": "queued", "measurementId": 1234, "address": "localhost:5000"}
    
    request = get_request("request-1")
    
    assert request == RequestStatus(requestId="request-1", llmconfig=llm_config, status="queued", measurementId=1234, address="localhost:5000")
    
    db.get_request.assert_called_once_with("request-1")

def test_stop_llm(mock_environment):
    db = mock_environment["db"]
    stop_llm_mock = mock_environment["stop_llm"]
    
    db.get_wrapper_by_id.return_value = {"id": "wrapper-1", "address": "localhost:5000", "status": "running"}
    
    stop_llm_mock.return_value = True
    
    result = stop_llm("wrapper-1", "localhost:5000")
    
    
    assert result == True
    
    stop_llm_mock.assert_called_once_with("localhost:5000")
    db.change_llm_wrapper_status_by_id.assert_called_once_with("wrapper-1", "stopping")
    
def test_stop_llm_with_failed_stop(mock_environment):
    db = mock_environment["db"]
    stop_llm_mock = mock_environment["stop_llm"]
    
    db.get_wrapper_by_id.return_value = {"id": "wrapper-1", "address": "localhost:5000", "status": "running"}
    
    stop_llm_mock.return_value = False
    
    result = stop_llm("wrapper-1", "localhost:5000")
    
    
    assert result == False
    
    stop_llm_mock.assert_called_once_with("localhost:5000")
    db.change_llm_wrapper_status_by_id.assert_any_call("wrapper-1", "stopping")
    
def test_release_llm(mock_environment):
    db = mock_environment["db"]
    
    db.get_request.return_value = {"id": "request-1", "config": {"model": "model1", "model_type": "model_type1"}, "status": "queued", "measurementId": 1234, "address": "localhost:5000"}
    db.get_wrapper_by_address.return_value = {"id": "wrapper-1", "address": "localhost:5000", "status": "prompting"}
    
    release_llm("request-1")
    
    db.get_request.assert_called_once_with("request-1")
    db.get_wrapper_by_address.assert_called_once_with("localhost:5000")
    db.change_llm_wrapper_status_by_id.assert_called_once_with("wrapper-1", "not_ready")
    db.update_measurement_status.assert_called_once_with(1234, "deployments_pending")
    
