import app.services.llm_wrapper_service as lws
from app.utils.logger import console_logger
from app.utils.configreader import ConfigReader

    
def main():
    console_logger.info("Starting LLM Wrapper Service")

    # Initialize ConfigReader
    config_reader = ConfigReader.get_instance()

    # Retrieve configuration values
    db_name = config_reader.get("database", "db_name")
    llm_wrapper_machines = config_reader.get("llm", "llm_wrapper_machines")

    console_logger.info(f"Database Name: {db_name}")
    console_logger.info(f"LLM Wrapper Machines: {llm_wrapper_machines}")

    return

if __name__ == "__main__":
    main()