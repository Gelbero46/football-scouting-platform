from sqlalchemy import Column, String, Integer, Date, Boolean, Text, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON
from sqlalchemy.orm import relationship
from app.models import BaseModel
import uuid
from datetime import datetime

class Shortlist(BaseModel):
    __tablename__ = "shortlists"
    
    # Basic Information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(String(20), nullable=False, index=True)  # 'player' or 'coach'
    
    # Ownership & Permissions
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    shared_with = Column(ARRAY(UUID), default=[])  # Array of user IDs with access
    organization_id = Column(UUID(as_uuid=True))
    
    # Status & Priority
    status = Column(String(50), default='active', index=True)
    # 'active', 'archived', 'completed', 'on_hold'
    priority = Column(String(20), default='medium')
    # 'low', 'medium', 'high', 'urgent'
    
    # Metadata & Organization
    tags = Column(ARRAY(String), default=[])
    category = Column(String(100))  # 'summer_targets', 'backup_options', etc.
    season = Column(String(20))  # '2024-25', '2025-26'
    
    # Timeline & Budget
    deadline = Column(Date)
    budget_eur = Column(Integer)  # Budget in EUR
    max_budget_eur = Column(Integer)  # Maximum budget
    
    # Progress Tracking
    target_count = Column(Integer)  # Target number of signings
    completed_count = Column(Integer, default=0)  # Number of completed signings
    
    # Settings
    auto_update = Column(Boolean, default=True)  # Auto-update player data
    notifications_enabled = Column(Boolean, default=True)
    
    # Notes & Comments
    notes = Column(Text)
    internal_notes = Column(Text)  # Private notes not shared
    
    # Relationships
    creator = relationship("User", back_populates="shortlists")
    items = relationship("ShortlistItem", back_populates="shortlist", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("type IN ('player', 'coach')", name='shortlist_type_check'),
        CheckConstraint("status IN ('active', 'archived', 'completed', 'on_hold')", name='shortlist_status_check'),
        CheckConstraint("priority IN ('low', 'medium', 'high', 'urgent')", name='shortlist_priority_check'),
    )
    
    def __repr__(self):
        return f"<Shortlist(name={self.name}, type={self.type}, status={self.status})>"
    
    @property
    def items_count(self):
        return len(self.items)
    
    @property
    def progress_percentage(self):
        if self.target_count and self.target_count > 0:
            return min(100, round((self.completed_count / self.target_count) * 100, 2))
        return 0
    
    @property
    def total_estimated_cost(self):
        """Calculate total estimated cost of all items in shortlist"""
        total = 0
        for item in self.items:
            if item.estimated_fee_eur:
                total += item.estimated_fee_eur
        return total
    
    def add_user_access(self, user_id: uuid.UUID):
        """Add user access to shortlist"""
        if self.shared_with is None:
            self.shared_with = []
        if str(user_id) not in self.shared_with:
            self.shared_with.append(str(user_id))
    
    def remove_user_access(self, user_id: uuid.UUID):
        """Remove user access from shortlist"""
        if self.shared_with and str(user_id) in self.shared_with:
            self.shared_with.remove(str(user_id))

class ShortlistItem(BaseModel):
    __tablename__ = "shortlist_items"
    
    # Parent Shortlist
    shortlist_id = Column(UUID(as_uuid=True), ForeignKey("shortlists.id"), nullable=False)
    
    # Referenced Entity (either player or coach, not both)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"))
    coach_id = Column(UUID(as_uuid=True), ForeignKey("coaches.id"))
    
    # Item Status & Priority
    status = Column(String(50), default='identified', index=True)
    # 'identified', 'scouted', 'analyzed', 'shortlisted', 'approached', 
    # 'negotiating', 'signed', 'rejected', 'unavailable'
    priority = Column(Integer, default=3)  # 1-5 star rating
    
    # Assessment & Notes
    notes = Column(Text)
    internal_notes = Column(Text)  # Private notes
    strengths = Column(ARRAY(String), default=[])
    weaknesses = Column(ARRAY(String), default=[])
    fit_analysis = Column(Text)  # How well they fit the team/role
    
    # Ratings
    scout_rating = Column(Integer)  # 0-100 scout assessment
    technical_rating = Column(Integer)  # 0-100 technical ability
    personality_rating = Column(Integer)  # 0-100 personality/attitude
    overall_fit_rating = Column(Integer)  # 0-100 overall fit for club
    
    # Financial Information
    estimated_fee_eur = Column(Integer)  # Estimated transfer fee
    wage_demands_eur = Column(Integer)  # Weekly wage demands
    total_cost_eur = Column(Integer)  # Total cost including wages, fees, etc.
    
    # Contract Details
    contract_length_years = Column(Integer)
    contract_options = Column(JSON)  # Extension options, clauses, etc.
    
    # Timeline & Deadlines
    target_completion_date = Column(Date)
    last_contacted_date = Column(Date)
    next_action_date = Column(Date)
    
    # Progress Tracking
    contact_attempts = Column(Integer, default=0)
    meetings_held = Column(Integer, default=0)
    offers_made = Column(Integer, default=0)
    
    # Agent & Contact Information
    agent_contact_info = Column(JSON)
    club_contact_info = Column(JSON)
    contact_history = Column(JSON)  # Array of contact records
    
    # System Fields
    added_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    last_updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    shortlist = relationship("Shortlist", back_populates="items")
    player = relationship("Player", back_populates="shortlist_items")
    coach = relationship("Coach", back_populates="shortlist_items")
    
    __table_args__ = (
        CheckConstraint(
            "(player_id IS NOT NULL AND coach_id IS NULL) OR "
            "(player_id IS NULL AND coach_id IS NOT NULL)",
            name='shortlist_item_reference_check'
        ),
        CheckConstraint(
            "status IN ('identified', 'scouted', 'analyzed', 'shortlisted', 'approached', "
            "'negotiating', 'signed', 'rejected', 'unavailable')",
            name='shortlist_item_status_check'
        ),
        CheckConstraint("priority >= 1 AND priority <= 5", name='shortlist_item_priority_check'),
        UniqueConstraint('shortlist_id', 'player_id', name='unique_shortlist_player'),
        UniqueConstraint('shortlist_id', 'coach_id', name='unique_shortlist_coach'),
    )
    
    def __repr__(self):
        entity_name = self.player.name if self.player else (self.coach.name if self.coach else "Unknown")
        return f"<ShortlistItem(entity={entity_name}, status={self.status}, priority={self.priority})>"
    
    @property
    def entity_name(self):
        """Get the name of the referenced entity (player or coach)"""
        if self.player:
            return self.player.name
        elif self.coach:
            return self.coach.name
        return "Unknown"
    
    @property
    def entity_type(self):
        """Get the type of the referenced entity"""
        return "player" if self.player else "coach" if self.coach else None
    
    @property
    def status_color(self):
        """Get color coding for status display"""
        colors = {
            'identified': 'gray',
            'scouted': 'blue',
            'analyzed': 'purple',
            'shortlisted': 'green',
            'approached': 'orange',
            'negotiating': 'yellow',
            'signed': 'emerald',
            'rejected': 'red',
            'unavailable': 'slate'
        }
        return colors.get(self.status, 'gray')
    
    def update_status(self, new_status: str, notes: str = None):
        """Update item status with optional notes"""
        valid_statuses = [
            'identified', 'scouted', 'analyzed', 'shortlisted', 
            'approached', 'negotiating', 'signed', 'rejected', 'unavailable'
        ]
        
        if new_status in valid_statuses:
            old_status = self.status
            self.status = new_status
            
            # Add to contact history
            if not self.contact_history:
                self.contact_history = []
            
            self.contact_history.append({
                'action': f'Status changed from {old_status} to {new_status}',
                'notes': notes,
                'timestamp': datetime.now().isoformat(),
                'user_id': None  # This would be set by the service layer
            })
    
    def add_contact_record(self, action: str, notes: str = None, user_id: uuid.UUID = None):
        """Add a contact record to the history"""
        if not self.contact_history:
            self.contact_history = []
        
        self.contact_history.append({
            'action': action,
            'notes': notes,
            'timestamp': datetime.now().isoformat(),
            'user_id': str(user_id) if user_id else None
        })
        
        # Update contact attempts counter
        if 'contact' in action.lower():
            self.contact_attempts = (self.contact_attempts or 0) + 1