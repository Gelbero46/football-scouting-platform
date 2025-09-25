from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Any, List

from app.core.database import get_db
from app.schemas.shortlist import ShortlistResponse, ShortlistCreate
from app.schemas.common import StandardResponse, PaginatedResponse

router = APIRouter()

@router.get("", response_model=PaginatedResponse[ShortlistResponse])
async def get_shortlists(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    type: str = Query(None, description="Filter by type (player/coach)"),
    db: Session = Depends(get_db)
) -> Any:
    """Get user's shortlists"""
    
    sample_shortlists = [
        {
            "id": "shortlist-1",
            "name": "Summer Striker Targets",
            "type": "player",
            "status": "active",
            "priority": "high",
            "items_count": 5,
            "created_at": "2024-01-15T10:30:00Z"
        },
        {
            "id": "shortlist-2", 
            "name": "Backup Goalkeeper Options",
            "type": "player",
            "status": "active",
            "priority": "medium",
            "items_count": 3,
            "created_at": "2024-01-10T14:15:00Z"
        }
    ]
    
    return {
        "success": True,
        "data": sample_shortlists,
        "meta": {
            "pagination": {
                "page": (skip // limit) + 1,
                "per_page": limit,
                "total": 2,
                "total_pages": 1
            }
        }
    }

@router.post("", response_model=StandardResponse[ShortlistResponse])
async def create_shortlist(
    shortlist_data: ShortlistCreate,
    db: Session = Depends(get_db)
) -> Any:
    """Create new shortlist"""
    return {
        "success": True,
        "data": {
            "id": "new-shortlist-id",
            "name": shortlist_data.name,
            "type": shortlist_data.type,
            "status": "active",
            "message": "Shortlist created successfully"
        }
    }

@router.get("/{shortlist_id}", response_model=StandardResponse[ShortlistResponse])
async def get_shortlist(
    shortlist_id: str,
    db: Session = Depends(get_db)
) -> Any:
    """Get shortlist details with items"""
    return {
        "success": True,
        "data": {
            "id": shortlist_id,
            "name": "Summer Striker Targets",
            "type": "player",
            "status": "active",
            "priority": "high",
            "items": [
                {
                    "id": "item-1",
                    "player_name": "Erling Haaland",
                    "status": "shortlisted",
                    "priority": 5,
                    "notes": "Perfect fit for our system"
                }
            ]
        }
    }