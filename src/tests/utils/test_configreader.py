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
    
    config_reader = ConfigReader()
    assert config_reader.get("test_section", "test_option") == "test_value"
