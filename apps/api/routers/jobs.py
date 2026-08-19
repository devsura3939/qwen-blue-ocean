"""
Jobs API router - Job queue management.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import Job
from schemas import JobStatusResponse

router = APIRouter()


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: int, db: AsyncSession = Depends(get_db)):
    """Get the status of a job."""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Calculate progress percent based on status
    progress_percent = None
    if job.status == "pending":
        progress_percent = 0.0
    elif job.status == "running":
        progress_percent = 50.0  # Placeholder - would be updated by worker
    elif job.status in ["completed", "failed"]:
        progress_percent = 100.0
    
    return JobStatusResponse(
        job_id=job.id,
        job_type=job.job_type,
        status=job.status,
        progress_percent=progress_percent,
        result=job.result,
        error_message=job.error_message,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
    )