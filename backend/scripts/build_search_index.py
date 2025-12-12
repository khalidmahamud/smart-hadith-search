# backend/scripts/build_search_index.py

import sqlite3
import re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "database" / "sqlite.db"

STOPWORDS_EN = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of",
    "with", "by", "from", "as", "is", "was", "are", "were", "been", "be", "have",
    "has", "had", "do", "does", "did", "will", "would", "could", "should", "may",
    "might", "must", "shall", "can", "need", "he", "she", "it", "they", "we", "i",
    "you", "his", "her", "its", "their", "our", "my", "your", "this", "that",
    "these", "those", "who", "whom", "which", "what", "where", "when", "why", "how",
    "said", "says", "saying", "told", "asked", "replied", "answered", "then", "so",
    "if", "not", "no", "yes", "all", "any", "some", "one", "two", "three", "him",
    "them", "us", "me", "about", "into", "over", "after", "before", "between",
    "under", "again", "there", "here", "up", "down", "out", "off", "more", "most",
    "other", "only", "same", "just", "also", "very", "much", "many", "such", "own",
    "each", "allah", "prophet", "messenger", "narrated", "abu", "ibn", "bin",
}

STOPWORDS_AR = {
    "من", "في", "على", "إلى", "عن", "مع", "هذا", "هذه", "ذلك", "تلك", "الذي",
    "التي", "الذين", "ما", "لا", "إن", "أن", "كان", "كانت", "يكون", "تكون",
    "هو", "هي", "هم", "أنا", "نحن", "أنت", "قال", "قالت", "قالوا", "ثم", "أو",
    "و", "ف", "ب", "ل", "ك", "حتى", "إذا", "لم", "لن", "قد", "عند", "بعد",
    "قبل", "بين", "كل", "بعض", "غير", "أي", "له", "لها", "لهم", "به", "بها",
}


def phonetic_code(s: str) -> str:
    """Generate phonetic code for fuzzy matching transliterations."""
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


def extract_words(text: str, lang: str) -> list:
    if not text:
        return []

    if lang == "ar":
        words = re.findall(r"[\u0600-\u06FF]+", text)
        words = [w for w in words if len(w) > 2 and w not in STOPWORDS_AR]
    elif lang in ("bn", "ur"):
        words = re.findall(r"[\u0980-\u09FF\u0600-\u06FF]+", text)
        words = [w for w in words if len(w) > 2]
    else:
        text_lower = text.lower()
        words = re.findall(r"[a-z]+", text_lower)
        words = [w for w in words if len(w) > 2 and w not in STOPWORDS_EN]

    return words


def main():
    print("🔧 Building search terms index...")
    
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    
    # Clear existing
    cur.execute("DELETE FROM search_terms")
    
    # Load hadiths
    cur.execute("SELECT hadith_id, ar_text, en_text, bn_text, ur_text FROM hadiths")
    rows = cur.fetchall()
    print(f"   Processing {len(rows)} hadiths...")

    term_counts = {"ar": Counter(), "en": Counter(), "bn": Counter(), "ur": Counter()}

    for hadith_id, ar_text, en_text, bn_text, ur_text in rows:
        texts = {"ar": ar_text, "en": en_text, "bn": bn_text, "ur": ur_text}
        for lang, text in texts.items():
            if text:
                words = extract_words(text, lang)
                term_counts[lang].update(words)

    # Insert terms with frequency >= 2
    insert_data = []
    for lang, counts in term_counts.items():
        for term, freq in counts.items():
            if freq >= 2:
                phon = phonetic_code(term) if lang == "en" else None
                insert_data.append((term, lang, freq, phon))

    cur.executemany(
        "INSERT INTO search_terms (term, language, frequency, phonetic) VALUES (?, ?, ?, ?)",
        insert_data,
    )
    con.commit()

    # Stats
    cur.execute("SELECT COUNT(*) FROM search_terms")
    total = cur.fetchone()[0]
    print(f"\n✅ Search terms built: {total} terms")
    
    for lang in ["ar", "en", "bn", "ur"]:
        cur.execute("SELECT COUNT(*) FROM search_terms WHERE language = ?", (lang,))
        count = cur.fetchone()[0]
        print(f"   {lang}: {count} terms")
    
    # Optimize
    con.execute("ANALYZE search_terms")
    con.close()
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
