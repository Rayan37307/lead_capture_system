from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid
from app.constants.enums import LeadIntent, LeadSource


class Message(BaseModel):
    id: Optional[int] = None # Will be populated from DB
    lead_id: Optional[str] = None # Will be populated from DB
    role: str  # "user" or "assistant"
    content: str
    timestamp: str # Storing as ISO format string


class LeadBase(BaseModel):
    tenant_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    source: LeadSource
    intent: LeadIntent = LeadIntent.COLD
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class Lead(LeadBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[Message] = []


class LeadCreate(BaseModel):
    # A simplified model for creating a lead, tenant_id will be passed separately
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    source: LeadSource
    intent: LeadIntent = LeadIntent.COLD


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    intent: Optional[LeadIntent] = None