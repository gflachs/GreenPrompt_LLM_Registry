import configparser
import sys
from typing import List, Tuple, Any
import os
import json
import logging


class ConfigReader:
    _instance = None
    
    @staticmethod
    def get_instance(stage: str = None):
        if ConfigReader._instance is None:
            ConfigReader._instance = ConfigReader(stage)
        return ConfigReader._instance

    def __new__(cls, stage: str = None):
        if cls._instance is None:
            cls._instance = super(ConfigReader, cls).__new__(cls)
            cls._instance.__initialize__(stage if stage else 'local-dev')
        return cls._instance

    def __initialize__(self, env='local-dev'):
        """Initialize the config reader with a default configuration file."""
        self.config = configparser.ConfigParser()
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # Eins nach oben navigieren
        config_file = os.path.join(base_dir, 'configs', f'config.{env}.ini')
        if not os.path.exists(config_file):
            logging.error(f"Configuration file '{config_file}' not found.")
            raise FileNotFoundError(f"Configuration file '{config_file}' not found.")
        self.config.read(config_file)

    def get(self, section: str, option: str) -> str:
        """Retrieve a value from the configuration file.

        Args:
            section (str): The section in the config file.
            option (str): The option within the section.

        Returns:
            str: The value of the specified option.
        """
        value = self.config.get(section, option)
        if section == "llm" and option == "llm_wrapper_machines":
            self.validate_llm_wrapper_config(value)
            value = json.loads(value)
        return value
    
    def validate_llm_wrapper_config(self, value: str):
        """Validate that the provided value is a valid JSON string.

        Args:
            value (str): The value to validate.

        Raises:
            ValueError: If the value is not a valid JSON string.
        """
        try:
            parsed_value = json.loads(value)
            if isinstance(parsed_value, list) and not parsed_value:
                logging.info("The 'llm_wrapper_machines' list is empty.")
                return "The 'llm_wrapper_machines' list is empty."
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON value: {value}")
            raise ValueError(f"Invalid JSON value: {value}") from e
        return parsed_value
    
    def set(self, section: str, option: str, value: str):
        """Set a value in the configuration file.

        Args:
            section (str): The section in the config file.
            option (str): The option within the section.
            value (str): The value to set.
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)
        with open("config.ini", "w") as configfile:
            self.config.write(configfile)