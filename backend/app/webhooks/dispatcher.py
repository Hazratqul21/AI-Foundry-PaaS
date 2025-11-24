import requests
import hmac
import hashlib
import json
from sqlalchemy.orm import Session
from .models import WebhookSubscription, WebhookEvent
from ..database import SessionLocal
from fastapi import BackgroundTasks
import logging

logger = logging.getLogger(__name__)

def sign_payload(payload: dict, secret: str) -> str:
    payload_bytes = json.dumps(payload).encode('utf-8')
    secret_bytes = secret.encode('utf-8')
    signature = hmac.new(secret_bytes, payload_bytes, hashlib.sha256).hexdigest()
    return signature

def _send_webhook_task(event_id: str, url: str, secret: str, payload: dict, event_type: str):
    db = SessionLocal()
    try:
        event_record = db.query(WebhookEvent).filter(WebhookEvent.id == event_id).first()
        if not event_record:
            return

        signature = sign_payload(payload, secret)
        headers = {
            "Content-Type": "application/json",
            "X-Hub-Signature-256": f"sha256={signature}",
            "X-Event-Type": event_type
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            event_record.status = "success" if 200 <= response.status_code < 300 else "failed"
            event_record.response_code = response.status_code
        except Exception as e:
            logger.error(f"Webhook failed: {e}")
            event_record.status = "failed"
            event_record.response_code = 0
        
        db.commit()
    finally:
        db.close()

def dispatch_event(
    db: Session, 
    organization_id: str, 
    event_type: str, 
    payload: dict, 
    background_tasks: BackgroundTasks
):
    # Find subscriptions for this org and event
    subscriptions = db.query(WebhookSubscription).filter(
        WebhookSubscription.organization_id == organization_id,
        WebhookSubscription.is_active == True
    ).all()

    for sub in subscriptions:
        if event_type in sub.events:
            # Create event record immediately as pending
            event_record = WebhookEvent(
                subscription_id=sub.id,
                event_type=event_type,
                payload=payload,
                status="pending"
            )
            db.add(event_record)
            db.commit()
            db.refresh(event_record)

            # Schedule background task
            background_tasks.add_task(
                _send_webhook_task, 
                event_record.id, 
                sub.url, 
                sub.secret, 
                payload, 
                event_type
            )
