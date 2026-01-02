from bson import ObjectId
from typing import List, Optional
from datetime import datetime
from app.database.mongodb import get_database
from app.models.lead import Lead, LeadCreate, LeadUpdate
from app.constants.enums import LeadIntent, LeadSource
from app.services.google_sheets_service import GoogleSheetsService


import logging
logger = logging.getLogger(__name__)

class LeadService:
    def __init__(self):
        self.google_sheets_service = GoogleSheetsService()

    async def create_lead(self, lead_data: LeadCreate) -> Lead:
        """Create a new lead in the database"""
        logger.info("--- create_lead started ---")
        db = await get_database()
        lead_dict = lead_data.dict()
        lead_dict["created_at"] = datetime.utcnow()
        lead_dict["updated_at"] = datetime.utcnow()
        
        logger.info("Inserting lead into database...")
        result = await db.leads.insert_one(lead_dict)
        created_lead = await db.leads.find_one({"_id": result.inserted_id})
        logger.info("Lead inserted.")
        
        # Sync to Google Sheets if enabled
        logger.info("Checking for Google Sheets sync...")
        if lead_data.source != LeadSource.WHATSAPP:  # Skip for WhatsApp to avoid duplicates
            await self.google_sheets_service.add_lead_to_sheet(created_lead)
        logger.info("Google Sheets sync checked.")
        
        # Trigger workflow for new lead
        logger.info("Triggering on_lead_created workflow...")
        from app.services.workflow_service import WorkflowService
        workflow_service = WorkflowService()
        await workflow_service.trigger_event("on_lead_created", created_lead)
        logger.info("Workflow triggered.")
        
        logger.info("--- create_lead finished ---")
        return Lead(**created_lead)


    async def get_lead_by_id(self, lead_id: str) -> Optional[Lead]:
        """Get a lead by its ID"""
        db = await get_database()
        try:
            object_id = ObjectId(lead_id)
        except Exception:
            return None
        lead_data = await db.leads.find_one({"_id": object_id})
        if lead_data:
            return Lead(**lead_data)
        return None

    async def get_lead_by_phone(self, phone: str) -> Optional[Lead]:
        """Get a lead by phone number"""
        db = await get_database()
        lead_data = await db.leads.find_one({"phone": phone})
        if lead_data:
            return Lead(**lead_data)
        return None

    async def update_lead(self, lead_id: str, lead_update: LeadUpdate) -> Optional[Lead]:
        """Update a lead's information"""
        db = await get_database()
        update_data = lead_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        try:
            object_id = ObjectId(lead_id)
        except Exception:
            return None

        result = await db.leads.update_one(
            {"_id": object_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            updated_lead = await db.leads.find_one({"_id": object_id})
            return Lead(**updated_lead)
        
        return None

    async def add_message_to_lead(self, lead_id: str, message: str, role: str) -> Optional[Lead]:
        """Add a message to a lead's conversation history"""
        db = await get_database()
        message_obj = {
            "role": role,
            "content": message,
            "timestamp": datetime.utcnow()
        }
        
        try:
            object_id = ObjectId(lead_id)
        except Exception:
            return None

        result = await db.leads.update_one(
            {"_id": object_id},
            {
                "$push": {"messages": message_obj},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        if result.modified_count > 0:
            updated_lead = await db.leads.find_one({"_id": object_id})
            return Lead(**updated_lead)
        
        return None

    async def update_lead_intent(self, lead_id: str, intent: LeadIntent) -> Optional[Lead]:
        """Update a lead's intent and trigger appropriate workflows"""
        db = await get_database()
        
        try:
            object_id = ObjectId(lead_id)
        except Exception:
            return None

        result = await db.leads.update_one(
            {"_id": object_id},
            {
                "$set": {
                    "intent": intent.value,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            updated_lead = await db.leads.find_one({"_id": object_id})
            
            # Trigger workflow if lead is now hot
            if intent == LeadIntent.HOT:
                from app.services.workflow_service import WorkflowService
                workflow_service = WorkflowService()
                await workflow_service.trigger_event("on_hot_lead", updated_lead)
            
            return Lead(**updated_lead)
        
        return None

    async def get_all_leads(self) -> List[Lead]:
        """Get all leads"""
        db = await get_database()
        leads_cursor = db.leads.find()
        leads = []
        async for lead in leads_cursor:
            leads.append(Lead(**lead))
        return leads

    async def get_leads_by_source(self, source: LeadSource) -> List[Lead]:
        """Get leads by source"""
        db = await get_database()
        leads_cursor = db.leads.find({"source": source.value})
        leads = []
        async for lead in leads_cursor:
            leads.append(Lead(**lead))
        return leads

    async def get_leads_by_intent(self, intent: LeadIntent) -> List[Lead]:
        """Get leads by intent"""
        db = await get_database()
        leads_cursor = db.leads.find({"intent": intent.value})
        leads = []
        async for lead in leads_cursor:
            leads.append(Lead(**lead))
        return leads