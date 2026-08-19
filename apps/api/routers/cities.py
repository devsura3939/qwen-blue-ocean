"""
Cities API router.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional

from database import get_db
from models import City, Country, CityBoundary
from schemas import (
    CityResponse,
    CitySearchRequest,
    CityResolveRequest,
    CityResolveResponse,
)

router = APIRouter()


@router.get("/search", response_model=List[CityResponse])
async def search_cities(
    q: str = Query(..., description="Search query"),
    country_code: Optional[str] = Query(None, description="Filter by country code"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Search cities by name."""
    query = select(City).join(Country).where(
        func.lower(City.name).like(f"%{q.lower()}%")
    )
    
    if country_code:
        query = query.where(Country.code == country_code.upper())
    
    query = query.order_by(City.population.desc().nullslast()).limit(limit)
    
    result = await db.execute(query)
    cities = result.scalars().all()
    return cities


@router.post("/resolve", response_model=CityResolveResponse)
async def resolve_city(
    request: CityResolveRequest,
    db: AsyncSession = Depends(get_db),
):
    """Resolve a city by country code and city name."""
    # Find country
    country_result = await db.execute(
        select(Country).where(Country.code == request.country_code.upper())
    )
    country = country_result.scalar_one_or_none()
    
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    
    # Find city
    city_result = await db.execute(
        select(City).where(
            City.country_id == country.id,
            func.lower(City.name) == request.city_name.lower()
        )
    )
    city = city_result.scalar_one_or_none()
    
    if not city:
        # Try partial match
        city_result = await db.execute(
            select(City).where(
                City.country_id == country.id,
                func.lower(City.name).like(f"%{request.city_name.lower()}%")
            ).order_by(City.population.desc().nullslast()).limit(1)
        )
        city = city_result.scalar_one_or_none()
        
        if not city:
            raise HTTPException(status_code=404, detail="City not found")
    
    # Check if boundary exists
    boundary_result = await db.execute(
        select(CityBoundary).where(CityBoundary.city_id == city.id)
    )
    boundary = boundary_result.scalar_one_or_none()
    
    return CityResolveResponse(
        city_id=city.id,
        city_name=city.name,
        country_code=country.code,
        country_name=country.name,
        latitude=float(city.latitude) if city.latitude else 0.0,
        longitude=float(city.longitude) if city.longitude else 0.0,
        population=city.population,
        boundary_available=boundary is not None,
    )


@router.get("/{city_id}", response_model=CityResponse)
async def get_city(city_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific city by ID."""
    result = await db.execute(select(City).where(City.id == city_id))
    city = result.scalar_one_or_none()
    
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    
    return city
