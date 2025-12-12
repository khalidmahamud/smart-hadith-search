# backend/search.py

import sqlite3
import re
from pathlib import Path
from functools import lru_cache

from rapidfuzz import fuzz, process

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "database" / "sqlite.db"


def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def phonetic_code(s: str) -> str:
    if not s:
        return ""
    
    s = s.lower().strip()
    s = re.sub(r"[^a-z]", "", s)
    
    if len(s) < 2:
        return s
    
    replacements = [
        (r"gh", "g"), (r"kh", "k"), (r"sh", "s"), (r"th", "t"),
        (r"dh", "d"), (r"zh", "z"), (r"ph", "f"), (r"qu", "k"),
        (r"ee", "i"), (r"aa", "a"), (r"oo", "u"), (r"ou", "u"),
        (r"ei", "i"), (r"ai", "a"), (r"ay", "a"),
    ]
    
    result = s
    for pattern, repl in replacements:
        result = re.sub(pattern, repl, result)
    
    first = result[0]
    rest = re.sub(r"[aeiou]", "", result[1:])
    result = first + rest
    result = re.sub(r"(.)\1+", r"\1", result)
    
    return result[:8]


def detect_language(text: str) -> str:
    """Detect primary language of text."""
    if re.search(r"[\u0600-\u06FF]", text):
        if re.search(r"[\u0980-\u09FF]", text):
            return "bn"
        return "ar"  # Could be Arabic or Urdu
    if re.search(r"[\u0980-\u09FF]", text):
        return "bn"
    return "en"


@lru_cache(maxsize=1)
def load_terms() -> dict:
    """Load terms grouped by language."""
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT term, language, phonetic FROM search_terms")
    
    terms = {"en": [], "ar": [], "bn": [], "ur": [], "all": []}
    phonetic_map = {}
    
    for row in cur.fetchall():
        term, lang, phon = row
        terms[lang].append(term)
        terms["all"].append(term)
        if phon:
            phonetic_map[phon] = term
    
    con.close()
    return {"terms": terms, "phonetic": phonetic_map}


def expand_query(query: str) -> dict:
    """Find phonetic and fuzzy matches for query words."""
    data = load_terms()
    words = [w for w in query.split() if len(w) >= 2]
    
    query_lang = detect_language(query)
    
    expansion = {
        "original": words,
        "expanded": set(words),
        "language": query_lang,
    }
    
    for word in words:
        word_lower = word.lower()
        
        if query_lang == "en":
            # Phonetic matches for English
            word_phon = phonetic_code(word)
            if word_phon:
                for phon, term in data["phonetic"].items():
                    if phon and (phon == word_phon or phon.startswith(word_phon) or word_phon.startswith(phon)):
                        expansion["expanded"].add(term)
            
            # Fuzzy matches for English
            matches = process.extract(word_lower, data["terms"]["en"], scorer=fuzz.ratio, score_cutoff=75, limit=5)
            for match, score, _ in matches:
                expansion["expanded"].add(match)
        else:
            # For non-English, use fuzzy matching on respective language terms
            lang_terms = data["terms"].get(query_lang, [])
            if lang_terms:
                matches = process.extract(word, lang_terms, scorer=fuzz.ratio, score_cutoff=70, limit=5)
                for match, score, _ in matches:
                    expansion["expanded"].add(match)
    
    expansion["expanded"] = list(expansion["expanded"])
    return expansion


def search(query: str, lang: str = None, book_id: int = None, limit: int = 20) -> dict:
    """
    Search hadiths using FTS5 with query expansion.
    """
    con = get_db()
    cur = con.cursor()
    
    expansion = expand_query(query)
    all_terms = expansion["expanded"]
    query_lang = expansion["language"]
    
    if not all_terms:
        return {"query": query, "expansion": expansion, "results": []}
    
    # Build FTS query
    fts_terms = " OR ".join(f'"{t}"' for t in all_terms)
    
    try:
        sql = """
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
                b.en_title as book_title,
                b.bn_title as book_title_bn,
                b.slug as book_slug,
                g.en_text as grade_text,
                g.bn_text as grade_text_bn,
                bm25(hadiths_fts) as score
            FROM hadiths_fts
            JOIN hadiths h ON h.hadith_id = hadiths_fts.rowid
            JOIN books b ON b.book_id = h.book_id
            LEFT JOIN grades g ON g.grade_id = h.grade_id
            WHERE hadiths_fts MATCH ?
        """
        params = [fts_terms]
        
        if book_id:
            sql += " AND h.book_id = ?"
            params.append(book_id)
        
        sql += " ORDER BY score LIMIT ?"
        params.append(limit)
        
        cur.execute(sql, params)
        rows = [dict(r) for r in cur.fetchall()]
        
    except sqlite3.OperationalError as e:
        print(f"FTS error: {e}")
        rows = []
    
    con.close()
    
    return {
        "query": query,
        "query_lang": query_lang,
        "expansion": expansion,
        "count": len(rows),
        "results": rows,
    }


def get_hadith(hadith_id: int) -> dict | None:
    """Get single hadith by ID."""
    con = get_db()
    cur = con.cursor()
    
    cur.execute("""
        SELECT 
            h.*,
            b.en_title as book_title,
            b.slug as book_slug,
            c.en_title as chapter_title,
            g.en_text as grade_text
        FROM hadiths h
        JOIN books b ON b.book_id = h.book_id
        JOIN chapters c ON c.chapter_id = h.chapter_id
        LEFT JOIN grades g ON g.grade_id = h.grade_id
        WHERE h.hadith_id = ?
    """, (hadith_id,))
    
    row = cur.fetchone()
    con.close()
    
    return dict(row) if row else None


def get_book_hadiths(book_id: int, chapter_id: int = None, page: int = 1, per_page: int = 50) -> dict:
    """Get hadiths by book with pagination."""
    con = get_db()
    cur = con.cursor()
    
    offset = (page - 1) * per_page
    
    sql = """
        SELECT h.*, g.en_text as grade_text
        FROM hadiths h
        LEFT JOIN grades g ON g.grade_id = h.grade_id
        WHERE h.book_id = ?
    """
    params = [book_id]
    
    if chapter_id:
        sql += " AND h.chapter_id = ?"
        params.append(chapter_id)
    
    count_sql = sql.replace("SELECT h.*, g.en_text as grade_text", "SELECT COUNT(*)")
    cur.execute(count_sql, params)
    total = cur.fetchone()[0]
    
    sql += " ORDER BY h.hadith_number LIMIT ? OFFSET ?"
    params.extend([per_page, offset])
    
    cur.execute(sql, params)
    rows = [dict(r) for r in cur.fetchall()]
    
    con.close()
    
    return {
        "results": rows,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
    }
