import json
import logging
import subprocess


logging.basicConfig(
    filename="llm_registry.log",  
    filemode="w",        
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def write_llm_config(model, model_type, llm_config_json_path="llm_config.json"):
    '''
    Writes the given model and model_type to a JSON file, overwriting existing content.
    :param model: Name of the model
    :param model_type: Type of the model
    :param llm_config_json_path: Path to the JSON configuration file
    :return: None
    '''
    try:
        config_data = {
            "model": model,
            "model_type": model_type
        }
        with open(llm_config_json_path, 'w') as file:
            json.dump(config_data, file, indent=4)
        logging.info(f"LLM config written to {llm_config_json_path}: model_name={model}, model_type={model_type}")

    except Exception as e:
        logging.error(f"Failed to write LLM config: {e}")


def read_llm_config(llm_config_json):
    '''
    Reads the given json file containing llm model information: model name, model type
    :param llm_config_json: json file of llm
    :return: model name, model type from llm
    '''
    try:
        with open(llm_config_json, 'r') as file:
            config_data = json.load(file)
        model = config_data.get('model')
        model_type = config_data.get('model_type')

        if model is None or model_type is None:
            logging.error("Model name or model type not found in configuration.")
            return None, None

        logging.info(f"Read LLM config: model_name={model}, model_type={model_type}")
        return model, model_type

    except Exception as e:
        logging.error(f"Failed to read LLM config: {e}")
        return None, None


def start_model_instance(model, model_type):
    """
    Starts a new LLM Wrapper/service for a specific model configuration,
    (so that each model runs in an isolated and manageable environment)
    :param model and model_type: model name and model type from llm, see json file
    :return: the Popen object of the started process or None in case of an error
    """
    try:
        logging.info(f"Starting model with config: model_name={model}, model_type={model_type}")

        # Starts a new model instance with an example code as placeholder
        # Niklas code llm_model.py?
        process = subprocess.Popen(["python", "-c", "import time; time.sleep(2)"],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process

    except Exception as e:
        logging.error(f"An exception occurred: {e}")
        return None
    

# def stop_model_instance(process):
#     """
#     Stops a running service for a specific model configuration
#     :param process: process that has to be stopped
#     """
#     if process:
#         logging.info("Stopping model...")
#         process.terminate()
#         process.wait()
#         logging.info("Model stopped.")
#     else:
#         logging.error("No process to stop.")


def main():
    # user input
    model = input("Please enter the model name: ")
    model_type = input("Please enter the model type: ")
    logging.info(f"User provided model name and type: model_name={model}, model_type={model_type}")

    # write json file
    write_llm_config(model, model_type)
    logging.info(f"Model and model type were successfully written to config.json: model_name={model}, model_type={model_type}")

    # read json file
    model, model_type = read_llm_config('llm_config.json')

    # start instance
    if model and model_type:
        process = start_model_instance(model, model_type)
        logging.info(f"Successfully read LLM config file: model_name={model}, model_type={model_type}")
    else:
        logging.error("Failed to read the model configuration.")

if __name__ == "__main__":
    main()
