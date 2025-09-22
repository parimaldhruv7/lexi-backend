from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List

from app.models.schemas import (
    Case, CaseSearchRequest, CaseSearchResponse, 
    SearchType, ErrorResponse
)
from app.services.jagriti_service import JagritiService

router = APIRouter()

def get_jagriti_service(request: Request) -> JagritiService:
    return request.app.state.jagriti_service

@router.post("/by-case-number", response_model=CaseSearchResponse)
async def search_by_case_number(
    search_request: CaseSearchRequest,
    jagriti_service: JagritiService = Depends(get_jagriti_service)
):
    """Search cases by case number"""
    try:
        cases = await jagriti_service.search_cases(
            SearchType.CASE_NUMBER,
            search_request.state,
            search_request.commission,
            search_request.search_value
        )
        
        return CaseSearchResponse(
            cases=cases,
            total_count=len(cases),
            search_parameters=search_request
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        # Likely captcha or portal change
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/by-complainant", response_model=CaseSearchResponse)
async def search_by_complainant(
    search_request: CaseSearchRequest,
    jagriti_service: JagritiService = Depends(get_jagriti_service)
):
    """Search cases by complainant name"""
    try:
        cases = await jagriti_service.search_cases(
            SearchType.COMPLAINANT,
            search_request.state,
            search_request.commission,
            search_request.search_value
        )
        
        return CaseSearchResponse(
            cases=cases,
            total_count=len(cases),
            search_parameters=search_request
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/by-respondent", response_model=CaseSearchResponse)
async def search_by_respondent(
    search_request: CaseSearchRequest,
    jagriti_service: JagritiService = Depends(get_jagriti_service)
):
    """Search cases by respondent name"""
    try:
        cases = await jagriti_service.search_cases(
            SearchType.RESPONDENT,
            search_request.state,
            search_request.commission,
            search_request.search_value
        )
        
        return CaseSearchResponse(
            cases=cases,
            total_count=len(cases),
            search_parameters=search_request
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/by-complainant-advocate", response_model=CaseSearchResponse)
async def search_by_complainant_advocate(
    search_request: CaseSearchRequest,
    jagriti_service: JagritiService = Depends(get_jagriti_service)
):
    """Search cases by complainant advocate name"""
    try:
        cases = await jagriti_service.search_cases(
            SearchType.COMPLAINANT_ADVOCATE,
            search_request.state,
            search_request.commission,
            search_request.search_value
        )
        
        return CaseSearchResponse(
            cases=cases,
            total_count=len(cases),
            search_parameters=search_request
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/by-respondent-advocate", response_model=CaseSearchResponse)
async def search_by_respondent_advocate(
    search_request: CaseSearchRequest,
    jagriti_service: JagritiService = Depends(get_jagriti_service)
):
    """Search cases by respondent advocate name"""
    try:
        cases = await jagriti_service.search_cases(
            SearchType.RESPONDENT_ADVOCATE,
            search_request.state,
            search_request.commission,
            search_request.search_value
        )
        
        return CaseSearchResponse(
            cases=cases,
            total_count=len(cases),
            search_parameters=search_request
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/by-industry-type", response_model=CaseSearchResponse)
async def search_by_industry_type(
    search_request: CaseSearchRequest,
    jagriti_service: JagritiService = Depends(get_jagriti_service)
):
    """Search cases by industry type"""
    try:
        cases = await jagriti_service.search_cases(
            SearchType.INDUSTRY_TYPE,
            search_request.state,
            search_request.commission,
            search_request.search_value
        )
        
        return CaseSearchResponse(
            cases=cases,
            total_count=len(cases),
            search_parameters=search_request
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/by-judge", response_model=CaseSearchResponse)
async def search_by_judge(
    search_request: CaseSearchRequest,
    jagriti_service: JagritiService = Depends(get_jagriti_service)
):
    """Search cases by judge name"""
    try:
        cases = await jagriti_service.search_cases(
            SearchType.JUDGE,
            search_request.state,
            search_request.commission,
            search_request.search_value
        )
        
        return CaseSearchResponse(
            cases=cases,
            total_count=len(cases),
            search_parameters=search_request
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Alternative GET endpoints with query parameters
@router.get("/by-case-number", response_model=CaseSearchResponse)
async def search_by_case_number_get(
    state: str,
    commission: str,
    search_value: str,
    jagriti_service: JagritiService = Depends(get_jagriti_service)
):
    """Search cases by case number (GET method)"""
    search_request = CaseSearchRequest(
        state=state,
        commission=commission,
        search_value=search_value
    )
    return await search_by_case_number(search_request, jagriti_service)

@router.get("/by-complainant", response_model=CaseSearchResponse)
async def search_by_complainant_get(
    state: str,
    commission: str,
    search_value: str,
    jagriti_service: JagritiService = Depends(get_jagriti_service)
):
    """Search cases by complainant name (GET method)"""
    search_request = CaseSearchRequest(
        state=state,
        commission=commission,
        search_value=search_value
    )
    return await search_by_complainant(search_request, jagriti_service)

@router.get("/by-respondent", response_model=CaseSearchResponse)
async def search_by_respondent_get(
    state: str,
    commission: str,
    search_value: str,
    jagriti_service: JagritiService = Depends(get_jagriti_service)
):
    """Search cases by respondent name (GET method)"""
    search_request = CaseSearchRequest(
        state=state,
        commission=commission,
        search_value=search_value
    )
    return await search_by_respondent(search_request, jagriti_service)

@router.get("/by-complainant-advocate", response_model=CaseSearchResponse)
async def search_by_complainant_advocate_get(
    state: str,
    commission: str,
    search_value: str,
    jagriti_service: JagritiService = Depends(get_jagriti_service)
):
    """Search cases by complainant advocate name (GET method)"""
    search_request = CaseSearchRequest(
        state=state,
        commission=commission,
        search_value=search_value
    )
    return await search_by_complainant_advocate(search_request, jagriti_service)

@router.get("/by-respondent-advocate", response_model=CaseSearchResponse)
async def search_by_respondent_advocate_get(
    state: str,
    commission: str,
    search_value: str,
    jagriti_service: JagritiService = Depends(get_jagriti_service)
):
    """Search cases by respondent advocate name (GET method)"""
    search_request = CaseSearchRequest(
        state=state,
        commission=commission,
        search_value=search_value
    )
    return await search_by_respondent_advocate(search_request, jagriti_service)

@router.get("/by-industry-type", response_model=CaseSearchResponse)
async def search_by_industry_type_get(
    state: str,
    commission: str,
    search_value: str,
    jagriti_service: JagritiService = Depends(get_jagriti_service)
):
    """Search cases by industry type (GET method)"""
    search_request = CaseSearchRequest(
        state=state,
        commission=commission,
        search_value=search_value
    )
    return await search_by_industry_type(search_request, jagriti_service)

@router.get("/by-judge", response_model=CaseSearchResponse)
async def search_by_judge_get(
    state: str,
    commission: str,
    search_value: str,
    jagriti_service: JagritiService = Depends(get_jagriti_service)
):
    """Search cases by judge name (GET method)"""
    search_request = CaseSearchRequest(
        state=state,
        commission=commission,
        search_value=search_value
    )
    return await search_by_judge(search_request, jagriti_service)