from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from pydantic_core import core_schema
from app.constants.enums import LeadIntent, LeadSource


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        def validate_from_str(value: str) -> ObjectId:
            if not ObjectId.is_valid(value):
                raise ValueError("Invalid objectid")
            return ObjectId(value)

        return core_schema.union_schema(
            [
                core_schema.is_instance_schema(ObjectId),
                core_schema.no_info_after_validator_function(
                    validate_from_str,
                    core_schema.str_schema(),
                ),
            ],
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        # Return a JSON schema representation for ObjectId
        return {'type': 'string', 'format': 'objectid'}


class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class LeadBase(BaseModel):
    tenant_id: PyObjectId = Field(default_factory=PyObjectId)
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    source: LeadSource
    intent: LeadIntent = LeadIntent.COLD
    messages: List[Message] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Lead(LeadBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    tenant_id: PyObjectId
    name: str
    email: str
    phone: str
    source: LeadSource
    intent: LeadIntent
    messages: List[Message]
    created_at: datetime
    updated_at: datetime


class LeadCreate(LeadBase):
    name: str
    email: str
    phone: str
    source: LeadSource


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    intent: Optional[LeadIntent] = None
    messages: Optional[List[Message]] = None