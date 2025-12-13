"""
Search Router - Handles search endpoints

Updated for semantic + full-text hybrid search using PostgreSQL + pgvector.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db_session
from app.models.schemas import SearchRequest, SearchResponse
import search as search_module

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search_hadiths(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Search hadiths using hybrid semantic + keyword search.

    The search combines:
    - **Semantic search**: Understands meaning (e.g., "patience" finds hadiths about "sabr")
    - **Full-text search**: Matches exact keywords
    - **RRF fusion**: Combines both rankings for best results

    Supports Arabic, English, Bengali, and Urdu queries.

    Example request:
    ```json
    {
        "query": "patience in hardship",
        "limit": 10
    }
    ```
    """
    try:
        result = await search_module.hybrid_search(
            db=db,
            query=request.query,
            book_id=request.book_id,
            limit=request.limit,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
