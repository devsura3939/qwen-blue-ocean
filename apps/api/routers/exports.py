"""
Exports API router - Data export functionality.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import csv
import json
import io

from database import get_db
from models import Business, CitySnapshot, Category
from schemas import ExportRequest, ExportResponse

router = APIRouter()


@router.post("", response_model=ExportResponse)
async def create_export(
    request: ExportRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create an export of business data."""
    # Get snapshot
    snapshot_result = await db.execute(
        select(CitySnapshot).where(CitySnapshot.id == request.city_snapshot_id)
    )
    snapshot = snapshot_result.scalar_one_or_none()
    
    if not snapshot:
        raise HTTPException(status_code=404, detail="City snapshot not found")
    
    # Query businesses
    query = select(Business).where(Business.city_snapshot_id == request.city_snapshot_id)
    
    if request.category_id:
        query = query.where(Business.category_id == request.category_id)
    
    result = await db.execute(query)
    businesses = result.scalars().all()
    
    # Define fields to export
    default_fields = [
        "id", "canonical_name", "category_name", "latitude", "longitude",
        "address_line", "phone", "email", "website", "facebook_url",
        "instagram_url", "linkedin_url", "sources", "place_confidence",
        "contact_confidence", "created_at"
    ]
    
    fields = request.include_fields or default_fields
    
    if request.format == "csv":
        # Generate CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        
        for business in businesses:
            row = {field: getattr(business, field, None) for field in fields}
            # Convert non-serializable types
            for key, value in row.items():
                if hasattr(value, '__dict__'):
                    row[key] = str(value)
                elif isinstance(value, (datetime,)):
                    row[key] = value.isoformat()
            writer.writerow(row)
        
        content = output.getvalue()
        output.close()
        
        # In production, this would upload to S3 or similar
        # For now, return a placeholder URL
        download_url = f"/api/exports/{request.city_snapshot_id}.{request.format}"
        
    else:  # json
        # Generate JSON
        data = []
        for business in businesses:
            row = {}
            for field in fields:
                value = getattr(business, field, None)
                if isinstance(value, (datetime,)):
                    value = value.isoformat()
                row[field] = value
            data.append(row)
        
        # In production, this would upload to S3 or similar
        download_url = f"/api/exports/{request.city_snapshot_id}.{request.format}"
    
    return ExportResponse(
        download_url=download_url,
        format=request.format,
        record_count=len(businesses),
        expires_at=datetime.utcnow() + timedelta(hours=24),
    )


@router.get("/{snapshot_id}.{format}")
async def download_export(snapshot_id: int, format: str):
    """Download an exported file."""
    # This is a placeholder - in production would serve actual file from storage
    raise HTTPException(
        status_code=501,
        detail="Export download not implemented. Use the export creation endpoint."
    )