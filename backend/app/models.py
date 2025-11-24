from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    type = Column(String)  # bank, mfi, fintech
    modules = Column(JSON, default=list) # List of active modules e.g., ["bankcall", "antifraud"]
    subscription_tier = Column(String)  # starter, business, enterprise
    billing_email = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    users = relationship("User", back_populates="organization")
    api_keys = relationship("APIKey", back_populates="organization")
    webhooks = relationship("WebhookSubscription", back_populates="organization")



class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String)
    role = Column(String, nullable=False)  # super_admin, org_admin, manager, viewer
    organization_id = Column(String, ForeignKey("organizations.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    organization = relationship("Organization", back_populates="users")
    api_keys = relationship("APIKey", back_populates="user")
    webhooks = relationship("WebhookSubscription", back_populates="user")


