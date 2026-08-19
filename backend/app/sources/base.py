from abc import ABC, abstractmethod
from typing import Any




class JobSource(ABC):


    @abstractmethod
    def fetch_jobs(self) -> list[dict[str, Any]]:
        """Fetch jobs from the source."""
        raise NotImplementedError
