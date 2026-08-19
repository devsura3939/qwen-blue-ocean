"""
Countries API router.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from database import get_db
from models import Country
from schemas import CountryResponse

router = APIRouter()


@router.get("", response_model=List[CountryResponse])
async def list_countries(db: AsyncSession = Depends(get_db)):
    """List all countries."""
    result = await db.execute(select(Country).order_by(Country.name))
    countries = result.scalars().all()
    return countries


@router.get("/{country_id}", response_model=CountryResponse)
async def get_country(country_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific country by ID."""
    result = await db.execute(select(Country).where(Country.id == country_id))
    country = result.scalar_one_or_none()
    
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    
    return country
