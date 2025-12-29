from sqlalchemy import Column, String, Integer, Date, Boolean, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import date, datetime
from app.models import BaseModel
import uuid

class Player(BaseModel):
    __tablename__ = "players"
    
    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    full_name = Column(String(255))
    date_of_birth = Column(Date)
    nationality = Column(String(100), index=True)
    second_nationality = Column(String(100))
    
    # Physical Attributes  
    height_cm = Column(Integer)  # Height in centimeters
    weight_kg = Column(Integer)  # Weight in kilograms
    preferred_foot = Column(String(10))  # 'left', 'right', 'both'
    
    # Career Information
    current_club = Column(String(255), index=True)
    position = Column(String(50), nullable=False, index=True)
    secondary_positions = Column(ARRAY(String), default=[])
    shirt_number = Column(Integer)
    
    # Contract & Financial Information
    contract_expires = Column(Date)
    market_value_eur = Column(Integer, index=True)  # Market value in EUR
    weekly_wage_eur = Column(Integer)  # Weekly wage in EUR
    release_clause_eur = Column(Integer)  # Release clause in EUR
    
    # Agent Information
    agent_name = Column(String(255))
    agent_contact = Column(JSON)  # {email, phone, agency, etc.}
    
    # Performance Data
    current_season_stats = Column(JSON)  # Current season statistics
    career_stats = Column(JSON)  # Career totals
    performance_history = Column(JSON)  # Array of season-by-season data
    
    # Advanced Analytics
    similarity_vector = Column(JSON)  # For ML similarity matching
    performance_metrics = Column(JSON)  # Advanced metrics like xG, xA, etc.
    tactical_attributes = Column(JSON)  # Tactical intelligence, positioning, etc.
    
    # Scouting Information
    scouting_notes = Column(Text)
    strengths = Column(ARRAY(String), default=[])  # Array of strength tags
    weaknesses = Column(ARRAY(String), default=[])  # Array of weakness tags
    tags = Column(ARRAY(String), default=[])  # General tags
    
    # Ratings
    overall_rating = Column(Integer)  # 0-100 overall rating
    potential_rating = Column(Integer)  # 0-100 potential rating
    scout_rating = Column(Integer)  # 0-100 scout assessment
    
    # Status & Availability
    availability_status = Column(String(50), default='available')  
    # 'available', 'transfer_listed', 'contract_extension', 'unavailable'
    injury_status = Column(String(100))
    injury_return_date = Column(Date)
    
    # Data Management
    data_source = Column(String(100), default='manual')  # 'manual', 'api_import', 'csv_import'
    data_quality_score = Column(Integer, default=0)  # 0-100 data completeness score
    last_updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # System Fields
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    creator = relationship("User", back_populates="created_players", foreign_keys=[created_by])
    shortlist_items = relationship("ShortlistItem", back_populates="player", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Player(name={self.name}, position={self.position}, club={self.current_club})>"
    
    @hybrid_property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    @property
    def display_name(self):
        return self.full_name or self.name
    
    @property
    def market_value_display(self):
        if self.market_value_eur:
            if self.market_value_eur >= 1000000:
                return f"€{self.market_value_eur / 1000000:.1f}M"
            elif self.market_value_eur >= 1000:
                return f"€{self.market_value_eur / 1000:.0f}K"
            else:
                return f"€{self.market_value_eur}"
        return "N/A"
    
    def get_current_season_stat(self, stat_name: str, default=0):
        """Get a specific stat from current season stats"""
        if self.current_season_stats and isinstance(self.current_season_stats, dict):
            return self.current_season_stats.get(stat_name, default)
        return default
    
    def update_performance_metrics(self, metrics: dict):
        """Update performance metrics with validation"""
        if not self.performance_metrics:
            self.performance_metrics = {}
        
        # Validate and update metrics
        valid_metrics = ['xG', 'xA', 'progressive_passes', 'defensive_actions', 'dribble_success_rate']
        for key, value in metrics.items():
            if key in valid_metrics and isinstance(value, (int, float)):
                self.performance_metrics[key] = value

# Create indexes for better query performance
Index('idx_players_name_club', Player.name, Player.current_club)
Index('idx_players_position_nationality', Player.position, Player.nationality)
Index('idx_players_market_value_desc', Player.market_value_eur.desc())
Index('idx_players_age_position', Player.date_of_birth, Player.position)