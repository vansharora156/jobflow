from datetime import datetime
import feedparser


from .base import JobSource




class FallbackRSSJobSource(JobSource):


    def __init__(self, feed_path: str):
        self.feed_path = feed_path


    def fetch_jobs(self):
        feed = feedparser.parse(self.feed_path)


        jobs = []


        for entry in feed.entries:
            title = entry.get("title", "")


            if ":" in title:
                company, job_title = title.split(":", 1)
            else:
                company = "Unknown"
                job_title = title


            published_at = self._parse_date(entry.get("published"))


            jobs.append({
                "title": job_title.strip(),
                "company": company.strip(),
                "location": entry.get("region"),
                "description": entry.get("description"),
                "url": entry.get("link"),
                "published_at": published_at,
            })


        return jobs


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
