from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas.lead import ChatRequest, ChatResponse
from app.services.ai_service import AIService
from app.services.lead_service import LeadService
from app.constants.enums import LeadSource
from app.models.lead import LeadCreate


router = APIRouter()
ai_service = AIService()
lead_service = LeadService()


import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ... (rest of the imports)

@router.post("/respond", response_model=ChatResponse)
async def chat_respond(chat_request: ChatRequest):
    """Generate AI response for chat messages"""
    logger.info("--- chat_respond started ---")
    try:
        # Get or create lead based on user_id and source
        logger.info("Getting or creating lead...")
        lead = None
        
        if chat_request.source == LeadSource.WHATSAPP.value:
            lead = await lead_service.get_lead_by_phone(chat_request.user_id)
        # Add other sources as needed
        
        if not lead:
            # Create a new lead
            logger.info("Creating a new lead...")
            lead_data = LeadCreate(
                name=chat_request.user_id,
                email="",
                phone=chat_request.user_id if chat_request.source == LeadSource.WHATSAPP.value else "",
                source=LeadSource(chat_request.source)
            )
            lead = await lead_service.create_lead(lead_data)
            logger.info("New lead created.")
        
        # Generate AI response
        logger.info("Generating AI response...")
        ai_response = await ai_service.generate_response(
            chat_request.message,
            lead.messages if lead.messages else []
        )
        logger.info("AI response generated.")
        
        # Detect intent
        logger.info("Detecting intent...")
        intent = await ai_service.detect_intent(chat_request.message, lead.messages if lead.messages else [])
        logger.info(f"Intent detected: {intent}")
        
        # Add the user message and AI response to the conversation
        logger.info("Adding messages to lead history...")
        await lead_service.add_message_to_lead(str(lead.id), chat_request.message, "user")
        await lead_service.add_message_to_lead(str(lead.id), ai_response, "assistant")
        logger.info("Messages added.")
        
        # Update intent if needed
        if intent in ["HOT", "WARM", "COLD"]:
            logger.info("Updating lead intent...")
            from app.constants.enums import LeadIntent
            intent_map = {
                "HOT": LeadIntent.HOT,
                "WARM": LeadIntent.WARM,
                "COLD": LeadIntent.COLD
            }
            await lead_service.update_lead_intent(str(lead.id), intent_map.get(intent, LeadIntent.COLD))
            logger.info("Lead intent updated.")
        
        logger.info("--- chat_respond finished ---")
        return ChatResponse(
            response=ai_response,
            intent=intent,
            follow_up=True  # In a real implementation, this would be determined by the AI
        )
    except Exception as e:
        logger.error(f"Error in chat_respond: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating chat response: {str(e)}")