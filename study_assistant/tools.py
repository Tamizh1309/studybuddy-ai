from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .assistant import StudyAssistant


def answer_question_from_materials(question: str, materials_dir: str | Path) -> str:
    assistant = StudyAssistant(materials_dir=materials_dir, memory_path=Path("memory/tool_history.json"))
    return assistant.answer_question(question)


def build_learning_plan(topic: str, materials_dir: str | Path, days: int = 7) -> List[str]:
    assistant = StudyAssistant(materials_dir=materials_dir, memory_path=Path("memory/tool_history.json"))
    return assistant.create_learning_plan(topic, days=days)


def create_quiz(topic: str, materials_dir: str | Path, count: int = 5) -> List[Dict[str, str]]:
    assistant = StudyAssistant(materials_dir=materials_dir, memory_path=Path("memory/tool_history.json"))
    return assistant.generate_quiz(topic, count=count)


__all__ = ["answer_question_from_materials", "build_learning_plan", "create_quiz"]
