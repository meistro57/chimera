from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Depends
from pydantic import BaseModel
from ..models.user import User
from ..core.database import get_database

class TokenData(BaseModel):
    username: Optional[str] = None

async def get_current_user(db: Session = Depends(get_database)):
    """Get current user - always returns None for anonymous access"""
    return None