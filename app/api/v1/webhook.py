from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from app.services.whatsapp_service import WhatsAppService
from app.services.instagram_service import InstagramService
from app.config.settings import settings


router = APIRouter()
whatsapp_service = WhatsAppService()
instagram_service = InstagramService()


@router.post("/whatsapp/{tenant_id}")
async def whatsapp_webhook(tenant_id: str, request: Request):
    """Handle WhatsApp webhook"""
    payload = await request.json()
    
    # Verify webhook signature if needed
    # signature = request.headers.get("X-Hub-Signature-256")
    # if not verify_signature(payload, signature):
    #     raise HTTPException(status_code=403, detail="Invalid signature")
    
    try:
        # Pass tenant_id to the service for processing
        result = await whatsapp_service.process_webhook_payload(payload, tenant_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing WhatsApp webhook for tenant {tenant_id}: {str(e)}")


@router.post("/instagram/{tenant_id}")
async def instagram_webhook(tenant_id: str, request: Request):
    """Handle Instagram webhook"""
    payload = await request.json()
    
    # Verify webhook signature if needed
    # signature = request.headers.get("X-Hub-Signature-256")
    # if not verify_signature(payload, signature):
    #     raise HTTPException(status_code=403, detail="Invalid signature")
    
    try:
        # Pass tenant_id to the service for processing
        result = await instagram_service.process_webhook_payload(payload, tenant_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing Instagram webhook for tenant {tenant_id}: {str(e)}")


@router.get("/whatsapp/{tenant_id}")
async def verify_whatsapp_webhook(
    tenant_id: str,
    hub_verify_token: str = None,
    hub_challenge: str = None
):
    """Verify WhatsApp webhook"""
    # In a multi-tenant setup, WHATSAPP_WEBHOOK_VERIFY_TOKEN should be tenant-specific
    # For now, we use a global token from settings or assume it's part of the tenant's config
    if hub_verify_token == settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN:
        return hub_challenge
    else:
        raise HTTPException(status_code=403, detail="Invalid verification token for tenant " + str(tenant_id))


@router.get("/instagram/{tenant_id}")
async def verify_instagram_webhook(
    tenant_id: str,
    hub_verify_token: str = None,
    hub_challenge: str = None
):
    """Verify Instagram webhook"""
    # In a multi-tenant setup, INSTAGRAM_WEBHOOK_VERIFY_TOKEN should be tenant-specific
    # For now, we use a global token from settings or assume it's part of the tenant's config
    if hub_verify_token == settings.INSTAGRAM_WEBHOOK_VERIFY_TOKEN:
        return hub_challenge
    else:
        raise HTTPException(status_code=403, detail="Invalid verification token for tenant " + str(tenant_id))


# The website_webhook is redundant if the chat widget directly calls /chat/respond.
# If there's a need for a generic website webhook that then routes to /chat/respond,
# it would be re-implemented here. For now, it is removed.