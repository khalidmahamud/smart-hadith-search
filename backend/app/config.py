from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # App metadata - used in API docs
    APP_NAME: str = "Smart Hadith Search API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database path - points to your existing sqlite.db
    # Path(__file__) = this config.py file
    # .parent.parent = go up 2 levels (app/ -> backend/)
    # Then into database/sqlite.db
    DATABASE_PATH: str = str(
        Path(__file__).parent.parent / "database" / "sqlite.db"
    )

    # CORS (Cross-Origin Resource Sharing)
    # Your Next.js frontend runs on localhost:3000
    # Without this, browsers block the frontend from calling localhost:8000
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # API versioning - all endpoints will be /api/v1/...
    # Later you can add /api/v2/ without breaking existing clients
    API_V1_PREFIX: str = "/api/v1"

    class Config:
        env_file = ".env"  # Optionally load from .env file


# Create a singleton instance - import this everywhere
settings = Settings()
