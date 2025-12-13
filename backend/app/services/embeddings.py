"""
Embedding Service for Semantic Search

This module handles converting text to numerical vectors (embeddings)
using a pre-trained multilingual transformer model.

How it works:
1. Load the model once at startup (cached in memory)
2. For searches: Convert user query to embedding (~10ms)
3. For migration: Batch convert all hadiths to embeddings

Model: paraphrase-multilingual-MiniLM-L12-v2
- 384 dimensions
- Supports 50+ languages (Arabic, Bengali, Urdu, English)
- ~440MB download (first time only)
"""

from functools import lru_cache
from sentence_transformers import SentenceTransformer

from app.config import settings


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Load and cache the embedding model.

    The model is loaded once and kept in memory for fast inference.
    First call downloads the model (~440MB) if not cached locally.

    Returns:
        SentenceTransformer: The loaded model ready for encoding
    """
    print(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
    model = SentenceTransformer(settings.EMBEDDING_MODEL)
    print(f"Model loaded. Embedding dimension: {model.get_sentence_embedding_dimension()}")
    return model


def generate_embedding(text: str) -> list[float]:
    """
    Generate embedding for a single text (used for search queries).

    Args:
        text: The text to embed (e.g., user's search query)

    Returns:
        List of 384 floats representing the text's semantic meaning
    """
    if not text or not text.strip():
        return []

    model = get_embedding_model()
    # normalize_embeddings=True: Vectors have unit length (required for cosine similarity)
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def generate_embeddings_batch(
    texts: list[str],
    batch_size: int = 32,
    show_progress: bool = True
) -> list[list[float]]:
    """
    Generate embeddings for multiple texts (used for migration).

    Processing 26,742 hadiths:
    - Batch size 32: ~14 minutes on CPU
    - Batch size 64: ~12 minutes on CPU
    - With GPU: ~2-3 minutes

    Args:
        texts: List of texts to embed
        batch_size: Number of texts to process at once (higher = faster but more memory)
        show_progress: Whether to show a progress bar

    Returns:
        List of embeddings, one per input text
    """
    if not texts:
        return []

    model = get_embedding_model()
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=show_progress,
    )
    return embeddings.tolist()


def prepare_hadith_text(hadith: dict) -> str:
    """
    Prepare hadith content for embedding.

    We combine English and Arabic text + narrators to create a rich
    representation that captures the semantic meaning in both languages.

    The multilingual model understands both languages, so the embedding
    will capture meaning from both.

    Args:
        hadith: Dictionary with hadith fields (en_text, ar_text, etc.)

    Returns:
        Combined text string ready for embedding
    """
    parts = []

    # English content
    if hadith.get("en_narrator"):
        parts.append(hadith["en_narrator"])
    if hadith.get("en_text"):
        parts.append(hadith["en_text"])

    # Arabic content (original language)
    if hadith.get("ar_narrator"):
        parts.append(hadith["ar_narrator"])
    if hadith.get("ar_text"):
        parts.append(hadith["ar_text"])

    # Join with newlines for clear separation
    return "\n".join(parts)


def compute_similarity(embedding1: list[float], embedding2: list[float]) -> float:
    """
    Compute cosine similarity between two embeddings.

    Since embeddings are normalized, cosine similarity = dot product.

    Returns:
        Similarity score between 0 and 1 (1 = identical meaning)
    """
    if not embedding1 or not embedding2:
        return 0.0

    # Dot product of normalized vectors = cosine similarity
    return sum(a * b for a, b in zip(embedding1, embedding2))
