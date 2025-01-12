import pytest
import time
from unittest.mock import MagicMock, patch
from app.utils.configreader import ConfigReader

@pytest.fixture(autouse=True)
def reset_singleton():
    # Vor jedem Test das Singleton zurücksetzen
    ConfigReader._instance = None
    yield
    # Nach dem Test kannst du es optional auch wieder auf None setzen
    ConfigReader._instance = None

def test_get(mocker):    
    mock_configparser = mocker.patch("app.utils.configreader.configparser")
    mock_cfg = MagicMock()
    mock_configparser.ConfigParser.return_value = mock_cfg
    mock_cfg.get.return_value = "test_value"
    
    config_reader = ConfigReader.get_instance()
    assert config_reader.get("test_section", "test_option") == "test_value"

def test_validate_llm_wrapper_config_valid_json():
    config_reader = ConfigReader.get_instance()
    valid_json_list = [
        '[]',  # leere Liste
        '[{"ip_address": "127.0.0.1", "user": "root", "password": "toor"}]',  # Liste mit einem Element
        '[{"ip_address": "127.0.0.1", "user": "root", "password": "toor"}, {"ip_address": "192.168.1.1", "user": "admin", "password": "admin"}]'  # Liste mit mehreren Elementen
    ]
    for valid_json in valid_json_list:
        if valid_json == '[]':
            assert config_reader.validate_llm_wrapper_config(valid_json) == "The 'llm_wrapper_machines' list is empty."
        else:
            try:
                config_reader.validate_llm_wrapper_config(valid_json)
            except ValueError:
                pytest.fail(f"validate_llm_wrapper_config raised ValueError unexpectedly for valid JSON: {valid_json}")

def test_validate_llm_wrapper_config_invalid_json():
    config_reader = ConfigReader.get_instance()
    invalid_json_list = [
        'invalid_json',  # kein JSON
        '{"ip_address": "127.0.0.1", "user": "root", "password": "toor"',   # kein JSON-Array
        '[{"ip_address": "127.0.0.1", "user": "root", "password": "toor"',  # unvollständiges JSON
        '{ip_address: "127.0.0.1", user: "root", password: "toor"}',        # fehlende Anführungszeichen
        '{"ip_address": "127.0.0.1", "user": "root", "password": "toor",}'  # zusätzliches Komma
    ]
    for invalid_json in invalid_json_list:
        with pytest.raises(ValueError, match=r"Invalid JSON value: .*"):
            config_reader.validate_llm_wrapper_config(invalid_json)