from fastapi import FastAPI
import app.services.llm_registry_service as llm_registry_service
from app.controller.promptingservice_controller import router as promptingservice_controller

app = FastAPI()

app.include_router(promptingservice_controller, prefix="/promptingservice", tags=["SomeController"])



@app.get("/")
async def root():
    return {"message": "Hello World"}