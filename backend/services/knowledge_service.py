"""Knowledge Document ingestion and RAG search service."""

import os
from pathlib import Path
from datetime import date
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.models.knowledge import KnowledgeDocument, KnowledgeChunk
from ai.retrieval.vector_store import RAGVectorStore
from backend.schemas.knowledge import KnowledgeSearchResultItem, KnowledgeSearchResponse

# Singleton RAG store
rag_store = RAGVectorStore()


class KnowledgeService:
    def __init__(self, db: Session):
        self.db = db
        self.rag_store = rag_store
        self._ensure_default_documents_indexed()

    def _ensure_default_documents_indexed(self):
        """Index default markdown knowledge documents from data/knowledge if store is empty."""
        if self.rag_store.chunks:
            return

        knowledge_dir = Path(__file__).resolve().parent.parent.parent / "data" / "knowledge"
        if not knowledge_dir.exists():
            return

        for md_file in knowledge_dir.glob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                # Parse metadata lines if present
                title = md_file.stem.replace("_", " ").title()
                publisher = "WealthOS Research"
                for line in content.splitlines()[:5]:
                    if line.startswith("# "):
                        title = line[2:].strip()
                    elif line.lower().startswith("publisher:"):
                        publisher = line.split(":", 1)[1].strip()

                self.rag_store.add_document(
                    doc_id=md_file.stem,
                    title=title,
                    publisher=publisher,
                    publication_date=date(2026, 1, 1),
                    content=content
                )
            except Exception:
                pass

    def search_knowledge(self, query: str, top_k: int = 3) -> KnowledgeSearchResponse:
        results = self.rag_store.search(query, top_k=top_k)
        items = [
            KnowledgeSearchResultItem(
                doc_id=r["doc_id"],
                title=r["title"],
                publisher=r["publisher"],
                publication_date=r.get("publication_date"),
                chunk_index=r["chunk_index"],
                content=r["content"],
                similarity_score=r["similarity_score"]
            )
            for r in results
        ]
        return KnowledgeSearchResponse(
            query=query,
            total_results=len(items),
            results=items
        )
