CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";


-- Users table (managed by Clerk, but we might need local reference)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clerk_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'analyst', 'coach', 'scout')),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    avatar_url TEXT,
    organization_id UUID,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Players table
CREATE TABLE players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- Basic Information
    name VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    date_of_birth DATE,
    nationality VARCHAR(100),
    second_nationality VARCHAR(100),
    
    -- Physical Attributes
    height_cm INTEGER,
    weight_kg INTEGER,
    preferred_foot VARCHAR(10) CHECK (preferred_foot IN ('left', 'right', 'both')),
    
    -- Career Information
    current_club VARCHAR(255),
    position VARCHAR(50) NOT NULL,
    secondary_positions TEXT[], -- Array of positions
    shirt_number INTEGER,
    
    -- Contract & Financial
    contract_expires DATE,
    market_value_eur INTEGER,
    weekly_wage_eur INTEGER,
    agent_name VARCHAR(255),
    agent_contact JSON, -- {email, phone, agency}
    
    -- Performance Metrics (JSON for flexibility)
    current_season_stats JSON,
    career_stats JSON,
    performance_history JSON[], -- Array of season performances
    
    -- Scouting Information
    scouting_notes TEXT,
    tags TEXT[], -- Array of tags like ['pace', 'technical', 'leadership']
    overall_rating INTEGER CHECK (overall_rating >= 0 AND overall_rating <= 100),
    potential_rating INTEGER CHECK (potential_rating >= 0 AND potential_rating <= 100),
    
    -- System Fields
    data_source VARCHAR(100), -- 'manual', 'api_import', 'csv_import'
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    
    -- Search optimization
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(name, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(current_club, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(position, '')), 'C')
    ) STORED
);

-- Coaches table
CREATE TABLE coaches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- Basic Information
    name VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    date_of_birth DATE,
    nationality VARCHAR(100),
    
    -- Career Information
    current_club VARCHAR(255),
    current_role VARCHAR(100), -- 'head_coach', 'assistant', 'youth_coach'
    coaching_level VARCHAR(50), -- 'amateur', 'semi_pro', 'professional', 'elite'
    
    -- Contract & Financial
    contract_expires DATE,
    estimated_salary_eur INTEGER,
    agent_name VARCHAR(255),
    agent_contact JSON,
    
    -- Coaching Style & Metrics
    preferred_formation VARCHAR(20),
    tactical_style JSON, -- {possession_based, counter_attack, high_press, etc.}
    coaching_metrics JSON, -- {win_rate, avg_points, player_development, etc.}
    career_history JSON[], -- Array of previous positions
    
    -- Achievements
    trophies JSON[], -- Array of trophies and honors
    certifications TEXT[], -- Coaching licenses and certifications
    
    -- Scouting Information
    scouting_notes TEXT,
    tags TEXT[],
    overall_rating INTEGER CHECK (overall_rating >= 0 AND overall_rating <= 100),
    
    -- System Fields
    data_source VARCHAR(100),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(name, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(current_club, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(current_role, '')), 'C')
    ) STORED
);

-- Shortlists table
CREATE TABLE shortlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(20) NOT NULL CHECK (type IN ('player', 'coach')),
    
    -- Ownership & Permissions
    created_by UUID REFERENCES users(id) NOT NULL,
    shared_with UUID[], -- Array of user IDs who can access
    organization_id UUID,
    
    -- Status & Priority
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'completed')),
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    
    -- Metadata
    tags TEXT[],
    deadline DATE,
    budget_eur INTEGER,
    
    -- System Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Shortlist items (players or coaches in shortlists)
CREATE TABLE shortlist_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shortlist_id UUID REFERENCES shortlists(id) ON DELETE CASCADE,
    
    -- Reference to either player or coach
    player_id UUID REFERENCES players(id) ON DELETE CASCADE,
    coach_id UUID REFERENCES coaches(id) ON DELETE CASCADE,
    
    -- Item-specific data
    status VARCHAR(50) DEFAULT 'identified' CHECK (
        status IN ('identified', 'scouted', 'analyzed', 'shortlisted', 
                  'approached', 'negotiating', 'signed', 'rejected', 'unavailable')
    ),
    priority INTEGER DEFAULT 3 CHECK (priority >= 1 AND priority <= 5), -- 1-5 stars
    
    -- Notes & Assessment
    notes TEXT,
    strengths TEXT[],
    weaknesses TEXT[],
    scout_rating INTEGER CHECK (scout_rating >= 0 AND scout_rating <= 100),
    
    -- Financial
    estimated_fee_eur INTEGER,
    wage_demands_eur INTEGER,
    
    -- Timeline
    added_by UUID REFERENCES users(id),
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT shortlist_items_reference_check 
        CHECK ((player_id IS NOT NULL AND coach_id IS NULL) OR 
               (player_id IS NULL AND coach_id IS NOT NULL))
);

-- Reports table
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(50) NOT NULL CHECK (type IN ('player_scout', 'coach_analysis', 'shortlist_summary', 'comparison')),
    title VARCHAR(255) NOT NULL,
    
    -- Report Configuration
    parameters JSON NOT NULL, -- Report-specific configuration
    filters JSON, -- Applied filters
    
    -- Generated Content
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'generating', 'completed', 'failed')),
    file_path TEXT, -- S3 path to generated PDF
    file_size INTEGER, -- File size in bytes
    
    -- Metadata
    generated_by UUID REFERENCES users(id),
    generated_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE, -- Auto-delete old reports
    download_count INTEGER DEFAULT 0,
    
    -- System Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    error_message TEXT -- If generation failed
);

-- Activity log for audit trail
CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL, -- 'player_viewed', 'shortlist_created', etc.
    resource_type VARCHAR(50) NOT NULL, -- 'player', 'coach', 'shortlist', etc.
    resource_id UUID NOT NULL,
    details JSON, -- Additional context
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);



-- Performance indexes
CREATE INDEX idx_players_position ON players(position);
CREATE INDEX idx_players_club ON players(current_club);
CREATE INDEX idx_players_nationality ON players(nationality);
CREATE INDEX idx_players_market_value ON players(market_value_eur DESC);
CREATE INDEX idx_players_search ON players USING GIN(search_vector);

CREATE INDEX idx_coaches_club ON coaches(current_club);
CREATE INDEX idx_coaches_role ON coaches(current_role);
CREATE INDEX idx_coaches_search ON coaches USING GIN(search_vector);

CREATE INDEX idx_shortlists_created_by ON shortlists(created_by);
CREATE INDEX idx_shortlists_type_status ON shortlists(type, status);

CREATE INDEX idx_shortlist_items_shortlist ON shortlist_items(shortlist_id);
CREATE INDEX idx_shortlist_items_player ON shortlist_items(player_id);
CREATE INDEX idx_shortlist_items_status ON shortlist_items(status);

CREATE INDEX idx_reports_generated_by ON reports(generated_by);
CREATE INDEX idx_reports_type_status ON reports(type, status);
CREATE INDEX idx_reports_expires_at ON reports(expires_at);

CREATE INDEX idx_activity_logs_user_created ON activity_logs(user_id, created_at DESC);
CREATE INDEX idx_activity_logs_resource ON activity_logs(resource_type, resource_id);