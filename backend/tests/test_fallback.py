from app.sources.fallback_source import FallbackRSSJobSource
from app.services.source_manager import SourceManager


class FailingSource:
    def fetch_jobs(self):
        raise Exception("Primary source blocked or offline")


def test_fallback_source():
    source = FallbackRSSJobSource("data/fallback_jobs.xml")
    jobs = source.fetch_jobs()
    assert len(jobs) == 2
    assert jobs[0]["company"] == "Example Corp"


def test_source_manager_failover():
    primary = FailingSource()
    fallback = FallbackRSSJobSource("data/fallback_jobs.xml")
    manager = SourceManager(primary=primary, fallback=fallback)
    jobs, source_used = manager.fetch_jobs()

    assert source_used == "fallback"
    assert len(jobs) == 2
