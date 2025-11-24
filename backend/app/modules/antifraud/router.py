from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...database import get_db
from ...auth.router import oauth2_scheme
from pydantic import BaseModel
from datetime import datetime
from ...api_keys.security import get_api_key
from ...api_keys.models import APIKey

router = APIRouter()

class TransactionCreate(BaseModel):
    transaction_id: str
    amount: float
    currency: str
    merchant: str
    location: str

class TransactionResponse(BaseModel):
    transaction_id: str
    decision: str
    risk_score: int
    reasons: List[str]

@router.post("/transactions/submit", response_model=TransactionResponse)
def submit_transaction(
    transaction: TransactionCreate,
    # Allow either JWT or API Key. For now, we'll just check if one is present.
    # In a real app, you might want a unified dependency that returns the user/org from either.
    token: str = Depends(oauth2_scheme), 
    # api_key: APIKey = Depends(get_api_key), # Uncomment when ready to test API Key only
    db: Session = Depends(get_db)
):
    # Mock logic for now, integrating existing logic would go here
    risk_score = 150  # Low risk
    decision = "APPROVED"
    reasons = []

    if transaction.amount > 10000:
        risk_score = 850
        decision = "BLOCKED"
        reasons.append("High transaction amount")

    return {
        "transaction_id": transaction.transaction_id,
        "decision": decision,
        "risk_score": risk_score,
        "reasons": reasons
    }
