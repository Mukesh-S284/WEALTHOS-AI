"""Knowledge and RAG Document database models."""

import uuid
from datetime import datetime, timezone, date
from sqlalchemy import Column, String, DateTime, Date, Text, Integer, Boolean, JSON, Index
from backend.core.database import Base


def get_utc_now():
    return datetime.now(timezone.utc)


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    source_publisher = Column(String(100), nullable=False) # e.g. "SEC", "FINRA", "Investopedia", "WealthOS Research"
    source_url = Column(String(500), nullable=True)
    publication_date = Column(Date, nullable=True)
    document_type = Column(String(50), default="educational", nullable=False) # regulatory, educational, disclosure
    ingestion_status = Column(String(20), default="completed", nullable=False) # pending, completed, failed
    chunk_count = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True) # list of floats for portable cosine similarity
    metadata_info = Column(JSON, default=dict, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    __table_args__ = (
        Index("idx_chunk_doc_index", "document_id", "chunk_index"),
    )
