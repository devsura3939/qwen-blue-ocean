"""
Businesses API router.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from database import get_db
from models import Business, CitySnapshot, Category
from schemas import BusinessResponse, BusinessFilterRequest, BusinessListResponse

router = APIRouter()


@router.post("/filter", response_model=BusinessListResponse)
async def filter_businesses(
    request: BusinessFilterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Filter businesses by various criteria."""
    query = select(Business).where(Business.city_snapshot_id == request.city_snapshot_id)
    
    if request.category_id:
        query = query.where(Business.category_id == request.category_id)
    
    if request.has_email is not None:
        if request.has_email:
            query = query.where(Business.email.isnot(None))
        else:
            query = query.where(Business.email.is_(None))
    
    if request.has_phone is not None:
        if request.has_phone:
            query = query.where(Business.phone.isnot(None))
        else:
            query = query.where(Business.phone.is_(None))
    
    if request.has_website is not None:
        if request.has_website:
            query = query.where(Business.website.isnot(None))
        else:
            query = query.where(Business.website.is_(None))
    
    # Pagination
    offset = (request.page - 1) * request.page_size
    query = query.offset(offset).limit(request.page_size)
    
    result = await db.execute(query)
    businesses = result.scalars().all()
    
    # Get total count
    count_query = select(func.count()).select_from(Business).where(
        Business.city_snapshot_id == request.city_snapshot_id
    )
    if request.category_id:
        count_query = count_query.where(Business.category_id == request.category_id)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    return BusinessListResponse(
        businesses=businesses,
        total=total or 0,
        page=request.page,
        page_size=request.page_size,
        has_more=(offset + request.page_size) < (total or 0),
    )


@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(business_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific business by ID."""
    result = await db.execute(select(Business).where(Business.id == business_id))
    business = result.scalar_one_or_none()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    return business