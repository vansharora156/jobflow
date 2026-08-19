from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.services.ingestion import IngestionService
from app.models.job_db import JobDB


def test_ingestion_and_deduplication():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    sample_jobs = [
        {
            "title": "Python Engineer",
            "company": "Tech Corp",
            "location": "Remote",
            "description": "Building APIs",
            "url": "https://example.com/job/1",
            "published_at": None,
        },
        {
            "title": "Python Engineer",
            "company": "Tech Corp",
            "location": "Remote",
            "description": "Building APIs",
            "url": "https://example.com/job/1",  # Duplicate URL
            "published_at": None,
        },
    ]

    service = IngestionService(db)
    result = service.ingest(sample_jobs)

    assert result["fetched"] == 2
    assert result["inserted"] == 1
    assert result["duplicates"] == 1
    assert result["failed"] == 0

    count = db.query(JobDB).count()
    assert count == 1
    db.close()
