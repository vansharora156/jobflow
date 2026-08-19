from dataclasses import dataclass
from datetime import datetime




@dataclass
class Job:
    title: str
    company: str
    location: str | None
    description: str | None
    url: str
    published_at: datetime | None
    source: str
