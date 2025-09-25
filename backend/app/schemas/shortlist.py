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