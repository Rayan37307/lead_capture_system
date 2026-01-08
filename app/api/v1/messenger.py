from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import hashlib
import hmac
import logging
from typing import Dict, Any, List

from app.schemas.lead import ChatRequest
from app.services.ai_service import AIService
from app.services.lead_service import LeadService
from app.constants.enums import LeadSource
from app.models.lead import LeadCreate
from app.config.settings import settings


router = APIRouter()
ai_service = AIService()
lead_service = LeadService()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """
    Verify the signature of the incoming webhook request
    """
    expected_signature = hmac.new(
        settings.FB_APP_SECRET.encode('utf-8'),
        payload,
        hashlib.sha1
    ).hexdigest()
    
    expected_header = f"sha1={expected_signature}"
    return hmac.compare_digest(signature, expected_header)


@router.get("/messenger/{tenant_id}")
async def verify_webhook(tenant_id: str, request: Request):
    """
    Verify the webhook with Facebook
    """
    try:
        # Get the verification parameters
        hub_verify_token = request.query_params.get("hub.verify_token")
        hub_challenge = request.query_params.get("hub.challenge")
        
        # Check if the verification token matches
        if hub_verify_token == settings.FB_WEBHOOK_VERIFY_TOKEN:
            logger.info(f"Webhook verified for tenant: {tenant_id}")
            return JSONResponse(content=int(hub_challenge))
        else:
            logger.error(f"Webhook verification failed for tenant: {tenant_id}")
            raise HTTPException(status_code=403, detail="Forbidden")
    except Exception as e:
        logger.error(f"Error during webhook verification: {e}")
        raise HTTPException(status_code=500, detail="Verification error")


@router.post("/messenger/{tenant_id}")
async def handle_messenger_webhook(tenant_id: str, request: Request, background_tasks: BackgroundTasks):
    """
    Handle incoming messages from Facebook Messenger
    """
    try:
        # Get the signature from the request header
        signature = request.headers.get("X-Hub-Signature")
        if not signature and settings.FB_APP_SECRET:
            logger.warning("No signature provided, skipping verification")
        elif signature and settings.FB_APP_SECRET:
            # Verify the signature
            body = await request.body()
            if not verify_webhook_signature(body, signature):
                logger.error("Invalid signature")
                raise HTTPException(status_code=403, detail="Forbidden")
        
        # Parse the request body
        payload = await request.json()
        logger.info(f"Received Messenger payload for tenant {tenant_id}: {payload}")
        
        # Process the messaging events
        for entry in payload.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                # Handle different types of messaging events
                if "message" in messaging_event and "text" in messaging_event["message"]:
                    # Extract message details
                    sender_id = messaging_event["sender"]["id"]
                    message_text = messaging_event["message"]["text"]
                    
                    logger.info(f"Processing message from {sender_id}: {message_text}")
                    
                    # Process the message in the background
                    background_tasks.add_task(
                        process_messenger_message,
                        tenant_id,
                        sender_id,
                        message_text
                    )
        
        # Return a success response
        return JSONResponse(content={"status": "success"})
    
    except Exception as e:
        logger.error(f"Error handling Messenger webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing Messenger webhook: {str(e)}")


async def process_messenger_message(tenant_id: str, sender_id: str, message_text: str):
    """
    Process a Messenger message in the background
    """
    try:
        logger.info(f"Processing Messenger message for tenant {tenant_id}, sender {sender_id}")
        
        # Create a chat request
        chat_request = ChatRequest(
            message=message_text,
            user_id=sender_id,
            source=LeadSource.FACEBOOK.value,  # Add FACEBOOK to LeadSource enum
            tenant_id=tenant_id
        )
        
        # Get or create lead based on sender_id
        lead = await lead_service.get_lead_by_facebook_id(sender_id, tenant_id)
        
        if not lead:
            # Create a new lead
            logger.info("Creating a new lead...")
            lead_data = LeadCreate(
                tenant_id=tenant_id,
                name=sender_id,  # We'll update with real name later if possible
                email="",
                phone="",
                source=LeadSource.FACEBOOK
            )
            lead = await lead_service.create_lead(lead_data)
            logger.info("New lead created.")
        
        # Generate AI response
        logger.info("Generating AI response...")
        ai_response = await ai_service.generate_response(
            chat_request.message,
            lead.messages if lead.messages else []
        )
        logger.info(f"AI response generated: {ai_response}")
        
        # Detect intent
        logger.info("Detecting intent...")
        intent = await ai_service.detect_intent(chat_request.message, lead.messages if lead.messages else [])
        logger.info(f"Intent detected: {intent}")
        
        # Add the user message and AI response to the conversation
        logger.info("Adding messages to lead history...")
        await lead_service.add_message_to_lead(str(lead.id), chat_request.message, "user", tenant_id)
        await lead_service.add_message_to_lead(str(lead.id), ai_response, "assistant", tenant_id)
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
            await lead_service.update_lead_intent(str(lead.id), intent_map.get(intent, LeadIntent.COLD), tenant_id)
            logger.info("Lead intent updated.")
        
        # Send the response back to the user via Facebook Messenger
        await send_messenger_response(sender_id, ai_response)
        
    except Exception as e:
        logger.error(f"Error processing Messenger message: {e}", exc_info=True)


async def send_messenger_response(recipient_id: str, message_text: str):
    """
    Send a response back to the user via Facebook Messenger
    """
    import httpx
    
    try:
        url = f"https://graph.facebook.com/v18.0/me/messages"
        
        params = {
            "access_token": settings.FB_PAGE_ACCESS_TOKEN
        }
        
        data = {
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "text": message_text
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, params=params, json=data)
            
        if response.status_code != 200:
            logger.error(f"Failed to send Messenger response: {response.text}")
        else:
            logger.info(f"Successfully sent response to {recipient_id}")
            
    except Exception as e:
        logger.error(f"Error sending Messenger response: {e}", exc_info=True)