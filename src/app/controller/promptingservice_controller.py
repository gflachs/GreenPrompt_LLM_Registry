from fastapi import APIRouter
import app.services.llm_registry_service as lms
from app.models.request import RequestPayload, RequestResponse, RequestStatus

router = APIRouter()

@router.post("/request", response_description="Creates new Deploymentrequests for the given LLMs and returns for each LLM a requestid, which can be used to get the status of the deployment", response_model=RequestResponse, status_code=201)
async def post_request(request: RequestPayload) -> RequestResponse:
    request_ids = lms.request_llm(request)
    return request_ids.model_dump()

@router.get("/request/{request_id}", response_description="Status of the request", response_model=RequestStatus)
async def get_request(request_id: str) -> RequestStatus:
    request = lms.get_request(request_id)
    return request

@router.delete("/request/{request_id}", response_description="Releases all resources associated with the request", status_code=204)
async def delete_request(request_id: str):
    lms.release_llm(request_id)
    return None

