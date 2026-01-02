from fastapi import APIRouter, HTTPException
from app.schemas.lead import LeadResponse
from app.models.lead import LeadCreate
from app.services.lead_service import LeadService
from app.constants.enums import LeadSource, LeadIntent


router = APIRouter()
lead_service = LeadService()


@router.post("/", response_model=LeadResponse)
async def create_lead(lead: LeadCreate):
    """Create a new lead"""
    try:
        created_lead = await lead_service.create_lead(lead)
        return LeadResponse(
            id=str(created_lead.id),
            name=created_lead.name,
            email=created_lead.email,
            phone=created_lead.phone,
            source=created_lead.source,
            intent=created_lead.intent,
            messages=created_lead.messages,
            created_at=created_lead.created_at,
            updated_at=created_lead.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating lead: {str(e)}")


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: str):
    """Get a lead by ID"""
    try:
        lead = await lead_service.get_lead_by_id(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        return LeadResponse(
            id=str(lead.id),
            name=lead.name,
            email=lead.email,
            phone=lead.phone,
            source=lead.source,
            intent=lead.intent,
            messages=lead.messages,
            created_at=lead.created_at,
            updated_at=lead.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching lead: {str(e)}")


@router.get("/")
async def get_all_leads():
    """Get all leads"""
    try:
        leads = await lead_service.get_all_leads()
        return [
            LeadResponse(
                id=str(lead.id),
                name=lead.name,
                email=lead.email,
                phone=lead.phone,
                source=lead.source,
                intent=lead.intent,
                messages=lead.messages,
                created_at=lead.created_at,
                updated_at=lead.updated_at
            )
            for lead in leads
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching leads: {str(e)}")


@router.get("/source/{source}")
async def get_leads_by_source(source: LeadSource):
    """Get leads by source"""
    try:
        leads = await lead_service.get_leads_by_source(source)
        return [
            LeadResponse(
                id=str(lead.id),
                name=lead.name,
                email=lead.email,
                phone=lead.phone,
                source=lead.source,
                intent=lead.intent,
                messages=lead.messages,
                created_at=lead.created_at,
                updated_at=lead.updated_at
            )
            for lead in leads
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching leads by source: {str(e)}")


@router.get("/intent/{intent}")
async def get_leads_by_intent(intent: LeadIntent):
    """Get leads by intent"""
    try:
        leads = await lead_service.get_leads_by_intent(intent)
        return [
            LeadResponse(
                id=str(lead.id),
                name=lead.name,
                email=lead.email,
                phone=lead.phone,
                source=lead.source,
                intent=lead.intent,
                messages=lead.messages,
                created_at=lead.created_at,
                updated_at=lead.updated_at
            )
            for lead in leads
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching leads by intent: {str(e)}")