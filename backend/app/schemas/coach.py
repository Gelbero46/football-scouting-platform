from pydantic import BaseModel, Field, ConfigDict  
from typing import Optional, Dict, Any, List
from datetime import datetime, date
import uuid

class CoachBase(BaseModel):
    name: str = Field(..., max_length=255)
    full_name: str = Field(..., max_length=255)
    current_club: Optional[str] = None
    current_role: Optional[str] = None
    nationality: Optional[str] = None

class CoachCreate(CoachBase):
    preferred_formation: Optional[str] = None
    date_of_birth: Optional[date] = None
    coaching_level: Optional[str] = None
    years_experience: Optional[int] = None
    estimated_salary_eur: Optional[int] = None
    scouting_notes: Optional[str] = None
    overall_rating: Optional[int] = None
    # potential_rating: Optional[int] = None

class CoachUpdate(CoachCreate):
    # name: Optional[str] = None
    # current_club: Optional[str] = None
    # current_role: Optional[str] = None
    # preferred_formation: Optional[str] = None
    # overall_rating: Optional[int] = Field(None, ge=0, le=100)
    # scouting_notes: Optional[str] = None
    pass

class CoachResponse(CoachBase):
    id: uuid.UUID
    age: Optional[int] = None
    preferred_formation: Optional[str] = None 
    years_experience: Optional[int] = None
    date_of_birth: Optional[date] = None
    estimated_salary_eur: Optional[int] = None
    scouting_notes: Optional[str] = None
    coaching_level: Optional[str] = None
    overall_rating: Optional[int] = None
    # potential_rating: Optional[int] = None
    tactical_style: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    # class Config:
    #     from_attributes = True
    model_config = ConfigDict(from_attributes=True)