-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Countries table
CREATE TABLE IF NOT EXISTS countries (
    id SERIAL PRIMARY KEY,
    code VARCHAR(2) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    name_local VARCHAR(100),
    continent VARCHAR(50),
    population BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Cities table
CREATE TABLE IF NOT EXISTS cities (
    id SERIAL PRIMARY KEY,
    country_id INTEGER REFERENCES countries(id),
    name VARCHAR(200) NOT NULL,
    name_local VARCHAR(200),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    population BIGINT,
    timezone VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(country_id, name)
);

-- City boundaries table
CREATE TABLE IF NOT EXISTS city_boundaries (
    id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
    boundary GEOMETRY(MULTIPOLYGON, 4326),
    bbox GEOMETRY(POLYGON, 4326),
    source VARCHAR(50),
    source_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_city_boundaries_city_id ON city_boundaries(city_id);
CREATE INDEX IF NOT EXISTS idx_city_boundaries_boundary ON city_boundaries USING GIST(boundary);

-- Categories table (hierarchical)
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    parent_id INTEGER REFERENCES categories(id),
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    category_path VARCHAR(500),
    level INTEGER DEFAULT 0,
    overture_category VARCHAR(200),
    osm_key VARCHAR(100),
    osm_value VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_categories_parent ON categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_categories_slug ON categories(slug);

-- City snapshots table
CREATE TABLE IF NOT EXISTS city_snapshots (
    id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending',
    total_places INTEGER DEFAULT 0,
    overture_places INTEGER DEFAULT 0,
    osm_places INTEGER DEFAULT 0,
    merged_duplicates INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_city_snapshots_city_id ON city_snapshots(city_id);
CREATE INDEX IF NOT EXISTS idx_city_snapshots_status ON city_snapshots(status);

-- Businesses table
CREATE TABLE IF NOT EXISTS businesses (
    id SERIAL PRIMARY KEY,
    city_snapshot_id INTEGER REFERENCES city_snapshots(id) ON DELETE CASCADE,
    canonical_name VARCHAR(500) NOT NULL,
    name_raw VARCHAR(500),
    
    -- Category
    category_id INTEGER REFERENCES categories(id),
    category_name VARCHAR(200),
    category_path VARCHAR(500),
    
    -- Location
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    geometry GEOMETRY(POINT, 4326),
    
    -- Address
    address_line VARCHAR(500),
    street VARCHAR(300),
    house_number VARCHAR(50),
    postcode VARCHAR(20),
    city VARCHAR(200),
    region VARCHAR(200),
    country VARCHAR(100),
    country_code VARCHAR(2),
    
    -- Contact information
    phone VARCHAR(50),
    phone_normalized VARCHAR(50),
    phone_confidence DECIMAL(3, 2) DEFAULT 0,
    phone_source VARCHAR(100),
    
    email VARCHAR(500),
    email_confidence DECIMAL(3, 2) DEFAULT 0,
    email_source_url TEXT,
    
    website VARCHAR(500),
    website_domain VARCHAR(200),
    
    -- Social profiles
    facebook_url TEXT,
    instagram_url TEXT,
    linkedin_url TEXT,
    tiktok_url TEXT,
    youtube_url TEXT,
    twitter_url TEXT,
    
    -- Additional info
    opening_hours TEXT,
    brand VARCHAR(200),
    
    -- Source references
    overture_id VARCHAR(100),
    osm_id VARCHAR(100),
    osm_type VARCHAR(10),
    
    -- Status and confidence
    operating_status VARCHAR(50),
    place_confidence DECIMAL(3, 2) DEFAULT 0,
    contact_confidence DECIMAL(3, 2) DEFAULT 0,
    contact_status VARCHAR(50) DEFAULT 'source_only',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_source_refresh TIMESTAMP WITH TIME ZONE,
    last_contact_crawl TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    sources TEXT[], -- Array of source names
    source_metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_businesses_snapshot ON businesses(city_snapshot_id);
CREATE INDEX IF NOT EXISTS idx_businesses_category ON businesses(category_id);
CREATE INDEX IF NOT EXISTS idx_businesses_geometry ON businesses USING GIST(geometry);
CREATE INDEX IF NOT EXISTS idx_businesses_location ON businesses(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_businesses_name ON businesses(canonical_name);
CREATE INDEX IF NOT EXISTS idx_businesses_overture ON businesses(overture_id);
CREATE INDEX IF NOT EXISTS idx_businesses_osm ON businesses(osm_id);

-- Business field evidence table (provenance tracking)
CREATE TABLE IF NOT EXISTS business_field_evidence (
    id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES businesses(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    field_value TEXT NOT NULL,
    source VARCHAR(100) NOT NULL,
    source_url TEXT,
    confidence DECIMAL(3, 2) DEFAULT 0,
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_evidence_business ON business_field_evidence(business_id);
CREATE INDEX IF NOT EXISTS idx_evidence_field ON business_field_evidence(field_name);

-- Crawl jobs table
CREATE TABLE IF NOT EXISTS crawl_jobs (
    id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES businesses(id) ON DELETE CASCADE,
    job_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    priority INTEGER DEFAULT 0,
    url TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_message TEXT,
    result JSONB,
    scheduled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_crawl_jobs_status ON crawl_jobs(status);
CREATE INDEX IF NOT EXISTS idx_crawl_jobs_priority ON crawl_jobs(priority, scheduled_at);
CREATE INDEX IF NOT EXISTS idx_crawl_jobs_business ON crawl_jobs(business_id);

-- Crawl results table
CREATE TABLE IF NOT EXISTS crawl_results (
    id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES businesses(id) ON DELETE CASCADE,
    requested_url TEXT NOT NULL,
    final_url TEXT,
    status_code INTEGER,
    crawl_duration_ms INTEGER,
    content_type VARCHAR(100),
    content_size_bytes INTEGER,
    links_found INTEGER DEFAULT 0,
    emails_found INTEGER DEFAULT 0,
    phones_found INTEGER DEFAULT 0,
    socials_found INTEGER DEFAULT 0,
    error_type VARCHAR(100),
    error_message TEXT,
    content_hash VARCHAR(64),
    etag VARCHAR(200),
    last_modified VARCHAR(100),
    crawled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_crawl_results_business ON crawl_results(business_id);
CREATE INDEX IF NOT EXISTS idx_crawl_results_crawled_at ON crawl_results(crawled_at);

-- Market analyses table
CREATE TABLE IF NOT EXISTS market_analyses (
    id SERIAL PRIMARY KEY,
    city_snapshot_id INTEGER REFERENCES city_snapshots(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id),
    
    -- Market metrics
    business_count INTEGER DEFAULT 0,
    city_population BIGINT,
    businesses_per_10k_people DECIMAL(10, 2),
    
    -- Peer comparison
    peer_city_median DECIMAL(10, 2),
    expected_business_count INTEGER,
    supply_gap INTEGER,
    undersupply_percentile DECIMAL(5, 2),
    
    -- Opportunity score
    opportunity_score DECIMAL(5, 2),
    supply_gap_score DECIMAL(5, 2),
    relative_undersupply_score DECIMAL(5, 2),
    market_size_score DECIMAL(5, 2),
    
    -- Peer cities used
    peer_cities INTEGER[], -- Array of city IDs
    
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_market_analyses_snapshot ON market_analyses(city_snapshot_id);
CREATE INDEX IF NOT EXISTS idx_market_analyses_category ON market_analyses(category_id);

-- Jobs queue table (PostgreSQL-based job queue)
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    job_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    payload JSONB NOT NULL,
    result JSONB,
    error_message TEXT,
    priority INTEGER DEFAULT 0,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    locked_by VARCHAR(100),
    locked_at TIMESTAMP WITH TIME ZONE,
    scheduled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_priority ON jobs(priority, scheduled_at);
CREATE INDEX IF NOT EXISTS idx_jobs_type ON jobs(job_type);

-- Cache table
CREATE TABLE IF NOT EXISTS cache (
    key VARCHAR(500) PRIMARY KEY,
    value JSONB NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache(expires_at);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_countries_updated_at BEFORE UPDATE ON countries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cities_updated_at BEFORE UPDATE ON cities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_city_boundaries_updated_at BEFORE UPDATE ON city_boundaries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_businesses_updated_at BEFORE UPDATE ON businesses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
