from pathlib import Path

from study_assistant import StudyAssistant


def test_answer_question_from_materials():
    assistant = StudyAssistant(materials_dir=Path("materials"), memory_path=Path("memory/test_history.json"))
    response = assistant.answer_question("What is machine learning?")

    assert "machine learning" in response.lower()
    assert (
        "course material" in response.lower()
        or "course context" in response.lower()
        or "artificial intelligence" in response.lower()
    )


def test_learning_plan_generation():
    assistant = StudyAssistant(materials_dir=Path("materials"), memory_path=Path("memory/test_history.json"))
    plan = assistant.create_learning_plan("artificial intelligence", days=4)

    assert len(plan) == 4
    assert all("Day" in item for item in plan)


def test_quiz_generation():
    assistant = StudyAssistant(materials_dir=Path("materials"), memory_path=Path("memory/test_history.json"))
    quiz = assistant.generate_quiz("artificial intelligence", count=2)

    assert len(quiz) == 2
    assert all("question" in item for item in quiz)
    assert all("answer" in item for item in quiz)


def test_quiz_evaluation():
    assistant = StudyAssistant(materials_dir=Path("materials"), memory_path=Path("memory/test_history.json"))
    quiz = assistant.generate_quiz("artificial intelligence", count=2)
    # Give the correct answers
    user_answers = [q.get("correct_index", 0) for q in quiz]
    evaluation = assistant.evaluate_quiz_answers("artificial intelligence", quiz, user_answers)

    assert evaluation["total_questions"] == 2
    assert evaluation["correct_answers"] == 2
    assert evaluation["percentage"] == 100.0
    assert "feedback" in evaluation
    assert len(evaluation["details"]) == 2


def test_flashcard_generation():
    assistant = StudyAssistant(materials_dir=Path("materials"), memory_path=Path("memory/test_history.json"))
    cards = assistant.generate_flashcards("artificial intelligence", count=4)

    assert len(cards) == 4
    for card in cards:
        assert "front" in card
        assert "back" in card
        assert "hint" in card


def test_material_summarization():
    assistant = StudyAssistant(materials_dir=Path("materials"), memory_path=Path("memory/test_history.json"))
    summary = assistant.summarize_material("artificial intelligence")

    assert "summary" in summary
    assert "key_concepts" in summary
    assert "takeaways" in summary
    assert isinstance(summary["takeaways"], list)


def test_memory_summary_tracks_history():
    history_path = Path("memory/test_memory_summary.json")
    assistant = StudyAssistant(materials_dir=Path("materials"), memory_path=history_path)
    assistant.answer_question("What is deep learning?")
    summary = assistant.get_memory_summary()

    assert "Q:" in summary
    assert "deep learning" in summary.lower()


def test_agent_architect():
    assistant = StudyAssistant(materials_dir=Path("materials"), memory_path=Path("memory/test_history.json"))
    result = assistant.run_study_architect("Prepare for Neural Networks Midterm", days=3, engine="local")

    assert result["days"] == 3
    assert len(result["reasoning_trace"]) == 4
    assert len(result["curriculum"]) == 3
    assert len(result["diagnostic_quiz"]) >= 1
    assert len(result["flashcards"]) >= 1


def test_concept_map_generation():
    assistant = StudyAssistant(materials_dir=Path("materials"), memory_path=Path("memory/test_history.json"))
    result = assistant.generate_concept_map("artificial intelligence", engine="local")

    assert "root" in result
    assert "branches" in result
    assert len(result["branches"]) >= 2
    assert "mermaid" in result
    assert "graph TD" in result["mermaid"]


def test_explain_code():
    assistant = StudyAssistant(materials_dir=Path("materials"), memory_path=Path("memory/test_history.json"))
    code_sample = "def fib(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a"
    result = assistant.explain_code(code_sample, language="python", analysis_type="complexity", engine="local")

    assert "complexity" in result
    assert result["complexity"]["time"] in ("O(n)", "O(1)")
    assert "breakdown" in result
    assert len(result["breakdown"]) >= 1
    assert "suggestions" in result

