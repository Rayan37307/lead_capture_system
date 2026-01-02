from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from app.services.whatsapp_service import WhatsAppService
from app.services.instagram_service import InstagramService
from app.config.settings import settings
from app.utils.security import verify_signature


router = APIRouter()
whatsapp_service = WhatsAppService()
instagram_service = InstagramService()


@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """Handle WhatsApp webhook"""
    payload = await request.json()
    
    # Verify webhook signature if needed
    # signature = request.headers.get("X-Hub-Signature-256")
    # if not verify_signature(payload, signature):
    #     raise HTTPException(status_code=403, detail="Invalid signature")
    
    try:
        result = await whatsapp_service.process_webhook_payload(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing WhatsApp webhook: {str(e)}")


@router.post("/instagram")
async def instagram_webhook(request: Request):
    """Handle Instagram webhook"""
    payload = await request.json()
    
    # Verify webhook signature if needed
    # signature = request.headers.get("X-Hub-Signature-256")
    # if not verify_signature(payload, signature):
    #     raise HTTPException(status_code=403, detail="Invalid signature")
    
    try:
        result = await instagram_service.process_webhook_payload(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing Instagram webhook: {str(e)}")


@router.get("/whatsapp")
async def verify_whatsapp_webhook(
    hub_verify_token: str = None,
    hub_challenge: str = None
):
    """Verify WhatsApp webhook"""
    if hub_verify_token == settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN:
        return hub_challenge
    else:
        raise HTTPException(status_code=403, detail="Invalid verification token")


@router.get("/instagram")
async def verify_instagram_webhook(
    hub_verify_token: str = None,
    hub_challenge: str = None
):
    """Verify Instagram webhook"""
    if hub_verify_token == settings.INSTAGRAM_WEBHOOK_VERIFY_TOKEN:
        return hub_challenge
    else:
        raise HTTPException(status_code=403, detail="Invalid verification token")


@router.post("/website")
async def website_webhook(request: Request):
    """Handle website chat webhook"""
    payload = await request.json()
    
    # Process website chat message
    # This would typically come from your Next.js frontend
    message = payload.get("message")
    user_id = payload.get("user_id")
    
    if not message or not user_id:
        raise HTTPException(status_code=400, detail="Message and user_id are required")
    
    # In a real implementation, you would process the website chat message
    # similar to how WhatsApp and Instagram messages are processed
    # For now, we'll return a placeholder response
    
    return {"status": "received", "message": "Website message received"}