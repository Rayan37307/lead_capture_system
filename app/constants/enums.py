from enum import Enum


class LeadSource(str, Enum):
    WEBSITE = "website"
    WHATSAPP = "whatsapp"
    INSTAGRAM = "instagram"


class LeadIntent(str, Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


class WorkflowEvent(str, Enum):
    ON_NEW_MESSAGE = "on_new_message"
    ON_LEAD_CREATED = "on_lead_created"
    ON_HOT_LEAD = "on_hot_lead"