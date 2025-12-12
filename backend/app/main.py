from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import search, hadiths, books

# ============================================
# CREATE THE FASTAPI APPLICATION
# ============================================
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Search 26,742 hadiths in Arabic, English, Bengali, and Urdu",
    # These URLs are where the auto-generated docs live:
    docs_url="/docs",  # Swagger UI - interactive API testing
    redoc_url="/redoc",  # ReDoc - prettier documentation
)

# ============================================
# CONFIGURE CORS MIDDLEWARE
# ============================================
# CORS = Cross-Origin Resource Sharing
#
# Problem: Browsers block requests from one domain to another by default
# Example: localhost:3000 (Next.js) → localhost:8000 (FastAPI) = BLOCKED!
#
# Solution: Tell FastAPI which domains are allowed to call us
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # Parsed from comma-separated env var
    allow_credentials=True,  # Allow cookies/auth headers
    allow_methods=["GET", "POST"],  # Which HTTP methods to allow
    allow_headers=["*"],  # Allow all headers
)

# ============================================
# MOUNT ROUTERS
# ============================================
# Each router handles a group of related endpoints
# prefix="/api/v1" means all routes get this prefix:
#   - search.router has "/search" → becomes "/api/v1/search"
#   - hadiths.router has "/hadiths/{id}" → becomes "/api/v1/hadiths/{id}"
#
# tags are for grouping in the /docs UI
app.include_router(
    search.router, prefix=settings.API_V1_PREFIX, tags=["Search"]
)
app.include_router(
    hadiths.router, prefix=settings.API_V1_PREFIX, tags=["Hadiths"]
)
app.include_router(books.router, prefix=settings.API_V1_PREFIX, tags=["Books"])


# ============================================
# HEALTH CHECK ENDPOINT
# ============================================
# This is a simple endpoint to check if the API is running
# and can connect to the database. Useful for:
# - Deployment health checks (Render pings this)
# - Monitoring services
# - Quick debugging
@app.get("/health", tags=["Health"])
def health_check():
    """Check if API and database are working"""
    import sys
    from pathlib import Path

    # Add backend directory to path so we can import search.py
    backend_path = Path(__file__).parent.parent
    sys.path.insert(0, str(backend_path))
    from search import get_db

    try:
        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM hadiths")
        count = cur.fetchone()[0]
        con.close()
        return {
            "status": "healthy",
            "database": "connected",
            "total_hadiths": count,
        }
    except Exception as e:
        return {"status": "unhealthy", "database": "error", "error": str(e)}
