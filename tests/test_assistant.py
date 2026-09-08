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
    assert all("question" in question for question in ["question"])
    assert all("answer" in item for item in quiz)


def test_memory_summary_tracks_history():
    history_path = Path("memory/test_memory_summary.json")
    assistant = StudyAssistant(materials_dir=Path("materials"), memory_path=history_path)
    assistant.answer_question("What is deep learning?")
    summary = assistant.get_memory_summary()

    assert "Q:" in summary
    assert "deep learning" in summary.lower()
