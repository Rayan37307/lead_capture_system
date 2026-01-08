from typing import Optional
from pydantic import BaseModel
from app.models.lead import PyObjectId


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
    tenant_id: Optional[PyObjectId] = None # Added tenant_id


class UserCreateRequest(BaseModel):
    email: str
    password: str
    tenant_id: PyObjectId # User creation requires a tenant_id

class UserResponse(BaseModel):
    id: PyObjectId
    email: str
    tenant_id: PyObjectId
