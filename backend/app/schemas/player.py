from pydantic import BaseModel, Field, ConfigDict, field_validator  
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import uuid

class PlayerBase(BaseModel):
    name: str = Field(..., max_length=255)
    full_name: Optional[str] = None
    position: str = Field(..., max_length=50)
    current_club: Optional[str] = None
    nationality: Optional[str] = None

class PlayerCreate(PlayerBase):
    date_of_birth: Optional[date] = None
    height_cm: Optional[int] = Field(None, ge=150, le=220)
    weight_kg: Optional[int] = Field(None, ge=50, le=120)
    preferred_foot: Optional[str] = Field(None, description="Preferred foot")
    
    @field_validator('preferred_foot')
    @classmethod
    def validate_preferred_foot(cls, v):
        if v is not None and v not in ['left', 'right', 'both']:
            raise ValueError('Preferred foot must be left, right, or both')
        return v
    secondary_positions: Optional[List[str]] = []
    market_value_eur: Optional[int] = Field(None, ge=0)

class PlayerUpdate(BaseModel):
    name: Optional[str] = None
    current_club: Optional[str] = None
    market_value_eur: Optional[int] = None
    overall_rating: Optional[int] = Field(None, ge=0, le=100)
    scouting_notes: Optional[str] = None

class PlayerResponse(PlayerBase):
    id: uuid.UUID
    age: Optional[int] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    preferred_foot: Optional[str] = None
    secondary_positions: Optional[List[str]] = []
    market_value_eur: Optional[int] = None
    overall_rating: Optional[int] = None
    potential_rating: Optional[int] = None
    current_season_stats: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    # class Config:
    #     from_attributes = True
    model_config = ConfigDict(from_attributes=True)