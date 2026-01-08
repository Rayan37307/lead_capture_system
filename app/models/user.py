from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.lead import PyObjectId # Re-use PyObjectId


class UserBase(BaseModel):
    email: str
    tenant_id: PyObjectId


class UserCreate(UserBase):
    password: str


class UserInDB(UserBase):
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class User(UserInDB):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
