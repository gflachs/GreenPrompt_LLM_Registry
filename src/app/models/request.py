from pydantic import BaseModel, Field
from typing import List, Dict, Any

class Args(BaseModel):
    prompting: Dict[str, Any]  
    deployment: Dict[str, Any]  

class LLMConfig(BaseModel):
    modeltyp: str = Field(..., description="Model type must be provided")
    model: str = Field(..., min_length=1, description="Model name cannot be empty")
    uses_chat_template: bool = Field(..., description="Uses chat template must be provided")
    args: Args  

class RequestPayload(BaseModel):
    llms: List[LLMConfig] 
    measurementId: int = Field(..., gt=0, description="Measurement ID must be positive")
    
class RequestSingleResponse(BaseModel):
    llmconfig: LLMConfig
    requestId: str = Field(..., description="Request ID must be provided")
    
class RequestResponse(BaseModel):
    requests: List[RequestSingleResponse]
    
class RequestStatus(BaseModel):
    requestId: str = Field(..., description="Request ID must be provided")
    llmconfig : LLMConfig
    status: str = Field(..., description="Status must be provided")
    measurementId: int = Field(..., gt=0, description="Measurement ID must be positive")
    address : str | None = Field(None, description="Address must be provided")
