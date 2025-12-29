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
    second_nationality: Optional[str]= None
    scouting_notes: Optional[str]= None

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
    weekly_wage_eur: Optional[int] = Field(None, ge=0)
    overall_rating: Optional[int]= Field(None, ge=0, le=100)
    potential_rating: Optional[int] = Field(None, ge=0, le=100)
 
class PlayerStats(BaseModel):
    """Player statistics schema"""
    goals: Optional[int] = 0
    assists: Optional[int] = 0
    appearances: Optional[int] = 0
    minutes_played: Optional[int] = 0
    yellow_cards: Optional[int] = 0
    red_cards: Optional[int] = 0

class PlayerSearchResponse(BaseModel):
    """Enhanced player response for search results"""
    id: uuid.UUID
    name: str
    position: str
    current_club: Optional[str] = None
    nationality: Optional[str] = None
    age: Optional[int] = None
    market_value_eur: Optional[int] = None
    overall_rating: Optional[int] = None
    match_score: Optional[float] = None  # For search relevance

class PlayerUpdate(PlayerCreate):
    # name: Optional[str] = None
    # current_club: Optional[str] = None
    # market_value_eur: Optional[int] = None
    # overall_rating: Optional[int] = Field(None, ge=0, le=100)
    # scouting_notes: Optional[str] = None

    pass

class PlayerResponse(PlayerBase):
    id: uuid.UUID
    age: Optional[int] = None
    date_of_birth: Optional[date] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    preferred_foot: Optional[str] = None
    secondary_positions: Optional[List[str]] = []
    market_value_eur: Optional[int] = None
    weekly_wage_eur: Optional[int] = None
    overall_rating: Optional[int] = None
    potential_rating: Optional[int] = None
    current_season_stats: Optional[Dict[str, Any]] = None
    created_by: Optional[uuid.UUID]
    created_at: datetime
    
    # class Config:
    #     from_attributes = True
    model_config = ConfigDict(from_attributes=True)