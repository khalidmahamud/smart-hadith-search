from pydantic_settings import BaseSettings
from pathlib import Path
import os


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
    # Set CORS_ORIGINS env var as comma-separated list for production
    # Example: CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        # Production origins will be added via environment variable
    ]

    # API versioning - all endpoints will be /api/v1/...
    # Later you can add /api/v2/ without breaking existing clients
    API_V1_PREFIX: str = "/api/v1"

    class Config:
        env_file = ".env"  # Optionally load from .env file

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parse CORS_ORIGINS from environment if set as comma-separated string
        cors_env = os.getenv("CORS_ORIGINS")
        if cors_env:
            self.CORS_ORIGINS = [origin.strip() for origin in cors_env.split(",")]


# Create a singleton instance - import this everywhere
settings = Settings()
