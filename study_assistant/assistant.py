from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .knowledge import KnowledgeBase
from .memory import ConversationMemory
from .gemini_client import GeminiClient
from .groq_client import GroqClient
from .ollama_client import OllamaClient


def _load_local_env() -> None:
    """Load key-values from local .env into os.environ if not already set."""
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parents[1] / ".env",
    ]
    for env_path in candidates:
        if env_path.exists():
            try:
                for line in env_path.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip("'").strip('"')
                    if key and key not in os.environ:
                        os.environ[key] = value
                break
            except Exception:
                pass


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
        _load_local_env()
        self.knowledge = KnowledgeBase(self.materials_dir)
        self.memory = ConversationMemory(self.memory_path)
        self.gemini = GeminiClient()
        self.groq = GroqClient()
        self.ollama = OllamaClient()

    def has_gemini(self) -> bool:
        return self.gemini.is_available()

    def has_groq(self) -> bool:
        return self.groq.is_available()

    def has_ollama(self) -> bool:
        return self.ollama.is_available()

    def has_active_ai_provider(self) -> bool:
        return self.has_gemini() or self.has_groq() or self.has_ollama()

    @property
    def gemini_model(self) -> str:
        return self.gemini.model

    @property
    def groq_model(self) -> str:
        return self.groq.model

    @property
    def ollama_model(self) -> str:
        return self.ollama.model

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
            except RuntimeError:
                # If selected engine fails, gracefully cascade to other active providers
                for client in (self.groq, self.ollama):
                    if client.is_available():
                        try:
                            answer = client.chat(question, context, subject, mode)
                            break
                        except RuntimeError:
                            pass
                if answer is None:
                    answer = self._fallback_answer(question, context)
        elif engine == "groq":
            try:
                answer = self.groq.chat(question, context, subject, mode)
            except RuntimeError:
                for client in (self.gemini, self.ollama):
                    if client.is_available():
                        try:
                            answer = client.chat(question, context, subject, mode)
                            break
                        except RuntimeError:
                            pass
                if answer is None:
                    answer = self._fallback_answer(question, context)
        elif engine == "ollama":
            try:
                answer = self.ollama.chat(question, context, subject, mode)
            except RuntimeError:
                for client in (self.gemini, self.groq):
                    if client.is_available():
                        try:
                            answer = client.chat(question, context, subject, mode)
                            break
                        except RuntimeError:
                            pass
                if answer is None:
                    answer = self._fallback_answer(question, context)
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
        q_clean = question.lower().strip().rstrip("!?.,")
        # Handle greetings
        if q_clean in {"hi", "hello", "hey", "hola", "greetings", "good morning", "good afternoon", "good evening", "sup"}:
            return (
                "Hello! 👋 I'm **StudyBuddy AI**, your autonomous agentic learning companion. "
                "I can help you master academic concepts, deconstruct curriculums into study roadmaps, "
                "practice with 3D active-recall flashcards, take graded quizzes, and analyze code. "
                "What topic or subject would you like to study today?"
            )

        # Handle identity & capabilities
        if any(ph in q_clean for ph in ["who are you", "what can you do", "what is this", "how does this work", "help"]):
            return (
                "I am **StudyBuddy AI**, an autonomous study assistant. Here is how I can help:\n\n"
                "- 💬 **AI Tutor**: Ask any question grounded in your course materials or broader concepts.\n"
                "- 🤖 **Agent Architect**: Build multi-day study pathways with diagnostic quizzes and flashcards.\n"
                "- 🕸️ **Concept Map**: Visualize concepts and hierarchies with interactive mind maps.\n"
                "- 🗂️ **3D Flashcards**: Master terminology through active recall.\n"
                "- 📝 **Interactive Quizzes**: Auto-graded quizzes with explanations.\n"
                "- 💻 **Code Explainer**: Big-O complexity analysis and code breakdown.\n"
                "- ⏱️ **Focus Timer**: Pomodoro productivity sessions that log to your study hours.\n\n"
                "Try asking me a question or uploading your course notes in the Library tab!"
            )

        if "No course material matched" in context:
            return (
                f"**Regarding '{question}':**\n\n"
                "I didn't find specific passages covering this in your currently uploaded course materials, "
                "and the live cloud AI provider is temporarily busy or reconnecting.\n\n"
                "💡 **Recommended next steps:**\n"
                "1. Make sure your question relates to your uploaded syllabus notes (or upload the relevant document in the Library tab).\n"
                "2. Ensure the **AI Engine** dropdown at the top is set to '⚡ Engine: Auto Cascade'.\n"
                "3. Try generating an autonomous roadmap using the **Agent Architect** tab!"
            )

        return self._build_answer_from_context(question, context)

    def create_learning_plan(self, topic: str, days: int = 7, engine: str = "auto") -> List[str]:
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

    generate_learning_plan = create_learning_plan

    def generate_quiz(self, topic: str, count: int = 5, engine: str = "auto") -> List[Dict[str, Any]]:
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

    def generate_flashcards(self, topic: str, count: int = 6, engine: str = "auto") -> List[Dict[str, str]]:
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

    def run_study_architect(self, goal: str, days: int = 5, engine: str = "auto") -> Dict[str, Any]:
        """Autonomous Agentic workflow: decomposes a learning goal into curriculum, diagnostic quiz, and recall deck."""
        clean_goal = (goal or "").strip() or "Master Artificial Intelligence Foundations"
        # Extract main topic
        topic = clean_goal.lower().replace("prepare for", "").replace("master", "").replace("learn", "").replace("study", "").strip() or clean_goal

        chunks = self.knowledge.search(topic, limit=4)
        sources = list(dict.fromkeys(c.source for c in chunks))

        # Generate components using existing grounded methods
        plan = self.create_learning_plan(topic, days=max(1, min(days, 30)), engine=engine)
        quiz = self.generate_quiz(topic, count=3, engine=engine)
        cards = self.generate_flashcards(topic, count=5, engine=engine)

        reasoning_trace = [
            {
                "step": 1,
                "phase": "Document Perception & Grounding",
                "status": "completed",
                "detail": f"Scanned RAG knowledge base. Grounded target goal in {len(sources)} source document(s): {', '.join(sources) if sources else 'Standard academic curriculum'}.",
            },
            {
                "step": 2,
                "phase": "Cognitive Load & Curriculum Scheduling",
                "status": "completed",
                "detail": f"Divided target concepts across a balanced {len(plan)}-day timeline with progressive complexity.",
            },
            {
                "step": 3,
                "phase": "Diagnostic Calibration Assessment",
                "status": "completed",
                "detail": f"Formulated {len(quiz)} conceptual diagnostic questions to test baseline comprehension.",
            },
            {
                "step": 4,
                "phase": "Active Recall & Spaced Repetition Synthesis",
                "status": "completed",
                "detail": f"Generated {len(cards)} active recall 3D flashcards with mnemonic hints for long-term retention.",
            },
        ]

        return {
            "goal": clean_goal,
            "topic": topic.title(),
            "days": len(plan),
            "sources": sources,
            "reasoning_trace": reasoning_trace,
            "curriculum": plan,
            "diagnostic_quiz": quiz,
            "flashcards": cards,
        }

    def generate_concept_map(self, topic: str = "", engine: str = "auto") -> Dict[str, Any]:
        """Generate structured nodes, relationships, and Mermaid graph syntax for visual concept mapping."""
        clean_topic = (topic or "").strip() or "Artificial Intelligence"
        chunks = self.knowledge.search(clean_topic, limit=3)

        # Build clean diagram title & identifier
        root_id = "root"
        root_label = clean_topic.title()

        # Build subtopics
        branches = [
            {
                "id": "b1",
                "name": "Core Principles",
                "desc": "Fundamental definitions, axioms, and working hypotheses.",
                "leaves": [
                    {"id": "l1", "name": "Axioms & Inputs", "desc": "Structured and unstructured data ingestion."},
                    {"id": "l2", "name": "Algorithmic Rules", "desc": "Mathematical and heuristic procedures."},
                ],
            },
            {
                "id": "b2",
                "name": "Mechanisms & Modeling",
                "desc": "System architecture, training procedures, and model inference.",
                "leaves": [
                    {"id": "l3", "name": "Training & Optimization", "desc": "Gradient updates, backprop, and validation."},
                    {"id": "l4", "name": "Inference & Prediction", "desc": "Real-time query processing and latency bounds."},
                ],
            },
            {
                "id": "b3",
                "name": "Applications & Impact",
                "desc": "Real-world operational systems, safety, and evaluation metrics.",
                "leaves": [
                    {"id": "l5", "name": "Agentic Workflows", "desc": "Multi-step reasoning and autonomous planning."},
                    {"id": "l6", "name": "Evaluation & Verification", "desc": "Accuracy, precision, recall, and safety benchmarks."},
                ],
            },
        ]

        if chunks:
            # Personalize first leaf from notes
            first_sentence = chunks[0].text.strip().split(".")[0][:50]
            branches[0]["leaves"][0]["desc"] = f"From {chunks[0].source}: {first_sentence}..."

        # Assemble Mermaid syntax
        mermaid_lines = ["graph TD", f'  {root_id}["✦ {root_label}"]:::rootStyle']
        for b in branches:
            mermaid_lines.append(f'  {root_id} -->|branches into| {b["id"]}["{b["name"]}"]:::branchStyle')
            for l in b["leaves"]:
                mermaid_lines.append(f'  {b["id"]} -->|details| {l["id"]}["{l["name"]}"]:::leafStyle')

        mermaid_lines.extend([
            "  classDef rootStyle fill:#4f46e5,stroke:#818cf8,stroke-width:2px,color:#fff,font-weight:bold,rx:8;",
            "  classDef branchStyle fill:#1e1b4b,stroke:#6366f1,stroke-width:1px,color:#e0e7ff,font-weight:600,rx:6;",
            "  classDef leafStyle fill:#0f172a,stroke:#38bdf8,stroke-width:1px,color:#94a3b8,rx:4;",
        ])

        return {
            "topic": clean_topic,
            "root": {"id": root_id, "label": root_label},
            "branches": branches,
            "mermaid": "\n".join(mermaid_lines),
        }

    def explain_code(
        self,
        code: str,
        language: str = "python",
        analysis_type: str = "explain",
        engine: str = "auto",
    ) -> Dict[str, Any]:
        """Analyze code for line-by-line explanation, complexity, edge cases, or optimization."""
        code_clean = (code or "").strip()
        if not code_clean:
            return {
                "summary": "No code snippet provided.",
                "analysis_type": analysis_type,
                "complexity": {"time": "O(1)", "space": "O(1)"},
                "breakdown": [],
                "suggestions": ["Please enter or paste a valid code snippet."],
            }

        # Check for AI engine completion
        context = self.knowledge.get_context(code_clean[:100], limit=2)
        prompt = (
            f"Analyze the following {language} code focusing on '{analysis_type}'.\n"
            f"Provide: 1) Executive Summary, 2) Time and Space Complexity (Big-O), "
            f"3) Line-by-line explanation, and 4) Edge cases or potential bugs.\n\n"
            f"```{language}\n{code_clean}\n```"
        )

        ai_response = None
        if engine in ("auto", "gemini") and self.gemini.is_available():
            try:
                ai_response = self.gemini.chat(prompt, context, "Software Engineering", "Explain")
            except Exception:
                pass
        elif engine in ("auto", "groq") and self.groq.is_available():
            try:
                ai_response = self.groq.chat(prompt, context, "Software Engineering", "Explain")
            except Exception:
                pass

        # Static Code Analysis Fallback
        lines = [line for line in code_clean.split("\n") if line.strip()]
        loop_count = sum(1 for line in lines if any(k in line for k in ("for ", "while ", ".forEach(", ".map(")))
        nested_loop = any(line.startswith("        for ") or line.startswith("        while ") for line in lines)
        has_recursion = any("return " in line and ("(" in line and ")" in line) for line in lines)

        time_comp = "O(n²)" if nested_loop else ("O(n)" if loop_count >= 1 else "O(1)")
        space_comp = "O(n)" if any(k in code_clean for k in ("append", "push", "[]", "{}", "list(", "dict(")) else "O(1)"

        breakdown = []
        for idx, line in enumerate(lines[:8], 1):
            explanation = "Initializes structure or assignment."
            if "def " in line or "function " in line:
                explanation = "Declares subroutine with input arguments."
            elif "for " in line or "while " in line:
                explanation = "Iterative loop traversing elements or conditions."
            elif "if " in line or "elif " in line:
                explanation = "Conditional branch evaluating control predicate."
            elif "return " in line:
                explanation = "Yields computed value to calling caller."
            breakdown.append({"line_number": idx, "code": line.strip(), "explanation": explanation})

        suggestions = [
            f"Time Complexity is estimated at {time_comp} based on loop depth.",
            f"Space Complexity is {space_comp} considering allocation patterns.",
            "Always validate input parameters against None, null, or empty containers.",
            "Consider adding docstrings and explicit type hints for maintainability.",
        ]

        summary = (
            ai_response
            if ai_response
            else f"This {language.capitalize()} snippet contains {len(lines)} line(s) of code. "
            f"It executes with an estimated {time_comp} runtime complexity and {space_comp} auxiliary memory usage."
        )

        return {
            "language": language,
            "analysis_type": analysis_type,
            "summary": summary,
            "complexity": {"time": time_comp, "space": space_comp},
            "breakdown": breakdown,
            "suggestions": suggestions,
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

