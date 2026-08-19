import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


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

# Mount static directory if available
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")




app.include_router(jobs_router)
app.include_router(health_router)




@app.get("/")
def root():
    return {
        "name": "JobFlow",
        "status": "running",
        "message": "Job ingestion API is online",
        "dashboard_url": "/dashboard",
        "docs_url": "/docs"
    }




@app.get("/dashboard", response_class=FileResponse)
def get_dashboard():
    dashboard_path = os.path.join(static_dir, "dashboard.html")
    return FileResponse(dashboard_path)




@app.get("/health")
def health():
    return {
        "status": "healthy",
    }
