from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from typing import Any, List, Optional
import uuid

from app.core.database import get_db
from app.core.dependencies import check_permission
from app.schemas.coach import CoachResponse, CoachCreate, CoachUpdate
from app.schemas.common import StandardResponse, PaginatedResponse
from app.models import Coach, User

router = APIRouter()

@router.get("", response_model=PaginatedResponse[CoachResponse])
async def get_coaches(
    current_user: User = Depends(check_permission('coach', 'read')),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_role: Optional[str] = Query(None, description="Filter by current role"),
    club: Optional[str] = Query(None, description="Filter by current club"),
    nationality: Optional[str] = Query(None, description="Filter by nationality"),
    formation: Optional[str] = Query(None, description="Filter by preferred formation"),
    search: Optional[str] = Query(None, description="Search coaches by name"),
    sort_by: Optional[str] = Query("name", description="Sort field"),
    sort_order: Optional[str] = Query("asc", description="Sort order: asc, desc"),
    db: Session = Depends(get_db)
    
) -> Any:
    """Get coaches with filtering and pagination"""
    
    query = db.query(Coach).filter(Coach.is_active == True)
    
    # Apply filters
    if current_role:
        query = query.filter(Coach.current_role.ilike(f"%{current_role}%"))
    
    if club:
        query = query.filter(Coach.current_club.ilike(f"%{club}%"))
    
    if nationality:
        query = query.filter(Coach.nationality.ilike(f"%{nationality}%"))
    
    if formation:
        query = query.filter(
            or_(
                Coach.preferred_formation.ilike(f"%{formation}%"),
                func.array_to_string(Coach.preferred_formations, ',').ilike(f"%{formation}%")
            )
        )
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Coach.name.ilike(search_term),
                Coach.full_name.ilike(search_term),
                Coach.current_club.ilike(search_term)
            )
        )
    
    # Apply sorting
    sort_field = getattr(Coach, sort_by, Coach.name)
    if sort_order.lower() == "desc":
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(asc(sort_field))
    
    # Pagination
    total = query.count()
    coaches = query.offset(skip).limit(limit).all()
    
    return {
        "success": True,
        "data": coaches,
        "meta": {
            "pagination": {
                "page": (skip // limit) + 1,
                "per_page": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit
            }
        }
    }

@router.get("/{coach_id}", response_model=StandardResponse[CoachResponse])
async def get_coach(
    coach_id: str,
    current_user: User = Depends(check_permission('coach', 'read')),
    db: Session = Depends(get_db)
) -> Any:
    """Get coach by ID"""
    
    try:
        coach_uuid = uuid.UUID(coach_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid coach ID format"
        )
    
    coach = db.query(Coach).filter(
        and_(Coach.id == coach_uuid, Coach.is_active == True)
    ).first()
    
    if not coach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coach not found"
        )
    
    return {
        "success": True,
        "data": coach
    }

@router.post("", response_model=StandardResponse[CoachResponse])
async def create_coach(
    coach_data: CoachCreate,
    current_user: User = Depends(check_permission('coach', 'read')),
    db: Session = Depends(get_db)
) -> Any:
    """Create new coach"""
    
    # Check for existing coach
    existing = db.query(Coach).filter(
        and_(
            Coach.name == coach_data.name,
            Coach.current_club == coach_data.current_club,
            Coach.is_active == True
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Coach with this name already exists at this club"
        )
    
    coach = Coach(
        **coach_data.model_dump(exclude_unset=True),
        data_source="manual"
    )
    
    db.add(coach)
    db.commit()
    db.refresh(coach)
    
    return {
        "success": True,
        "data": coach
    }

@router.put("/{coach_id}", response_model=StandardResponse[CoachResponse])
async def update_coach(
    coach_id: str,
    coach_data: CoachUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission('coach', 'update'))
) -> Any:
    """Update coach information"""
    try:
        coach_uuid = uuid.UUID(coach_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid coach ID format"
        )
    
    coach = db.query(Coach).filter(
        and_(
            Coach.id == coach_uuid,
            Coach.is_active == True
        )
    ).first()
    
    if not coach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coach not found"
        )
    
    # Update fields
    update_data = coach_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(coach, field, value)
    
    db.commit()
    db.refresh(coach)
    
    return {
        "success": True,
        "data": coach
    }


@router.delete("/{coach_id}")
async def delete_coach(
    coach_id: str,
    current_user: User = Depends(check_permission('coach', 'delete')),
    db: Session = Depends(get_db)
) -> Any:
    """Soft delete coach (mark as inactive)"""
    
    try:
        coach_uuid = uuid.UUID(coach_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid coach ID format"
        )
    
    coach = db.query(Coach).filter(Coach.id == coach_uuid).first()
    
    if not coach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coach not found"
        )
    
    # Soft delete
    coach.is_active = False
    db.commit()
    
    return {
        "success": True,
        "data": {"message": "Coach deleted successfully"}
    }


@router.get("/{coach_id}/similar", response_model=StandardResponse[List[CoachResponse]])
async def get_similar_coaches(
    coach_id: str,
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
) -> Any:
    """Get coaches similar to the specified coach"""
    
    try:
        coach_uuid = uuid.UUID(coach_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid coach ID format"
        )
    
    target_coach = db.query(Coach).filter(
        and_(Coach.id == coach_uuid, Coach.is_active == True)
    ).first()
    
    if not target_coach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coach not found"
        )
    
    # Find similar coaches
    similar_query = db.query(Coach).filter(
        and_(
            Coach.id != coach_uuid,
            Coach.is_active == True,
            Coach.current_role == target_coach.current_role,
            Coach.preferred_formation == target_coach.preferred_formation
        )
    ).limit(limit)
    
    similar_coaches = similar_query.all()
    
    return {
        "success": True,
        "data": similar_coaches
    }