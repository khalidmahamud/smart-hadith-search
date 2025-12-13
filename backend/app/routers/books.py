"""
Books Router - Browse hadith collections

Updated for async PostgreSQL access.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db_session
from app.models.schemas import (
    BooksResponse,
    Book,
    ChaptersResponse,
    PaginatedHadiths,
)
import search as search_module

router = APIRouter()


@router.get("/books", response_model=BooksResponse)
async def get_books(db: AsyncSession = Depends(get_db_session)):
    """
    List all hadith books with hadith counts.

    Returns: Sahih Bukhari, Sunan an-Nasa'i, etc.
    """
    sql = text("""
        SELECT b.*, COUNT(h.hadith_id) as hadith_count
        FROM books b
        LEFT JOIN hadiths h ON h.book_id = b.book_id
        GROUP BY b.book_id
        ORDER BY b.book_id
    """)

    result = await db.execute(sql)
    books = [dict(row._mapping) for row in result.fetchall()]

    return {"books": books}


@router.get("/books/{book_id}", response_model=Book)
async def get_book(
    book_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """Get a single book by ID with hadith count."""
    sql = text("""
        SELECT b.*, COUNT(h.hadith_id) as hadith_count
        FROM books b
        LEFT JOIN hadiths h ON h.book_id = b.book_id
        WHERE b.book_id = :book_id
        GROUP BY b.book_id
    """)

    result = await db.execute(sql, {"book_id": book_id})
    row = result.fetchone()

    if row is None:
        raise HTTPException(
            status_code=404, detail=f"Book {book_id} not found"
        )

    return dict(row._mapping)


@router.get("/books/{book_id}/chapters", response_model=ChaptersResponse)
async def get_chapters(
    book_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """
    List all chapters in a book with hadith counts.

    Chapters are ordered by order_index for proper display.
    """
    sql = text("""
        SELECT c.*, COUNT(h.hadith_id) as hadith_count
        FROM chapters c
        LEFT JOIN hadiths h ON h.chapter_id = c.chapter_id
        WHERE c.book_id = :book_id
        GROUP BY c.chapter_id
        ORDER BY c.order_index
    """)

    result = await db.execute(sql, {"book_id": book_id})
    chapters = [dict(row._mapping) for row in result.fetchall()]

    return {"book_id": book_id, "chapters": chapters}


@router.get("/books/{book_id}/hadiths", response_model=PaginatedHadiths)
async def get_book_hadiths(
    book_id: int,
    db: AsyncSession = Depends(get_db_session),
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
    result = await search_module.get_book_hadiths(
        db=db,
        book_id=book_id,
        chapter_id=chapter_id,
        page=page,
        per_page=per_page,
    )
    return result
