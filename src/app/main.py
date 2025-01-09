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
    #@TODO: read the config for the llm_wrapper_machines and write them to the db
    
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
    
    #@TODO: stop all llm_wrapper_machines
    #llm_wrapper_service.shutdown_wrapper()
    


app = FastAPI(lifespan=lifespan)

app.include_router(promptingservice_controller, prefix="/promptingservice", tags=["SomeController"])



@app.get("/")
async def root():
    return {"message": "Hello World"}