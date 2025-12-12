import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException

from app.models.schemas import HadithDetail

# Import your existing search.py module
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))
import search as search_module

router = APIRouter()


@router.get("/hadiths/{hadith_id}", response_model=HadithDetail)
def get_hadith(hadith_id: int):
    """
    Get a single hadith by ID with full details.

    Returns all translations (Arabic, English, Bengali, Urdu),
    narrator chains, book info, chapter info, and grade.
    """
    # Call your existing get_hadith() function
    result = search_module.get_hadith(hadith_id)

    # If hadith doesn't exist, return 404 Not Found
    if result is None:
        raise HTTPException(
            status_code=404, detail=f"Hadith {hadith_id} not found"
        )

    return result
