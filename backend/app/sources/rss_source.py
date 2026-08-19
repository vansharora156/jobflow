import re
from datetime import datetime
from typing import Any


import feedparser


from .base import JobSource




class RSSJobSource(JobSource):


    def __init__(self, feed_url: str):
        self.feed_url = feed_url


    def fetch_jobs(self) -> list[dict[str, Any]]:
        feed = feedparser.parse(self.feed_url)


        jobs = []


        for entry in feed.entries:
            company, title = self._parse_title(
                entry.get("title", "")
            )


            jobs.append({
                "title": title,
                "company": company,
                "location": entry.get("region"),
                "description": self._clean_html(
                    entry.get("summary")
                ),
                "url": entry.get("link"),
                "published_at": self._parse_date(
                    entry.get("published")
                ),
            })


        return jobs


    @staticmethod
    def _parse_title(value: str) -> tuple[str, str]:
        if ":" in value:
            company, title = value.split(":", 1)


            return (
                company.strip(),
                title.strip(),
            )


        return (
            "Unknown",
            value.strip(),
        )


    @staticmethod
    def _clean_html(value: str | None) -> str | None:
        if not value:
            return None


        return re.sub(
            r"<[^>]+>",
            " ",
            value,
        ).strip()


    @staticmethod
    def _parse_date(value: str | None) -> datetime | None:
        if not value:
            return None


        try:
            parsed = datetime.strptime(
                value,
                "%a, %d %b %Y %H:%M:%S %z",
            )


            return parsed.replace(tzinfo=None)


        except ValueError:
            return None
