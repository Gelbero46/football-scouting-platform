from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from typing import Any, List, Optional
import uuid

from app.core.database import get_db
from app.schemas.shortlist import (
    ShortlistResponse, ShortlistCreate, ShortlistUpdate,
    ShortlistItemResponse, ShortlistItemCreate, ShortlistItemUpdate
)
from app.schemas.common import StandardResponse, PaginatedResponse
from app.models import Shortlist, ShortlistItem, Player, Coach

router = APIRouter()

@router.get("", response_model=PaginatedResponse[ShortlistResponse])
async def get_shortlists(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    type: Optional[str] = Query(None, description="Filter by type (player/coach)"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
) -> Any:
    """Get user's shortlists with items count"""
    
    query = db.query(Shortlist)
    
    # Apply filters
    if type:
        query = query.filter(Shortlist.type == type)
    
    if status:
        query = query.filter(Shortlist.status == status)
    
    # Order by created date (newest first)
    query = query.order_by(desc(Shortlist.created_at))
    
    # Pagination
    total = query.count()
    shortlists = query.offset(skip).limit(limit).all()
    
    # Add items count to each shortlist
    for shortlist in shortlists:
        shortlist.items_count = len(shortlist.items)
    
    return {
        "success": True,
        "data": shortlists,
        "meta": {
            "pagination": {
                "page": (skip // limit) + 1,
                "per_page": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit
            }
        }
    }

@router.post("", response_model=StandardResponse[ShortlistResponse])
async def create_shortlist(
    shortlist_data: ShortlistCreate,
    db: Session = Depends(get_db)
) -> Any:
    """Create new shortlist"""
    
    shortlist = Shortlist(
        **shortlist_data.model_dump(exclude_unset=True),
        # created_by=current_user.id,  # Add when auth is ready
    )
    
    db.add(shortlist)
    db.commit()
    db.refresh(shortlist)
    
    return {
        "success": True,
        "data": shortlist
    }

@router.get("/{shortlist_id}", response_model=StandardResponse[ShortlistResponse])
async def get_shortlist(
    shortlist_id: str,
    db: Session = Depends(get_db)
) -> Any:
    """Get shortlist details with all items"""
    
    try:
        shortlist_uuid = uuid.UUID(shortlist_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid shortlist ID format"
        )
    
    # Load shortlist with items and related entities
    shortlist = db.query(Shortlist).options(
        joinedload(Shortlist.items).joinedload(ShortlistItem.player),
        joinedload(Shortlist.items).joinedload(ShortlistItem.coach)
    ).filter(Shortlist.id == shortlist_uuid).first()
    
    if not shortlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shortlist not found"
        )
    
    # Transform items for response
    items_response = []
    for item in shortlist.items:
        item_data = {
            "id": item.id,
            "status": item.status,
            "priority": item.priority,
            "notes": item.notes,
            "scout_rating": item.scout_rating,
            "estimated_fee_eur": item.estimated_fee_eur,
            "added_at": item.added_at
        }
        
        if item.player:
            item_data.update({
                "entity_type": "player",
                "entity_id": item.player.id,
                "entity_name": item.player.name,
                "position": item.player.position,
                "club": item.player.current_club,
                "market_value_eur": item.player.market_value_eur
            })
        elif item.coach:
            item_data.update({
                "entity_type": "coach", 
                "entity_id": item.coach.id,
                "entity_name": item.coach.name,
                "role": item.coach.current_role,
                "club": item.coach.current_club
            })
        
        items_response.append(item_data)
    
    # Add computed fields
    shortlist.items_count = len(shortlist.items)
    shortlist.total_estimated_cost = sum(
        item.estimated_fee_eur for item in shortlist.items 
        if item.estimated_fee_eur
    )
    
    response_data = {
        **shortlist.__dict__,
        "items": items_response
    }
    
    return {
        "success": True,
        "data": response_data
    }

@router.post("/{shortlist_id}/items", response_model=StandardResponse)
async def add_shortlist_item(
    shortlist_id: str,
    item_data: ShortlistItemCreate,
    db: Session = Depends(get_db)
) -> Any:
    """Add item to shortlist"""
    
    try:
        shortlist_uuid = uuid.UUID(shortlist_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid shortlist ID format"
        )
    
    # Verify shortlist exists
    shortlist = db.query(Shortlist).filter(
        Shortlist.id == shortlist_uuid
    ).first()
    
    if not shortlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shortlist not found"
        )
    
    # Verify entity exists
    if item_data.player_id:
        entity = db.query(Player).filter(Player.id == item_data.player_id).first()
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found"
            )
        # Check if already in shortlist
        existing = db.query(ShortlistItem).filter(
            and_(
                ShortlistItem.shortlist_id == shortlist_uuid,
                ShortlistItem.player_id == item_data.player_id
            )
        ).first()
        
    elif item_data.coach_id:
        entity = db.query(Coach).filter(Coach.id == item_data.coach_id).first()
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coach not found"
            )
        # Check if already in shortlist
        existing = db.query(ShortlistItem).filter(
            and_(
                ShortlistItem.shortlist_id == shortlist_uuid,
                ShortlistItem.coach_id == item_data.coach_id
            )
        ).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either player_id or coach_id must be provided"
        )
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Entity already exists in this shortlist"
        )
    
    # Create shortlist item
    shortlist_item = ShortlistItem(
        shortlist_id=shortlist_uuid,
        **item_data.model_dump(exclude_unset=True)
    )
    
    db.add(shortlist_item)
    db.commit()
    db.refresh(shortlist_item)
    
    return {
        "success": True,
        "data": {
            "message": "Item added to shortlist successfully",
            "item_id": shortlist_item.id
        }
    }

@router.put("/{shortlist_id}/items/{item_id}")
async def update_shortlist_item(
    shortlist_id: str,
    item_id: str,
    item_data: ShortlistItemUpdate,
    db: Session = Depends(get_db)
) -> Any:
    """Update shortlist item"""
    
    try:
        shortlist_uuid = uuid.UUID(shortlist_id)
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID format"
        )
    
    # Find the item
    item = db.query(ShortlistItem).filter(
        and_(
            ShortlistItem.id == item_uuid,
            ShortlistItem.shortlist_id == shortlist_uuid
        )
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shortlist item not found"
        )
    
    # Update fields
    update_data = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    
    return {
        "success": True,
        "data": {
            "message": "Shortlist item updated successfully"
        }
    }

@router.delete("/{shortlist_id}/items/{item_id}")
async def remove_shortlist_item(
    shortlist_id: str,
    item_id: str,
    db: Session = Depends(get_db)
) -> Any:
    """Remove item from shortlist"""
    
    try:
        shortlist_uuid = uuid.UUID(shortlist_id)
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID format"
        )
    
    item = db.query(ShortlistItem).filter(
        and_(
            ShortlistItem.id == item_uuid,
            ShortlistItem.shortlist_id == shortlist_uuid
        )
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shortlist item not found"
        )
    
    db.delete(item)
    db.commit()
    
    return {
        "success": True,
        "data": {
            "message": "Item removed from shortlist successfully"
        }
    }