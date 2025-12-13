"""
Smart Hadith Search API

FastAPI application with hybrid semantic + keyword search.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.db import async_session_maker
from app.routers import search, hadiths, books


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    Startup:
    - Pre-load the embedding model (~440MB) so first search is fast
    - Model stays in memory for the lifetime of the app

    Shutdown:
    - Clean up resources
    """
    # Startup: Load embedding model into memory
    print("Starting up Smart Hadith Search API...")
    print("Loading embedding model (this may take a moment on first run)...")

    from app.services.embeddings import get_embedding_model
    model = get_embedding_model()
    print(f"Embedding model loaded: {settings.EMBEDDING_MODEL}")
    print(f"Embedding dimension: {model.get_sentence_embedding_dimension()}")

    yield  # App is running

    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Search 26,742 hadiths using semantic + keyword hybrid search. "
                "Supports Arabic, English, Bengali, and Urdu.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(
    search.router, prefix=settings.API_V1_PREFIX, tags=["Search"]
)
app.include_router(
    hadiths.router, prefix=settings.API_V1_PREFIX, tags=["Hadiths"]
)
app.include_router(
    books.router, prefix=settings.API_V1_PREFIX, tags=["Books"]
)


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Check if API and database are working.

    Used by deployment platforms for health monitoring.
    """
    try:
        async with async_session_maker() as session:
            result = await session.execute(text("SELECT COUNT(*) FROM hadiths"))
            count = result.scalar()
            return {
                "status": "healthy",
                "database": "connected",
                "total_hadiths": count,
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e),
        }
