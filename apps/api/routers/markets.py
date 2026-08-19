"""
Markets API router - Market analysis and opportunity discovery.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from database import get_db
from models import CitySnapshot, MarketAnalysis, Category, City
from schemas import (
    MarketAnalysisRequest,
    MarketAnalysisResponse,
    OpportunityDiscoveryRequest,
    OpportunityDiscoveryResponse,
    OpportunityScore,
)

router = APIRouter()


@router.post("/analyze", response_model=MarketAnalysisResponse)
async def analyze_market(
    request: MarketAnalysisRequest,
    db: AsyncSession = Depends(get_db),
):
    """Analyze a specific market category in a city."""
    # Get snapshot
    snapshot_result = await db.execute(
        select(CitySnapshot).where(CitySnapshot.id == request.city_snapshot_id)
    )
    snapshot = snapshot_result.scalar_one_or_none()
    
    if not snapshot:
        raise HTTPException(status_code=404, detail="City snapshot not found")
    
    # Get category
    category_result = await db.execute(
        select(Category).where(Category.id == request.category_id)
    )
    category = category_result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if analysis already exists
    existing_analysis = await db.execute(
        select(MarketAnalysis).where(
            MarketAnalysis.city_snapshot_id == request.city_snapshot_id,
            MarketAnalysis.category_id == request.category_id
        )
    )
    analysis = existing_analysis.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Market analysis not found. Please run opportunity discovery first."
        )
    
    return MarketAnalysisResponse(
        category_id=analysis.category_id,
        category_name=category.name,
        category_path=category.category_path,
        business_count=analysis.business_count,
        city_population=analysis.city_population,
        businesses_per_10k_people=analysis.businesses_per_10k_people,
        peer_city_median=analysis.peer_city_median,
        expected_business_count=analysis.expected_business_count,
        supply_gap=analysis.supply_gap,
        undersupply_percentile=analysis.undersupply_percentile,
        opportunity_score=analysis.opportunity_score,
        peer_cities=analysis.peer_cities or [],
        analyzed_at=analysis.analyzed_at,
    )


@router.post("/opportunities/discover", response_model=OpportunityDiscoveryResponse)
async def discover_opportunities(
    request: OpportunityDiscoveryRequest,
    db: AsyncSession = Depends(get_db),
):
    """Discover business opportunities in a city."""
    # Get snapshot
    snapshot_result = await db.execute(
        select(CitySnapshot).where(CitySnapshot.id == request.city_snapshot_id)
    )
    snapshot = snapshot_result.scalar_one_or_none()
    
    if not snapshot:
        raise HTTPException(status_code=404, detail="City snapshot not found")
    
    # Get city info
    city_result = await db.execute(
        select(City).where(City.id == snapshot.city_id)
    )
    city = city_result.scalar_one_or_none()
    
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    
    # Get all market analyses for this snapshot
    analyses_result = await db.execute(
        select(MarketAnalysis)
        .where(MarketAnalysis.city_snapshot_id == request.city_snapshot_id)
        .order_by(MarketAnalysis.opportunity_score.desc())
        .limit(request.max_categories)
    )
    analyses = analyses_result.scalars().all()
    
    if not analyses:
        # No analyses available yet - return empty
        return OpportunityDiscoveryResponse(
            city_id=city.id,
            city_name=city.name,
            opportunities=[],
            total_categories_analyzed=0,
        )
    
    # Build opportunities list
    opportunities = []
    for rank, analysis in enumerate(analyses, 1):
        # Get category name
        category_result = await db.execute(
            select(Category).where(Category.id == analysis.category_id)
        )
        category = category_result.scalar_one_or_none()
        
        if category:
            opportunities.append(OpportunityScore(
                rank=rank,
                category_id=category.id,
                category_name=category.name,
                category_path=category.category_path,
                existing_count=analysis.business_count,
                expected_count=analysis.expected_business_count,
                gap=analysis.supply_gap,
                score=analysis.opportunity_score or 0,
                data_confidence=0.8,  # Placeholder - would be calculated from data quality
            ))
    
    return OpportunityDiscoveryResponse(
        city_id=city.id,
        city_name=city.name,
        opportunities=opportunities,
        total_categories_analyzed=len(analyses),
    )