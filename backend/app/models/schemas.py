from pydantic import BaseModel, Field
from typing import Optional

# ============================================
# REQUEST MODELS - What clients send TO us
# ============================================


class SearchRequest(BaseModel):
    """
    Request body for POST /search

    Example JSON:
    {
        "query": "prayer",
        "book_id": 1,
        "limit": 10
    }
    """

    # Field(...) means REQUIRED (the ... is Python's Ellipsis)
    # min_length=2 prevents single-character searches
    query: str = Field(
        ..., min_length=2, max_length=500, description="Search query"
    )

    # Optional fields - can be None or omitted
    # pattern validates against regex: only en, ar, bn, ur allowed
    lang: Optional[str] = Field(
        None, pattern="^(en|ar|bn|ur)$", description="Filter by language"
    )

    # ge=1 means "greater than or equal to 1"
    book_id: Optional[int] = Field(None, ge=1, description="Filter by book ID")

    # Default value of 20, must be between 1 and 100
    limit: int = Field(20, ge=1, le=100, description="Max results to return")


# ============================================
# RESPONSE MODELS - What we send BACK
# ============================================


class QueryExpansion(BaseModel):
    """Shows how the search query was expanded by phonetic/fuzzy matching"""

    original: list[str]  # Original query words
    expanded: list[str]  # Expanded terms (includes fuzzy matches)
    language: str  # Detected language


class HadithResult(BaseModel):
    """Single hadith in search results"""

    hadith_id: int
    book_id: int
    chapter_id: int
    hadith_number: int
    grade_id: Optional[int]  # Some hadiths don't have grades
    en_text: Optional[str]  # English translation (may be missing)
    ar_text: str  # Arabic is always present
    bn_text: Optional[str]  # Bengali
    ur_text: Optional[str]  # Urdu
    en_narrator: Optional[str]
    ar_narrator: Optional[str]
    bn_narrator: Optional[str]
    book_title: str
    book_title_bn: Optional[str]
    book_slug: str
    grade_text: Optional[str]
    grade_text_bn: Optional[str]
    score: float  # BM25 relevance score from FTS5


class SearchResponse(BaseModel):
    """Complete response from POST /search"""

    query: str  # Echo back the original query
    query_lang: str  # Detected language
    expansion: QueryExpansion  # How query was expanded
    count: int  # Number of results
    results: list[HadithResult]  # The actual hadiths


class HadithDetail(BaseModel):
    """Full hadith details for GET /hadiths/{id}"""

    hadith_id: int
    book_id: int
    chapter_id: int
    hadith_number: int
    grade_id: Optional[int]
    ar_text: str
    ar_narrator: Optional[str]
    en_text: Optional[str]
    en_narrator: Optional[str]
    bn_text: Optional[str]
    bn_narrator: Optional[str]
    ur_text: Optional[str]
    ur_narrator: Optional[str]
    book_title: str
    book_slug: str
    chapter_title: str
    grade_text: Optional[str]


class Book(BaseModel):
    """Book info with hadith count"""

    book_id: int
    slug: str  # URL-friendly name like "sahih-bukhari"
    en_title: str
    ar_title: Optional[str]
    bn_title: Optional[str]
    ur_title: Optional[str]
    description: Optional[str]
    hadith_count: int  # Total hadiths in this book


class BooksResponse(BaseModel):
    """Response from GET /books"""

    books: list[Book]


class Chapter(BaseModel):
    """Chapter info with hadith count"""

    chapter_id: int
    order_index: int  # For sorting chapters
    en_title: Optional[str]
    ar_title: Optional[str]
    bn_title: Optional[str]
    ur_title: Optional[str]
    hadith_count: int


class ChaptersResponse(BaseModel):
    """Response from GET /books/{id}/chapters"""

    book_id: int
    chapters: list[Chapter]


class HadithListItem(BaseModel):
    """Hadith item for list/browse views (simpler, no joined fields)"""
    hadith_id: int
    book_id: int
    chapter_id: int
    hadith_number: int
    grade_id: Optional[int]
    ar_text: str
    ar_narrator: Optional[str]
    en_text: Optional[str]
    en_narrator: Optional[str]
    bn_text: Optional[str]
    bn_narrator: Optional[str]
    ur_text: Optional[str]
    ur_narrator: Optional[str]
    grade_text: Optional[str]

class PaginatedHadiths(BaseModel):
    """Paginated response for browsing hadiths"""

    results: list[HadithListItem]
    total: int  # Total hadiths matching filter
    page: int  # Current page number
    per_page: int  # Items per page
    pages: int  # Total number of pages


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    database: str
    total_hadiths: int
