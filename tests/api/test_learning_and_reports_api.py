"""API integration tests for Learning Coach, Scam Awareness, and Health Reports."""


def test_learning_endpoints_flow(client, auth_headers):
    # 1. List topics
    resp = client.get("/api/v1/learning/topics", headers=auth_headers)
    assert resp.status_code == 200
    topics = resp.json()
    assert isinstance(topics, list)
    assert len(topics) >= 5
    first_id = topics[0]["topic_id"]

    # 2. Get specific topic details
    resp2 = client.get(f"/api/v1/learning/topics/{first_id}", headers=auth_headers)
    assert resp2.status_code == 200
    topic_data = resp2.json()
    assert topic_data["id"] == first_id
    assert "content" in topic_data
    assert len(topic_data["quiz"]) >= 1

    # 3. Submit quiz
    quiz = topic_data["quiz"]
    answers = {q["id"]: q["correct_option_index"] for q in quiz}
    submit_payload = {
        "topic_id": first_id,
        "selected_answers": answers
    }
    resp3 = client.post("/api/v1/learning/quiz/submit", json=submit_payload, headers=auth_headers)
    assert resp3.status_code == 200
    result = resp3.json()
    assert result["score_percentage"] == 100
    assert result["passed"] is True
    assert result["correct_count"] == len(quiz)


def test_scam_analysis_api(client, auth_headers):
    payload = {
        "message_text": "Double your money in 48 hours! 100% risk-free guaranteed return! Send OTP to activate your account."
    }
    resp = client.post("/api/v1/scam/analyze", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["threat_score"] >= 35
    assert data["risk_level"] in ("HIGH_RISK", "CRITICAL_SCAM")
    assert len(data["detected_red_flags"]) >= 2
    assert len(data["official_verification_steps"]) > 0


def test_health_report_api(client, auth_headers):
    resp = client.get("/api/v1/reports/health", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert 0 <= data["overall_health_score"] <= 100
    assert data["rating"] in ("Excellent", "Good", "Fair", "Needs Attention")
    assert len(data["indicators"]) == 7
    assert "disclaimer" in data
