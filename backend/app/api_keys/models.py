from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import uuid
import secrets

def generate_uuid():
    return str(uuid.uuid4())

def generate_api_key():
    return f"pk_{secrets.token_urlsafe(32)}"

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, default=generate_uuid)
    key_hash = Column(String, unique=True, index=True, nullable=False)
    prefix = Column(String, nullable=False) # First 8 chars for display
    name = Column(String, nullable=False)  # e.g., "Production Key", "Test Key"
    user_id = Column(String, ForeignKey("users.id"))
    organization_id = Column(String, ForeignKey("organizations.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="api_keys")
    organization = relationship("Organization", back_populates="api_keys")
