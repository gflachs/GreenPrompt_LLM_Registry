import os
import sqlite3
import threading
from typing import List, Dict, Any, Tuple
from app.utils.configreader import ConfigReader
from app.utils.logger import console_logger

class DatabaseController:
    __thread_local = threading.local()
    __lock = threading.Lock()

    @classmethod
    def get_instance(cls, db_name: str):
        """
        Gibt eine thread-lokale Instanz des DatabaseController zurück.
        :param db_name: Name der SQLite-Datenbankdatei
        :return: Thread-lokale Instanz des DatabaseController
        """
        if not hasattr(cls.__thread_local, "instance"):
            with cls.__lock:
                if not hasattr(cls.__thread_local, "instance"):
                    cls.__thread_local.instance = cls(db_name)
        return cls.__thread_local.instance

    def __init__(self, db_name: str):
        """Initialisiert den DatabaseController mit einer SQLite-Verbindung."""
        if hasattr(self, "_initialized") and self._initialized:
            return  # Verhindere doppelte Initialisierung
        self._initialized = True
        self.db_path = db_name
        self.connection = sqlite3.connect(db_name, check_same_thread=False)  # Thread-Check deaktivieren

    def close(self):
        """Schließt die Verbindung für den aktuellen Thread."""
        if hasattr(self, "_initialized") and self._initialized:
            self.connection.close()
            del self.__thread_local.instance

    def create_table(self, table_name: str, columns: List[Tuple[str, str]]):
        """Create a table with the specified name and columns.

        Args:
            table_name (str): The name of the table.
            columns (List[Tuple[str, str]]): A list of column definitions, where each tuple contains the column name and type.
        """
        with self.connection:
            cursor = self.connection.cursor()
            columns_definition = ", ".join([f"{name} {type}" for name, type in columns])
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_definition})"
            cursor.execute(query)
            self.connection.commit()

    def insert_data(self, table_name: str, data: List[Tuple[Any, ...]], columns: List[str] = None):
        """Insert multiple rows of data into a table.

        Args:
            table_name (str): The name of the table.
            data (List[Tuple[Any, ...]]): A list of tuples, where each tuple contains the values for one row.
            columns (List[str]): Optional list of column names to insert into. Defaults to all columns.
        """
        if columns:
            columns_str = ", ".join(columns)
            placeholders = ", ".join(["?" for _ in columns])
            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        else:
            placeholders = ", ".join(["?" for _ in data[0]])
            query = f"INSERT INTO {table_name} VALUES ({placeholders})"
        
        with self.connection:
            cursor = self.connection.cursor()
            cursor.executemany(query, data)
            self.connection.commit()

        
    def update_data(self, table_name: str, column: str, value: Any, condition_column: str, condition_value: Any):
        """Update data in a table.

        Args:
            table_name (str): The name of the table.
            column (str): The column to update.
            value (Any): The new value.
            condition_column (str): The column to use for the condition.
            condition_value (Any): The value to match in the condition column.
        """
        query = f"UPDATE {table_name} SET {column} = ? WHERE {condition_column} = ?"
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(query, (value, condition_value))
            self.connection.commit()

    def fetch_all(self, table_name: str) -> List[Dict[str, Any]]:
        """Fetch all rows from a table.

        Args:
            table_name (str): The name of the table.

        Returns:
            List[Dict[str, Any]]: A list of rows, where each row is represented as a dictionary.
        """
        query = f"SELECT * FROM {table_name}"
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]


    def search(self, table_name: str, column: str, value: Any) -> List[Dict[str, Any]]:
        """Search for rows in a table where a specific column matches a value.

        Args:
            table_name (str): The name of the table.
            column (str): The column to search in.
            value (Any): The value to search for.

        Returns:
            List[Dict[str, Any]]: A list of rows, where each row is represented as a dictionary.
        """
        query = f"SELECT * FROM {table_name} WHERE {column} = ?"
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(query, (value,))
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def search_multiple(self, table_name: str, conditions: List[Tuple[str, Any]]) -> List[Dict[str, Any]]:
        """Search for rows in a table where multiple columns match specific values.

        Args:
            table_name (str): The name of the table.
            conditions (List[Tuple[str, Any]]): A list of tuples, where each tuple contains the column name and value to search for.

        Returns:
            List[Dict[str, Any]]: A list of rows, where each row is represented as a dictionary.
        """
        query = f"SELECT * FROM {table_name} WHERE {' AND '.join([f'{column} = ?' for column, _ in conditions])}"
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(query, [value for _, value in conditions])
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def return_custom_query(self, query: str) -> List[Dict[str, Any]]:
        """Return the result of a custom query.

        Args:
            query (str): The query to execute.

        Returns:
            List[Dict[str, Any]]: A list of rows, where each row is represented as a dictionary.
        """
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        
    def reset_database(self):
        """
        Löscht die SQLite-Datenbankdatei und erstellt eine neue leere Datei.
        :param db_path: Pfad zur SQLite-Datenbankdatei
        """
        self.connection.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            console_logger.info(f"Datenbankdatei {self.db_path} wurde gelöscht.")
        else:
            console_logger.info(f"Datenbankdatei {self.db_path} existiert nicht.")

        # Neue leere Datenbank erstellen (optional, falls Struktur neu aufgesetzt werden muss)
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
    
    def close(self):
        """Close the database connection."""
        self.connection.close()

class LLMRegistryDbController:
    __instance = None
    __lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            with cls.__lock:
                if cls.__instance is None:  # Doppelprüfung
                    cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return  # Verhindert doppelte Initialisierung
        self._initialized = True

        console_logger.info("Initializing LLM Registry Database Controller...")
        config_reader = ConfigReader.get_instance()
        db_name = config_reader.get("database", "db_name")
        console_logger.info(f"Using database: {db_name}")
        self.db_controller = DatabaseController.get_instance(db_name)
        self.db_controller.reset_database()
        self.__create_tables__()

        
    def __create_tables__(self):
        self.db_controller.create_table("llm_wrapper", [
            ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
            ("llm", "TEXT"),
            ("llm_config", "TEXT"),
            ("address", "TEXT"),
            ("username", "TEXT"),
            ("password", "TEXT"),
            ("status", "TEXT")
        ])
        self.db_controller.create_table("llm_request", [
            ("id", "TEXT PRIMARY KEY"),
            ("llm_config", "TEXT"),
            ("status", "TEXT"),
            ("measurementId", "INTEGER"),
            ("address", "TEXT")
        ])
        self.db_controller.create_table("measurements", [
            ("id", "INTEGER PRIMARY KEY"),
            ("status", "TEXT"),
            ("wrapper_id", "INTEGER")
        ])

    @classmethod
    def get_instance(cls):
        return cls()

    def close(self):
        if self.db_controller:
            self.db_controller.close()
        LLMRegistryDbController.__instance = None

    def __del__(self):
        self.close()
        
    def get_all_wrappers(self):
        return self.db_controller.fetch_all("llm_wrapper")
        
    def add_llm_wrapper(self, name: str, config: str, address: str, username: str, password: str, status: str):
        self.db_controller.insert_data("llm_wrapper", [(name, config, address, username, password, status)], ["llm", "llm_config", "address", "username", "password", "status"])
        
    def get_llm_wrappers(self):
        console_logger.info("Fetching all LLM wrappers...")
        return self.db_controller.fetch_all("llm_wrapper")
    
    def change_llm_wrapper_status_by_id(self, wrapper_id: int, status: str):
        self.db_controller.update_data("llm_wrapper", "status", status, "id", wrapper_id)
        
    def change_llm_wrapper_config_by_id(self, wrapper_id: int, config: str):
        self.db_controller.update_data("llm_wrapper", "llm_config", config, "id", wrapper_id)
    
    def change_llm_wrapper_status_by_address(self, address: str, status: str):
        self.db_controller.update_data("llm_wrapper", "status", status, "address", address)
        
    def get_all_wrapper_with_status(self, status: str):
        return self.db_controller.search("llm_wrapper", "status", status)
    
    def get_wrapper_by_id(self, wrapper_id: int):
        wrapper = self.db_controller.search("llm_wrapper", "id", wrapper_id)
        if wrapper:
            return wrapper[0]
        return None

    def get_wrapper_by_address(self, address: str):
        wrapper = self.db_controller.search("llm_wrapper", "address", address)
        if wrapper:
            return wrapper[0]
        return None
    
    def get_all_wrapper_for_llm(self, llm: str):
        return self.db_controller.search("llm_wrapper", "llm", llm)
    
    def get_all_wrapper_for_llm_and_status(self, llm: str, status: str):
        return self.db_controller.search_multiple("llm_wrapper", [("llm", llm), ("status", status)])
    
    def get_all_wrapper_for_llm_config(self, llm_config: str):
        return self.db_controller.search("llm_wrapper", "llm_config", llm_config)
    
    def get_all_wrapper_for_llm_config_and_status(self, llm_config: str, status: str):
        return self.db_controller.search_multiple("llm_wrapper", [("llm_config", llm_config), ("status", status)])
    
    def add_request(self, request_id: str, llm_config: str, measurement_id: int):
        self.db_controller.insert_data("llm_request", [(request_id, llm_config, "queued", measurement_id, None)])
        
    def get_request(self, request_id: str):
        requests = self.db_controller.search("llm_request", "id", request_id)
        if requests:
            return requests[0]
        return None
    
    def get_all_requests_with_status(self, status: str):
        return self.db_controller.search("llm_request", "status", status)
    
    def get_next_undeployed_request_for_llm_config_and_measurement(self, llm_config: str, measurement_id: int):
        requests = self.db_controller.search_multiple("llm_request", [("llm_config", llm_config), ("measurementId", measurement_id), ("status", "queued")])
        if requests:
            return requests[0]
        return None
    
    def set_request_address(self, request_id: str, address: str):
        self.db_controller.update_data("llm_request", "address", address, "id", request_id)
        self.db_controller.update_data("llm_request", "status", "deployed", "id", request_id)
    
    def update_request_status(self, request_id: str, status: str):
        self.db_controller.update_data("llm_request", "status", status, "id", request_id)
    
    def add_measurement(self, measurement_id: int):
        #check if the measurement already exists
        if self.get_measurement(measurement_id):
            return
        self.db_controller.insert_data("measurements", [(measurement_id, "deployments_pending", None)])
        
    def get_measurement(self, measurement_id: int):
        measurements = self.db_controller.search("measurements", "id", measurement_id)
        if measurements:
            return measurements[0]
        return None
    
    def get_measurements_waiting_for_deployment(self):
        return self.db_controller.search("measurements", "status", "deployments_pending")
      
    def update_measurement_wrapper_id(self, measurement_id: int, wrapper_id: int):
        self.db_controller.update_data("measurements", "wrapper_id", wrapper_id, "id", measurement_id)
        
    def get_all_requests_for_measurement(self, measurement_id: int):
        return self.db_controller.search("llm_request", "measurementId", measurement_id)
    
    def get_next_undeployed_request(self, measurement_id: int):
        requests = self.get_all_requests_for_measurement(measurement_id)
        for request in requests:
            if request["status"] == "queued":
                return request
        return None
    
    def update_measurement_status(self, measurement_id: int, status: str):
        self.db_controller.update_data("measurements", "status", status, "id", measurement_id)
        
    #find all requests, where an llm_wrapper exists with the status "ready" and the llm_config is the same, where the wrapper_id of the requests measurement is None
    def find_best_deployments(self):
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
        return self.db_controller.return_custom_query(query)
    
    def clear_all(self):
        self.db_controller.reset_database()
        self.__create_tables__()                                                        
        
        
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
