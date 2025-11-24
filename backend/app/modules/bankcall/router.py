from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ...auth.router import oauth2_scheme

router = APIRouter()

class CallInitiate(BaseModel):
    phone_number: str
    scenario_id: str
    customer_name: str

class CallResponse(BaseModel):
    call_id: str
    status: str
    estimated_start_time: str

from ...api_keys.security import get_api_key
from ...api_keys.models import APIKey

@router.post("/calls/initiate", response_model=CallResponse)
def initiate_call(
    call_data: CallInitiate,
    token: str = Depends(oauth2_scheme),
    # api_key: APIKey = Depends(get_api_key)
):
    # Mock logic for BankCall
    return {
        "call_id": "call_12345",
        "status": "initiated",
        "estimated_start_time": "Now"
    }
