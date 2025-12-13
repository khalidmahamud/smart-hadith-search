"""
Hybrid Search Module for Smart Hadith Search

This module implements semantic + full-text hybrid search using:
- pgvector: Vector similarity search (semantic meaning)
- PostgreSQL tsvector: Full-text search (keyword matching)
- RRF (Reciprocal Rank Fusion): Combines both rankings

How it works:
1. User enters a query (e.g., "patience in hardship")
2. Query is converted to an embedding vector
3. Two parallel searches run:
   - Semantic: Find hadiths with similar embeddings
   - Full-text: Find hadiths containing the keywords
4. Results are combined using RRF for final ranking
"""

import re
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.services.embeddings import generate_embedding


def detect_language(query: str) -> str:
    """
    Detect the primary language of a query.

    Uses Unicode ranges to identify scripts:
    - Arabic: U+0600-U+06FF
    - Bengali: U+0980-U+09FF
    - Default: English

    Args:
        query: User's search query

    Returns:
        Language code: 'ar', 'bn', or 'en'
    """
    if re.search(r"[\u0600-\u06FF]", query):
        # Could be Arabic or Urdu (both use Arabic script)
        if re.search(r"[\u0980-\u09FF]", query):
            return "bn"
        return "ar"
    if re.search(r"[\u0980-\u09FF]", query):
        return "bn"
    return "en"


async def hybrid_search(
    db: AsyncSession,
    query: str,
    book_id: int | None = None,
    limit: int = 20,
) -> dict:
    """
    Perform hybrid search combining semantic and full-text search.

    This is the main search function that:
    1. Generates an embedding for the query
    2. Calls the hybrid_search SQL function
    3. Fetches full hadith details for the results

    Args:
        db: Async database session
        query: User's search query
        book_id: Optional filter by book
        limit: Maximum results to return

    Returns:
        Dictionary with query info and ranked results
    """
    query = query.strip()
    if not query:
        return {"query": "", "query_lang": "en", "count": 0, "results": []}

    query_lang = detect_language(query)

    # Generate embedding for semantic search
    query_embedding = generate_embedding(query)

    if not query_embedding:
        # Fallback to full-text only if embedding fails
        return await fulltext_search(db, query, book_id, limit, query_lang)

    # Format embedding as PostgreSQL array string
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    # Call the hybrid_search function we defined in PostgreSQL
    # Note: We embed the vector string directly since SQLAlchemy has issues with ::vector cast
    sql = text(f"""
        WITH ranked AS (
            SELECT hadith_id, score
            FROM hybrid_search(
                :query_text,
                '{embedding_str}'::vector,
                :match_count,
                :fulltext_weight,
                :semantic_weight,
                :rrf_k,
                :book_id
            )
        )
        SELECT
            h.hadith_id,
            h.book_id,
            h.chapter_id,
            h.hadith_number,
            h.grade_id,
            h.en_text,
            h.ar_text,
            h.bn_text,
            h.ur_text,
            h.en_narrator,
            h.ar_narrator,
            h.bn_narrator,
            h.ur_narrator,
            b.en_title as book_title,
            b.bn_title as book_title_bn,
            b.slug as book_slug,
            g.en_text as grade_text,
            g.bn_text as grade_text_bn,
            r.score
        FROM ranked r
        JOIN hadiths h ON h.hadith_id = r.hadith_id
        JOIN books b ON b.book_id = h.book_id
        LEFT JOIN grades g ON g.grade_id = h.grade_id
        ORDER BY r.score DESC
    """)

    result = await db.execute(sql, {
        "query_text": query,
        "match_count": limit,
        "fulltext_weight": settings.FULLTEXT_WEIGHT,
        "semantic_weight": settings.SEMANTIC_WEIGHT,
        "rrf_k": settings.RRF_K,
        "book_id": book_id,
    })

    rows = [dict(row._mapping) for row in result.fetchall()]

    return {
        "query": query,
        "query_lang": query_lang,
        "count": len(rows),
        "results": rows,
    }


async def semantic_search(
    db: AsyncSession,
    query: str,
    book_id: int | None = None,
    limit: int = 20,
) -> dict:
    """
    Pure semantic search (embedding similarity only).

    Use this when you want meaning-based search without keyword matching.
    Useful for conceptual queries like "being kind to parents".

    Args:
        db: Async database session
        query: User's search query
        book_id: Optional filter by book
        limit: Maximum results to return

    Returns:
        Dictionary with query info and ranked results
    """
    query = query.strip()
    if not query:
        return {"query": "", "query_lang": "en", "count": 0, "results": []}

    query_lang = detect_language(query)
    query_embedding = generate_embedding(query)

    if not query_embedding:
        return {"query": query, "query_lang": query_lang, "count": 0, "results": []}

    # Format embedding as PostgreSQL array string
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    sql = text(f"""
        WITH ranked AS (
            SELECT hadith_id, similarity
            FROM semantic_search(
                '{embedding_str}'::vector,
                :match_count,
                :book_id
            )
        )
        SELECT
            h.hadith_id,
            h.book_id,
            h.chapter_id,
            h.hadith_number,
            h.grade_id,
            h.en_text,
            h.ar_text,
            h.bn_text,
            h.ur_text,
            h.en_narrator,
            h.ar_narrator,
            h.bn_narrator,
            h.ur_narrator,
            b.en_title as book_title,
            b.bn_title as book_title_bn,
            b.slug as book_slug,
            g.en_text as grade_text,
            g.bn_text as grade_text_bn,
            r.similarity as score
        FROM ranked r
        JOIN hadiths h ON h.hadith_id = r.hadith_id
        JOIN books b ON b.book_id = h.book_id
        LEFT JOIN grades g ON g.grade_id = h.grade_id
        ORDER BY r.similarity DESC
    """)

    result = await db.execute(sql, {
        "match_count": limit,
        "book_id": book_id,
    })

    rows = [dict(row._mapping) for row in result.fetchall()]

    return {
        "query": query,
        "query_lang": query_lang,
        "count": len(rows),
        "results": rows,
    }


async def fulltext_search(
    db: AsyncSession,
    query: str,
    book_id: int | None = None,
    limit: int = 20,
    query_lang: str = "en",
) -> dict:
    """
    Pure full-text search (keyword matching only).

    Fallback when embedding generation fails or for exact phrase matching.

    Args:
        db: Async database session
        query: User's search query
        book_id: Optional filter by book
        limit: Maximum results to return
        query_lang: Detected query language

    Returns:
        Dictionary with query info and ranked results
    """
    # Choose the appropriate tsvector column based on language
    fts_column = "fts_ar" if query_lang == "ar" else "fts_en"
    ts_config = "simple" if query_lang == "ar" else "english"

    sql = text(f"""
        SELECT
            h.hadith_id,
            h.book_id,
            h.chapter_id,
            h.hadith_number,
            h.grade_id,
            h.en_text,
            h.ar_text,
            h.bn_text,
            h.ur_text,
            h.en_narrator,
            h.ar_narrator,
            h.bn_narrator,
            h.ur_narrator,
            b.en_title as book_title,
            b.bn_title as book_title_bn,
            b.slug as book_slug,
            g.en_text as grade_text,
            g.bn_text as grade_text_bn,
            ts_rank_cd(h.{fts_column}, plainto_tsquery('{ts_config}', :query)) as score
        FROM hadiths h
        JOIN books b ON b.book_id = h.book_id
        LEFT JOIN grades g ON g.grade_id = h.grade_id
        WHERE h.{fts_column} @@ plainto_tsquery('{ts_config}', :query)
          AND (:book_id IS NULL OR h.book_id = :book_id)
        ORDER BY score DESC
        LIMIT :limit
    """)

    result = await db.execute(sql, {
        "query": query,
        "book_id": book_id,
        "limit": limit,
    })

    rows = [dict(row._mapping) for row in result.fetchall()]

    return {
        "query": query,
        "query_lang": query_lang,
        "count": len(rows),
        "results": rows,
    }


async def get_hadith(db: AsyncSession, hadith_id: int) -> dict | None:
    """
    Get a single hadith by ID with full details.

    Args:
        db: Async database session
        hadith_id: The hadith's primary key

    Returns:
        Dictionary with hadith details or None if not found
    """
    sql = text("""
        SELECT
            h.*,
            b.en_title as book_title,
            b.bn_title as book_title_bn,
            b.slug as book_slug,
            c.en_title as chapter_title,
            c.bn_title as chapter_title_bn,
            g.en_text as grade_text,
            g.bn_text as grade_text_bn
        FROM hadiths h
        JOIN books b ON b.book_id = h.book_id
        JOIN chapters c ON c.chapter_id = h.chapter_id
        LEFT JOIN grades g ON g.grade_id = h.grade_id
        WHERE h.hadith_id = :hadith_id
    """)

    result = await db.execute(sql, {"hadith_id": hadith_id})
    row = result.fetchone()

    if row:
        row_dict = dict(row._mapping)
        # Remove the embedding from response (too large, not needed)
        row_dict.pop("embedding", None)
        row_dict.pop("fts_en", None)
        row_dict.pop("fts_ar", None)
        return row_dict
    return None


async def get_book_hadiths(
    db: AsyncSession,
    book_id: int,
    chapter_id: int | None = None,
    page: int = 1,
    per_page: int = 50,
) -> dict:
    """
    Get hadiths by book with pagination.

    Args:
        db: Async database session
        book_id: Book to fetch from
        chapter_id: Optional chapter filter
        page: Page number (1-indexed)
        per_page: Results per page

    Returns:
        Dictionary with paginated results and metadata
    """
    offset = (page - 1) * per_page

    # Count total
    count_sql = text("""
        SELECT COUNT(*)
        FROM hadiths h
        WHERE h.book_id = :book_id
          AND (:chapter_id IS NULL OR h.chapter_id = :chapter_id)
    """)
    count_result = await db.execute(count_sql, {
        "book_id": book_id,
        "chapter_id": chapter_id,
    })
    total = count_result.scalar()

    # Fetch page
    sql = text("""
        SELECT
            h.hadith_id,
            h.book_id,
            h.chapter_id,
            h.hadith_number,
            h.grade_id,
            h.en_text,
            h.ar_text,
            h.bn_text,
            h.ur_text,
            h.en_narrator,
            h.ar_narrator,
            h.bn_narrator,
            h.ur_narrator,
            g.en_text as grade_text,
            g.bn_text as grade_text_bn
        FROM hadiths h
        LEFT JOIN grades g ON g.grade_id = h.grade_id
        WHERE h.book_id = :book_id
          AND (:chapter_id IS NULL OR h.chapter_id = :chapter_id)
        ORDER BY h.hadith_number
        LIMIT :limit OFFSET :offset
    """)

    result = await db.execute(sql, {
        "book_id": book_id,
        "chapter_id": chapter_id,
        "limit": per_page,
        "offset": offset,
    })

    rows = [dict(row._mapping) for row in result.fetchall()]

    return {
        "results": rows,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page if total else 0,
    }
