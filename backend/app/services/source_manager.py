from app.services.logger import logger




class SourceManager:


    def __init__(self, primary, fallback):
        self.primary = primary
        self.fallback = fallback


    def fetch_jobs(self):
        try:
            jobs = self.primary.fetch_jobs()


            if jobs:
                logger.info(
                    "Primary source succeeded: %d jobs",
                    len(jobs),
                )


                return jobs, "primary"


            logger.warning(
                "Primary source returned no jobs; using fallback"
            )


        except Exception as exc:
            logger.error(
                "Primary source failed: %s",
                exc,
            )


        jobs = self.fallback.fetch_jobs()


        logger.info(
            "Fallback source returned %d jobs",
            len(jobs),
        )


        return jobs, "fallback"
