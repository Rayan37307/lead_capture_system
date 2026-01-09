from typing import Dict, Any
from app.services.ai_service import AIService
from app.services.lead_service import LeadService
from app.constants.enums import LeadSource
from app.models.lead import LeadCreate


class InstagramService:
    def __init__(self):
        self.ai_service = AIService()
        self.lead_service = LeadService()

    async def process_webhook_payload(self, payload: Dict[str, Any], tenant_id: str) -> Dict[str, str]:
        """Process incoming Instagram webhook payload"""
        for entry in payload.get("entry", []):
            messaging_events = entry.get("messaging", [])
            
            for event in messaging_events:
                if "message" in event and "text" in event["message"]:
                    return await self._handle_text_message(event, tenant_id)
        
        return {"status": "processed"}

    async def _handle_text_message(self, event: Dict[str, Any], tenant_id: str) -> Dict[str, str]:
        """Handle incoming text message from Instagram"""
        sender_id = event["sender"]["id"]
        text = event["message"]["text"]
        
        # For Instagram, we might need to get the user's information
        # This is a simplified implementation
        user_name = f"instagram_user_{sender_id}"
        
        # Check if lead already exists, filtered by tenant_id
        # In a real implementation, you'd need to store Instagram user IDs
        # and match them to leads
        lead = None  # Placeholder - in real implementation, find by Instagram ID and tenant_id
        
        # For now, if lead is None, we create a new one with tenant_id
        if not lead:
            # Create new lead with tenant_id
            lead_data = LeadCreate(
                name=user_name,
                email="",  # We'll update this later when we get the email
                phone="",  # We'll update this later when we get the phone
                source=LeadSource.INSTAGRAM
            )
            lead = await self.lead_service.create_lead(lead_data, tenant_id)
        
        # Add the message to the lead's conversation history
        await self.lead_service.add_message_to_lead(str(lead.id), text, "user", tenant_id)
        
        # Generate AI response
        ai_response = await self.ai_service.generate_response(
            text, 
            lead.messages
        )
        
        # Detect intent
        intent = await self.ai_service.detect_intent(text, lead.messages)
        
        # Update lead intent if needed
        if intent in ["HOT", "WARM", "COLD"]:
            from app.constants.enums import LeadIntent
            intent_map = {
                "HOT": LeadIntent.HOT,
                "WARM": LeadIntent.WARM,
                "COLD": LeadIntent.COLD
            }
            await self.lead_service.update_lead_intent(str(lead.id), intent_map.get(intent, LeadIntent.COLD), tenant_id)
        
        # Add AI response to conversation history
        await self.lead_service.add_message_to_lead(str(lead.id), ai_response, "assistant", tenant_id)
        
        return {
            "recipient_id": sender_id,
            "response": ai_response
        }