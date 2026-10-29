"""Financial Learning Coach schemas."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class QuizQuestion(BaseModel):
    id: str
    question: str
    options: List[str]
    correct_option_index: int
    explanation: str


class LessonTopic(BaseModel):
    id: str
    title: str
    category: str
    read_time_minutes: int
    summary: str
    content: str
    quiz: List[QuizQuestion]


class QuizSubmissionRequest(BaseModel):
    topic_id: str
    selected_answers: Dict[str, int] # question_id -> option_index


class QuizResultResponse(BaseModel):
    topic_id: str
    total_questions: int
    correct_count: int
    score_percentage: int
    passed: bool # >= 70%
    question_results: List[Dict[str, Any]]


class UserLearningProgressResponse(BaseModel):
    topic_id: str
    title: str
    completed: bool
    quiz_score: Optional[int] = None
    quiz_attempts: int
    last_studied_at: Optional[str] = None
