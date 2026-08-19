from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session


from app.database import get_db
from app.services.ingestion import IngestionService
from app.sources.rss_source import RSSJobSource




router = APIRouter(prefix="/jobs", tags=["Jobs"])




@router.get("/count")
def get_job_count(db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT COUNT(*) FROM jobs")
    )


    count = result.scalar()


    return {
        "job_count": count
    }




@router.post("/ingest")
def ingest_jobs(db: Session = Depends(get_db)):
    source = RSSJobSource(
        feed_url="YOUR_FEED_URL_HERE"
    )


    service = IngestionService(
        db=db,
        source=source,
    )


    return service.ingest()
