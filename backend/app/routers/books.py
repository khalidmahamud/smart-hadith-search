import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import (
    BooksResponse,
    Book,
    ChaptersResponse,
    PaginatedHadiths,
)

# Import your existing search.py module
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))
import search as search_module

router = APIRouter()


# ============================================
# GET /books - List all books
# ============================================
@router.get("/books", response_model=BooksResponse)
def get_books():
    """
    List all hadith books with hadith counts.

    Returns: Sahih Bukhari, Sunan an-Nasa'i, etc.
    """
    con = search_module.get_db()
    cur = con.cursor()

    # This query wasn't in search.py, so we write it here
    # LEFT JOIN ensures books with 0 hadiths still appear
    # GROUP BY aggregates the COUNT per book
    cur.execute(
        """
        SELECT b.*, COUNT(h.hadith_id) as hadith_count
        FROM books b
        LEFT JOIN hadiths h ON h.book_id = b.book_id
        GROUP BY b.book_id
        ORDER BY b.book_id
    """
    )

    books = [dict(row) for row in cur.fetchall()]
    con.close()

    return {"books": books}


# ============================================
# GET /books/{book_id} - Get single book
# ============================================
@router.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    """Get a single book by ID with hadith count."""
    con = search_module.get_db()
    cur = con.cursor()

    cur.execute(
        """
        SELECT b.*, COUNT(h.hadith_id) as hadith_count
        FROM books b
        LEFT JOIN hadiths h ON h.book_id = b.book_id
        WHERE b.book_id = ?
        GROUP BY b.book_id
    """,
        (book_id,),
    )

    row = cur.fetchone()
    con.close()

    if row is None:
        raise HTTPException(
            status_code=404, detail=f"Book {book_id} not found"
        )

    return dict(row)


# ============================================
# GET /books/{book_id}/chapters - List chapters
# ============================================
@router.get("/books/{book_id}/chapters", response_model=ChaptersResponse)
def get_chapters(book_id: int):
    """
    List all chapters in a book with hadith counts.

    Chapters are ordered by order_index for proper display.
    """
    con = search_module.get_db()
    cur = con.cursor()

    cur.execute(
        """
        SELECT c.*, COUNT(h.hadith_id) as hadith_count
        FROM chapters c
        LEFT JOIN hadiths h ON h.chapter_id = c.chapter_id
        WHERE c.book_id = ?
        GROUP BY c.chapter_id
        ORDER BY c.order_index
    """,
        (book_id,),
    )

    chapters = [dict(row) for row in cur.fetchall()]
    con.close()

    return {"book_id": book_id, "chapters": chapters}


# ============================================
# GET /books/{book_id}/hadiths - Paginated hadiths
# ============================================
@router.get("/books/{book_id}/hadiths", response_model=PaginatedHadiths)
def get_book_hadiths(
    book_id: int,
    # Query parameters with defaults and validation
    chapter_id: int = Query(None, description="Filter by chapter ID"),
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    per_page: int = Query(
        50, ge=1, le=100, description="Items per page (max 100)"
    ),
):
    """
    Get hadiths from a book with pagination.

    Use chapter_id to filter by specific chapter.
    Pagination prevents loading thousands of hadiths at once.
    """
    # This wraps your existing get_book_hadiths() function
    result = search_module.get_book_hadiths(
        book_id=book_id, chapter_id=chapter_id, page=page, per_page=per_page
    )
    return result
