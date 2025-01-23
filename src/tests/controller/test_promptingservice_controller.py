import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app  # Deine FastAPI-Anwendung
from app.models.request import RequestPayload, RequestResponse, RequestStatus, LLMConfig, Args, RequestSingleResponse

client = TestClient(app)  # Test-Client erstellen

# Fixture für Beispiel-Request-Payload
@pytest.fixture
def sample_request_payload():
    return {
        "llms": [
            {
                "modeltyp": "https://example.com/model",
                "model": "example-model",
                "uses_chat_template": True,
                "args": {
                    "prompting": {"temperature": 0.7, "user": "test_user"},
                    "deployment": {"gpu_enabled": True, "batch_size": 8}
                }
            }
        ],
        "measurementId": 1234
    }

@pytest.fixture
def sample_request_invalid_payload_missing_url():
    return {
        "llms": [
            {
                "model": "example-model",
                "uses_chat_template": True,
                "args": {
                    "prompting": {"temperature": 0.7, "user": "test_user"},
                    "deployment": {"gpu_enabled": True, "batch_size": 8}
                }
            }
        ],
        "measurementId": 1234
    }
    
@pytest.fixture
def sample_request_invalid_payload_missing_model():
    return {
        "llms": [
            {
                "modeltyp": "https://example.com/model",
                "uses_chat_template": True,
                "args": {
                    "prompting": {"temperature": 0.7, "user": "test_user"},
                    "deployment": {"gpu_enabled": True, "batch_size": 8}
                }
            }
        ],
        "measurementId": 1234
    }
    
@pytest.fixture
def sample_request_invalid_payload_missing_deplyoment_args():
    return {
        "llms": [
            {
                "modeltyp": "https://example.com/model",
                "model": "example-model",
                "uses_chat_template": True,
                "args": {
                    "prompting": {"temperature": 0.7, "user": "test_user"}
                }
            }
        ],
        "measurementId": 1234
    }
    
@pytest.fixture
def sample_request_invalid_payload_missing_prompting_args():
    return {
        "llms": [
            {
                "modeltyp": "https://example.com/model",
                "model": "example-model",
                "uses_chat_template": True,
                "args": {
                    "deployment": {"gpu_enabled": True, "batch_size": 8}
                }
            }
        ],
        "measurementId": 1234
    }
    
@pytest.fixture
def sample_request_invalid_payload_missing_measurementId():
    return {
        "llms": [
            {
                "modeltyp": "https://example.com/model",
                "model": "example-model",
                "uses_chat_template": True,
                "args": {
                    "prompting": {"temperature": 0.7, "user": "test_user"},
                    "deployment": {"gpu_enabled": True, "batch_size": 8}
                }
            }
        ]
    }
    
    

# Mock für POST /request
@patch("app.services.llm_registry_service.request_llm")
def test_post_request_with_mock(mock_request_llm, sample_request_payload):
    
    request = RequestPayload.model_validate(sample_request_payload)
    single_response = RequestSingleResponse(llmconfig=request.llms[0], requestId="1")
    response = RequestResponse(requests=[single_response])


    # Mock die Rückgabe von lms.request_llm
    mock_request_llm.return_value = response
    
    response = client.post("/promptingservice/request", json=sample_request_payload)
    
    assert response.status_code == 201
    response_data = response.json()
    
    # Überprüfen, ob die Mock-Funktion aufgerufen wurde
    mock_request_llm.assert_called_once_with(request)
    
    # Überprüfen der API-Antwort
    assert "requests" in response_data
    assert len(response_data["requests"]) == 1
    assert response_data["requests"][0]["requestId"] == "1"
    
@patch("app.services.llm_registry_service.request_llm")
def test_post_request_with_mock_invalid_payload(mock_request_llm, sample_request_invalid_payload_missing_url, sample_request_invalid_payload_missing_model, sample_request_invalid_payload_missing_deplyoment_args, sample_request_invalid_payload_missing_prompting_args, sample_request_invalid_payload_missing_measurementId):
    
    response = client.post("/promptingservice/request", json=sample_request_invalid_payload_missing_url)
    assert response.status_code == 422
    
    response = client.post("/promptingservice/request", json=sample_request_invalid_payload_missing_model)
    assert response.status_code == 422
    
    response = client.post("/promptingservice/request", json=sample_request_invalid_payload_missing_deplyoment_args)
    assert response.status_code == 422
    
    response = client.post("/promptingservice/request", json=sample_request_invalid_payload_missing_prompting_args)
    assert response.status_code == 422
    
    response = client.post("/promptingservice/request", json=sample_request_invalid_payload_missing_measurementId)
    assert response.status_code == 422

    # Überprüfen, ob die Mock-Funktion aufgerufen wurde
    mock_request_llm.assert_not_called()
    
    # Überprüfen der API-Antwort
    assert response.status_code == 422


# Mock für GET /request/{request_id}
@patch("app.services.llm_registry_service.get_request")
def test_get_request_with_mock(mock_get_request):
    # Mock die Rückgabe von lms.get_request
    request = RequestStatus(
        requestId="1",
        llmconfig=LLMConfig(modeltyp="http://example.com/model", model="example-model", uses_chat_template=True, args=Args(prompting={"temperature": 0.7, "user": "test_user"}, deployment={"gpu_enabled": True, "batch_size": 8})),
        status="completed",
        measurementId=1234,
        address="http://example.com/request/1"
    )
    mock_get_request.return_value = request
    
    response = client.get("/promptingservice/request/1")
    
    assert response.status_code == 200
    response_data = response.json()
    
    # Überprüfen, ob die Mock-Funktion aufgerufen wurde
    mock_get_request.assert_called_once_with("1")
    
    # Überprüfen der API-Antwort
    assert response_data["requestId"] == "1"
    assert response_data["status"] == "completed"
    assert response_data["address"] == "http://example.com/request/1"


# Mock für DELETE /request/{request_id}
@patch("app.services.llm_registry_service.release_llm")
def test_delete_request_with_mock(mock_release_llm):
    # Mock für release_llm (keine Rückgabe nötig, da DELETE 204 ist)
    mock_release_llm.return_value = None

    response = client.delete("/promptingservice/request/1")

    assert response.status_code == 204
    assert response.text == ""  # Keine Antwort erwartet
    
    # Überprüfen, ob die Mock-Funktion aufgerufen wurde
    mock_release_llm.assert_called_once_with("1")
