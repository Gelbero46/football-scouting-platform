from sqlalchemy import Column, String, Integer, Text, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from app.models import BaseModel
import uuid

class Report(BaseModel):
    __tablename__ = "reports"
    
    # Basic Information
    title = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False, index=True)
    # 'player_scout', 'coach_analysis', 'shortlist_summary', 'comparison', 'market_analysis'
    
    # Report Configuration
    parameters = Column(JSON, nullable=False)  # Report-specific configuration
    filters = Column(JSON)  # Applied filters and criteria
    template_id = Column(String(100))  # Template used for generation
    
    # Generation Details
    status = Column(String(20), default='pending', index=True)
    # 'pending', 'generating', 'completed', 'failed', 'expired'
    
    # File Information
    file_path = Column(Text)  # Storage path (S3, local, etc.)
    file_name = Column(String(255))
    file_size = Column(Integer)  # File size in bytes
    file_format = Column(String(20), default='pdf')  # pdf, xlsx, csv
    
    # Metadata
    page_count = Column(Integer)
    sections_included = Column(JSON)  # Array of included sections
    language = Column(String(10), default='en')
    
    # Access & Security
    generated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    shared_with = Column(JSON)  # Array of user IDs or 'public'
    access_level = Column(String(20), default='private')  # 'private', 'internal', 'public'
    
    # Lifecycle
    generated_at = Column(String(255))  # ISO datetime when completed
    expires_at = Column(String(255))  # Auto-deletion date
    download_count = Column(Integer, default=0)
    last_downloaded_at = Column(String(255))
    
    # Error Handling
    error_message = Column(Text)  # If generation failed
    retry_count = Column(Integer, default=0)
    
    # Performance Metrics
    generation_time_seconds = Column(Integer)  # Time taken to generate
    data_points_included = Column(Integer)  # Number of data points
    
    # Version Control
    version = Column(String(20), default='1.0')
    parent_report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id"))  # For regenerated reports
    
    # Relationships
    generated_by_user = relationship("User", back_populates="reports")
    child_reports = relationship("Report", remote_side=[parent_report_id])
    
    __table_args__ = (
        CheckConstraint(
            "type IN ('player_scout', 'coach_analysis', 'shortlist_summary', 'comparison', 'market_analysis')",
            name='report_type_check'
        ),
        CheckConstraint(
            "status IN ('pending', 'generating', 'completed', 'failed', 'expired')",
            name='report_status_check'
        ),
        CheckConstraint(
            "access_level IN ('private', 'internal', 'public')",
            name='report_access_level_check'
        ),
    )
    
    def __repr__(self):
        return f"<Report(title={self.title}, type={self.type}, status={self.status})>"
    
    @property
    def file_size_display(self):
        """Human readable file size"""
        if not self.file_size:
            return "N/A"
        
        if self.file_size >= 1024**3:  # GB
            return f"{self.file_size / (1024**3):.1f} GB"
        elif self.file_size >= 1024**2:  # MB
            return f"{self.file_size / (1024**2):.1f} MB"
        elif self.file_size >= 1024:  # KB
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size} bytes"
    
    @property
    def is_expired(self):
        """Check if report has expired"""
        if self.expires_at:
            from datetime import datetime
            try:
                expires = datetime.fromisoformat(self.expires_at.replace('Z', '+00:00'))
                return datetime.utcnow().replace(tzinfo=expires.tzinfo) > expires
            except:
                pass
        return False
    
    def increment_download_count(self):
        """Increment download counter and update last download time"""
        from datetime import datetime
        self.download_count = (self.download_count or 0) + 1
        self.last_downloaded_at = datetime.utcnow().isoformat()
    
    def mark_as_failed(self, error_message: str):
        """Mark report generation as failed"""
        self.status = 'failed'
        self.error_message = error_message
        self.retry_count = (self.retry_count or 0) + 1
