from pydantic import BaseModel, Field, ConfigDict, field_validator  
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class ReportBase(BaseModel):
    title: str = Field(..., max_length=255)
    type: str = Field(..., description="Report type")
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        valid_types = ['player_scout', 'coach_analysis', 'shortlist_summary', 'comparison']
        if v not in valid_types:
            raise ValueError(f'Invalid report type. Must be one of: {valid_types}')
        return v

class ReportCreate(ReportBase):
    parameters: Dict[str, Any] = Field(..., description="Report configuration")
    filters: Optional[Dict[str, Any]] = None

class ReportResponse(ReportBase):
    id: uuid.UUID
    status: str
    file_size: Optional[int] = None
    generated_at: Optional[datetime] = None
    download_count: int = 0
    
    # class Config:
    #     from_attributes = True
    model_config = ConfigDict(from_attributes=True)