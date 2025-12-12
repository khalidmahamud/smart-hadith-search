from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # App metadata - used in API docs
    APP_NAME: str = "Smart Hadith Search API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database path - points to your existing sqlite.db
    DATABASE_PATH: str = str(
        Path(__file__).parent.parent / "database" / "sqlite.db"
    )

    # CORS - accepts comma-separated string or JSON array from env
    # Example: CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
    CORS_ORIGINS: str = "http://localhost:3000"

    # API versioning
    API_V1_PREFIX: str = "/api/v1"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS as comma-separated list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"


# Create a singleton instance
settings = Settings()
