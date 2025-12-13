#!/usr/bin/env python3
"""
Migration Script: SQLite → Supabase PostgreSQL

This script:
1. Reads all data from your existing SQLite database
2. Generates embeddings for all hadiths using sentence-transformers
3. Inserts everything into Supabase PostgreSQL

Run this ONCE after setting up your Supabase database.

Usage:
    cd backend
    python scripts/migrate_to_supabase.py

Prerequisites:
1. Schema must be created in Supabase (run supabase_schema.sql first)
2. SUPABASE_DB_URL must be set in .env
3. pip install -r requirements.txt
"""

import asyncio
import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncpg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Configuration
SQLITE_PATH = Path(__file__).parent.parent / "database" / "sqlite.db"
BATCH_SIZE = 64  # For embedding generation
INSERT_BATCH_SIZE = 100  # For database inserts


def get_supabase_url() -> str:
    """Get Supabase connection URL from environment."""
    url = os.getenv("SUPABASE_DB_URL", "")
    if not url:
        print("ERROR: SUPABASE_DB_URL not set in environment!")
        print("Please add it to your .env file:")
        print("SUPABASE_DB_URL=postgresql+asyncpg://postgres:PASSWORD@db.PROJECT.supabase.co:6543/postgres")
        sys.exit(1)

    # asyncpg needs the URL without the +asyncpg part
    return url.replace("postgresql+asyncpg://", "postgresql://")


def load_sqlite_data() -> dict:
    """Load all data from SQLite database."""
    print(f"\n📖 Reading from SQLite: {SQLITE_PATH}")

    if not SQLITE_PATH.exists():
        print(f"ERROR: SQLite database not found at {SQLITE_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row

    data = {}

    # Load books
    cursor = conn.execute("SELECT * FROM books ORDER BY book_id")
    data["books"] = [dict(row) for row in cursor.fetchall()]
    print(f"   Books: {len(data['books'])}")

    # Load chapters
    cursor = conn.execute("SELECT * FROM chapters ORDER BY chapter_id")
    data["chapters"] = [dict(row) for row in cursor.fetchall()]
    print(f"   Chapters: {len(data['chapters'])}")

    # Load grades
    cursor = conn.execute("SELECT * FROM grades ORDER BY grade_id")
    data["grades"] = [dict(row) for row in cursor.fetchall()]
    print(f"   Grades: {len(data['grades'])}")

    # Load hadiths
    cursor = conn.execute("SELECT * FROM hadiths ORDER BY hadith_id")
    data["hadiths"] = [dict(row) for row in cursor.fetchall()]
    print(f"   Hadiths: {len(data['hadiths'])}")

    conn.close()
    return data


def prepare_hadith_text(hadith: dict) -> str:
    """Prepare hadith text for embedding."""
    parts = []

    # English content
    if hadith.get("en_narrator"):
        parts.append(hadith["en_narrator"])
    if hadith.get("en_text"):
        parts.append(hadith["en_text"])

    # Arabic content
    if hadith.get("ar_narrator"):
        parts.append(hadith["ar_narrator"])
    if hadith.get("ar_text"):
        parts.append(hadith["ar_text"])

    return "\n".join(parts)


EMBEDDINGS_CACHE_FILE = Path(__file__).parent.parent / "database" / "embeddings_cache.npy"


def generate_embeddings(hadiths: list) -> list:
    """Generate embeddings for all hadiths (with caching to avoid re-generation)."""

    # Check if we have cached embeddings
    if EMBEDDINGS_CACHE_FILE.exists():
        print(f"\n📦 Found cached embeddings at {EMBEDDINGS_CACHE_FILE}")
        print("   Loading from cache (delete this file to regenerate)...")
        import numpy as np
        embeddings = np.load(EMBEDDINGS_CACHE_FILE)
        print(f"   Loaded {len(embeddings)} embeddings from cache")
        return embeddings.tolist()

    print(f"\n🧠 Generating embeddings for {len(hadiths)} hadiths...")
    print("   This may take 10-30 minutes depending on your hardware.")
    print("   (First run will download the model ~440MB)")

    from sentence_transformers import SentenceTransformer
    import numpy as np

    # Load model
    model_name = "paraphrase-multilingual-MiniLM-L12-v2"
    print(f"\n   Loading model: {model_name}")
    model = SentenceTransformer(model_name)
    print(f"   Model loaded. Dimension: {model.get_sentence_embedding_dimension()}")

    # Prepare texts
    print("\n   Preparing texts...")
    texts = [prepare_hadith_text(h) for h in hadiths]

    # Generate embeddings
    print(f"\n   Generating embeddings (batch size: {BATCH_SIZE})...")
    start_time = datetime.now()

    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    elapsed = datetime.now() - start_time
    print(f"\n   ✅ Embeddings generated in {elapsed}")

    # Save to cache file
    print(f"\n   💾 Saving embeddings to cache: {EMBEDDINGS_CACHE_FILE}")
    np.save(EMBEDDINGS_CACHE_FILE, embeddings)
    print("   Embeddings cached! (won't need to regenerate if migration fails)")

    return embeddings.tolist()


async def migrate_to_supabase(data: dict, embeddings: list):
    """Insert all data into Supabase PostgreSQL."""
    import socket

    # Force IPv4 (some networks have broken IPv6)
    # This monkey-patches socket to prefer IPv4
    _original_getaddrinfo = socket.getaddrinfo
    def _getaddrinfo_ipv4_only(*args, **kwargs):
        responses = _original_getaddrinfo(*args, **kwargs)
        return [r for r in responses if r[0] == socket.AF_INET] or responses
    socket.getaddrinfo = _getaddrinfo_ipv4_only

    url = get_supabase_url()
    print(f"\n🚀 Connecting to Supabase (forcing IPv4)...")

    conn = await asyncpg.connect(url)
    print("   Connected!")

    try:
        # Clear existing data (in case of re-run)
        print("\n   Clearing existing data...")
        await conn.execute("DELETE FROM hadiths")
        await conn.execute("DELETE FROM chapters")
        await conn.execute("DELETE FROM grades")
        await conn.execute("DELETE FROM books")

        # Insert books
        print(f"\n   Inserting {len(data['books'])} books...")
        for book in data["books"]:
            await conn.execute(
                """
                INSERT INTO books (book_id, slug, en_title, ar_title, bn_title, ur_title, description)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                book["book_id"],
                book["slug"],
                book["en_title"],
                book.get("ar_title"),
                book.get("bn_title"),
                book.get("ur_title"),
                book.get("description"),
            )

        # Insert grades
        print(f"   Inserting {len(data['grades'])} grades...")
        for grade in data["grades"]:
            await conn.execute(
                """
                INSERT INTO grades (grade_id, en_text, ar_text, bn_text, ur_text)
                VALUES ($1, $2, $3, $4, $5)
                """,
                grade["grade_id"],
                grade.get("en_text"),
                grade.get("ar_text"),
                grade.get("bn_text"),
                grade.get("ur_text"),
            )

        # Insert chapters
        print(f"   Inserting {len(data['chapters'])} chapters...")
        for chapter in data["chapters"]:
            await conn.execute(
                """
                INSERT INTO chapters (chapter_id, book_id, order_index, en_title, ar_title, bn_title, ur_title)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                chapter["chapter_id"],
                chapter["book_id"],
                chapter["order_index"],
                chapter.get("en_title"),
                chapter.get("ar_title"),
                chapter.get("bn_title"),
                chapter.get("ur_title"),
            )

        # Insert hadiths with embeddings
        print(f"   Inserting {len(data['hadiths'])} hadiths with embeddings...")
        hadiths = data["hadiths"]

        for i, (hadith, embedding) in enumerate(zip(hadiths, embeddings)):
            # Convert embedding list to PostgreSQL vector format
            embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"

            await conn.execute(
                """
                INSERT INTO hadiths (
                    hadith_id, book_id, chapter_id, hadith_number, grade_id,
                    ar_text, ar_narrator, en_text, en_narrator,
                    bn_text, bn_narrator, ur_text, ur_narrator,
                    embedding
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14::vector)
                """,
                hadith["hadith_id"],
                hadith["book_id"],
                hadith["chapter_id"],
                hadith["hadith_number"],
                hadith.get("grade_id"),
                hadith["ar_text"],
                hadith.get("ar_narrator"),
                hadith.get("en_text"),
                hadith.get("en_narrator"),
                hadith.get("bn_text"),
                hadith.get("bn_narrator"),
                hadith.get("ur_text"),
                hadith.get("ur_narrator"),
                embedding_str,
            )

            if (i + 1) % 1000 == 0:
                print(f"      Inserted {i + 1}/{len(hadiths)} hadiths...")

        print(f"\n   ✅ All hadiths inserted!")

        # Verify counts
        print("\n   Verifying data...")
        counts = {}
        for table in ["books", "chapters", "grades", "hadiths"]:
            result = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
            counts[table] = result
            print(f"      {table}: {result}")

        # Verify embeddings
        embed_count = await conn.fetchval(
            "SELECT COUNT(*) FROM hadiths WHERE embedding IS NOT NULL"
        )
        print(f"      hadiths with embeddings: {embed_count}")

    finally:
        await conn.close()

    return counts


async def main():
    """Main migration function."""
    print("=" * 60)
    print("Smart Hadith Search - Migration to Supabase")
    print("=" * 60)

    # Step 1: Load SQLite data
    data = load_sqlite_data()

    # Step 2: Generate embeddings
    embeddings = generate_embeddings(data["hadiths"])

    # Step 3: Migrate to Supabase
    counts = await migrate_to_supabase(data, embeddings)

    print("\n" + "=" * 60)
    print("✅ MIGRATION COMPLETE!")
    print("=" * 60)
    print(f"\nMigrated to Supabase:")
    print(f"   - {counts['books']} books")
    print(f"   - {counts['chapters']} chapters")
    print(f"   - {counts['grades']} grades")
    print(f"   - {counts['hadiths']} hadiths (with embeddings)")
    print("\nYou can now start the API:")
    print("   cd backend && uvicorn app.main:app --reload")


if __name__ == "__main__":
    asyncio.run(main())
