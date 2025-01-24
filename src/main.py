from contextlib import asynccontextmanager
from fastapi import FastAPI
import app.services.llm_registry_service as llm_registry_service
import app.services.llm_wrapper_status_service as llm_wrapper_status_service
from app.utils.configreader import ConfigReader
from app.controller.promptingservice_controller import router as promptingservice_controller
from app.utils.logger import console_logger

configreader = ConfigReader.get_instance()

@asynccontextmanager
async def lifespan(app: FastAPI):
    console_logger.info("Starting up the application")
    
    #read the config for the llm_wrapper_machines
    db_name = configreader.get("database", "db_name")
    llm_wrapper_machines = configreader.get("llm", "llm_wrapper_machines")

    #@TODO: write them to the db
    for machine in llm_wrapper_machines:
        llm_registry_service.add_machine(machine["ip_address"], machine["password"], machine["user"])
    
    #start the check status thread
    llm_wrapper_status_service.start_check_status()
    #start the registry service queue
    llm_registry_service.start()
    
    yield
    
    console_logger.info("Shutting down the application")
    
    #stop the check status thread
    llm_wrapper_status_service.stop_check_status()
    #stop the registry service queue
    llm_registry_service.shutdown()
    


app = FastAPI(lifespan=lifespan)

app.include_router(promptingservice_controller, prefix="/promptingservice", tags=["SomeController"])


@app.get("/")
async def root():
    return {"message": "Hello World"}