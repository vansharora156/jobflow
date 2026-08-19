import feedparser


from app.config import settings




feed = feedparser.parse(settings.job_feed_url)


print("Feed title:")
print(feed.feed.get("title"))


print("\nNumber of entries:")
print(len(feed.entries))


for index, entry in enumerate(feed.entries[:3], start=1):
    print(f"\n--- Entry {index} ---")


    for key, value in entry.items():
        print(f"{key}: {value}")
