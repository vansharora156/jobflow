from fastapi import APIRouter


router = APIRouter(
    prefix="/sources",
    tags=["Sources"],
)




@router.get("/health")
def source_health():
    return {
        "primary": {
            "name": "we_work_remotely",
            "status": "configured",
        },
        "fallback": {
            "name": "jobflow_sandbox",
            "status": "configured",
        },
    }
