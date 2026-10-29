"""Unit tests for Financial Learning Coach service."""

import pytest
from sqlalchemy.orm import Session
from backend.services.learning_service import LearningService, CURRICULUM
from backend.schemas.learning import QuizSubmissionRequest
from backend.models.user import User
from backend.core.exceptions import NotFoundException


def test_curriculum_coverage_and_structure(db_session: Session, test_user: User):
    service = LearningService(db_session)
    topics = service.list_topics(test_user)
    
    assert len(topics) >= 5
    topic_ids = [t.topic_id for t in topics]
    assert "budgeting_50_30_20" in topic_ids
    assert "emergency_funds" in topic_ids
    assert "sips_dollar_cost_averaging" in topic_ids
    assert "asset_allocation_risk" in topic_ids
    assert "crypto_volatility_risks" in topic_ids

    for t in topics:
        assert t.title
        assert t.completed is False
        assert t.quiz_score is None


def test_get_topic_valid_and_invalid(db_session: Session):
    service = LearningService(db_session)
    topic = service.get_topic("budgeting_50_30_20")
    assert topic.id == "budgeting_50_30_20"
    assert len(topic.quiz) >= 3
    for q in topic.quiz:
        assert len(q.options) >= 2
        assert 0 <= q.correct_option_index < len(q.options)
        assert q.explanation

    with pytest.raises(NotFoundException):
        service.get_topic("non_existent_topic_xyz")


def test_submit_quiz_pass_and_fail(db_session: Session, test_user: User):
    service = LearningService(db_session)
    topic = service.get_topic("budgeting_50_30_20")
    
    # Perfect score submission
    answers = {q.id: q.correct_option_index for q in topic.quiz}
    req = QuizSubmissionRequest(topic_id="budgeting_50_30_20", selected_answers=answers)
    res = service.submit_quiz(test_user, req)

    assert res.score_percentage == 100
    assert res.passed is True
    assert res.correct_count == len(topic.quiz)
    assert len(res.question_results) == len(topic.quiz)
    for qr in res.question_results:
        assert qr["is_correct"] is True

    # Verify updated topic list shows completed
    topics = service.list_topics(test_user)
    t = next(x for x in topics if x.topic_id == "budgeting_50_30_20")
    assert t.completed is True
    assert t.quiz_score == 100
    assert t.quiz_attempts == 1

    # Failing submission (all wrong options)
    wrong_answers = {q.id: (q.correct_option_index + 1) % len(q.options) for q in topic.quiz}
    req2 = QuizSubmissionRequest(topic_id="budgeting_50_30_20", selected_answers=wrong_answers)
    res2 = service.submit_quiz(test_user, req2)

    assert res2.score_percentage == 0
    assert res2.passed is False
    assert res2.correct_count == 0

    # Best score remains 100 in database
    topics_after = service.list_topics(test_user)
    t_after = next(x for x in topics_after if x.topic_id == "budgeting_50_30_20")
    assert t_after.quiz_score == 100
    assert t_after.quiz_attempts == 2
