"""Knowledge Base and RAG API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services.knowledge_service import KnowledgeService
from backend.schemas.knowledge import KnowledgeSearchRequest, KnowledgeSearchResponse
from backend.api.deps import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/knowledge", tags=["RAG Financial Knowledge"])


@router.post("/search", response_model=KnowledgeSearchResponse)
def search_knowledge(
    payload: KnowledgeSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search approved financial education documents and disclosures using vector similarity."""
    service = KnowledgeService(db)
    return service.search_knowledge(payload.query, top_k=payload.top_k)
