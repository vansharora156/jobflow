import re
import time
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


    def __init__(
        self,
        feed_url: str,
        min_request_interval: float = 5.0,
    ):
        self.feed_url = feed_url
        self.min_request_interval = min_request_interval
        self._last_request_time = 0.0
        self.last_status = "unknown"
        self.last_error = None


    def _wait_for_rate_limit(self):
        elapsed = time.monotonic() - self._last_request_time


        if elapsed < self.min_request_interval and self._last_request_time > 0:
            wait_time = self.min_request_interval - elapsed
            logger.info("Enforcing rate limit interval | waiting %.2fs", wait_time)
            time.sleep(wait_time)


        self._last_request_time = time.monotonic()


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
        self._wait_for_rate_limit()


        logger.info(
            "Fetching RSS feed from %s (timeout=15s, max_retries=3)",
            self.feed_url,
        )


        try:
            response = httpx.get(
                self.feed_url,
                timeout=15.0,
                follow_redirects=True,
            )


            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")


                if retry_after:
                    logger.warning("HTTP 429 Rate limited. Retry-After header: %s seconds", retry_after)
                    time.sleep(float(retry_after))


                raise httpx.HTTPStatusError(
                    "Rate limited by source",
                    request=response.request,
                    response=response,
                )


            response.raise_for_status()


            self.last_status = "healthy"
            self.last_error = None
            return feedparser.parse(response.text)


        except Exception as exc:
            self.last_status = "unhealthy"
            self.last_error = str(exc)
            logger.error("Source request failed | error=%s", exc)
            raise


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
