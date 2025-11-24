from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, JSON, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class WebhookSubscription(Base):
    __tablename__ = "webhook_subscriptions"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    organization_id = Column(String, ForeignKey("organizations.id"))
    url = Column(String, nullable=False)
    events = Column(JSON, nullable=False)  # List of events e.g., ["transaction.blocked", "call.completed"]
    secret = Column(String, nullable=False) # For signature verification
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="webhooks")
    organization = relationship("Organization", back_populates="webhooks")

class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    subscription_id = Column(String, ForeignKey("webhook_subscriptions.id"))
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(String, default="pending") # pending, success, failed
    response_code = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
