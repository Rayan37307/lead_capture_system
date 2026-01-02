from typing import List, Optional
from pydantic import BaseModel
from app.models.lead import LeadBase, Message


class WebhookPayload(BaseModel):
    object: str
    entry: List[dict]


class ChatRequest(BaseModel):
    message: str
    user_id: str
    source: str  # website, whatsapp, instagram


class ChatResponse(BaseModel):
    response: str
    intent: Optional[str] = None
    follow_up: bool = True


class LeadResponse(LeadBase):
    id: str


class AnalyticsSummary(BaseModel):
    total_conversations: int
    leads_captured: int
    hot_leads: int
    warm_leads: int
    cold_leads: int
    avg_response_time: float
    conversion_rate: float