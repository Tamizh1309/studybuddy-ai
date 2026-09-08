from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from .knowledge import KnowledgeBase
from .memory import ConversationMemory
from .gemini_client import GeminiClient
from .ollama_client import OllamaClient


@dataclass
class StudyAssistant:
    """A compact RAG-based assistant for learning plans, Q&A, and quizzes."""

    materials_dir: str | Path
    memory_path: str | Path = "memory/history.json"
    knowledge: KnowledgeBase = field(init=False)
    memory: ConversationMemory = field(init=False)
    ollama: OllamaClient = field(init=False)
    gemini: GeminiClient = field(init=False)

    def __post_init__(self) -> None:
        self.knowledge = KnowledgeBase(self.materials_dir)
        self.memory = ConversationMemory(self.memory_path)
        self.ollama = OllamaClient()
        self.gemini = GeminiClient()

    def answer_question(
        self,
        question: str,
        subject: str = "Any subject",
        mode: str = "Explain",
    ) -> str:
        context = self.knowledge.get_context(question, limit=3)
        try:
            answer = self.gemini.chat(question, context, subject, mode)
        except RuntimeError:
            try:
                answer = self.ollama.chat(question, context, subject, mode)
            except RuntimeError:
                answer = self._fallback_answer(question, context)
        self.memory.add_turn(question, answer)
        return answer

    def _fallback_answer(self, question: str, context: str) -> str:
        if "No course material matched" in context:
            return (
                "I could not answer this general question because Gemini and Ollama are offline "
                "and it is not covered by the uploaded course materials. Configure GEMINI_API_KEY "
                f"or start Ollama with `ollama run {self.ollama.model}`, then try again."
            )
        return self._build_answer_from_context(question, context)

    def create_learning_plan(self, topic: str, days: int = 7) -> List[str]:
        matches = self.knowledge.search(topic, limit=3)
        if not matches:
            return [
                f"Start with a short overview of {topic}.",
                "Break the topic into core ideas and examples.",
                "Review the material and summarize what you learned.",
            ]

        plan: List[str] = []
        for day in range(1, max(2, days) + 1):
            focus = matches[min(day - 1, len(matches) - 1)].text
            plan.append(
                f"Day {day}: Review the concept '{topic}' and study the key material: {focus[:120].rstrip()}"
            )
        if len(plan) < days:
            for extra_day in range(len(plan) + 1, days + 1):
                plan.append(f"Day {extra_day}: Revise notes, test recall, and practice exercises around {topic}.")
        return plan[:days]

    def generate_quiz(self, topic: str, count: int = 5) -> List[Dict[str, str]]:
        matches = self.knowledge.search(topic, limit=3)
        if not matches:
            return [{"question": f"What is {topic}?", "answer": "This topic is not yet covered by the document set."}]

        questions: List[Dict[str, str]] = []
        for index, chunk in enumerate(matches, start=1):
            snippet = chunk.text.strip()
            if len(snippet) > 140:
                snippet = snippet[:140].rstrip() + "..."
            questions.append(
                {
                    "question": f"Question {index}: Based on the course material, what is the main idea in the following note: '{snippet}'?",
                    "answer": "Use the relevant course concept described in the linked material and summarize it in your own words.",
                }
            )

        fallback_questions = [
            f"Question {len(questions) + 1}: What is the core definition of {topic}?",
            f"Question {len(questions) + 2}: How can a learner study {topic} effectively over time?",
            f"Question {len(questions) + 3}: Which real-world examples are best connected to {topic}?",
        ]

        for prompt in fallback_questions:
            if len(questions) >= count:
                break
            questions.append(
                {
                    "question": prompt,
                    "answer": "Respond by explaining the concept using evidence from the course material and practical examples.",
                }
            )

        return questions[:count]

    def _build_answer_from_context(self, question: str, context: str) -> str:
        first_match = context.split("\n\n")[0]
        quote = first_match.replace("[", "").replace("]", "").split(" ", 1)[1] if "[" in first_match else first_match
        return (
            f"Based on the course material, {question} is best explained by the key idea that: "
            f"{quote[:300].rstrip()}. "
            "In short, the material emphasizes the core concept, supporting examples, and relevant terminology."
        )

    def get_memory_summary(self) -> str:
        return self.memory.summary()


__all__ = ["StudyAssistant"]
