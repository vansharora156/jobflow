from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


from app.models.job_db import JobDB
from app.sources.rss_source import RSSJobSource




class IngestionService:


    def __init__(self, db: Session, source: RSSJobSource):
        self.db = db
        self.source = source


    def ingest(self) -> dict:
        jobs = self.source.fetch_jobs()


        inserted = 0
        duplicates = 0
        failed = 0


        for job in jobs:
            try:
                published_at = self._parse_date(
                    job.get("published_at")
                )


                job_record = JobDB(
                    title=job.get("title") or "Unknown",
                    company=job.get("company") or "Unknown",
                    location=job.get("location"),
                    description=job.get("description"),
                    url=job.get("url"),
                    published_at=published_at,
                    source="rss",
                )


                self.db.add(job_record)
                self.db.commit()


                inserted += 1


            except IntegrityError:
                self.db.rollback()
                duplicates += 1


            except Exception:
                self.db.rollback()
                failed += 1


        return {
            "fetched": len(jobs),
            "inserted": inserted,
            "duplicates": duplicates,
            "failed": failed,
        }


    @staticmethod
    def _parse_date(value: str | None) -> datetime | None:
        if not value:
            return None


        try:
            return datetime.strptime(
                value,
                "%a, %d %b %Y %H:%M:%S %z",
            )
        except ValueError:
            return None
