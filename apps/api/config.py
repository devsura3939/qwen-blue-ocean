"""
Configuration settings for the API.
"""
from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:postgres@postgres:5432/business_gap_finder"
    
    # Application
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]
    
    # Crawler settings
    crawler_max_concurrency: int = 10
    crawler_browser_concurrency: int = 2
    crawler_timeout: int = 30
    crawler_max_pages_per_site: int = 6
    crawler_user_agent: str = "BusinessGapFinder/1.0 (+https://github.com/example/business-gap-finder)"
    
    # Rate limiting
    rate_limit_requests_per_second: int = 5
    domain_rate_limit_delay: float = 1.0
    
    # Cache TTL (seconds)
    cache_ttl_city: int = 86400  # 24 hours
    cache_ttl_boundary: int = 604800  # 7 days
    cache_ttl_overture: int = 604800  # 7 days
    cache_ttl_osm: int = 86400  # 24 hours
    
    # Security - SSRF protection
    ssrf_allowed_schemes: List[str] = ["http", "https"]
    ssrf_blocked_ips: List[str] = [
        "127.0.0.1",
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16",
        "169.254.169.254",  # AWS metadata
        "::1",
        "fc00::/7",
        "fe80::/10",
    ]
    
    # Optional API keys (not required for baseline)
    google_places_api_key: Optional[str] = None
    mapbox_api_key: Optional[str] = None
    nominatim_email: Optional[str] = None
    
    # Overture Maps configuration
    overture_release: Optional[str] = None  # Auto-detect if not set
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
