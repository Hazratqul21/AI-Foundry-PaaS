from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models import User
from .models import WebhookSubscription
from pydantic import BaseModel, HttpUrl
from datetime import datetime
import secrets

router = APIRouter()

class WebhookCreate(BaseModel):
    url: HttpUrl
    events: List[str]

class WebhookResponse(BaseModel):
    id: str
    url: HttpUrl
    events: List[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class WebhookCreatedResponse(WebhookResponse):
    secret: str # Only returned once

@router.get("/", response_model=List[WebhookResponse])
def list_webhooks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(WebhookSubscription).filter(WebhookSubscription.user_id == current_user.id).all()

@router.post("/", response_model=WebhookCreatedResponse)
def create_webhook(
    webhook_data: WebhookCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_webhook = WebhookSubscription(
        url=str(webhook_data.url),
        events=webhook_data.events,
        secret=secrets.token_hex(24),
        user_id=current_user.id,
        organization_id=current_user.organization_id
    )
    db.add(new_webhook)
    db.commit()
    db.refresh(new_webhook)
    return new_webhook

@router.delete("/{webhook_id}")
def delete_webhook(
    webhook_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    webhook = db.query(WebhookSubscription).filter(WebhookSubscription.id == webhook_id, WebhookSubscription.user_id == current_user.id).first()
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    db.delete(webhook)
    db.commit()
    return {"message": "Webhook deleted"}
