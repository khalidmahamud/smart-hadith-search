#!/usr/bin/env python3
"""Download the SQLite database from GitHub LFS"""
import urllib.request
import os
from pathlib import Path

# GitHub raw URL for LFS files - we'll use a release instead
DB_URL = os.getenv("DATABASE_URL_DOWNLOAD")
DB_PATH = Path(__file__).parent / "database" / "sqlite.db"

def download_db():
    if DB_PATH.exists() and DB_PATH.stat().st_size > 1000000:  # >1MB means real file
        print(f"Database already exists: {DB_PATH} ({DB_PATH.stat().st_size} bytes)")
        return

    if not DB_URL:
        print("DATABASE_URL_DOWNLOAD not set, skipping download")
        return

    print(f"Downloading database from {DB_URL}...")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(DB_URL, DB_PATH)
    print(f"Downloaded: {DB_PATH.stat().st_size} bytes")

if __name__ == "__main__":
    download_db()
