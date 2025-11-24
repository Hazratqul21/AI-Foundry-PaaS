from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models import User
from .models import APIKey
from pydantic import BaseModel
from datetime import datetime
import secrets
import hashlib

router = APIRouter()

def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()

@router.get("/", response_model=List[APIKeyResponse])
def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(APIKey).filter(APIKey.user_id == current_user.id).all()

@router.post("/", response_model=APIKeyCreatedResponse)
def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    raw_key = f"pk_{secrets.token_urlsafe(32)}"
    hashed_key = hash_key(raw_key)
    prefix = raw_key[:8]

    new_key = APIKey(
        name=key_data.name,
        key_hash=hashed_key,
        prefix=prefix,
        user_id=current_user.id,
        organization_id=current_user.organization_id
    )
    db.add(new_key)
    db.commit()
    db.refresh(new_key)
    
    return {
        "id": new_key.id,
        "prefix": new_key.prefix,
        "name": new_key.name,
        "created_at": new_key.created_at,
        "is_active": new_key.is_active,
        "key": raw_key # Return full key only here
    }

@router.delete("/{key_id}")
def revoke_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    key = db.query(APIKey).filter(APIKey.id == key_id, APIKey.user_id == current_user.id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API Key not found")
    
    db.delete(key)
    db.commit()
    return {"message": "API Key revoked"}
