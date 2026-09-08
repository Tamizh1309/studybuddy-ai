from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .knowledge import KnowledgeBase
from .memory import ConversationMemory
from .gemini_client import GeminiClient
from .groq_client import GroqClient
from .ollama_client import OllamaClient


@dataclass
class StudyAssistant:
    """An Agentic RAG-based assistant for study plans, Q&A, quizzes, flashcards, and summaries."""

    materials_dir: str | Path
    memory_path: str | Path = "memory/history.json"
    knowledge: KnowledgeBase = field(init=False)
    memory: ConversationMemory = field(init=False)
    gemini: GeminiClient = field(init=False)
    groq: GroqClient = field(init=False)
    ollama: OllamaClient = field(init=False)

    def __post_init__(self) -> None:
        self.knowledge = KnowledgeBase(self.materials_dir)
        self.memory = ConversationMemory(self.memory_path)
        self.gemini = GeminiClient()
        self.groq = GroqClient()
        self.ollama = OllamaClient()

    def answer_question(
        self,
        question: str,
        subject: str = "Any subject",
        mode: str = "Explain",
        engine: str = "auto",
    ) -> str:
        context = self.knowledge.get_context(question, limit=3)
        answer: Optional[str] = None

        if engine == "gemini":
            try:
                answer = self.gemini.chat(question, context, subject, mode)
            except RuntimeError as exc:
                answer = f"Gemini Error: {exc}. Falling back to local RAG.\n\n" + self._fallback_answer(question, context)
        elif engine == "groq":
            try:
                answer = self.groq.chat(question, context, subject, mode)
            except RuntimeError as exc:
                answer = f"Groq Error: {exc}. Falling back to local RAG.\n\n" + self._fallback_answer(question, context)
        elif engine == "ollama":
            try:
                answer = self.ollama.chat(question, context, subject, mode)
            except RuntimeError as exc:
                answer = f"Ollama Error: {exc}. Falling back to local RAG.\n\n" + self._fallback_answer(question, context)
        elif engine == "local":
            answer = self._fallback_answer(question, context)
        else:
            # Auto cascading fallback: Gemini -> Groq -> Ollama -> local RAG
            for client in (self.gemini, self.groq, self.ollama):
                if client.is_available():
                    try:
                        answer = client.chat(question, context, subject, mode)
                        break
                    except RuntimeError:
                        continue

            if answer is None:
                answer = self._fallback_answer(question, context)

        self.memory.add_turn(question, answer)
        return answer

    def _fallback_answer(self, question: str, context: str) -> str:
        if "No course material matched" in context:
            return (
                "I could not answer this general question because configured AI providers (Gemini, Groq, Ollama) "
                "are offline or not configured with an API key, and the topic is not covered in your uploaded course materials. "
                "Set GEMINI_API_KEY, GROQ_API_KEY, or start Ollama to enable unrestricted AI answering."
            )
        return self._build_answer_from_context(question, context)

    def create_learning_plan(self, topic: str, days: int = 7) -> List[str]:
        matches = self.knowledge.search(topic, limit=3)
        if not matches:
            return [
                f"Day 1: Start with a foundational overview of {topic}.",
                f"Day 2: Break down core principles and terminology of {topic}.",
                f"Day 3: Review practical examples and case studies in {topic}.",
                f"Day 4: Work through practice problems and self-assessment questions.",
                f"Day 5: Revise key concepts and compile summary study notes.",
            ][:days]

        plan: List[str] = []
        for day in range(1, max(2, days) + 1):
            focus = matches[min(day - 1, len(matches) - 1)].text
            plan.append(
                f"Day {day}: Study '{topic}' fundamentals from material: {focus[:120].rstrip()}"
            )
        if len(plan) < days:
            for extra_day in range(len(plan) + 1, days + 1):
                plan.append(f"Day {extra_day}: Revise notes, test recall, and practice exercises around {topic}.")
        return plan[:days]

    def generate_quiz(self, topic: str, count: int = 5) -> List[Dict[str, Any]]:
        matches = self.knowledge.search(topic, limit=count)
        questions: List[Dict[str, Any]] = []

        if matches:
            for index, chunk in enumerate(matches, start=1):
                snippet = chunk.text.strip()
                if len(snippet) > 130:
                    snippet = snippet[:130].rstrip() + "..."
                questions.append(
                    {
                        "id": index,
                        "question": f"Based on course note ({chunk.source}), what is the primary takeaway of: '{snippet}'?",
                        "options": [
                            f"It explains the core definition and mechanism of {topic}.",
                            f"It contradicts standard theories in {topic}.",
                            f"It only applies in theoretical simulations, not real practice.",
                            "It describes an unrelated historical footnote.",
                        ],
                        "correct_index": 0,
                        "answer": f"It highlights the core mechanism from {chunk.source}: '{snippet}'.",
                        "explanation": f"Grounded directly in {chunk.source}. Review this source note for complete details.",
                    }
                )

        fallback_templates = [
            (
                f"What is the foundational definition of {topic}?",
                [f"A core discipline/system focused on {topic} principles.", "An obsolete computational framework.", "A marketing term without technical basis.", "None of the above."],
                0,
                f"The core definition establishes fundamental axioms and working methods of {topic}.",
            ),
            (
                f"Which scenario best demonstrates practical application of {topic}?",
                [f"Solving domain problems using methodical {topic} workflows.", "Random guesswork without verified data.", "Ignoring empirical evaluation metrics.", "Discarding course guidelines."],
                0,
                f"Real-world efficacy requires structured application of {topic} concepts.",
            ),
            (
                f"What is a recommended strategy to master {topic}?",
                [f"Active recall, progressive testing, and concept mapping.", "Passive rereading without practice.", "Memorizing terms without understanding.", "Skipping foundation chapters."],
                0,
                "Cognitive science shows active recall and spaced repetition maximize retention.",
            ),
            (
                f"How does {topic} integrate with broader fields?",
                [f"It connects theory with empirical implementation.", "It operates in total isolation from other subjects.", "It replaces all mathematical foundations.", "It has no practical utility."],
                0,
                "Interdisciplinary synergy creates robust learning and practical value.",
            ),
        ]

        for q_text, options, c_idx, expl in fallback_templates:
            if len(questions) >= count:
                break
            questions.append(
                {
                    "id": len(questions) + 1,
                    "question": q_text,
                    "options": options,
                    "correct_index": c_idx,
                    "answer": options[c_idx],
                    "explanation": expl,
                }
            )

        return questions[:count]

    def evaluate_quiz_answers(
        self,
        topic: str,
        questions: List[Dict[str, Any]],
        user_answers: List[Any],
    ) -> Dict[str, Any]:
        """Grade submitted quiz answers and return score, breakdown, and personalized recommendations."""
        total = len(questions)
        correct_count = 0
        details = []

        for idx, q in enumerate(questions):
            user_ans = user_answers[idx] if idx < len(user_answers) else None
            correct_idx = q.get("correct_index", 0)
            correct_text = q.get("options", [q.get("answer", "")])[correct_idx] if q.get("options") else q.get("answer", "")

            is_correct = False
            if isinstance(user_ans, int):
                is_correct = (user_ans == correct_idx)
                selected_text = q.get("options", [])[user_ans] if 0 <= user_ans < len(q.get("options", [])) else "No selection"
            elif isinstance(user_ans, str):
                is_correct = (user_ans.strip().lower() in correct_text.lower()) or (str(correct_idx) == user_ans.strip())
                selected_text = user_ans
            else:
                selected_text = "Unanswered"

            if is_correct:
                correct_count += 1

            details.append(
                {
                    "question_id": q.get("id", idx + 1),
                    "question": q.get("question"),
                    "user_answer": selected_text,
                    "correct_answer": correct_text,
                    "is_correct": is_correct,
                    "explanation": q.get("explanation") or q.get("answer"),
                }
            )

        percentage = round((correct_count / total * 100), 1) if total > 0 else 0
        feedback = (
            "Outstanding work! You have demonstrated strong mastery of this topic."
            if percentage >= 80
            else "Good effort! Revise the flagged questions to solidify your understanding."
            if percentage >= 50
            else "Needs more practice. Spend some time reviewing course notes and flashcards before retrying."
        )

        return {
            "topic": topic,
            "total_questions": total,
            "correct_answers": correct_count,
            "percentage": percentage,
            "feedback": feedback,
            "details": details,
        }

    def generate_flashcards(self, topic: str, count: int = 6) -> List[Dict[str, str]]:
        """Generate interactive flashcards for active recall study."""
        matches = self.knowledge.search(topic, limit=count)
        flashcards: List[Dict[str, str]] = []

        if matches:
            for idx, chunk in enumerate(matches, start=1):
                clean_text = chunk.text.strip().replace("\n", " ")
                # Split into short front/back
                sentences = [s.strip() for s in clean_text.split(".") if len(s.strip()) > 15]
                if len(sentences) >= 2:
                    front = f"Concept in {chunk.source}: {sentences[0]}?"
                    back = ". ".join(sentences[1:3]) + "."
                else:
                    front = f"What is the key takeaway in {chunk.source} regarding '{topic}'?"
                    back = clean_text[:200]

                flashcards.append(
                    {
                        "id": str(idx),
                        "front": front,
                        "back": back,
                        "hint": f"Refer to {chunk.source}",
                        "tag": chunk.source,
                    }
                )

        default_cards = [
            {
                "id": str(len(flashcards) + 1),
                "front": f"What is the fundamental objective of studying {topic}?",
                "back": f"To understand core principles, systematic frameworks, and practical problem-solving in {topic}.",
                "hint": "Think about theoretical foundations and application.",
                "tag": "Core Concept",
            },
            {
                "id": str(len(flashcards) + 2),
                "front": f"What is Active Recall and how does it apply to {topic}?",
                "back": "Active recall is the practice of retrieving information from memory rather than passively rereading, boosting retention by up to 50%.",
                "hint": "Testing yourself instead of looking at notes.",
                "tag": "Study Science",
            },
            {
                "id": str(len(flashcards) + 3),
                "front": f"What is the Spaced Repetition technique?",
                "back": "Reviewing material at increasing intervals over time to counteract the Ebbinghaus forgetting curve.",
                "hint": "Spacing out revision sessions.",
                "tag": "Productivity",
            },
            {
                "id": str(len(flashcards) + 4),
                "front": f"Key Terminology Check: How do you define key components of {topic}?",
                "back": f"Break {topic} into modular components: definitions, inputs, processing logic, and output validation.",
                "hint": "Modular decomposition.",
                "tag": "Architecture",
            },
        ]

        for card in default_cards:
            if len(flashcards) >= count:
                break
            flashcards.append(card)

        return flashcards[:count]

    def summarize_material(self, topic: str = "") -> Dict[str, Any]:
        """Generate an executive summary, glossary, and key exam takeaways from course notes."""
        sources = self.knowledge.materials()
        chunks = self.knowledge.search(topic or "overview", limit=5) if topic else self.knowledge.chunks[:5]

        if not chunks:
            return {
                "title": topic or "Course Materials",
                "sources": sources,
                "summary": "No course materials are currently indexed. Upload notes (.txt, .md, .pdf, .docx, .pptx) to generate summaries.",
                "key_concepts": [],
                "takeaways": ["Upload learning materials to unlock automatic cheat-sheet generation."],
            }

        combined_text = " ".join(chunk.text for chunk in chunks)
        sentences = [s.strip() for s in combined_text.split(".") if len(s.strip()) > 20]

        summary = " ".join(sentences[:3]) + "." if sentences else "Course materials cover foundational principles and practical applications."

        key_concepts = []
        for idx, chunk in enumerate(chunks[:4], start=1):
            sample = chunk.text.strip().split(".")[0]
            key_concepts.append(
                {
                    "term": f"Concept {idx} ({chunk.source})",
                    "definition": sample[:160] + "..." if len(sample) > 160 else sample,
                }
            )

        takeaways = [
            f"Review foundational terms in {', '.join(sources[:3]) if sources else 'uploaded notes'}.",
            "Practice continuous active recall using the interactive flashcard deck.",
            "Verify comprehension with the quiz generator before moving to advanced topics.",
        ]

        return {
            "title": topic.title() if topic else "Course Overview",
            "sources": sources,
            "summary": summary,
            "key_concepts": key_concepts,
            "takeaways": takeaways,
        }

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
