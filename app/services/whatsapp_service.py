from typing import Dict, Any
from app.services.ai_service import AIService
from app.services.lead_service import LeadService
from app.constants.enums import LeadSource
from app.models.lead import LeadCreate


class WhatsAppService:
    def __init__(self):
        self.ai_service = AIService()
        self.lead_service = LeadService()

    async def process_webhook_payload(self, payload: Dict[str, Any], tenant_id: str) -> Dict[str, str]:
        """Process incoming WhatsApp webhook payload"""
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                
                for message in messages:
                    if message.get("type") == "text":
                        return await self._handle_text_message(message, value, tenant_id)
        
        return {"status": "processed"}

    async def _handle_text_message(self, message: Dict[str, Any], value: Dict[str, Any], tenant_id: str) -> Dict[str, str]:
        """Handle incoming text message"""
        phone_number = message["from"]
        text = message["text"]["body"]
        
        # Check if lead already exists, filtered by tenant_id
        lead = await self.lead_service.get_lead_by_phone(phone_number, tenant_id)
        
        if not lead:
            # Create new lead with tenant_id
            lead_data = LeadCreate(
                tenant_id=tenant_id,
                name=phone_number,  # We'll update this later when we get the name
                email="",  # We'll update this later when we get the email
                phone=phone_number,
                source=LeadSource.WHATSAPP
            )
            lead = await self.lead_service.create_lead(lead_data)
        
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
            "recipient_id": phone_number,
            "response": ai_response
        }