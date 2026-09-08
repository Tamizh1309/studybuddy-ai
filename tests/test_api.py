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


def test_api_agent_architect(client):
    response = client.post(
        "/api/agent/architect",
        json={"goal": "Master Machine Learning Foundations", "days": 3, "engine": "local"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "curriculum" in data
    assert "diagnostic_quiz" in data
    assert "flashcards" in data
    assert "reasoning_trace" in data
    assert len(data["reasoning_trace"]) == 4


def test_api_concept_map(client):
    response = client.post(
        "/api/concept-map",
        json={"topic": "Deep Learning", "engine": "local"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "root" in data
    assert "branches" in data
    assert "mermaid" in data


def test_api_code_explain(client):
    response = client.post(
        "/api/code-explain",
        json={
            "code": "def binary_search(arr, target):\n    low, high = 0, len(arr) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    return -1",
            "language": "python",
            "analysis_type": "complexity",
            "engine": "local",
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "complexity" in data
    assert "breakdown" in data
    assert "summary" in data


def test_api_material_content(client):
    # Get available materials first
    materials_res = client.get("/api/materials")
    assert materials_res.status_code == 200
    m_data = materials_res.get_json()
    if m_data.get("materials"):
        first_doc = m_data["materials"][0]
        content_res = client.get(f"/api/materials/{first_doc}/content")
        assert content_res.status_code == 200
        c_data = content_res.get_json()
        assert "content" in c_data
        assert len(c_data["content"]) > 0


def test_api_progress_streaks_badges(client):
    # Test GET progress
    get_res = client.get("/api/progress")
    assert get_res.status_code == 200
    data = get_res.get_json()
    assert "streak_days" in data
    assert "badges" in data
    assert "First Steps" in data["badges"]

    # Test POST progress update
    post_res = client.post(
        "/api/progress",
        json={"completed_topics": 2, "study_hours": 1.5, "quizzes_completed": 2, "streak_days": 3},
    )
    assert post_res.status_code == 200
    updated = post_res.get_json()
    assert updated["streak_days"] == 3
    assert "Curriculum Explorer" in updated["badges"]
    assert "Focus Titan" in updated["badges"]
    assert "Quiz Ace" in updated["badges"]

