"""StudyBuddy AI package."""

from .assistant import StudyAssistant
from .tools import answer_question_from_materials, build_learning_plan, create_quiz
from .ollama_client import OllamaClient
from .gemini_client import GeminiClient

__all__ = [
    "StudyAssistant",
    "OllamaClient",
    "GeminiClient",
    "answer_question_from_materials",
    "build_learning_plan",
    "create_quiz",
]
