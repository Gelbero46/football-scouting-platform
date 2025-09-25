from pydantic import BaseModel, Field, ConfigDict  
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

class CoachBase(BaseModel):
    name: str = Field(..., max_length=255)
    current_club: Optional[str] = None
    current_role: Optional[str] = None
    nationality: Optional[str] = None

class CoachCreate(CoachBase):
    preferred_formation: Optional[str] = None
    coaching_level: Optional[str] = None

class CoachResponse(CoachBase):
    id: uuid.UUID
    preferred_formation: Optional[str] = None
    tactical_style: Optional[Dict[str, Any]] = None
    overall_rating: Optional[int] = None
    created_at: datetime
    
    # class Config:
    #     from_attributes = True
    model_config = ConfigDict(from_attributes=True)