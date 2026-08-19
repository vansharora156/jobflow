from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import Session


from app.config import settings
from app.database import get_db
from app.models.job_db import JobDB
from app.services.ingestion import IngestionService
from app.sources.rss_source import RSSJobSource
from app.sources.fallback_source import FallbackRSSJobSource
from app.services.source_manager import SourceManager




router = APIRouter(prefix="/jobs", tags=["Jobs"])




@router.get("/")
def get_jobs(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    limit = min(max(limit, 1), 100)
    offset = max(offset, 0)


    statement = (
        select(JobDB)
        .order_by(JobDB.published_at.desc())
        .offset(offset)
        .limit(limit)
    )


    jobs = db.scalars(statement).all()


    return jobs




@router.get("/count")
def get_job_count(db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT COUNT(*) FROM jobs")
    )


    return {
        "job_count": result.scalar()
    }




@router.get("/{job_id}")
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = db.get(JobDB, job_id)


    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )


    return job




@router.post("/ingest")
def ingest_jobs(db: Session = Depends(get_db)):
    primary = RSSJobSource(
        feed_url=settings.job_feed_url
    )


    fallback = FallbackRSSJobSource(
        "data/fallback_jobs.xml"
    )


    source_manager = SourceManager(
        primary=primary,
        fallback=fallback,
    )


    jobs, source_used = source_manager.fetch_jobs()


    service = IngestionService(db)


    result = service.ingest(jobs)


    result["source"] = source_used


    return result
