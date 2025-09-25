from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Any, List, Optional

from app.core.database import get_db
from app.schemas.coach import CoachResponse, CoachCreate
from app.schemas.common import StandardResponse, PaginatedResponse

router = APIRouter()

@router.get("", response_model=PaginatedResponse[CoachResponse])
async def get_coaches(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_role: Optional[str] = Query(None, description="Filter by current role"),
    club: Optional[str] = Query(None, description="Filter by current club"),
    search: Optional[str] = Query(None, description="Search coaches by name"),
    db: Session = Depends(get_db)
) -> Any:
    """Get coaches with optional filtering and pagination"""
    
    sample_coaches = [
        {
            "id": "coach-1",
            "name": "Pep Guardiola",
            "current_club": "Manchester City",
            "current_role": "head_coach",
            "nationality": "Spain",
            "preferred_formation": "4-3-3",
            "overall_rating": 95
        },
        {
            "id": "coach-2",
            "name": "Jürgen Klopp",
            "current_club": "Liverpool", 
            "current_role": "head_coach",
            "nationality": "Germany",
            "preferred_formation": "4-3-3",
            "overall_rating": 94
        }
    ]
    
    return {
        "success": True,
        "data": sample_coaches,
        "meta": {
            "pagination": {
                "page": (skip // limit) + 1,
                "per_page": limit,
                "total": 2,
                "total_pages": 1
            }
        }
    }

@router.get("/{coach_id}", response_model=StandardResponse[CoachResponse])
async def get_coach(
    coach_id: str,
    db: Session = Depends(get_db)
) -> Any:
    """Get coach by ID"""
    return {
        "success": True,
        "data": {
            "id": coach_id,
            "name": "Pep Guardiola",
            "current_club": "Manchester City",
            "current_role": "head_coach",
            "nationality": "Spain",
            "preferred_formation": "4-3-3",
            "overall_rating": 95,
            "tactical_style": {
                "possession_based": 0.95,
                "high_press": 0.88,
                "counter_attack": 0.65
            }
        }
    }