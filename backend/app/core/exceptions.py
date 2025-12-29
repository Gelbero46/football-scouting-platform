"""Custom exceptions for consistent error handling"""

from fastapi import HTTPException, status
from typing import Any, Optional


class BaseAPIException(HTTPException):
    """Base exception for all API errors"""
    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[dict] = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(status_code=status_code, detail=message)


class AuthenticationError(BaseAPIException):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed", details: Optional[dict] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationError(BaseAPIException):
    """Raised when user doesn't have permission"""
    def __init__(self, message: str = "Permission denied", details: Optional[dict] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details=details
        )


class UserNotFoundError(BaseAPIException):
    """Raised when user is not found"""
    def __init__(self, message: str = "User not found", details: Optional[dict] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            error_code="USER_NOT_FOUND",
            details=details
        )


class ClerkAPIError(BaseAPIException):
    """Raised when Clerk API fails"""
    def __init__(self, message: str = "Clerk service error", details: Optional[dict] = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message=message,
            error_code="CLERK_API_ERROR",
            details=details
        )

