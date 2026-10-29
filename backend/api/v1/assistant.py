"""AI Financial Assistant API routes."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.user import User
from backend.models.assistant import AssistantSession
from backend.schemas.assistant import (
    AssistantChatRequest,
    AssistantChatResponse,
    AssistantSessionResponse
)
from backend.api.deps import get_current_user
from ai.assistant.agent import FinancialAssistantAgent
from backend.services.knowledge_service import rag_store
from backend.core.exceptions import NotFoundException

router = APIRouter(prefix="/assistant", tags=["AI Finance Assistant"])


@router.post("/chat", response_model=AssistantChatResponse)
def chat_with_assistant(
    payload: AssistantChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a question to the WealthOS AI Assistant.
    The assistant analyzes context, executes registered financial tools against user data,
    retrieves knowledge from verified documents, and returns grounded answers.
    """
    session_id = payload.session_id or str(uuid.uuid4())
    agent = FinancialAssistantAgent(db, rag_store)
    response_data = agent.handle_user_message(current_user, session_id, payload.message)
    return AssistantChatResponse(**response_data)


@router.get("/sessions", response_model=List[AssistantSessionResponse])
def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all user assistant conversation sessions."""
    sessions = db.query(AssistantSession).filter(
        AssistantSession.user_id == current_user.id
    ).order_by(AssistantSession.updated_at.desc()).all()
    return sessions


@router.get("/sessions/{session_id}", response_model=AssistantSessionResponse)
def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve full message history for a conversation session."""
    session = db.query(AssistantSession).filter(
        AssistantSession.id == session_id,
        AssistantSession.user_id == current_user.id
    ).first()
    if not session:
        raise NotFoundException("AssistantSession", session_id)
    return session


@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an assistant conversation session."""
    session = db.query(AssistantSession).filter(
        AssistantSession.id == session_id,
        AssistantSession.user_id == current_user.id
    ).first()
    if not session:
        raise NotFoundException("AssistantSession", session_id)
    db.delete(session)
    db.commit()
    return {"message": "Session deleted successfully."}
