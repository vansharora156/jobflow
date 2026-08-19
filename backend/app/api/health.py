from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.job_db import JobDB


router = APIRouter(
    prefix="/sources",
    tags=["Sources"],
)


# Global status tracker for last ingestion run
last_ingestion_status = {
    "last_run": None,
    "last_source": None,
    "last_result": None,
    "primary_status": "healthy",
    "primary_error": None,
}


@router.get("/health")
def source_health(db: Session = Depends(get_db)):
    total_jobs = db.execute(text("SELECT COUNT(*) FROM jobs")).scalar() or 0
    latest_job = db.scalars(select(JobDB).order_by(JobDB.created_at.desc()).limit(1)).first()

    return {
        "primary": {
            "name": "We Work Remotely RSS",
            "url": "https://weworkremotely.com/remote-jobs.rss",
            "status": last_ingestion_status["primary_status"],
            "last_error": last_ingestion_status["primary_error"],
        },
        "fallback": {
            "name": "JobFlow Sandbox XML",
            "status": "available",
        },
        "stats": {
            "total_jobs_in_db": total_jobs,
            "last_ingested_at": latest_job.created_at.isoformat() if latest_job else None,
            "last_run_details": last_ingestion_status["last_result"],
        }
    }
