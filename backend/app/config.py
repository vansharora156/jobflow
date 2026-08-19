from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    job_feed_url: str = "https://weworkremotely.com/remote-jobs.rss"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
