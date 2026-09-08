from __future__ import annotations

import sys
import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from study_assistant import StudyAssistant
from study_assistant.document_parser import SUPPORTED_EXTENSIONS, extract_text

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
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
assistant = StudyAssistant(materials_dir=MATERIALS_DIR, memory_path=MEMORY_PATH)


@app.errorhandler(413)
def request_too_large(_error: object) -> tuple[dict, int]:
    return jsonify({"error": "Upload is too large. The maximum size is 10 MB."}), 413


@app.errorhandler(500)
def internal_error(_error: object) -> tuple[dict, int]:
    return jsonify({"error": "StudyBuddy AI encountered a server error. Please try again."}), 500


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/api/health")
def health() -> tuple[dict, int]:
    return jsonify(
        {
            "status": "ok",
            "app": "StudyBuddy AI",
            "features": [
                "universal_qa", "rag", "study_plans", "quizzes", "progress",
                "uploads", "pdf_docx_pptx_ingestion", "pwa", "text_to_speech",
            ],
        }
    ), 200


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
    try:
        days = int(payload.get("days", 5) or 5)
    except (TypeError, ValueError):
        return jsonify({"error": "days must be a number."}), 400

    return jsonify({"plan": assistant.create_learning_plan(topic, days=max(1, days))}), 200


@app.route("/api/quiz", methods=["POST"])
def quiz() -> tuple[dict, int]:
    payload = request.get_json(silent=True) or {}
    topic = (payload.get("topic") or "").strip() or "artificial intelligence"
    try:
        count = int(payload.get("count", 3) or 3)
    except (TypeError, ValueError):
        return jsonify({"error": "count must be a number."}), 400

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
    filename = Path(uploaded.filename).name
    if not filename.lower().endswith(SUPPORTED_EXTENSIONS):
        return jsonify({"error": "Supported files: .txt, .md, .pdf, .docx, .pptx."}), 400

    try:
        text = extract_text(filename, uploaded.read()).strip()
    except (ValueError, ImportError, OSError) as exc:
        return jsonify({"error": f"Could not read this file: {exc}"}), 400
    if not text:
        return jsonify({"error": "No readable text was found in this file."}), 400

    destination = MATERIALS_DIR / filename
    destination = destination.with_suffix(".md")
    destination.write_text(text, encoding="utf-8")
    assistant.knowledge.chunks.clear()
    assistant.knowledge._index_materials()
    return jsonify({"message": f"{destination.name} uploaded successfully."}), 201


@app.route("/api/materials")
def materials() -> tuple[dict, int]:
    sources = assistant.knowledge.materials()
    return jsonify({"count": len(sources), "materials": sources}), 200


@app.route("/api/progress", methods=["GET", "POST"])
def progress() -> tuple[dict, int]:
    if request.method == "POST":
        payload = request.get_json(silent=True) or {}
        try:
            completed_topics = int(payload.get("completed_topics", 0) or 0)
            study_hours = float(payload.get("study_hours", 0) or 0)
            quizzes_completed = int(payload.get("quizzes_completed", 0) or 0)
        except (TypeError, ValueError):
            return jsonify({"error": "Progress values must be numbers."}), 400
        current = {
            "completed_topics": max(0, completed_topics),
            "study_hours": max(0, study_hours),
            "quizzes_completed": max(0, quizzes_completed),
        }
        PROGRESS_PATH.write_text(json.dumps(current, indent=2), encoding="utf-8")
        return jsonify(current), 200

    if not PROGRESS_PATH.exists():
        return jsonify({"completed_topics": 0, "study_hours": 0, "quizzes_completed": 0}), 200
    return jsonify(json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
