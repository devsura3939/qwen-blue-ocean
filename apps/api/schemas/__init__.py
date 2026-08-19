"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, Field, HttpUrl, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


# Country schemas
class CountryBase(BaseModel):
    code: str
    name: str
    name_local: Optional[str] = None
    continent: Optional[str] = None
    population: Optional[int] = None


class CountryCreate(CountryBase):
    pass


class CountryResponse(CountryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# City schemas
class CityBase(BaseModel):
    name: str
    name_local: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    population: Optional[int] = None
    timezone: Optional[str] = None


class CityCreate(CityBase):
    country_id: int


class CityResponse(CityBase):
    id: int
    country_id: int
    country: Optional[CountryResponse] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CitySearchRequest(BaseModel):
    query: str
    country_code: Optional[str] = None


class CityResolveRequest(BaseModel):
    country_code: str
    city_name: str


class CityResolveResponse(BaseModel):
    city_id: int
    city_name: str
    country_code: str
    country_name: str
    latitude: float
    longitude: float
    population: Optional[int] = None
    boundary_available: bool = False


# Category schemas
class CategoryBase(BaseModel):
    name: str
    slug: str
    category_path: Optional[str] = None
    level: int = 0
    overture_category: Optional[str] = None
    osm_key: Optional[str] = None
    osm_value: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: int
    parent_id: Optional[int] = None
    children: List['CategoryResponse'] = []
    
    class Config:
        from_attributes = True


class CategoryTreeResponse(BaseModel):
    categories: List[CategoryResponse]


# Business schemas
class BusinessBase(BaseModel):
    canonical_name: str
    name_raw: Optional[str] = None
    category_name: Optional[str] = None
    category_path: Optional[str] = None
    latitude: Decimal
    longitude: Decimal
    address_line: Optional[str] = None
    street: Optional[str] = None
    house_number: Optional[str] = None
    postcode: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    phone: Optional[str] = None
    phone_normalized: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    website_domain: Optional[str] = None
    facebook_url: Optional[str] = None
    instagram_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    tiktok_url: Optional[str] = None
    opening_hours: Optional[str] = None
    brand: Optional[str] = None
    operating_status: Optional[str] = None
    place_confidence: Optional[Decimal] = None
    contact_confidence: Optional[Decimal] = None
    contact_status: Optional[str] = None
    sources: Optional[List[str]] = None


class BusinessResponse(BusinessBase):
    id: int
    city_snapshot_id: int
    category_id: Optional[int] = None
    overture_id: Optional[str] = None
    osm_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BusinessListResponse(BaseModel):
    businesses: List[BusinessResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class BusinessFilterRequest(BaseModel):
    city_snapshot_id: int
    category_id: Optional[int] = None
    category_slug: Optional[str] = None
    has_email: Optional[bool] = None
    has_phone: Optional[bool] = None
    has_website: Optional[bool] = None
    has_instagram: Optional[bool] = None
    has_facebook: Optional[bool] = None
    min_contact_confidence: Optional[Decimal] = None
    min_place_confidence: Optional[Decimal] = None
    page: int = 1
    page_size: int = 50


# City Snapshot schemas
class CitySnapshotBase(BaseModel):
    city_id: int


class CitySnapshotResponse(BaseModel):
    id: int
    city_id: int
    status: str
    total_places: int
    overture_places: int
    osm_places: int
    merged_duplicates: int
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class CitySnapshotStatusResponse(BaseModel):
    snapshot_id: int
    status: str
    progress_percent: float
    total_places: int
    message: Optional[str] = None


# Market Analysis schemas
class MarketAnalysisRequest(BaseModel):
    city_snapshot_id: int
    category_id: int


class MarketAnalysisResponse(BaseModel):
    category_id: int
    category_name: str
    category_path: Optional[str] = None
    business_count: int
    city_population: Optional[int] = None
    businesses_per_10k_people: Optional[Decimal] = None
    peer_city_median: Optional[Decimal] = None
    expected_business_count: Optional[int] = None
    supply_gap: Optional[int] = None
    undersupply_percentile: Optional[Decimal] = None
    opportunity_score: Optional[Decimal] = None
    peer_cities: List[int] = []
    analyzed_at: datetime


class OpportunityDiscoveryRequest(BaseModel):
    city_snapshot_id: int
    min_categories: int = 10
    max_categories: int = 50


class OpportunityScore(BaseModel):
    rank: int
    category_id: int
    category_name: str
    category_path: Optional[str] = None
    existing_count: int
    expected_count: Optional[int] = None
    gap: Optional[int] = None
    score: Decimal
    data_confidence: Decimal


class OpportunityDiscoveryResponse(BaseModel):
    city_id: int
    city_name: str
    opportunities: List[OpportunityScore]
    total_categories_analyzed: int


# Crawl Job schemas
class CrawlJobRequest(BaseModel):
    business_id: int
    job_type: str = "enrich_contact"
    priority: int = 0


class CrawlJobResponse(BaseModel):
    id: int
    business_id: int
    job_type: str
    status: str
    priority: int
    url: Optional[str] = None
    retry_count: int
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Export schemas
class ExportRequest(BaseModel):
    city_snapshot_id: int
    category_id: Optional[int] = None
    format: str = "csv"  # csv or json
    include_fields: Optional[List[str]] = None


class ExportResponse(BaseModel):
    download_url: str
    format: str
    record_count: int
    expires_at: datetime


# Job Queue schemas
class JobStatusResponse(BaseModel):
    job_id: int
    job_type: str
    status: str
    progress_percent: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# Contact enrichment schemas
class ContactEnrichmentRequest(BaseModel):
    business_ids: List[int]
    priority: str = "normal"  # normal, high, low


class ContactEnrichmentStatus(BaseModel):
    business_id: int
    status: str  # complete, partial, source_only, website_crawled, website_blocked, website_missing, crawl_failed
    emails_found: int = 0
    phones_found: int = 0
    socials_found: int = 0
    last_crawl: Optional[datetime] = None


# Error response
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


# Pagination
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    has_more: bool
