from pathlib import Path

from study_assistant import StudyAssistant


def test_answer_question_from_materials():
    assistant = StudyAssistant(materials_dir=Path("materials"), memory_path=Path("memory/test_history.json"))
    response = assistant.answer_question("What is machine learning?")

    assert "machine learning" in response.lower()
    assert "course material" in response.lower()


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
