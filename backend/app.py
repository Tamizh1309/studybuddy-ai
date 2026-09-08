from __future__ import annotations

import sys
import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from study_assistant import StudyAssistant

ROOT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT_DIR / "frontend"
MATERIALS_DIR = ROOT_DIR / "materials"
MEMORY_PATH = ROOT_DIR / "memory" / "web_history.json"
PROGRESS_PATH = ROOT_DIR / "memory" / "progress.json"

app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIR),
    static_url_path="/static",
    template_folder=str(FRONTEND_DIR),
)
assistant = StudyAssistant(materials_dir=MATERIALS_DIR, memory_path=MEMORY_PATH)


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/api/health")
def health() -> tuple[dict, int]:
    return jsonify({"status": "ok", "app": "StudyBuddy AI"}), 200


@app.route("/api/answer", methods=["POST"])
def answer() -> tuple[dict, int]:
    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()
    subject = (payload.get("subject") or "Any subject").strip()
    mode = (payload.get("mode") or "Explain").strip()
    if not question:
        return jsonify({"error": "Question is required."}), 400

    return jsonify({"answer": assistant.answer_question(question, subject, mode)}), 200


@app.route("/api/plan", methods=["POST"])
def learning_plan() -> tuple[dict, int]:
    payload = request.get_json(silent=True) or {}
    topic = (payload.get("topic") or "").strip() or "artificial intelligence"
    days = int(payload.get("days", 5) or 5)

    return jsonify({"plan": assistant.create_learning_plan(topic, days=max(1, days))}), 200


@app.route("/api/quiz", methods=["POST"])
def quiz() -> tuple[dict, int]:
    payload = request.get_json(silent=True) or {}
    topic = (payload.get("topic") or "").strip() or "artificial intelligence"
    count = int(payload.get("count", 3) or 3)

    return jsonify({"quiz": assistant.generate_quiz(topic, count=max(1, count))}), 200


@app.route("/api/memory")
def memory_summary() -> tuple[dict, int]:
    return jsonify({"summary": assistant.get_memory_summary()}), 200


@app.route("/api/memory", methods=["DELETE"])
def clear_memory() -> tuple[dict, int]:
    assistant.memory.clear()
    return jsonify({"message": "Conversation memory cleared."}), 200


@app.route("/api/ollama-status")
def ollama_status() -> tuple[dict, int]:
    return jsonify(
        {
            "available": assistant.ollama.is_available(),
            "model": assistant.ollama.model,
            "gemini_available": assistant.gemini.is_available(),
            "gemini_model": assistant.gemini.model,
        }
    ), 200


@app.route("/api/upload", methods=["POST"])
def upload_material() -> tuple[dict, int]:
    uploaded = request.files.get("file")
    if uploaded is None or not uploaded.filename:
        return jsonify({"error": "A course file is required."}), 400
    if not uploaded.filename.lower().endswith((".txt", ".md")):
        return jsonify({"error": "Only .txt and .md files are supported."}), 400

    destination = MATERIALS_DIR / Path(uploaded.filename).name
    destination.write_text(uploaded.read().decode("utf-8", errors="ignore"), encoding="utf-8")
    assistant.knowledge.chunks.clear()
    assistant.knowledge._index_materials()
    return jsonify({"message": f"{destination.name} uploaded successfully."}), 201


@app.route("/api/progress", methods=["GET", "POST"])
def progress() -> tuple[dict, int]:
    if request.method == "POST":
        payload = request.get_json(silent=True) or {}
        current = {
            "completed_topics": max(0, int(payload.get("completed_topics", 0) or 0)),
            "study_hours": max(0, float(payload.get("study_hours", 0) or 0)),
            "quizzes_completed": max(0, int(payload.get("quizzes_completed", 0) or 0)),
        }
        PROGRESS_PATH.write_text(json.dumps(current, indent=2), encoding="utf-8")
        return jsonify(current), 200

    if not PROGRESS_PATH.exists():
        return jsonify({"completed_topics": 0, "study_hours": 0, "quizzes_completed": 0}), 200
    return jsonify(json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
