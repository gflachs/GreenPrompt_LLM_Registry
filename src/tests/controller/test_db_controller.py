import pytest
import time
from unittest.mock import MagicMock, patch
from app.controller.db_controller import LLMRegistryDbController, DatabaseController
from app.utils.configreader import ConfigReader

@pytest.fixture
def mock_db_controller(mocker):
    db_controller = MagicMock()
    mocker.patch('app.controller.db_controller.DatabaseController.get_instance', return_value=db_controller)
    return db_controller



@pytest.fixture
def mock_config_reader(mocker):
    config_reader = MagicMock()
    config_reader.get.return_value = "test_db"
    mocker.patch('app.utils.configreader.ConfigReader.get_instance', return_value=config_reader)
    return config_reader

@pytest.fixture(autouse=True)
def reset_singletons():
    from app.controller.db_controller import DatabaseController, LLMRegistryDbController
    # Zugriff auf die privat umbenannten Variablen der Singleton-Instanz
    DatabaseController._DatabaseController__instance = None
    LLMRegistryDbController._LLMRegistryDbController__instance = None




def test_singleton(mock_db_controller, mock_config_reader):
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    db_controller2 = LLMRegistryDbController.get_instance()
    assert db_controller == db_controller2
    

    
def test_table_creation(mock_db_controller, mock_config_reader):

    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    
    mock_db_controller.create_table.assert_any_call("llm_wrapper", [
            ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
            ("llm", "TEXT"),
            ("llm_config", "TEXT"),
            ("address", "TEXT"),
            ("username", "TEXT"),
            ("password", "TEXT"),
            ("status", "TEXT")
        ])
    
    mock_db_controller.create_table.assert_any_call("llm_request", [
            ("id", "TEXT PRIMARY KEY"),
            ("llm_config", "TEXT"),
            ("status", "TEXT"),
            ("measurementId", "INTEGER"),
            ("address", "TEXT")
        ])
    
    mock_db_controller.create_table.assert_any_call("measurements", [
            ("id", "INTEGER PRIMARY KEY"),
            ("status", "TEXT"),
            ("wrapper_id", "INTEGER")
        ])
    
def test_insert_wrapper(mock_db_controller, mock_config_reader):
        
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    db_controller.add_llm_wrapper("llm", "config", "address", "root", "password", "status")
    
    mock_db_controller.insert_data.assert_called_once_with("llm_wrapper", [("llm", "config", "address", "root", "password", "status")], ["llm", "llm_config", "address", "username", "password", "status"])
        
def test_get_llm_wrappers(mock_db_controller, mock_config_reader):
        
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    mock_db_controller.fetch_all.return_value = [{"id": 1, "llm": "llm", "llm_config": "config", "address": "address", "status": "status"}]
    
    wrappers= db_controller.get_llm_wrappers()
    
    mock_db_controller.fetch_all.assert_called_once_with("llm_wrapper")
    
    assert len(wrappers) == 1
    assert wrappers[0]["id"] == 1
    assert wrappers[0]["llm"] == "llm"
    assert wrappers[0]["llm_config"] == "config"
    assert wrappers[0]["address"] == "address"
    assert wrappers[0]["status"] == "status"
    
def test_change_llm_wrapper_status_by_id(mock_db_controller, mock_config_reader):
        
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    db_controller.change_llm_wrapper_status_by_id(1, "status")
    
    mock_db_controller.update_data.assert_called_once_with("llm_wrapper", "status", "status", "id", 1)
    
def test_change_llm_wrapper_config_by_id(mock_db_controller, mock_config_reader):
            
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    db_controller.change_llm_wrapper_config_by_id(1, "config")
    
    mock_db_controller.update_data.assert_called_once_with("llm_wrapper", "llm_config", "config", "id", 1)

def test_change_llm_wrapper_status_by_address(mock_db_controller, mock_config_reader):
        
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    db_controller.change_llm_wrapper_status_by_address("address", "status")
    
    mock_db_controller.update_data.assert_called_once_with("llm_wrapper", "status", "status", "address", "address")
    
def test_get_all_wrapper_with_status(mock_db_controller, mock_config_reader):
        
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    mock_db_controller.search.return_value = [{"id": 1, "llm": "llm", "llm_config": "config", "address": "address", "status": "status"}]
    
    wrappers= db_controller.get_all_wrapper_with_status("status")
    
    mock_db_controller.search.assert_called_once_with("llm_wrapper", "status", "status")
    
    assert len(wrappers) == 1
    assert wrappers[0]["id"] == 1
    assert wrappers[0]["llm"] == "llm"
    assert wrappers[0]["llm_config"] == "config"
    assert wrappers[0]["address"] == "address"
    assert wrappers[0]["status"] == "status"
    
def test_get_wrapper_by_id(mock_db_controller, mock_config_reader):
            
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    mock_db_controller.search.return_value = [{"id": 1, "llm": "llm", "llm_config": "config", "address": "address", "status": "status"}]
    
    wrapper= db_controller.get_wrapper_by_id(1)
    
    mock_db_controller.search.assert_called_once_with("llm_wrapper", "id", 1)
    
    assert wrapper["id"] == 1
    assert wrapper["llm"] == "llm"
    assert wrapper["llm_config"] == "config"
    assert wrapper["address"] == "address"
    assert wrapper["status"] == "status"

def test_get_wrapper_by_address(mock_db_controller, mock_config_reader):
                
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    mock_db_controller.search.return_value = [{"id": 1, "llm": "llm", "llm_config": "config", "address": "address", "status": "status"}]
    
    wrapper= db_controller.get_wrapper_by_address("address")
    
    mock_db_controller.search.assert_called_once_with("llm_wrapper", "address", "address")
    
    assert wrapper["id"] == 1
    assert wrapper["llm"] == "llm"
    assert wrapper["llm_config"] == "config"
    assert wrapper["address"] == "address"
    assert wrapper["status"] == "status"

def test_get_all_wrapper_for_llm(mock_db_controller, mock_config_reader):
        
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    mock_db_controller.search.return_value = [{"id": 1, "llm": "llm", "llm_config": "config", "address": "address", "status": "status"}]
    
    wrappers= db_controller.get_all_wrapper_for_llm("llm")
    
    mock_db_controller.search.assert_called_once_with("llm_wrapper", "llm", "llm")
    
    assert len(wrappers) == 1
    assert wrappers[0]["id"] == 1
    assert wrappers[0]["llm"] == "llm"
    assert wrappers[0]["llm_config"] == "config"
    assert wrappers[0]["address"] == "address"
    assert wrappers[0]["status"] == "status"
    
def test_get_all_wrapper_for_llm_and_status(mock_db_controller, mock_config_reader):
        
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    mock_db_controller.search_multiple.return_value = [{"id": 1, "llm": "llm", "llm_config": "config", "address": "address", "status": "status"}]
    
    wrappers= db_controller.get_all_wrapper_for_llm_and_status("llm", "status")
    
    mock_db_controller.search_multiple.assert_called_once_with("llm_wrapper", [("llm", "llm"), ("status", "status")])
    
    assert len(wrappers) == 1
    assert wrappers[0]["id"] == 1
    assert wrappers[0]["llm"] == "llm"
    assert wrappers[0]["llm_config"] == "config"
    assert wrappers[0]["address"] == "address"
    assert wrappers[0]["status"] == "status"

def test_get_all_wrapper_for_llm_config(mock_db_controller, mock_config_reader):
        
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    mock_db_controller.search.return_value = [{"id": 1, "llm": "llm", "llm_config": "config", "address": "address", "status": "status"}]
    
    wrappers= db_controller.get_all_wrapper_for_llm_config("config")
    
    mock_db_controller.search.assert_called_once_with("llm_wrapper", "llm_config", "config")
    
    assert len(wrappers) == 1
    assert wrappers[0]["id"] == 1
    assert wrappers[0]["llm"] == "llm"
    assert wrappers[0]["llm_config"] == "config"
    assert wrappers[0]["address"] == "address"
    assert wrappers[0]["status"] == "status"
    
def test_get_all_wrapper_for_llm_config_and_status(mock_db_controller, mock_config_reader):
        
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    mock_db_controller.search_multiple.return_value = [{"id": 1, "llm": "llm", "llm_config": "config", "address": "address", "status": "status"}]
    
    wrappers= db_controller.get_all_wrapper_for_llm_config_and_status("config", "status")
    
    mock_db_controller.search_multiple.assert_called_once_with("llm_wrapper", [("llm_config", "config"), ("status", "status")])
    
    assert len(wrappers) == 1
    assert wrappers[0]["id"] == 1
    assert wrappers[0]["llm"] == "llm"
    assert wrappers[0]["llm_config"] == "config"
    assert wrappers[0]["address"] == "address"
    assert wrappers[0]["status"] == "status"
    
def test_add_request(mock_db_controller, mock_config_reader):
        
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    db_controller.add_request("id", "config", 1)
    
    mock_db_controller.insert_data.assert_called_once_with("llm_request", [("id", "config", "queued", 1, None)])
    
def test_get_request(mock_db_controller, mock_config_reader):
            
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    mock_db_controller.search.return_value = [{"id": "id", "llm_config": "config", "status": "status", "measurementId": 1, "address": "address"}]
    
    request= db_controller.get_request("id")
    
    mock_db_controller.search.assert_called_once_with("llm_request", "id", "id")
    
    assert request["id"] == "id"
    assert request["llm_config"] == "config"
    assert request["status"] == "status"
    assert request["measurementId"] == 1
    assert request["address"] == "address"
    
def test_get_all_requests_with_status(mock_db_controller, mock_config_reader):
        
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    mock_db_controller.search.return_value = [{"id": "id", "llm_config": "config", "status": "status", "measurementId": 1, "address": "address"}]
    
    requests= db_controller.get_all_requests_with_status("status")
    
    mock_db_controller.search.assert_called_once_with("llm_request", "status", "status")
    
    assert len(requests) == 1
    assert requests[0]["id"] == "id"
    assert requests[0]["llm_config"] == "config"
    assert requests[0]["status"] == "status"
    assert requests[0]["measurementId"] == 1
    assert requests[0]["address"] == "address"
    
def test_get_next_undeployed_request_for_llm_config_and_measurement(mock_db_controller, mock_config_reader):
        
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    mock_db_controller.search_multiple.return_value = [{"id": "id", "llm_config": "config", "status": "status", "measurementId": 1, "address": "address"}]
    
    request= db_controller.get_next_undeployed_request_for_llm_config_and_measurement("config", 1)
    
    mock_db_controller.search_multiple.assert_called_once_with("llm_request", [("llm_config", "config"), ("measurementId", 1), ("status", "queued")])
    
    assert request["id"] == "id"
    assert request["llm_config"] == "config"
    assert request["status"] == "status"
    assert request["measurementId"] == 1
    assert request["address"] == "address"
    
def test_set_request_address(mock_db_controller, mock_config_reader):
                
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    db_controller.set_request_address("id", "address")
    
    mock_db_controller.update_data.assert_any_call("llm_request", "address", "address", "id", "id")
    mock_db_controller.update_data.assert_any_call("llm_request", "status", "deployed", "id", "id")
    
def test_update_request_status(mock_db_controller, mock_config_reader):
                    
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    db_controller.update_request_status("id", "status")
    
    mock_db_controller.update_data.assert_called_once_with("llm_request", "status", "status", "id", "id")
    
def test_add_measurement(mock_db_controller, mock_config_reader):
        
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    mock_db_controller.search.return_value = []
    
    db_controller.add_measurement(1)
    
    mock_db_controller.insert_data.assert_called_once_with("measurements", [(1, "deployments_pending", None)])
    mock_db_controller.search.assert_called_once_with("measurements", "id", 1)
    
def test_add_measurement_when_measurement_exists(mock_db_controller, mock_config_reader):
        
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()

    mock_db_controller.search.return_value = [{"id": 1, "status": "deployments_pending", "wrapper_id": None}]

    db_controller.add_measurement(1)

    mock_db_controller.insert_data.assert_not_called()
    mock_db_controller.search.assert_called_once_with("measurements", "id", 1)
    
def test_get_measurement(mock_db_controller, mock_config_reader):
            
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    mock_db_controller.search.return_value = [{"id": 1, "status": "deployments_pending", "wrapper_id": None}]
    
    measurement= db_controller.get_measurement(1)
    
    mock_db_controller.search.assert_called_once_with("measurements", "id", 1)
    
    assert measurement["id"] == 1
    assert measurement["status"] == "deployments_pending"
    assert measurement["wrapper_id"] == None
    
def test_get_measurements_waiting_for_deployment(mock_db_controller, mock_config_reader):
        
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    mock_db_controller.search.return_value = [{"id": 1, "status": "deployments_pending", "wrapper_id": 1}]
    
    measurements= db_controller.get_measurements_waiting_for_deployment()
    
    mock_db_controller.search.assert_called_once_with("measurements", "status", "deployments_pending")
    
    assert len(measurements) == 1
    assert measurements[0]["id"] == 1
    assert measurements[0]["status"] == "deployments_pending"
    assert measurements[0]["wrapper_id"] == 1
    
def test_update_measurement_wrapper_id(mock_db_controller, mock_config_reader):
        
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    db_controller.update_measurement_wrapper_id(1, 1)
    
    mock_db_controller.update_data.assert_called_once_with("measurements", "wrapper_id", 1, "id", 1)
    
def test_get_all_requests_for_measurement(mock_db_controller, mock_config_reader):
        
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    mock_db_controller.search.return_value = [{"id": "id", "llm_config": "config", "status": "status", "measurementId": 1, "address": "address"}]
    
    requests= db_controller.get_all_requests_for_measurement(1)
    
    mock_db_controller.search.assert_called_once_with("llm_request", "measurementId", 1)
    
    assert len(requests) == 1
    assert requests[0]["id"] == "id"
    assert requests[0]["llm_config"] == "config"
    assert requests[0]["status"] == "status"
    assert requests[0]["measurementId"] == 1
    assert requests[0]["address"] == "address"
    
def test_get_next_undeployed_request(mock_db_controller, mock_config_reader):
        
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    mock_db_controller.search.return_value = [{"id": "id", "llm_config": "config", "status": "queued", "measurementId": 1, "address": "address"}]
    
    request= db_controller.get_next_undeployed_request(1)
    
    mock_db_controller.search.assert_called_once_with("llm_request", "measurementId", 1)
    
    assert request["id"] == "id"
    assert request["llm_config"] == "config"
    assert request["status"] == "queued"
    assert request["measurementId"] == 1
    assert request["address"] == "address"
    
def test_update_measurement_status(mock_db_controller, mock_config_reader):
        
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    db_controller.update_measurement_status(1, "status")
    
    mock_db_controller.update_data.assert_called_once_with("measurements", "status", "status", "id", 1)
    
def test_find_best_deployments(mock_db_controller, mock_config_reader):
        
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    mock_db_controller.return_custom_query.return_value = [{"id": 1, "llm": "llm", "llm_config": "config", "address": "address", "status": "status"}]
    
    wrappers= db_controller.find_best_deployments()
    query = """
        SELECT llm_request.id as llm_request_id, llm_request.llm_config as llm_config, llm_request.measurementId as measurementId, llm_wrapper.id as wrapper_id, llm_wrapper.address as address
        FROM llm_request
        JOIN llm_wrapper
        ON llm_request.llm_config = llm_wrapper.llm_config
        JOIN measurements
        ON llm_request.measurementId = measurements.id
        WHERE llm_request.measurementId = measurements.id
        AND measurements.wrapper_id IS NULL
        AND llm_wrapper.status = 'ready'
        AND llm_request.status = 'queued'
        AND llm_request.llm_config = llm_wrapper.llm_config
        """
    
    mock_db_controller.return_custom_query.assert_called_once_with(query)
    
    
    assert len(wrappers) == 1
    assert wrappers[0]["id"] == 1
    assert wrappers[0]["llm"] == "llm"
    assert wrappers[0]["llm_config"] == "config"
    assert wrappers[0]["address"] == "address"
    assert wrappers[0]["status"] == "status"

def test_get_all_wrappers(mock_db_controller, mock_config_reader):
                
    mock_config_reader.get.return_value = "sqlite:///:memory:"

    db_controller = LLMRegistryDbController.get_instance()
    
    mock_db_controller.fetch_all.return_value = [{"id": 1, "llm": "llm", "llm_config": "config", "address": "address", "status": "status"}]
    
    wrappers= db_controller.get_all_wrappers()
    
    mock_db_controller.fetch_all.assert_called_once_with("llm_wrapper")
    
    assert len(wrappers) == 1
    assert wrappers[0]["id"] == 1
    assert wrappers[0]["llm"] == "llm"
    assert wrappers[0]["llm_config"] == "config"
    assert wrappers[0]["address"] == "address"
    assert wrappers[0]["status"] == "status"
    
    
    
    
#DatabaseController Tests
    
def test_create_table(mocker):
    #mock sqlite3
    sqlite3 = MagicMock()
    mocker.patch('app.controller.db_controller.sqlite3', sqlite3)
    
    db = MagicMock()
    sqlite3.connect.return_value = db
    
    curser = MagicMock()
    db.cursor.return_value = curser
    
    
    db_controller = DatabaseController("test_db")
    
    db_controller.create_table("table", [("id", "INTEGER PRIMARY KEY")])
    
    curser.execute.assert_called_once_with("CREATE TABLE IF NOT EXISTS table (id INTEGER PRIMARY KEY)")
    db.commit.assert_called_once()

    
def test_insert_data(mocker):
    #mock sqlite3
    sqlite3 = MagicMock()
    mocker.patch('app.controller.db_controller.sqlite3', sqlite3)
    
    db = MagicMock()
    sqlite3.connect.return_value = db
    
    curser = MagicMock()
    db.cursor.return_value = curser
    
    
    
    
    db_controller = DatabaseController("test_db")
    
    db_controller.insert_data("table", [(1, "test"), ("name", "test")])
    
    curser.executemany.assert_called_once_with("INSERT INTO table VALUES (?, ?)", [(1, "test"), ("name", "test")])
    db.commit.assert_called_once()
    
def test_fetch_all(mocker):
    from app.controller.db_controller import DatabaseController
    from unittest.mock import MagicMock

    # Mock sqlite3
    sqlite3 = MagicMock()
    mocker.patch('app.controller.db_controller.sqlite3', sqlite3)

    db = MagicMock()
    sqlite3.connect.return_value = db

    cursor = MagicMock()
    db.cursor.return_value = cursor

    # Mock cursor description (Spaltennamen) und fetchall-Rückgabe
    cursor.description = [("id",), ("test",)]
    cursor.fetchall.return_value = [(1, "test"), (2, "test2")]

    # Instantiate the controller
    db_controller = DatabaseController("test_db")

    # Call the method
    result = db_controller.fetch_all("table")

    # Assertions
    cursor.execute.assert_called_once_with("SELECT * FROM table")
    assert result == [{"id": 1, "test": "test"}, {"id": 2, "test": "test2"}]
    
def test_search(mocker):
    from app.controller.db_controller import DatabaseController
    from unittest.mock import MagicMock

    # Mock sqlite3
    sqlite3 = MagicMock()
    mocker.patch('app.controller.db_controller.sqlite3', sqlite3)

    db = MagicMock()
    sqlite3.connect.return_value = db

    cursor = MagicMock()
    db.cursor.return_value = cursor

    # Mock cursor description (Spaltennamen) und fetchall-Rückgabe
    cursor.description = [("id",), ("test",)]
    cursor.fetchall.return_value = [(1, "test")]

    # Instantiate the controller
    db_controller = DatabaseController("test_db")

    # Call the method
    result = db_controller.search("table", "id", 1)

    # Assertions
    cursor.execute.assert_called_once_with("SELECT * FROM table WHERE id = ?", (1,))
    assert result == [{"id": 1, "test": "test"}]
    
def test_search_multiple(mocker):
    from app.controller.db_controller import DatabaseController
    from unittest.mock import MagicMock

    # Mock sqlite3
    sqlite3 = MagicMock()
    mocker.patch('app.controller.db_controller.sqlite3', sqlite3)

    db = MagicMock()
    sqlite3.connect.return_value = db

    cursor = MagicMock()
    db.cursor.return_value = cursor

    # Mock cursor description (Spaltennamen) und fetchall-Rückgabe
    cursor.description = [("id",), ("test",)]
    cursor.fetchall.return_value = [(1, "test")]

    # Instantiate the controller
    db_controller = DatabaseController("test_db")

    # Call the method
    result = db_controller.search_multiple("table", [("id", 1), ("test", "test")])

    # Assertions
    cursor.execute.assert_called_once_with("SELECT * FROM table WHERE id = ? AND test = ?", [1, "test"])
    assert result == [{"id": 1, "test": "test"}]
    
def test_update_data(mocker):
    from app.controller.db_controller import DatabaseController
    from unittest.mock import MagicMock

    # Mock sqlite3
    sqlite3 = MagicMock()
    mocker.patch('app.controller.db_controller.sqlite3', sqlite3)

    db = MagicMock()
    sqlite3.connect.return_value = db

    cursor = MagicMock()
    db.cursor.return_value = cursor

    # Instantiate the controller
    db_controller = DatabaseController("test_db")

    # Call the method
    db_controller.update_data("table", "test", "test2", "id", 1)

    # Assertions
    cursor.execute.assert_called_once_with("UPDATE table SET test = ? WHERE id = ?", ("test2", 1))
    db.commit.assert_called_once()
    
def test_return_custom_query(mocker):
    from app.controller.db_controller import DatabaseController
    from unittest.mock import MagicMock

    # Mock sqlite3
    sqlite3 = MagicMock()
    mocker.patch('app.controller.db_controller.sqlite3', sqlite3)

    db = MagicMock()
    sqlite3.connect.return_value = db

    cursor = MagicMock()
    db.cursor.return_value = cursor

    # Mock cursor description (Spaltennamen) und fetchall-Rückgabe
    cursor.description = [("id",), ("test",)]
    cursor.fetchall.return_value = [(1, "test")]

    # Instantiate the controller
    db_controller = DatabaseController("test_db")

    # Call the method
    result = db_controller.return_custom_query("SELECT * FROM table")

    # Assertions
    cursor.execute.assert_called_once_with("SELECT * FROM table")
    assert result == [{"id": 1, "test": "test"}]
    