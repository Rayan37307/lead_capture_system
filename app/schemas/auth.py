from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
    tenant_id: Optional[str] = None # Changed to string


class UserCreateRequest(BaseModel):
    email: str
    password: str
    tenant_id: str # Changed to string

class UserResponse(BaseModel):
    id: str
    email: str
    tenant_id: str
