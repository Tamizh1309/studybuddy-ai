import json
import pytest
from backend.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"StudyBuddy" in response.data


def test_api_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["app"] == "StudyBuddy AI"


def test_api_ai_status(client):
    response = client.get("/api/ai-status")
    assert response.status_code == 200
    data = response.get_json()
    assert "available" in data
    assert "gemini_available" in data
    assert "groq_available" in data
    assert "engines" in data



def test_api_answer(client):
    response = client.post(
        "/api/answer",
        json={"question": "What is AI?", "subject": "CS", "mode": "Explain", "engine": "local"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "answer" in data
    assert len(data["answer"]) > 0


def test_api_flashcards(client):
    response = client.post(
        "/api/flashcards",
        json={"topic": "artificial intelligence", "count": 2, "engine": "local"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "flashcards" in data
    assert len(data["flashcards"]) >= 1


def test_api_quiz_and_evaluate(client):
    quiz_res = client.post(
        "/api/quiz",
        json={"topic": "artificial intelligence", "count": 2, "engine": "local"},
    )
    assert quiz_res.status_code == 200
    quiz_data = quiz_res.get_json()
    assert "quiz" in quiz_data

    eval_res = client.post(
        "/api/quiz/evaluate",
        json={
            "topic": "artificial intelligence",
            "questions": quiz_data["quiz"],
            "answers": [q.get("answer", "") for q in quiz_data["quiz"]],
            "engine": "local",
        },
    )
    assert eval_res.status_code == 200
    eval_data = eval_res.get_json()
    assert "score" in eval_data
    assert "percentage" in eval_data


def test_api_pomodoro(client):
    response = client.post(
        "/api/pomodoro",
        json={"duration_minutes": 25},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "study_hours" in data
    assert data["logged_minutes"] == 25


def test_api_summarize(client):
    response = client.post(
        "/api/summarize",
        json={"topic": "artificial intelligence", "engine": "local"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "summary" in data
    assert "key_terms" in data


def test_api_export(client):
    response = client.post(
        "/api/export",
        json={"type": "plan", "content": "# Plan", "topic": "AI"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "filename" in data
