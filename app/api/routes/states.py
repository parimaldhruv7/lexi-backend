from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List

from app.models.schemas import State, StatesResponse
from app.services.jagriti_service import JagritiService

router = APIRouter()

def get_jagriti_service(request: Request) -> JagritiService:
    return request.app.state.jagriti_service

@router.get("", response_model=StatesResponse)
async def get_states(jagriti_service: JagritiService = Depends(get_jagriti_service)):
    """Get list of all available states with their internal IDs"""
    try:
        states = await jagriti_service.get_states()
        return StatesResponse(states=states)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch states: {str(e)}")

@router.get("/", response_model=StatesResponse)
async def get_states_alt(jagriti_service: JagritiService = Depends(get_jagriti_service)):
    """Alternative endpoint for getting states"""
    return await get_states(jagriti_service)