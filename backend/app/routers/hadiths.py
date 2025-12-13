"""
Hadiths Router - Get individual hadith details

Updated for async PostgreSQL access.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db_session
from app.models.schemas import HadithDetail
import search as search_module

router = APIRouter()


@router.get("/hadiths/{hadith_id}", response_model=HadithDetail)
async def get_hadith(
    hadith_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get a single hadith by ID with full details.

    Returns all translations (Arabic, English, Bengali, Urdu),
    narrator chains, book info, chapter info, and grade.
    """
    result = await search_module.get_hadith(db, hadith_id)

    if result is None:
        raise HTTPException(
            status_code=404, detail=f"Hadith {hadith_id} not found"
        )

    return result
