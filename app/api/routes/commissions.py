from fastapi import APIRouter, HTTPException, Depends, Request, Path
from typing import List

from app.models.schemas import Commission, CommissionsResponse
from app.services.jagriti_service import JagritiService

router = APIRouter()

def get_jagriti_service(request: Request) -> JagritiService:
    return request.app.state.jagriti_service

@router.get("/{state_id}", response_model=CommissionsResponse)
async def get_commissions(
    state_id: str = Path(..., description="State ID"),
    jagriti_service: JagritiService = Depends(get_jagriti_service)
):
    """Get list of commissions for a specific state with their internal IDs"""
    try:
        commissions = await jagriti_service.get_commissions(state_id)
        return CommissionsResponse(
            commissions=commissions,
            state_id=state_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch commissions for state {state_id}: {str(e)}"
        )