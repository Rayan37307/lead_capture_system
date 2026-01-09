from typing import List, Optional
from datetime import datetime
import logging

from app.models.lead import Lead, LeadCreate, LeadUpdate
from app.constants.enums import LeadIntent
from app.database import sqlite_handler
from app.services.google_sheets_service import GoogleSheetsService

logger = logging.getLogger(__name__)

class LeadService:
    def __init__(self):
        self.google_sheets_service = GoogleSheetsService()
        # The new handler does not require a global client, so init is simpler.

    def _dict_to_lead_model(self, lead_dict: Optional[dict]) -> Optional[Lead]:
        """Converts a dictionary from the DB to a Pydantic Lead model."""
        if not lead_dict:
            return None
        # Pydantic can be particular about 'id' vs '_id'.
        # Our new schema uses 'id' consistently.
        lead_dict['_id'] = lead_dict.get('id')
        return Lead.model_validate(lead_dict)

    async def create_lead(self, lead_data: LeadCreate, tenant_id: str) -> Optional[Lead]:
        """Create a new lead in the database."""
        logger.info(f"--- Creating lead for tenant {tenant_id} ---")
        
        # Initialize the database for the tenant if it's the first time
        await sqlite_handler.initialize_database(tenant_id)
        
        created_lead_dict = await sqlite_handler.create_lead(tenant_id, lead_data)
        
        if not created_lead_dict:
            logger.error("Lead creation failed in database handler.")
            return None
        
        logger.info(f"Lead {created_lead_dict['id']} inserted into database.")

        # Sync to Google Sheets if enabled
        # This part remains mostly the same, but we pass the dict
        # await self.google_sheets_service.add_lead_to_sheet(created_lead_dict)

        # Trigger workflow for new lead
        # from app.services.workflow_service import WorkflowService
        # workflow_service = WorkflowService()
        # await workflow_service.trigger_event("on_lead_created", created_lead_dict)

        logger.info("--- create_lead finished ---")
        return self._dict_to_lead_model(created_lead_dict)

    async def get_lead_by_id(self, lead_id: str, tenant_id: str) -> Optional[Lead]:
        """Get a lead by its ID."""
        lead_dict = await sqlite_handler.get_lead_by_id(tenant_id, lead_id)
        return self._dict_to_lead_model(lead_dict)

    async def get_lead_by_facebook_id(self, facebook_id: str, tenant_id: str) -> Optional[Lead]:
        """Get a lead by Facebook ID."""
        # This assumes the facebook_id is stored in the 'facebook_id' column
        lead_dict = await sqlite_handler.get_lead_by_facebook_id(tenant_id, facebook_id)
        if not lead_dict:
             # Fallback for old data structure, might be removed later
            logger.info(f"Could not find lead by facebook_id, trying by name for tenant {tenant_id}")
            # This logic would need a new DB handler function if we want to keep it
            pass
        return self._dict_to_lead_model(lead_dict)

    async def update_lead(self, lead_id: str, lead_update: LeadUpdate, tenant_id: str) -> Optional[Lead]:
        """Update a lead's information."""
        # This requires a new, more complex function in the sqlite_handler
        # For now, we only implement intent updates and adding messages
        # as a full update is more involved.
        logger.warning("Full lead update not yet implemented for SQLite.")
        return await self.get_lead_by_id(lead_id, tenant_id)


    async def add_message_to_lead(self, lead_id: str, message: str, role: str, tenant_id: str) -> Optional[Lead]:
        """Add a message to a lead's conversation history."""
        updated_lead_dict = await sqlite_handler.add_message_to_lead(tenant_id, lead_id, role, message)
        return self._dict_to_lead_model(updated_lead_dict)

    async def update_lead_intent(self, lead_id: str, intent: LeadIntent, tenant_id: str) -> Optional[Lead]:
        """Update a lead's intent and trigger appropriate workflows."""
        updated_lead_dict = await sqlite_handler.update_lead_intent(tenant_id, lead_id, intent)
        
        if updated_lead_dict and intent == LeadIntent.HOT:
            logger.info(f"Triggering 'on_hot_lead' workflow for lead {lead_id}")
            # from app.services.workflow_service import WorkflowService
            # workflow_service = WorkflowService()
            # await workflow_service.trigger_event("on_hot_lead", updated_lead_dict)
            pass

        return self._dict_to_lead_model(updated_lead_dict)

    async def get_all_leads(self, tenant_id: str) -> List[Lead]:
        """Get all leads for a tenant."""
        leads_list = await sqlite_handler.get_all_leads(tenant_id)
        return [self._dict_to_lead_model(lead) for lead in leads_list if lead]
    
    # get_leads_by_source and get_leads_by_intent would need new handler functions
    # async def get_leads_by_source(...)
    # async def get_leads_by_intent(...)
