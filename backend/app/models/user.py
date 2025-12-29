from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.models import BaseModel
import uuid

class User(BaseModel):
    __tablename__ = "users"
    
    # Authentication
    clerk_id = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    
    # Profile Information
    first_name = Column(String(100))
    last_name = Column(String(100))
    avatar_url = Column(Text)
    
    # Role & Permissions
    role = Column(String(50), nullable=False, index=True)
    # Roles: 'admin', 'analyst', 'coach', 'scout'
    
    # Organization
    organization_id = Column(UUID(as_uuid=True))
    organization_name = Column(String(255))
    
    # Settings & Preferences
    preferences = Column(Text)  # JSON string for user preferences
    timezone = Column(String(50), default='UTC')
    language = Column(String(10), default='en')
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_login_at = Column(String(255))  # ISO datetime string
    
    # Relationships
    created_players = relationship("Player", back_populates="creator", foreign_keys="Player.created_by")
    created_coaches = relationship("Coach", back_populates="creator", foreign_keys="Coach.created_by")
    shortlists = relationship("Shortlist", back_populates="creator", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="generated_by_user", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(email={self.email}, role={self.role})>"
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.email
    
    def has_permission(self, resource: str, action: str) -> bool:
        """Check if user has permission for specific resource/action"""
        permissions = {
            'admin': {'*': ['*']},
            'analyst': {
                'player': ['create', 'read', 'update', 'delete'],
                'coach': ['create', 'read', 'update', 'delete'],
                'shortlist': ['create', 'read', 'update', 'delete'],
                'report': ['create', 'read', 'delete'],
                'analytics': ['read']
            },
            'coach': {
                'player': ['read'],
                'coach': ['read'],
                'shortlist': ['create', 'read', 'update'],
                'report': ['create', 'read']
            },
            'scout': {
                'player': ['read', 'update'],  # Regional only
                'shortlist': ['create', 'read', 'update'],
                'report': ['create', 'read']
            }
        }
        
        role_perms = permissions.get(self.role, {})
        resource_perms = role_perms.get(resource, [])
        
        return '*' in role_perms or action in resource_perms or '*' in resource_perms