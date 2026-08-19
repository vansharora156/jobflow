from fastapi import FastAPI


from app.api.jobs import router as jobs_router
from app.api.health import router as health_router
from app.database import Base, engine
from app.models.job_db import JobDB




Base.metadata.create_all(bind=engine)




app = FastAPI(
    title="JobFlow API",
    description="Resilient Job Listing Ingestion Platform",
    version="1.0.0",
)




app.include_router(jobs_router)
app.include_router(health_router)




@app.get("/")
def root():
    return {
        "name": "JobFlow",
        "status": "running",
        "message": "Job ingestion API is online",
    }




@app.get("/health")
def health():
    return {
        "status": "healthy",
    }
