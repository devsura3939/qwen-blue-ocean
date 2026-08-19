"""
SQLAlchemy models for the application.
"""
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Text, Numeric, Boolean, ARRAY, JSON
from sqlalchemy.dialects.postgresql import TIMESTAMP, JSONB, GEOMETRY
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Country(Base):
    __tablename__ = "countries"
    
    id = Column(Integer, primary_key=True)
    code = Column(String(2), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    name_local = Column(String(100))
    continent = Column(String(50))
    population = Column(BigInteger)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    cities = relationship("City", back_populates="country")


class City(Base):
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id"))
    name = Column(String(200), nullable=False)
    name_local = Column(String(200))
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    population = Column(BigInteger)
    timezone = Column(String(50))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    country = relationship("Country", back_populates="cities")
    boundaries = relationship("CityBoundary", back_populates="city", uselist=False)
    snapshots = relationship("CitySnapshot", back_populates="city")
    
    __table_args__ = (
        # Unique constraint for country_id + name
        {'postgresql_unique_constraint': 'unique_country_city'}
    )


class CityBoundary(Base):
    __tablename__ = "city_boundaries"
    
    id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"))
    boundary = Column(GEOMETRY('MULTIPOLYGON', 4326))
    bbox = Column(GEOMETRY('POLYGON', 4326))
    source = Column(String(50))
    source_id = Column(String(100))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    city = relationship("City", back_populates="boundaries")


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("categories.id"))
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    category_path = Column(String(500))
    level = Column(Integer, default=0)
    overture_category = Column(String(200))
    osm_key = Column(String(100))
    osm_value = Column(String(100))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    parent = relationship("Category", remote_side=[id], backref="children")
    businesses = relationship("Business", back_populates="category")


class CitySnapshot(Base):
    __tablename__ = "city_snapshots"
    
    id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"))
    status = Column(String(50), default="pending")
    total_places = Column(Integer, default=0)
    overture_places = Column(Integer, default=0)
    osm_places = Column(Integer, default=0)
    merged_duplicates = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(TIMESTAMP(timezone=True))
    completed_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    city = relationship("City", back_populates="snapshots")
    businesses = relationship("Business", back_populates="snapshot")


class Business(Base):
    __tablename__ = "businesses"
    
    id = Column(Integer, primary_key=True)
    city_snapshot_id = Column(Integer, ForeignKey("city_snapshots.id", ondelete="CASCADE"))
    canonical_name = Column(String(500), nullable=False)
    name_raw = Column(String(500))
    
    # Category
    category_id = Column(Integer, ForeignKey("categories.id"))
    category_name = Column(String(200))
    category_path = Column(String(500))
    
    # Location
    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)
    geometry = Column(GEOMETRY('POINT', 4326))
    
    # Address
    address_line = Column(String(500))
    street = Column(String(300))
    house_number = Column(String(50))
    postcode = Column(String(20))
    city = Column(String(200))
    region = Column(String(200))
    country = Column(String(100))
    country_code = Column(String(2))
    
    # Contact information
    phone = Column(String(50))
    phone_normalized = Column(String(50))
    phone_confidence = Column(Numeric(3, 2), default=0)
    phone_source = Column(String(100))
    
    email = Column(String(500))
    email_confidence = Column(Numeric(3, 2), default=0)
    email_source_url = Column(Text)
    
    website = Column(String(500))
    website_domain = Column(String(200))
    
    # Social profiles
    facebook_url = Column(Text)
    instagram_url = Column(Text)
    linkedin_url = Column(Text)
    tiktok_url = Column(Text)
    youtube_url = Column(Text)
    twitter_url = Column(Text)
    
    # Additional info
    opening_hours = Column(Text)
    brand = Column(String(200))
    
    # Source references
    overture_id = Column(String(100))
    osm_id = Column(String(100))
    osm_type = Column(String(10))
    
    # Status and confidence
    operating_status = Column(String(50))
    place_confidence = Column(Numeric(3, 2), default=0)
    contact_confidence = Column(Numeric(3, 2), default=0)
    contact_status = Column(String(50), default="source_only")
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    last_source_refresh = Column(TIMESTAMP(timezone=True))
    last_contact_crawl = Column(TIMESTAMP(timezone=True))
    
    # Metadata
    sources = Column(ARRAY(String))
    source_metadata = Column(JSONB)
    
    snapshot = relationship("CitySnapshot", back_populates="businesses")
    category = relationship("Category", back_populates="businesses")
    evidence = relationship("BusinessFieldEvidence", back_populates="business")
    crawl_jobs = relationship("CrawlJob", back_populates="business")
    crawl_results = relationship("CrawlResult", back_populates="business")


class BusinessFieldEvidence(Base):
    __tablename__ = "business_field_evidence"
    
    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"))
    field_name = Column(String(100), nullable=False)
    field_value = Column(Text, nullable=False)
    source = Column(String(100), nullable=False)
    source_url = Column(Text)
    confidence = Column(Numeric(3, 2), default=0)
    collected_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    metadata = Column(JSONB)
    
    business = relationship("Business", back_populates="evidence")


class CrawlJob(Base):
    __tablename__ = "crawl_jobs"
    
    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"))
    job_type = Column(String(50), nullable=False)
    status = Column(String(50), default="pending")
    priority = Column(Integer, default=0)
    url = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    error_message = Column(Text)
    result = Column(JSONB)
    scheduled_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    started_at = Column(TIMESTAMP(timezone=True))
    completed_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    business = relationship("Business", back_populates="crawl_jobs")


class CrawlResult(Base):
    __tablename__ = "crawl_results"
    
    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"))
    requested_url = Column(Text, nullable=False)
    final_url = Column(Text)
    status_code = Column(Integer)
    crawl_duration_ms = Column(Integer)
    content_type = Column(String(100))
    content_size_bytes = Column(Integer)
    links_found = Column(Integer, default=0)
    emails_found = Column(Integer, default=0)
    phones_found = Column(Integer, default=0)
    socials_found = Column(Integer, default=0)
    error_type = Column(String(100))
    error_message = Column(Text)
    content_hash = Column(String(64))
    etag = Column(String(200))
    last_modified = Column(String(100))
    crawled_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    metadata = Column(JSONB)
    
    business = relationship("Business", back_populates="crawl_results")


class MarketAnalysis(Base):
    __tablename__ = "market_analyses"
    
    id = Column(Integer, primary_key=True)
    city_snapshot_id = Column(Integer, ForeignKey("city_snapshots.id", ondelete="CASCADE"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    # Market metrics
    business_count = Column(Integer, default=0)
    city_population = Column(BigInteger)
    businesses_per_10k_people = Column(Numeric(10, 2))
    
    # Peer comparison
    peer_city_median = Column(Numeric(10, 2))
    expected_business_count = Column(Integer)
    supply_gap = Column(Integer)
    undersupply_percentile = Column(Numeric(5, 2))
    
    # Opportunity score
    opportunity_score = Column(Numeric(5, 2))
    supply_gap_score = Column(Numeric(5, 2))
    relative_undersupply_score = Column(Numeric(5, 2))
    market_size_score = Column(Numeric(5, 2))
    
    # Peer cities used
    peer_cities = Column(ARRAY(Integer))
    
    analyzed_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Job(Base):
    """PostgreSQL-based job queue table."""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True)
    job_type = Column(String(100), nullable=False)
    status = Column(String(50), default="pending")
    payload = Column(JSONB, nullable=False)
    result = Column(JSONB)
    error_message = Column(Text)
    priority = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    locked_by = Column(String(100))
    locked_at = Column(TIMESTAMP(timezone=True))
    scheduled_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    started_at = Column(TIMESTAMP(timezone=True))
    completed_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Cache(Base):
    __tablename__ = "cache"
    
    key = Column(String(500), primary_key=True)
    value = Column(JSONB, nullable=False)
    expires_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
