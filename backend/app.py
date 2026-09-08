from __future__ import annotations

import sys
import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request, Response

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from study_assistant import StudyAssistant
from study_assistant.document_parser import SUPPORTED_EXTENSIONS, extract_text

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
                "universal_qa",
                "rag",
                "study_plans",
                "quizzes",
                "interactive_quiz_evaluation",
                "smart_flashcards",
                "document_summarizer",
                "pomodoro_focus_tracking",
                "study_export",
                "progress",
                "uploads",
                "pdf_docx_pptx_ingestion",
                "pwa",
                "text_to_speech",
                "agent_architect",
                "concept_map",
                "code_explainer",
                "document_viewer",
                "streaks_and_badges",
            ],
        }
    ), 200


@app.route("/api/answer", methods=["POST"])
def answer() -> tuple[dict, int]:
    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()
    subject = (payload.get("subject") or "Any subject").strip()
    mode = (payload.get("mode") or "Explain").strip()
    engine = (payload.get("engine") or "auto").strip().lower()
    if not question:
        return jsonify({"error": "Question is required."}), 400

    return jsonify({"answer": assistant.answer_question(question, subject, mode, engine=engine)}), 200


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


@app.route("/api/quiz/evaluate", methods=["POST"])
def evaluate_quiz() -> tuple[dict, int]:
    payload = request.get_json(silent=True) or {}
    topic = (payload.get("topic") or "").strip() or "General Study"
    questions = payload.get("questions") or []
    user_answers = payload.get("user_answers") or payload.get("answers") or []

    if not questions:
        return jsonify({"error": "Questions are required for evaluation."}), 400

    result = assistant.evaluate_quiz_answers(topic, questions, user_answers)

    # Provide alias keys for frontend and test convenience
    result["score"] = result.get("correct_answers", 0)
    result["total"] = result.get("total_questions", len(questions))
    result["breakdown"] = result.get("details", [])

    # Auto-increment quizzes_completed in user progress
    try:
        current_progress = _get_or_create_progress()
        current_progress["quizzes_completed"] = current_progress.get("quizzes_completed", 0) + 1
        PROGRESS_PATH.write_text(json.dumps(current_progress, indent=2), encoding="utf-8")
        result["progress"] = current_progress
    except Exception:
        pass

    return jsonify(result), 200


@app.route("/api/flashcards", methods=["POST"])
def flashcards() -> tuple[dict, int]:
    payload = request.get_json(silent=True) or {}
    topic = (payload.get("topic") or "").strip() or "artificial intelligence"
    try:
        count = int(payload.get("count", 6) or 6)
    except (TypeError, ValueError):
        count = 6

    cards = assistant.generate_flashcards(topic, count=max(1, count))
    return jsonify({"topic": topic, "count": len(cards), "flashcards": cards}), 200


@app.route("/api/summarize", methods=["POST"])
def summarize() -> tuple[dict, int]:
    payload = request.get_json(silent=True) or {}
    topic = (payload.get("topic") or "").strip()
    summary_data = assistant.summarize_material(topic)
    summary_data["key_terms"] = summary_data.get("key_concepts", [])
    return jsonify(summary_data), 200


@app.route("/api/pomodoro", methods=["POST"])
def log_pomodoro() -> tuple[dict, int]:
    """Log completed focus minutes and credit directly to study hours."""
    payload = request.get_json(silent=True) or {}
    try:
        minutes = float(payload.get("duration_minutes") or payload.get("minutes", 25) or 25)
    except (TypeError, ValueError):
        minutes = 25.0

    hours_added = round(max(1.0, minutes) / 60.0, 2)
    current_progress = _get_or_create_progress()
    current_progress["study_hours"] = round(current_progress.get("study_hours", 0) + hours_added, 2)
    PROGRESS_PATH.write_text(json.dumps(current_progress, indent=2), encoding="utf-8")

    return jsonify({
        "message": f"Great focus session! Added {hours_added} hr ({minutes:.0f} mins) to your progress.",
        "progress": current_progress,
        "study_hours": current_progress.get("study_hours", 0.0),
        "logged_minutes": int(minutes),
    }), 200


@app.route("/api/export", methods=["POST"])
def export_content() -> tuple[dict, int]:
    """Generate markdown or text export for offline study."""
    payload = request.get_json(silent=True) or {}
    export_type = payload.get("type", "study_guide")
    title = payload.get("title") or payload.get("topic") or "StudyBuddy AI Notes"
    data = payload.get("data") or payload.get("content")

    markdown_lines = [f"# {title}", f"*Generated by StudyBuddy AI*", "---", ""]

    if export_type == "plan" and isinstance(data, list):
        markdown_lines.append("## Daily Study Plan")
        for item in data:
            markdown_lines.append(f"- {item}")
    elif export_type == "quiz" and isinstance(data, list):
        markdown_lines.append("## Practice Quiz & Answer Key")
        for idx, item in enumerate(data, 1):
            markdown_lines.append(f"### Q{idx}: {item.get('question')}")
            if item.get("options"):
                for opt_idx, opt in enumerate(item["options"]):
                    markdown_lines.append(f"  - [{chr(65+opt_idx)}] {opt}")
            markdown_lines.append(f"\n**Correct Answer**: {item.get('answer')}")
            if item.get("explanation"):
                markdown_lines.append(f"**Explanation**: {item.get('explanation')}\n")
    elif export_type == "flashcards" and isinstance(data, list):
        markdown_lines.append("## Active Recall Flashcards")
        for idx, card in enumerate(data, 1):
            markdown_lines.append(f"### Card {idx} [{card.get('tag', 'General')}]")
            markdown_lines.append(f"**Front (Prompt)**: {card.get('front')}")
            markdown_lines.append(f"**Back (Answer)**: {card.get('back')}")
            if card.get("hint"):
                markdown_lines.append(f"*Hint*: {card.get('hint')}\n")
    elif export_type == "summary" and isinstance(data, dict):
        markdown_lines.append("## Executive Summary")
        markdown_lines.append(data.get("summary", ""))
        markdown_lines.append("\n### Key Concepts")
        for concept in data.get("key_concepts", []):
            markdown_lines.append(f"- **{concept.get('term')}**: {concept.get('definition')}")
        markdown_lines.append("\n### Actionable Takeaways")
        for take in data.get("takeaways", []):
            markdown_lines.append(f"- {take}")
    else:
        markdown_lines.append(str(data))

    content = "\n".join(markdown_lines)
    return jsonify({
        "status": "success",
        "markdown": content,
        "filename": f"{title.lower().replace(' ', '_')}.md"
    }), 200


@app.route("/api/memory")
def memory_summary() -> tuple[dict, int]:
    return jsonify({"summary": assistant.get_memory_summary()}), 200


@app.route("/api/memory", methods=["DELETE"])
def clear_memory() -> tuple[dict, int]:
    assistant.memory.clear()
    return jsonify({"message": "Conversation memory cleared."}), 200


@app.route("/api/ollama-status")
@app.route("/api/ai-status")
def ai_status() -> tuple[dict, int]:
    gemini_avail = assistant.gemini.is_available()
    groq_avail = assistant.groq.is_available()
    ollama_avail = assistant.ollama.is_available()

    primary_provider = (
        "Gemini" if gemini_avail else ("Groq" if groq_avail else ("Ollama" if ollama_avail else "Local RAG"))
    )

    return jsonify(
        {
            "primary": primary_provider,
            "gemini_available": gemini_avail,
            "gemini_model": assistant.gemini.model,
            "groq_available": groq_avail,
            "groq_model": assistant.groq.model,
            "ollama_available": ollama_avail,
            "ollama_model": assistant.ollama.model,
            "available": ollama_avail,
            "model": assistant.ollama.model,
            "engines": ["auto", "gemini", "groq", "ollama", "local"],
        }
    ), 200


@app.route("/api/agent/architect", methods=["POST"])
def agent_architect() -> tuple[dict, int]:
    """Autonomous agentic pipeline generating holistic study plan, diagnostic quiz, and recall deck."""
    payload = request.get_json(silent=True) or {}
    goal = (payload.get("goal") or "").strip() or "Master Artificial Intelligence Foundations"
    try:
        days = int(payload.get("days", 5) or 5)
    except (TypeError, ValueError):
        days = 5
    engine = (payload.get("engine") or "auto").strip().lower()

    result = assistant.run_study_architect(goal, days=days, engine=engine)

    # Award "Agent Architect" badge
    progress_data = _get_or_create_progress()
    badges = set(progress_data.get("badges", []))
    badges.add("Agent Architect")
    progress_data["badges"] = sorted(list(badges))
    PROGRESS_PATH.write_text(json.dumps(progress_data, indent=2), encoding="utf-8")
    result["progress"] = progress_data

    return jsonify(result), 200


@app.route("/api/concept-map", methods=["POST"])
def concept_map() -> tuple[dict, int]:
    """Generate structured concept nodes, relationships, and Mermaid graph syntax."""
    payload = request.get_json(silent=True) or {}
    topic = (payload.get("topic") or "").strip()
    engine = (payload.get("engine") or "auto").strip().lower()

    result = assistant.generate_concept_map(topic=topic, engine=engine)
    return jsonify(result), 200


@app.route("/api/code-explain", methods=["POST"])
def code_explain() -> tuple[dict, int]:
    """Breakdown code snippets with Big-O time/space complexity, edge cases, and optimizations."""
    payload = request.get_json(silent=True) or {}
    code = (payload.get("code") or "").strip()
    language = (payload.get("language") or "python").strip().lower()
    analysis_type = (payload.get("analysis_type") or "explain").strip().lower()
    engine = (payload.get("engine") or "auto").strip().lower()

    if not code:
        return jsonify({"error": "Code snippet is required."}), 400

    result = assistant.explain_code(code, language=language, analysis_type=analysis_type, engine=engine)
    return jsonify(result), 200


@app.route("/api/materials/<path:filename>/content")
def material_content(filename: str) -> tuple[dict, int]:
    """Read full text content of an ingested document for in-browser viewer."""
    clean_name = Path(filename).name
    target_path = MATERIALS_DIR / clean_name
    if not target_path.exists():
        target_path = MATERIALS_DIR / f"{clean_name}.md"
    if not target_path.exists():
        # Try matching without suffix
        matches = list(MATERIALS_DIR.glob(f"{clean_name}*"))
        if matches:
            target_path = matches[0]
        else:
            return jsonify({"error": f"Material '{clean_name}' not found."}), 404

    try:
        content = target_path.read_text(encoding="utf-8")
        return jsonify({"filename": target_path.name, "content": content, "size_bytes": len(content)}), 200
    except Exception as exc:
        return jsonify({"error": f"Could not read material: {exc}"}), 500


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


def _get_or_create_progress() -> dict:
    default_progress = {
        "completed_topics": 0,
        "study_hours": 0.0,
        "quizzes_completed": 0,
        "streak_days": 1,
        "badges": ["First Steps"],
    }
    if not PROGRESS_PATH.exists():
        return default_progress
    try:
        data = json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
        # Ensure keys exist
        data.setdefault("streak_days", 1)
        data.setdefault("badges", ["First Steps"])
        # Evaluate badges dynamically based on milestones
        badges = set(data.get("badges", []))
        badges.add("First Steps")
        if data.get("completed_topics", 0) >= 1:
            badges.add("Curriculum Explorer")
        if data.get("study_hours", 0.0) >= 0.25:
            badges.add("Focus Titan")
        if data.get("quizzes_completed", 0) >= 1:
            badges.add("Quiz Ace")
        data["badges"] = sorted(list(badges))
        return data
    except Exception:
        return default_progress


@app.route("/api/progress", methods=["GET", "POST"])
def progress() -> tuple[dict, int]:
    current = _get_or_create_progress()
    if request.method == "POST":
        payload = request.get_json(silent=True) or {}
        try:
            completed_topics = int(payload.get("completed_topics", current.get("completed_topics", 0)) or 0)
            study_hours = float(payload.get("study_hours", current.get("study_hours", 0.0)) or 0)
            quizzes_completed = int(payload.get("quizzes_completed", current.get("quizzes_completed", 0)) or 0)
            streak_days = int(payload.get("streak_days", current.get("streak_days", 1)) or 1)
        except (TypeError, ValueError):
            return jsonify({"error": "Progress values must be numbers."}), 400

        current["completed_topics"] = max(0, completed_topics)
        current["study_hours"] = max(0.0, round(study_hours, 2))
        current["quizzes_completed"] = max(0, quizzes_completed)
        current["streak_days"] = max(1, streak_days)

        # Dynamic badge updates
        badges = set(current.get("badges", ["First Steps"]))
        if current["completed_topics"] >= 1:
            badges.add("Curriculum Explorer")
        if current["study_hours"] >= 0.25:
            badges.add("Focus Titan")
        if current["quizzes_completed"] >= 1:
            badges.add("Quiz Ace")
        current["badges"] = sorted(list(badges))

        PROGRESS_PATH.write_text(json.dumps(current, indent=2), encoding="utf-8")
        return jsonify(current), 200

    return jsonify(current), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
