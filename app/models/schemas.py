from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from enum import Enum

class SearchType(str, Enum):
    CASE_NUMBER = "case_number"
    COMPLAINANT = "complainant"
    RESPONDENT = "respondent"
    COMPLAINANT_ADVOCATE = "complainant_advocate"
    RESPONDENT_ADVOCATE = "respondent_advocate"
    INDUSTRY_TYPE = "industry_type"
    JUDGE = "judge"

class CaseSearchRequest(BaseModel):
    state: str = Field(..., description="State name (e.g., 'KARNATAKA')")
    commission: str = Field(..., description="Commission name (e.g., 'Bangalore 1st & Rural Additional')")
    search_value: str = Field(..., description="Search term")
    
    class Config:
        json_schema_extra = {
            "example": {
                "state": "KARNATAKA",
                "commission": "Bangalore 1st & Rural Additional",
                "search_value": "Reddy"
            }
        }

class Case(BaseModel):
    case_number: str = Field(..., description="Case number")
    case_stage: str = Field(..., description="Current stage of the case")
    filing_date: str = Field(..., description="Case filing date (YYYY-MM-DD)")
    complainant: str = Field(..., description="Complainant name")
    complainant_advocate: str = Field(..., description="Complainant's advocate")
    respondent: str = Field(..., description="Respondent name") 
    respondent_advocate: str = Field(..., description="Respondent's advocate")
    document_link: str = Field(..., description="Link to case documents")
    
    class Config:
        json_schema_extra = {
            "example": {
                "case_number": "123/2025",
                "case_stage": "Hearing",
                "filing_date": "2025-02-01",
                "complainant": "John Doe",
                "complainant_advocate": "Adv. Reddy",
                "respondent": "XYZ Ltd.",
                "respondent_advocate": "Adv. Mehta",
                "document_link": "https://e-jagriti.gov.in/.../case123"
            }
        }

class State(BaseModel):
    id: str = Field(..., description="Internal state ID")
    name: str = Field(..., description="State name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "KA",
                "name": "KARNATAKA"
            }
        }

class Commission(BaseModel):
    id: str = Field(..., description="Internal commission ID")
    name: str = Field(..., description="Commission name")
    state_id: str = Field(..., description="Parent state ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "KA_BLR_1",
                "name": "Bangalore 1st & Rural Additional",
                "state_id": "KA"
            }
        }

class CaseSearchResponse(BaseModel):
    cases: List[Case] = Field(..., description="List of matching cases")
    total_count: int = Field(..., description="Total number of cases found")
    search_parameters: CaseSearchRequest = Field(..., description="Search parameters used")
    
class StatesResponse(BaseModel):
    states: List[State] = Field(..., description="List of available states")
    
class CommissionsResponse(BaseModel):
    commissions: List[Commission] = Field(..., description="List of commissions for the state")
    state_id: str = Field(..., description="State ID")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")