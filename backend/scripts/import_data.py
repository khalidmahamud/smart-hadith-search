# backend/scripts/import_data.py

import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
DB_PATH = ROOT / "backend" / "database" / "sqlite.db"
SCHEMA_PATH = ROOT / "backend" / "database" / "schema.sql"


def import_csv(con: sqlite3.Connection, csv_path: Path, table: str, columns: list[str]) -> int:
    placeholders = ",".join("?" * len(columns))
    cols_str = ",".join(columns)
    sql = f"INSERT INTO {table}({cols_str}) VALUES ({placeholders})"
    
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for r in reader:
            row = tuple(r.get(c) or None for c in columns)
            rows.append(row)
    
    con.executemany(sql, rows)
    return len(rows)


def main():
    # Delete existing db for clean start
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"🗑️  Deleted existing database")
    
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = OFF")  # Disable during import
    con.execute("PRAGMA journal_mode = WAL")
    con.execute("PRAGMA synchronous = NORMAL")
    con.execute("PRAGMA temp_store = MEMORY")
    con.execute("PRAGMA cache_size = -64000")  # 64MB cache
    
    # Create tables (without triggers initially for faster import)
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    
    # Remove trigger definitions temporarily
    schema_no_triggers = "\n".join(
        line for line in schema.split("\n") 
        if "CREATE TRIGGER" not in line and "END;" not in line 
        and "INSERT INTO hadiths_fts" not in line
        and "VALUES ('delete'" not in line
        and "NEW.hadith_id" not in line
        and "OLD.hadith_id" not in line
    )
    
    con.executescript(schema_no_triggers)
    print("✅ Schema created")
    
    # Import in FK-safe order
    print("\n📥 Importing data...")
    
    n = import_csv(con, DATA / "books.csv", "books", [
        "book_id", "slug", "en_title", "bn_title", "ur_title", "ar_title", "description"
    ])
    print(f"   books: {n}")
    
    n = import_csv(con, DATA / "chapters.csv", "chapters", [
        "chapter_id", "book_id", "order_index", "bn_title", "en_title", "ur_title", "ar_title"
    ])
    print(f"   chapters: {n}")
    
    n = import_csv(con, DATA / "grades.csv", "grades", [
        "grade_id", "bn_text", "en_text", "ur_text", "ar_text"
    ])
    print(f"   grades: {n}")
    
    n = import_csv(con, DATA / "hadiths.csv", "hadiths", [
        "hadith_id", "book_id", "hadith_number", "chapter_id",
        "bn_narrator", "bn_text", "en_narrator", "en_text",
        "ur_narrator", "ur_text", "ar_narrator", "ar_text", "grade_id"
    ])
    print(f"   hadiths: {n}")
    
    con.commit()
    
    # Build FTS index
    print("\n🔍 Building FTS index...")
    con.execute("""
        INSERT INTO hadiths_fts(rowid, en_text, ar_text, bn_text, ur_text, en_narrator, ar_narrator)
        SELECT hadith_id, en_text, ar_text, bn_text, ur_text, en_narrator, ar_narrator 
        FROM hadiths
    """)
    con.commit()
    
    # Now create triggers for future updates
    print("⚡ Creating triggers...")
    con.executescript("""
        CREATE TRIGGER IF NOT EXISTS hadiths_fts_insert AFTER INSERT ON hadiths BEGIN
            INSERT INTO hadiths_fts(rowid, en_text, ar_text, bn_text, ur_text, en_narrator, ar_narrator)
            VALUES (NEW.hadith_id, NEW.en_text, NEW.ar_text, NEW.bn_text, NEW.ur_text, NEW.en_narrator, NEW.ar_narrator);
        END;

        CREATE TRIGGER IF NOT EXISTS hadiths_fts_delete AFTER DELETE ON hadiths BEGIN
            INSERT INTO hadiths_fts(hadiths_fts, rowid, en_text, ar_text, bn_text, ur_text, en_narrator, ar_narrator)
            VALUES ('delete', OLD.hadith_id, OLD.en_text, OLD.ar_text, OLD.bn_text, OLD.ur_text, OLD.en_narrator, OLD.ar_narrator);
        END;

        CREATE TRIGGER IF NOT EXISTS hadiths_fts_update AFTER UPDATE ON hadiths BEGIN
            INSERT INTO hadiths_fts(hadiths_fts, rowid, en_text, ar_text, bn_text, ur_text, en_narrator, ar_narrator)
            VALUES ('delete', OLD.hadith_id, OLD.en_text, OLD.ar_text, OLD.bn_text, OLD.ur_text, OLD.en_narrator, OLD.ar_narrator);
            INSERT INTO hadiths_fts(rowid, en_text, ar_text, bn_text, ur_text, en_narrator, ar_narrator)
            VALUES (NEW.hadith_id, NEW.en_text, NEW.ar_text, NEW.bn_text, NEW.ur_text, NEW.en_narrator, NEW.ar_narrator);
        END;
    """)
    
    # Re-enable FK and optimize
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("VACUUM")
    con.execute("ANALYZE")
    con.commit()
    
    # Verify
    print("\n📊 Verification:")
    cur = con.cursor()
    for table in ["books", "chapters", "grades", "hadiths", "hadiths_fts"]:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        print(f"   {table}: {cur.fetchone()[0]}")
    
    con.close()
    print(f"\n✅ Database created: {DB_PATH}")


if __name__ == "__main__":
    main()
