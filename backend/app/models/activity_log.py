from sqlalchemy import Column, String, Text, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import UUID, JSON, INET
from sqlalchemy.orm import relationship
from app.models import BaseModel
import uuid

class ActivityLog(BaseModel):
    __tablename__ = "activity_logs"
    
    # User & Action
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(100), nullable=False, index=True)
    # Examples: 'player_viewed', 'shortlist_created', 'report_generated', 'user_login'
    
    # Resource Information
    resource_type = Column(String(50), nullable=False, index=True)
    # 'player', 'coach', 'shortlist', 'report', 'user', 'system'
    resource_id = Column(UUID(as_uuid=True), index=True)
    resource_name = Column(String(255))  # Human readable resource name
    
    # Action Details
    details = Column(JSON)  # Additional context about the action
    old_values = Column(JSON)  # Previous values (for updates)
    new_values = Column(JSON)  # New values (for updates)
    
    # Request Information
    ip_address = Column(INET)
    user_agent = Column(Text)
    request_method = Column(String(10))  # GET, POST, PUT, DELETE
    request_path = Column(String(500))
    request_duration_ms = Column(Integer)  # Request processing time
    
    # Context
    session_id = Column(String(255))
    organization_id = Column(UUID(as_uuid=True))
    severity = Column(String(20), default='info')  # 'debug', 'info', 'warning', 'error', 'critical'
    
    # Relationships
    user = relationship("User", back_populates="activity_logs")
    
    def __repr__(self):
        return f"<ActivityLog(action={self.action}, resource={self.resource_type}:{self.resource_id})>"
    
    @classmethod
    def log_action(cls, user_id: uuid.UUID, action: str, resource_type: str, 
                   resource_id: uuid.UUID = None, details: dict = None, **kwargs):
        """Helper method to create activity log entries"""
        return cls(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            **kwargs
        )

# Create composite indexes for common query patterns
Index('idx_activity_user_created', ActivityLog.user_id, ActivityLog.created_at.desc())
Index('idx_activity_resource', ActivityLog.resource_type, ActivityLog.resource_id)
Index('idx_activity_action_created', ActivityLog.action, ActivityLog.created_at.desc())
