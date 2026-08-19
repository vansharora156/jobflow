import feedparser
from typing import Any


from .base import JobSource




class RSSJobSource(JobSource):


    def __init__(self, feed_url: str):
        self.feed_url = feed_url


    def fetch_jobs(self) -> list[dict[str, Any]]:
        feed = feedparser.parse(self.feed_url)


        jobs = []


        for entry in feed.entries:
            jobs.append({
                "title": entry.get("title"),
                "url": entry.get("link"),
                "description": entry.get("summary"),
                "published_at": entry.get("published"),
            })


        return jobs
