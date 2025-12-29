
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from typing import Any
from svix.webhooks import Webhook, WebhookVerificationError

from app.core.database import get_db
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.core.clerk_auth import clerk_client
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.common import StandardResponse
from app.models import User
from app.core.exceptions import AuthenticationError

router = APIRouter()


@router.get("/me", response_model=StandardResponse[UserResponse])
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get current authenticated user information"""
    return {
        "success": True,
        "data": current_user
    }


@router.put("/me", response_model=StandardResponse[UserResponse])
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update current user's profile"""
    update_data = user_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "success": True,
        "data": current_user
    }


@router.post("/sync")
async def sync_user_with_clerk(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Sync user data with Clerk"""
    try:
        clerk_user = clerk_client.users.get(user_id=current_user.clerk_id)
        
        # Update local user
        if clerk_user.email_addresses:
            for email in clerk_user.email_addresses:
                if email.id == clerk_user.primary_email_address_id:
                    current_user.email = email.email_address
                    break
        
        current_user.first_name = clerk_user.first_name or current_user.first_name
        current_user.last_name = clerk_user.last_name or current_user.last_name
        current_user.avatar_url = clerk_user.image_url or current_user.avatar_url
        
        db.commit()
        db.refresh(current_user)
        
        return {
            "success": True,
            "data": current_user,
            "message": "User synced successfully"
        }
    except Exception as e:
        raise AuthenticationError(
            message="Failed to sync with Clerk",
            details={"error": str(e)}
        )


@router.post("/webhook/clerk")
async def clerk_webhook(
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """
    Webhook endpoint for Clerk events.
    Configure in Clerk Dashboard: https://dashboard.clerk.com
    """
    if not settings.CLERK_WEBHOOK_SECRET:
        raise AuthenticationError(
            message="Webhook secret not configured"
        )
    
    # Verify webhook signature
    try:
        wh = Webhook(settings.CLERK_WEBHOOK_SECRET)
        payload = await request.body()
        headers = dict(request.headers)
        
        evt = wh.verify(payload, headers)
    except WebhookVerificationError:
        raise AuthenticationError(
            message="Invalid webhook signature"
        )
    
    # Handle events
    event_type = evt.get("type")
    clerk_user = evt.get("data")
    
    if event_type == "user.created":
        user = User(
            clerk_id=clerk_user["id"],
            email=clerk_user["email_addresses"][0]["email_address"],
            first_name=clerk_user.get("first_name", ""),
            last_name=clerk_user.get("last_name", ""),
            avatar_url=clerk_user.get("image_url"),
            role="coach",
            is_active=True
        )
        db.add(user)
        db.commit()
        
    elif event_type == "user.updated":
        user = db.query(User).filter(User.clerk_id == clerk_user["id"]).first()
        if user:
            user.email = clerk_user["email_addresses"][0]["email_address"]
            user.first_name = clerk_user.get("first_name", "")
            user.last_name = clerk_user.get("last_name", "")
            user.avatar_url = clerk_user.get("image_url")
            db.commit()
            
    elif event_type == "user.deleted":
        user = db.query(User).filter(User.clerk_id == clerk_user["id"]).first()
        if user:
            user.is_active = False
            db.commit()
    
    return {"success": True}
