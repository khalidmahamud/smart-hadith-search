from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # App metadata - used in API docs
    APP_NAME: str = "Smart Hadith Search API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Legacy SQLite path (kept for migration script)
    DATABASE_PATH: str = str(
        Path(__file__).parent.parent / "database" / "sqlite.db"
    )

    # Supabase PostgreSQL connection
    # Format: postgresql+asyncpg://postgres:[PASSWORD]@db.[PROJECT].supabase.co:6543/postgres
    SUPABASE_DB_URL: str = ""

    # Embedding model configuration
    # Model: paraphrase-multilingual-MiniLM-L12-v2 (supports Arabic, Bengali, Urdu, English)
    EMBEDDING_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_DIM: int = 384  # Output dimensions of the model

    # Hybrid search tuning (Reciprocal Rank Fusion)
    # Higher weight = more influence on final ranking
    SEMANTIC_WEIGHT: float = 1.0   # Weight for semantic/embedding search
    FULLTEXT_WEIGHT: float = 1.0   # Weight for keyword/full-text search
    RRF_K: int = 60  # RRF constant (default 60, higher = more uniform blending)

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
