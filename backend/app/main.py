from fastapi import FastAPI


app = FastAPI(
    title="JobFlow API",
    description="Resilient Job Listing Ingestion Platform",
    version="1.0.0",
)




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
        "status": "healthy"
    }
