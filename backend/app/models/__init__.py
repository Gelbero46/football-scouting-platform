from sqlalchemy import Column, DateTime, String, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"

class TimestampMixin:
    """Mixin for models that need timestamp tracking"""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SoftDeleteMixin:
    """Mixin for soft delete functionality"""
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True))

# Import all models to ensure they're registered with SQLAlchemy
from app.models.user import User
from app.models.player import Player
from app.models.coach import Coach
from app.models.shortlist import Shortlist, ShortlistItem
from app.models.report import Report
from app.models.activity_log import ActivityLog

# Export all models for easy importing
__all__ = [
    'Base',
    'BaseModel',
    'TimestampMixin', 
    'SoftDeleteMixin',
    'User',
    'Player',
    'Coach',
    'Shortlist',
    'ShortlistItem',
    'Report',
    'ActivityLog'
]
