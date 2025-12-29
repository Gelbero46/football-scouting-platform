# app/core/dependencies.py
"""FastAPI dependencies for authentication"""

from fastapi import Depends, Request
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.core.clerk_auth import get_current_user_token, clerk_client
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.models import User
from app.core.config import settings

logger = logging.getLogger(__name__)


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from database.
    Creates user if doesn't exist (first-time login).
    """
    # Verify token and get claims
    logger.info("Checking for token in header...")
    token_data = await get_current_user_token(request)
    print("token Data------", token_data)
    # Extract user_id from token
    clerk_user_id = token_data.get("sub")
    
    if not clerk_user_id:
        raise AuthenticationError(
            message="Invalid token",
            details={"reason": "Missing user ID"}
        )
    
    # Check if user exists in database
    user = db.query(User).filter(User.clerk_id == clerk_user_id).first()
    
    # Create user if first time login
    if not user:
        try:
            # Fetch full user details from Clerk
            clerk_user = clerk_client.users.get(user_id=clerk_user_id)
            
            # Get primary email
            primary_email = None
            if clerk_user.email_addresses:
                for email in clerk_user.email_addresses:
                    if email.id == clerk_user.primary_email_address_id:
                        primary_email = email.email_address
                        break
            
            if not primary_email:
                raise AuthenticationError(
                    message="No email found",
                    details={"reason": "User must have a primary email"}
                )
            
            user_role = "coach" # Default role

            # If email in SUPER_ADMIN_EMAILS, force role to 'admin'
            if primary_email in settings.SUPER_ADMIN_EMAILS:
                user_role = 'admin'

            # Create new user in database
            user = User(
                clerk_id=clerk_user_id,
                email=primary_email,
                first_name=clerk_user.first_name or "",
                last_name=clerk_user.last_name or "",
                avatar_url=clerk_user.image_url,
                role=user_role,  
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"Created new user: {user.email}")
            
        except AuthenticationError:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create user: {str(e)}")
            raise AuthenticationError(
                message="Failed to create user",
                details={"error": str(e)}
            )
    
    # Check if user is active
    if not user.is_active:
        raise AuthorizationError(
            message="Account is deactivated",
            details={"user_id": str(user.id)}
        )
    
    return user


async def get_current_active_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure current user is an admin"""
    if current_user.role != "admin":
        raise AuthorizationError(
            message="Admin access required",
            details={"current_role": current_user.role}
        )
    return current_user


async def get_current_active_analyst(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure current user is an analyst or admin"""
    if current_user.role not in ["admin", "analyst"]:
        raise AuthorizationError(
            message="Analyst or Admin access required",
            details={"current_role": current_user.role}
        )
    return current_user


def check_permission(resource: str, action: str):
    """
    Dependency factory for checking specific permissions.
    Usage: Depends(check_permission('player', 'delete'))
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if not current_user.has_permission(resource, action):
            logger.info(f"You don't have permission to ****** {action} {resource}")
            raise AuthorizationError(
                message="Entity not Authorized",
                details=f"You don't have permission to {action} {resource}"
            )
        return current_user
    
    return permission_checker