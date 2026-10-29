"""Financial Learning Coach API routes."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services.learning_service import LearningService
from backend.schemas.learning import (
    LessonTopic,
    UserLearningProgressResponse,
    QuizSubmissionRequest,
    QuizResultResponse
)
from backend.api.deps import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/learning", tags=["Financial Learning Coach"])


@router.get("/topics", response_model=List[UserLearningProgressResponse])
def list_topics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all financial education topics and current user progress."""
    service = LearningService(db)
    return service.list_topics(current_user)


@router.get("/topics/{topic_id}", response_model=LessonTopic)
def get_topic(
    topic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve full lesson material and interactive quiz for a topic."""
    service = LearningService(db)
    return service.get_topic(topic_id)


@router.post("/quiz/submit", response_model=QuizResultResponse)
def submit_quiz(
    payload: QuizSubmissionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit quiz answers, receive immediate scored feedback with explanations, and update progress."""
    service = LearningService(db)
    return service.submit_quiz(current_user, payload)
