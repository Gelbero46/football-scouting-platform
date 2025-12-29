from pydantic import BaseModel, Field, ConfigDict, field_validator  
from typing import Optional, List
from datetime import datetime
import uuid

class ShortlistBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    type: str = Field(..., description="Type: player or coach")
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        if v not in ['player', 'coach']:
            raise ValueError('Type must be player or coach')
        return v

class ShortlistCreate(ShortlistBase):
    priority: Optional[str] = Field("medium", description="Priority level")
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        if v not in ['low', 'medium', 'high', 'urgent']:
            raise ValueError('Invalid priority level')
        return v

class ShortlistItemResponse(BaseModel):
    id: uuid.UUID
    player_name: Optional[str] = None
    coach_name: Optional[str] = None
    status: str
    priority: int
    notes: Optional[str] = None


class ShortlistItemCreate(BaseModel):
    player_id: Optional[uuid.UUID] = None
    coach_id: Optional[uuid.UUID] = None
    status: str = Field("identified", description="Item status")
    priority: int = Field(3, ge=1, le=5, description="Priority level (1-5 stars)")
    notes: Optional[str] = None
    estimated_fee_eur: Optional[int] = None
    wage_demands_eur: Optional[int] = None

class ShortlistItemUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    scout_rating: Optional[int] = Field(None, ge=0, le=100)
    estimated_fee_eur: Optional[int] = None
    wage_demands_eur: Optional[int] = None

class ShortlistUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    deadline: Optional[datetime] = None
    budget_eur: Optional[int] = None


class ShortlistResponse(ShortlistBase):
    id: uuid.UUID
    status: str
    priority: str
    items_count: Optional[int] = 0
    items: Optional[List[ShortlistItemResponse]] = []
    created_at: datetime
    
    # class Config:
    #     from_attributes = True
    model_config = ConfigDict(from_attributes=True)