# backend/scripts/test_search.py

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from search import search

LANG_PRIORITY = {
    "en": ["en_text", "ar_text", "bn_text", "ur_text"],
    "bn": ["bn_text", "en_text", "ar_text", "ur_text"],
    "ar": ["ar_text", "en_text", "bn_text", "ur_text"],
    "ur": ["ur_text", "en_text", "ar_text", "bn_text"],
}


def get_display_text(result: dict, lang: str) -> str:
    """Get text in preferred language order."""
    priority = LANG_PRIORITY.get(lang, LANG_PRIORITY["en"])
    for field in priority:
        if result.get(field):
            return result[field]
    return ""


def main():
    print("Hadith Search Test")
    print("=" * 60)
    
    while True:
        q = input("\nQuery (or 'q' to quit): ").strip()
        if q.lower() == 'q':
            break
        
        result = search(q, limit=5)
        query_lang = result.get("query_lang", "en")
        
        print(f"\n📝 Original: {result['expansion']['original']}")
        print(f"🌐 Detected language: {query_lang}")
        
        expanded_extra = set(result['expansion']['expanded']) - set(result['expansion']['original'])
        if expanded_extra:
            print(f"🔄 Expanded: {list(expanded_extra)}")
        
        print(f"\n📊 Found {result['count']} results:")
        
        for r in result['results']:
            print(f"\n{'─'*60}")
            
            # Book title in query language
            if query_lang == "bn" and r.get('book_title_bn'):
                print(f"📖 {r['book_title_bn']} #{r['hadith_number']}")
            else:
                print(f"📖 {r['book_title']} #{r['hadith_number']}")
            
            # Grade in query language
            if query_lang == "bn" and r.get('grade_text_bn'):
                print(f"📋 মান: {r['grade_text_bn']}")
            elif r.get('grade_text'):
                print(f"📋 Grade: {r['grade_text']}")
            
            # Text in query language
            text = get_display_text(r, query_lang)
            print(text[:500] + "..." if len(text) > 500 else text)


if __name__ == "__main__":
    main()