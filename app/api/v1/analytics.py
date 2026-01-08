from fastapi import APIRouter, Depends
from app.schemas.lead import AnalyticsSummary
from app.services.lead_service import LeadService
from app.constants.enums import LeadIntent
from app.utils.security import get_current_user # Import get_current_user
from app.models.user import User # Import User model


router = APIRouter()
lead_service = LeadService()


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    current_user: User = Depends(get_current_user)
):
    """Get analytics summary"""
    # In a real implementation, this would aggregate data from the database
    # For now, we'll return placeholder values
    
    # Get all leads for the current tenant
    all_leads = await lead_service.get_all_leads(current_user.tenant_id)
    
    # Calculate metrics
    total_conversations = len(all_leads)  # Simplified: each lead represents a conversation
    leads_captured = len(all_leads)
    
    hot_leads = len([lead for lead in all_leads if lead.intent == LeadIntent.HOT])
    warm_leads = len([lead for lead in all_leads if lead.intent == LeadIntent.WARM])
    cold_leads = len([lead for lead in all_leads if lead.intent == LeadIntent.COLD])
    
    # Placeholder values for other metrics
    avg_response_time = 0.0  # In seconds
    conversion_rate = 0.0  # As a percentage
    
    return AnalyticsSummary(
        total_conversations=total_conversations,
        leads_captured=leads_captured,
        hot_leads=hot_leads,
        warm_leads=warm_leads,
        cold_leads=cold_leads,
        avg_response_time=avg_response_time,
        conversion_rate=conversion_rate
    )


@router.get("/detailed")
async def get_detailed_analytics(
    current_user: User = Depends(get_current_user) # Protect this endpoint too
):
    """Get detailed analytics"""
    # This would return more detailed analytics data
    # For now, we'll return a placeholder
    return {
        "message": "Detailed analytics endpoint for tenant " + str(current_user.tenant_id),
        "data": {}
    }