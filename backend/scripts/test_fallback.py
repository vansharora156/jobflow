from app.sources.fallback_source import FallbackRSSJobSource




source = FallbackRSSJobSource(
    "data/fallback_jobs.xml"
)


jobs = source.fetch_jobs()


print(f"Fetched {len(jobs)} fallback jobs\n")


for job in jobs:
    print(job)
