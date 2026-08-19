from datetime import datetime


from pydantic import BaseModel, HttpUrl




class JobCreate(BaseModel):
    title: str
    company: str
    location: str | None = None
    description: str | None = None
    url: HttpUrl
    published_at: datetime | None = None
    source: str




class JobResponse(JobCreate):
    id: int
