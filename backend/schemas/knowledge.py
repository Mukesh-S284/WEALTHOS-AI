"""Knowledge and RAG schemas."""

from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class KnowledgeSearchResultItem(BaseModel):
    doc_id: str
    title: str
    publisher: str
    publication_date: Optional[str] = None
    chunk_index: int
    content: str
    similarity_score: float


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(3, ge=1, le=10)


class KnowledgeSearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[KnowledgeSearchResultItem]
