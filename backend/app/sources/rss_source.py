import re
from datetime import datetime
from typing import Any


import feedparser
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


from .base import JobSource
from app.services.logger import logger




class RSSJobSource(JobSource):


    def __init__(self, feed_url: str):
        self.feed_url = feed_url


    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(
            multiplier=1,
            min=1,
            max=8,
        ),
        retry=retry_if_exception_type(
            (httpx.TimeoutException, httpx.HTTPError)
        ),
        reraise=True,
    )
    def _fetch_feed(self) -> feedparser.FeedParserDict:
        logger.info(
            "Fetching RSS feed from %s (timeout=15s, max_retries=3)",
            self.feed_url,
        )


        response = httpx.get(
            self.feed_url,
            timeout=15.0,
            follow_redirects=True,
        )


        response.raise_for_status()


        return feedparser.parse(response.text)


    def fetch_jobs(self) -> list[dict[str, Any]]:
        feed = self._fetch_feed()


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
