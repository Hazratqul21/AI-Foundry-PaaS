from fastapi import Security, HTTPException, status, Depends
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from ..database import get_db
from .models import APIKey
from datetime import datetime
import hashlib

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()

async def get_api_key(
    api_key_header: str = Security(api_key_header),
    db: Session = Depends(get_db)
):
    if not api_key_header:
        return None

    hashed_input = hash_key(api_key_header)
    
    # Find key by hash
    key_record = db.query(APIKey).filter(APIKey.key_hash == hashed_input, APIKey.is_active == True).first()
    
    if not key_record:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate API Key"
        )
    
    # Update last used timestamp
    key_record.last_used_at = datetime.utcnow()
    db.commit()
    
    return key_record
