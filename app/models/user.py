from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import uuid

class UserBase(BaseModel):
    email: str
    tenant_id: str


class UserCreate(UserBase):
    password: str


class UserInDB(UserBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class User(UserInDB):
    """Pydantic model for a user retrieved from the DB."""
    pass
