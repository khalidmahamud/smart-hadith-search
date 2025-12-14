# Smart Hadith Search

A semantic search engine for Islamic hadith collections, combining ML-powered embeddings with full-text search to deliver intelligent, multi-language search across 26,000+ hadiths.

## Features

- **Hybrid Search** – Combines semantic similarity (sentence transformers) with PostgreSQL full-text search using Reciprocal Rank Fusion
- **Multi-Language Support** – Search and browse in Arabic, English, Bengali, and Urdu
- **Automatic Language Detection** – Queries are detected and routed to appropriate search indexes
- **Browse Collections** – Explore hadith books, chapters, and individual hadiths with pagination
- **Hadith Grading** – Visual indicators for authenticity grades (Sahih, Hasan, Da'if, etc.)

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, Python 3.11+ |
| Frontend | Next.js 16, React 19, TypeScript |
| Database | PostgreSQL (Supabase), pgvector |
| ML Model | `paraphrase-multilingual-MiniLM-L12-v2` |
| Styling | Tailwind CSS |
| DevOps | Docker, GitHub Actions |

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL with pgvector extension (or Supabase account)

### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export SUPABASE_DB_URL="postgresql+asyncpg://user:pass@host:port/db"
export CORS_ORIGINS="http://localhost:3000"

# Run the server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install

# Set environment variables
export NEXT_PUBLIC_API_URL="http://localhost:8000/api/v1"

# Run development server
npm run dev
```

### Docker

```bash
# Build and run backend
docker build -t smart-hadith-backend ./backend
docker run -p 8000:8000 --env-file .env smart-hadith-backend
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SUPABASE_DB_URL` | PostgreSQL connection string (async) |
| `CORS_ORIGINS` | Allowed origins (comma-separated) |
| `NEXT_PUBLIC_API_URL` | Backend API URL for frontend |
| `SEMANTIC_WEIGHT` | Weight for semantic search (default: 1.0) |
| `FULLTEXT_WEIGHT` | Weight for full-text search (default: 1.0) |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/search` | Hybrid search with query |
| GET | `/api/v1/books` | List all hadith collections |
| GET | `/api/v1/books/{id}` | Get book details |
| GET | `/api/v1/books/{id}/chapters` | List chapters in a book |
| GET | `/api/v1/books/{id}/hadiths` | Paginated hadiths by book |
| GET | `/api/v1/hadiths/{id}` | Get single hadith details |
| GET | `/health` | Health check |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI application
│   │   ├── config.py         # Settings
│   │   ├── db.py             # Database connection
│   │   ├── routers/          # API endpoints
│   │   └── services/         # Business logic
│   ├── search.py             # Hybrid search implementation
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages
│   │   ├── components/       # React components
│   │   └── lib/              # API client & types
│   └── package.json
└── docker-compose.yml
```

## License

MIT
