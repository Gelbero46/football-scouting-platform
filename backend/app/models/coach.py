from sqlalchemy import Column, String, Integer, Date, Boolean, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import date
from app.models import BaseModel
import uuid
from datetime import datetime

class Coach(BaseModel):
    __tablename__ = "coaches"
    
    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    full_name = Column(String(255))
    date_of_birth = Column(Date)
    nationality = Column(String(100), index=True)
    
    # Career Information
    current_club = Column(String(255), index=True)
    current_role = Column(String(100), index=True)  # 'head_coach', 'assistant', 'youth_coach'
    coaching_level = Column(String(50))  # 'amateur', 'semi_pro', 'professional', 'elite'
    years_experience = Column(Integer)
    
    # Contract & Financial
    contract_expires = Column(Date)
    estimated_salary_eur = Column(Integer)  # Annual salary in EUR
    
    # Agent Information
    agent_name = Column(String(255))
    agent_contact = Column(JSON)  # {email, phone, agency}
    
    # Tactical Information
    preferred_formation = Column(String(20), index=True)  # '4-3-3', '4-2-3-1', etc.
    preferred_formations = Column(ARRAY(String), default=[])  # Multiple formations
    tactical_style = Column(JSON)  # Detailed tactical preferences
    
    # Coaching Philosophy & Attributes
    coaching_philosophy = Column(Text)
    leadership_style = Column(String(100))  # 'authoritarian', 'democratic', 'collaborative'
    communication_style = Column(String(100))  # 'direct', 'supportive', 'analytical'
    
    # Performance Metrics
    coaching_metrics = Column(JSON)  # Win rates, points per game, etc.
    team_performance = Column(JSON)  # Team statistics under this coach
    player_development = Column(JSON)  # Player improvement records
    
    # Career History
    career_history = Column(JSON)  # Array of previous positions
    achievements = Column(JSON)  # Trophies, honors, awards
    certifications = Column(ARRAY(String), default=[])  # Coaching licenses
    
    # Languages
    languages_spoken = Column(ARRAY(String), default=[])
    
    # Strengths & Style Analysis
    strengths = Column(ARRAY(String), default=[])
    weaknesses = Column(ARRAY(String), default=[])
    coaching_specialties = Column(ARRAY(String), default=[])  # Youth development, tactics, etc.
    
    # Scouting Information
    scouting_notes = Column(Text)
    tags = Column(ARRAY(String), default=[])
    overall_rating = Column(Integer)  # 0-100 overall coaching rating
    
    # Availability & Status
    availability_status = Column(String(50), default='available')
    # 'available', 'under_contract', 'sabbatical', 'retired'
    available_from_date = Column(Date)
    
    # Preferences & Requirements
    preferred_leagues = Column(ARRAY(String), default=[])
    salary_expectations = Column(JSON)  # Min/max expectations
    contract_preferences = Column(JSON)  # Length, clauses, etc.
    
    # Data Management
    data_source = Column(String(100), default='manual')
    last_updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    creator = relationship("User", back_populates="created_coaches", foreign_keys=[created_by])
    shortlist_items = relationship("ShortlistItem", back_populates="coach", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Coach(name={self.name}, role={self.current_role}, club={self.current_club})>"
    
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
    
    def get_win_rate(self, competition='all'):
        """Calculate win rate from coaching metrics"""
        if self.coaching_metrics and isinstance(self.coaching_metrics, dict):
            metrics = self.coaching_metrics.get(competition, self.coaching_metrics.get('overall', {}))
            wins = metrics.get('wins', 0)
            total_games = metrics.get('total_games', 0)
            if total_games > 0:
                return round((wins / total_games) * 100, 2)
        return 0
    
    def get_points_per_game(self, competition='all'):
        """Calculate average points per game"""
        if self.coaching_metrics and isinstance(self.coaching_metrics, dict):
            metrics = self.coaching_metrics.get(competition, self.coaching_metrics.get('overall', {}))
            points = metrics.get('points', 0)
            games = metrics.get('total_games', 0)
            if games > 0:
                return round(points / games, 2)
        return 0
    
    def add_achievement(self, title: str, year: int, description: str = None):
        """Add a new achievement to the coach's record"""
        if not self.achievements:
            self.achievements = []
        
        achievement = {
            'title': title,
            'year': year,
            'description': description,
            'added_at': datetime.now().isoformat()
        }
        self.achievements.append(achievement)

# Create indexes for better query performance
Index('idx_coaches_name_club', Coach.name, Coach.current_club)
Index('idx_coaches_role_level', Coach.current_role, Coach.coaching_level)
Index('idx_coaches_formation_style', Coach.preferred_formation, Coach.leadership_style)
Index('idx_coaches_nationality_experience', Coach.nationality, Coach.years_experience)