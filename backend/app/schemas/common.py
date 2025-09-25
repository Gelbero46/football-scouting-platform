from pydantic import BaseModel, Field, ConfigDict  
from typing import Any, Dict, Generic, List, Optional, TypeVar
from datetime import datetime

DataT = TypeVar('DataT')

class PaginationMeta(BaseModel):
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")

class StandardResponse(BaseModel, Generic[DataT]):
    success: bool = Field(True, description="Indicates if the request was successful")
    data: DataT = Field(..., description="Response data")
    message: Optional[str] = Field(None, description="Optional message")

class PaginatedResponse(BaseModel, Generic[DataT]):
    success: bool = Field(True, description="Indicates if the request was successful")
    data: List[DataT] = Field(..., description="List of items")
    meta: Dict[str, Any] = Field(..., description="Pagination metadata")

class ErrorResponse(BaseModel):
    success: bool = Field(False, description="Always false for error responses")
    error: Dict[str, Any] = Field(..., description="Error details")