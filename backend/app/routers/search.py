import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException

from app.models.schemas import SearchRequest, SearchResponse

# ============================================
# IMPORT YOUR EXISTING search.py
# ============================================
# Problem: search.py is in backend/, but we're in backend/app/routers/
# Solution: Add backend/ to Python's path so we can import it
#
# Path(__file__) = this file (search.py in routers/)
# .parent = routers/
# .parent.parent = app/
# .parent.parent.parent = backend/  ← where search.py lives
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))
import search as search_module  # Now we can use search_module.search()

# ============================================
# CREATE THE ROUTER
# ============================================
router = APIRouter()


# ============================================
# SEARCH ENDPOINT
# ============================================
@router.post("/search", response_model=SearchResponse)
def search_hadiths(request: SearchRequest):
    """
    Search hadiths with intelligent query expansion.

    - Supports Arabic, English, Bengali, and Urdu
    - Uses phonetic matching for English transliterations
    - Uses fuzzy matching for spelling variations

    Example request:
    {
        "query": "prayer",
        "limit": 10
    }
    """
    try:
        # Call YOUR existing search() function from search.py
        # This is the wrapper - FastAPI handles HTTP, your code handles logic
        result = search_module.search(
            query=request.query,
            lang=request.lang,
            book_id=request.book_id,
            limit=request.limit,
        )
        return result
    except Exception as e:
        # If something goes wrong, return a 500 error with details
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
