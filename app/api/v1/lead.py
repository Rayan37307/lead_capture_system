from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.lead import LeadResponse
from app.models.lead import LeadCreate
from app.services.lead_service import LeadService
from app.constants.enums import LeadSource, LeadIntent
from app.utils.security import get_current_user # Import get_current_user
from app.models.user import User # Import User model


router = APIRouter()
lead_service = LeadService()


@router.post("/", response_model=LeadResponse)
async def create_lead(
    lead: LeadCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new lead"""
    if lead.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Lead tenant_id does not match authenticated user's tenant_id"
        )
    try:
        created_lead = await lead_service.create_lead(lead)
        return LeadResponse(
            id=str(created_lead.id),
            tenant_id=created_lead.tenant_id, # Include tenant_id in response
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
async def get_lead(
    lead_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a lead by ID"""
    try:
        lead = await lead_service.get_lead_by_id(lead_id, current_user.tenant_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Enforce tenant ownership for retrieved lead
        if lead.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this lead")

        return LeadResponse(
            id=str(lead.id),
            tenant_id=lead.tenant_id, # Include tenant_id in response
            name=lead.name,
            email=lead.email,
            phone=lead.phone,
            source=lead.source,
            intent=lead.intent,
            messages=lead.messages,
            created_at=lead.created_at,
            updated_at=lead.updated_at
        )
    except HTTPException: # Re-raise HTTPExceptions
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching lead: {str(e)}")

@router.get("/")
async def get_all_leads(
    current_user: User = Depends(get_current_user)
):
    """Get all leads"""
    try:
        leads = await lead_service.get_all_leads(current_user.tenant_id)
        return [
            LeadResponse(
                id=str(lead.id),
                tenant_id=lead.tenant_id, # Include tenant_id in response
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
async def get_leads_by_source(
    source: LeadSource,
    current_user: User = Depends(get_current_user)
):
    """Get leads by source"""
    try:
        leads = await lead_service.get_leads_by_source(source, current_user.tenant_id)
        return [
            LeadResponse(
                id=str(lead.id),
                tenant_id=lead.tenant_id, # Include tenant_id in response
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


async def get_leads_by_intent(


    intent: LeadIntent,


    current_user: User = Depends(get_current_user)


):


    """Get leads by intent"""


    try:


        leads = await lead_service.get_leads_by_intent(intent, current_user.tenant_id)


        return [


            LeadResponse(


                id=str(lead.id),


                tenant_id=lead.tenant_id, # Include tenant_id in response


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

