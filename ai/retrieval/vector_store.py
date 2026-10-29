"""RAG Vector Store and Semantic Search for approved financial knowledge."""

import re
from typing import List, Dict, Any, Optional
from datetime import date
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def sanitize_retrieved_text(text: str) -> str:
    """
    Sanitize untrusted text from documents to prevent indirect prompt injection.
    Neutralizes instructions attempting to override system behavior.
    """
    injection_patterns = [
        r"(ignore|disregard|forget)\s+(all\s+)?(previous|prior|above)\s+instructions",
        r"system\s*prompt",
        r"you\s+are\s+now\s+(an?\s+)?unrestricted",
        r"reveal\s+(the\s+)?(api[_\s]?key|secret|password)",
        r"<script.*?>.*?</script>",
        r"javascript:",
    ]
    sanitized = text
    for pat in injection_patterns:
        sanitized = re.sub(pat, "[FILTERED_INSTRUCTION]", sanitized, flags=re.IGNORECASE)
    return sanitized


class RAGVectorStore:
    """
    Fast, deterministic vector store using TF-IDF word & character n-gram cosine similarity.
    Does not require external paid API calls or GPU runtimes.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True
        )
        self.chunks: List[Dict[str, Any]] = []
        self.fitted_matrix = None

    def add_document(
        self,
        doc_id: str,
        title: str,
        publisher: str,
        publication_date: Optional[date],
        content: str,
        chunk_size_words: int = 250
    ) -> int:
        """Split document into chunks and add to vector store."""
        words = content.split()
        chunks_added = 0
        i = 0
        chunk_idx = 0

        while i < len(words):
            chunk_words = words[i:i + chunk_size_words]
            chunk_text = " ".join(chunk_words)
            clean_text = sanitize_retrieved_text(chunk_text)

            self.chunks.append({
                "doc_id": doc_id,
                "title": title,
                "publisher": publisher,
                "publication_date": publication_date.isoformat() if publication_date else None,
                "chunk_index": chunk_idx,
                "content": clean_text
            })
            chunk_idx += 1
            chunks_added += 1
            # 50 words overlap
            i += max(1, chunk_size_words - 50)

        self._fit_index()
        return chunks_added

    def _fit_index(self):
        """Fit vectorizer on all current chunks."""
        if not self.chunks:
            self.fitted_matrix = None
            return
        corpus = [c["content"] for c in self.chunks]
        self.fitted_matrix = self.vectorizer.fit_transform(corpus)

    def search(self, query: str, top_k: int = 3, min_score: float = 0.05) -> List[Dict[str, Any]]:
        """Retrieve most relevant chunks with similarity score and provenance."""
        if not self.chunks or self.fitted_matrix is None:
            return []

        clean_query = sanitize_retrieved_text(query)
        q_vec = self.vectorizer.transform([clean_query])
        sims = cosine_similarity(q_vec, self.fitted_matrix)[0]

        top_indices = np.argsort(sims)[::-1][:top_k]
        results = []

        for idx in top_indices:
            score = float(sims[idx])
            if score >= min_score:
                chunk = self.chunks[idx].copy()
                chunk["similarity_score"] = round(score, 4)
                results.append(chunk)

        return results
