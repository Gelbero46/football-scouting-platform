from pydantic import BaseModel, Field, EmailStr, ConfigDict  
from typing import Optional
from datetime import datetime
import uuid

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str = Field(..., description="User role: admin, analyst, coach, scout")

class UserCreate(UserBase):
    clerk_id: str = Field(..., description="Clerk user ID")

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: uuid.UUID
    clerk_id: str
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    # class Config:
    #     from_attributes = True
    model_config = ConfigDict(from_attributes=True)