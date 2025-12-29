"""Clerk authentication using the official Python SDK"""

from fastapi import Request, HTTPException, status
from clerk_backend_api import Clerk
from clerk_backend_api.security.types import AuthenticateRequestOptions
import logging

from app.core.config import settings
from app.core.exceptions import AuthenticationError

logger = logging.getLogger(__name__)

# Initialize Clerk client
clerk_client = Clerk(bearer_auth=settings.CLERK_SECRET_KEY)


async def get_current_user_token(request: Request) -> dict:
    """
    Verify Clerk JWT token using the official SDK's authenticate_request method.
    
    This is the modern, recommended way as of Clerk Python SDK (Oct 2024).
    """
    try:
        # Use Clerk's built-in authenticate_request method
        request_state = clerk_client.authenticate_request(
            request,
            AuthenticateRequestOptions(
                authorized_parties=settings.ALLOWED_ORIGINS,  # Optional: restrict to specific domains
                # secret_key is automatically used from clerk_client initialization
            )
        )

        print("request_state*****", request_state)
        
        # Check if request is authenticated
        if not request_state.is_signed_in:
            raise AuthenticationError(
                message="Not authenticated",
                details={"reason": "Invalid or missing token"}
            )
        
        # Return the session claims (contains user_id in 'sub', email, etc.)
        return request_state.payload
        
    except AuthenticationError:
        # Re-raise our custom exception
        raise
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise AuthenticationError(
            message="Authentication failed",
            details={"error": str(e)}
        )


async def get_clerk_user(user_id: str):
    """
    Fetch user details from Clerk API.
    
    Args:
        user_id: Clerk user ID (from token's 'sub' claim)
    """
    try:
        user = clerk_client.users.get(user_id=user_id)
        return user
    except Exception as e:
        logger.error(f"Failed to fetch user from Clerk: {str(e)}")
        raise AuthenticationError(
            message="User not found in Clerk",
            details={"user_id": user_id}
        )
    

async def list_clerk_users(limit: int = 10, offset: int = 0):
    """List users from Clerk (useful for admin panels)"""
    try:
        users = clerk_client.users.list(limit=limit, offset=offset)
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )
