from fastapi import APIRouter, Depends
from sqlalchemy import select, text
from sqlalchemy.orm import Session


from app.config import settings
from app.database import get_db
from app.models.job_db import JobDB
from app.services.ingestion import IngestionService
from app.sources.rss_source import RSSJobSource




router = APIRouter(prefix="/jobs", tags=["Jobs"])




@router.get("/")
def get_jobs(
    db: Session = Depends(get_db),
    limit: int = 20,
):
    statement = (
        select(JobDB)
        .order_by(JobDB.published_at.desc())
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




@router.post("/ingest")
def ingest_jobs(db: Session = Depends(get_db)):
    source = RSSJobSource(
        feed_url=settings.job_feed_url
    )


    service = IngestionService(
        db=db,
        source=source,
    )


    return service.ingest()
