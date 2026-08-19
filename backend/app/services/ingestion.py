from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


from app.models.job_db import JobDB
from app.services.logger import logger




class IngestionService:


    def __init__(
        self,
        db: Session,
    ):
        self.db = db


    def ingest(self, jobs: list[dict]) -> dict:
        logger.info(
            "Starting ingestion of %d jobs",
            len(jobs),
        )


        inserted = 0
        duplicates = 0
        failed = 0


        for job in jobs:
            savepoint = self.db.begin_nested()
            try:
                job_record = JobDB(
                    title=job.get("title") or "Unknown",
                    company=job.get("company") or "Unknown",
                    location=job.get("location"),
                    description=job.get("description"),
                    url=job.get("url"),
                    published_at=job.get("published_at"),
                    source="weworkremotely",
                )


                self.db.add(job_record)
                self.db.flush()
                savepoint.commit()


                inserted += 1


            except IntegrityError:
                savepoint.rollback()
                duplicates += 1


            except Exception as exc:
                savepoint.rollback()
                logger.error("Failed to ingest job item: %s", exc)
                failed += 1


        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise


        logger.info(
            "Ingestion completed | fetched=%d inserted=%d duplicates=%d failed=%d",
            len(jobs),
            inserted,
            duplicates,
            failed,
        )


        return {
            "fetched": len(jobs),
            "inserted": inserted,
            "duplicates": duplicates,
            "failed": failed,
        }
