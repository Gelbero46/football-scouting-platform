from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from typing import Any, List, Optional
import uuid

from app.core.dependencies import get_current_user, check_permission
from app.core.database import get_db
from app.schemas.player import PlayerResponse, PlayerCreate, PlayerUpdate
from app.schemas.common import StandardResponse, PaginatedResponse
from app.models import Player, User

router = APIRouter()

@router.get("", response_model=PaginatedResponse[PlayerResponse])
async def get_players(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    position: Optional[str] = Query(None, description="Filter by position"),
    club: Optional[str] = Query(None, description="Filter by current club"),
    nationality: Optional[str] = Query(None, description="Filter by nationality"),
    min_value: Optional[int] = Query(None, description="Minimum market value in EUR"),
    max_value: Optional[int] = Query(None, description="Maximum market value in EUR"),
    search: Optional[str] = Query(None, description="Search players by name or club"),
    sort_by: Optional[str] = Query("name", description="Sort field: name, market_value, overall_rating"),
    sort_order: Optional[str] = Query("asc", description="Sort order: asc, desc"),
    current_user: User = Depends(check_permission('player', 'read')),
    db: Session = Depends(get_db)
) -> Any:
    """Get players with advanced filtering, search, and pagination"""
    
    # Base query
    query = db.query(Player).filter(Player.is_active == True)
    
    # Apply filters
    if position:
        query = query.filter(
            or_(
                Player.position.ilike(f"%{position}%"),
                func.array_to_string(Player.secondary_positions, ',').ilike(f"%{position}%")
            )
        )
    
    if club:
        query = query.filter(Player.current_club.ilike(f"%{club}%"))
    
    if nationality:
        query = query.filter(
            or_(
                Player.nationality.ilike(f"%{nationality}%"),
                Player.second_nationality.ilike(f"%{nationality}%")
            )
        )
    
    if min_value is not None:
        query = query.filter(Player.market_value_eur >= min_value)
    
    if max_value is not None:
        query = query.filter(Player.market_value_eur <= max_value)
    
    # Full-text search
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Player.name.ilike(search_term),
                Player.full_name.ilike(search_term),
                Player.current_club.ilike(search_term)
            )
        )
    
    # Apply sorting
    sort_field = getattr(Player, sort_by, Player.name)
    if sort_order.lower() == "desc":
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(asc(sort_field))
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination
    players = query.offset(skip).limit(limit).all()
    
    # Calculate pagination metadata
    total_pages = (total + limit - 1) // limit
    current_page = (skip // limit) + 1
    
    return {
        "success": True,
        "data": players,
        "meta": {
            "pagination": {
                "page": current_page,
                "per_page": limit,
                "total": total,
                "total_pages": total_pages
            }
        }
    }

@router.get("/{player_id}", response_model=StandardResponse[PlayerResponse])
async def get_player(
    player_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission('player', 'read'))
) -> Any:
    """Get player by ID with full details"""
    
    try:
        player_uuid = uuid.UUID(player_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid player ID format"
        )
    
    player = db.query(Player).filter(
        and_(
            Player.id == player_uuid,
            Player.is_active == True
        )
    ).first()
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    return {
        "success": True,
        "data": player
    }

@router.post("", response_model=StandardResponse[PlayerResponse])
async def create_player(
    player_data: PlayerCreate,
    current_user: User = Depends(check_permission('player', 'create')),
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user),
  
) -> Any:
    """Create new player"""
    
    # Check if player with same name and club already exists
    existing = db.query(Player).filter(
        and_(
            Player.name == player_data.name,
            Player.current_club == player_data.current_club,
            Player.is_active == True
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Player with this name already exists at this club"
        )
    
    # Create new player
    player = Player(
        **player_data.model_dump(exclude_unset=True),
        created_by=current_user.id,
        data_source="manual"
    )
    
    db.add(player)
    db.commit()
    db.refresh(player)
    
    return {
        "success": True,
        "data": player
    }

@router.put("/{player_id}", response_model=StandardResponse[PlayerResponse])
async def update_player(
    player_id: str,
    player_data: PlayerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission('player', 'update'))
) -> Any:
    """Update player information"""
    
    try:
        player_uuid = uuid.UUID(player_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid player ID format"
        )
    
    player = db.query(Player).filter(
        and_(
            Player.id == player_uuid,
            Player.is_active == True
        )
    ).first()
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    # Update fields
    update_data = player_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(player, field, value)
    
    db.commit()
    db.refresh(player)
    
    return {
        "success": True,
        "data": player
    }

@router.delete("/{player_id}")
async def delete_player(
    player_id: str,
    current_user: User = Depends(check_permission('player', 'delete')),
    db: Session = Depends(get_db)
) -> Any:
    """Soft delete player (mark as inactive)"""
    
    try:
        player_uuid = uuid.UUID(player_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid player ID format"
        )
    
    player = db.query(Player).filter(Player.id == player_uuid).first()
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    # Soft delete
    player.is_active = False
    db.commit()
    
    return {
        "success": True,
        "data": {"message": "Player deleted successfully"}
    }

@router.get("/{player_id}/similar", response_model=StandardResponse[List[PlayerResponse]])
async def get_similar_players(
    player_id: str,
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission('player', 'read'))
) -> Any:
    """Get players similar to the specified player"""
    
    try:
        player_uuid = uuid.UUID(player_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid player ID format"
        )
    
    # Get the target player
    target_player = db.query(Player).filter(
        and_(Player.id == player_uuid, Player.is_active == True)
    ).first()
    
    if not target_player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    # Find similar players based on position, age, and market value
    similar_query = db.query(Player).filter(
        and_(
            Player.id != player_uuid,
            Player.is_active == True,
            Player.position == target_player.position
        )
    )
    
    # Add age similarity (within 3 years)
    if target_player.date_of_birth:
        similar_query = similar_query.filter(
            func.abs(
                func.extract('year', func.age(Player.date_of_birth)) - 
                func.extract('year', func.age(target_player.date_of_birth))
            ) <= 3
        )
    
    # Add market value similarity (within 50% range)
    if target_player.market_value_eur:
        min_value = target_player.market_value_eur * 0.5
        max_value = target_player.market_value_eur * 1.5
        similar_query = similar_query.filter(
            and_(
                Player.market_value_eur >= min_value,
                Player.market_value_eur <= max_value
            )
        )
    
    # Order by market value similarity and limit results
    similar_players = similar_query.order_by(
        func.abs(Player.market_value_eur - target_player.market_value_eur)
    ).limit(limit).all()
    
    return {
        "success": True,
        "data": similar_players
    }

@router.get("/search/advanced")
async def advanced_search(
    query: str = Query(..., description="Search query"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission('player', 'read'))
    
) -> Any:
    """Advanced full-text search using PostgreSQL features"""
    
    # Use PostgreSQL full-text search
    players = db.query(Player).filter(
        and_(
            Player.search_vector.match(query),
            Player.is_active == True
        )
    ).order_by(
        func.ts_rank(Player.search_vector, func.plainto_tsquery(query)).desc()
    ).limit(20).all()
    
    return {
        "success": True,
        "data": players,
        "meta": {
            "search_query": query,
            "results_count": len(players)
        }
    }

@router.get("/stats/summary")
async def get_players_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission('player', 'read'))
) -> Any:
    """Get summary statistics for all players"""
    
    stats = db.query(
        func.count(Player.id).label('total_players'),
        func.count(func.distinct(Player.nationality)).label('total_nationalities'),
        func.count(func.distinct(Player.current_club)).label('total_clubs'),
        func.count(func.distinct(Player.position)).label('total_positions'),
        func.avg(Player.market_value_eur).label('avg_market_value'),
        func.max(Player.market_value_eur).label('max_market_value'),
        func.min(Player.market_value_eur).label('min_market_value')
    ).filter(Player.is_active == True).first()
    
    # Position breakdown
    position_stats = db.query(
        Player.position,
        func.count(Player.id).label('count')
    ).filter(
        Player.is_active == True
    ).group_by(Player.position).all()
    
    return {
        "success": True,
        "data": {
            "overview": {
                "total_players": stats.total_players,
                "total_nationalities": stats.total_nationalities,
                "total_clubs": stats.total_clubs,
                "total_positions": stats.total_positions,
                "avg_market_value_eur": int(stats.avg_market_value) if stats.avg_market_value else 0,
                "max_market_value_eur": stats.max_market_value,
                "min_market_value_eur": stats.min_market_value
            },
            "position_breakdown": [
                {"position": pos, "count": count} 
                for pos, count in position_stats
            ]
        }
    }