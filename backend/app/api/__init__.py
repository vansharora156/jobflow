"""
API Router Package
"""

from fastapi import APIRouter

router = APIRouter()

# Example placeholder endpoint
@router.get("/status")
def status():
    return {"status": "ok", "service": "JobFlow API"}
