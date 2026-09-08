from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class ConversationMemory:
    """Stores structured learning context, student profile, quiz history, weak topics, and chat turns."""

    def __init__(self, storage_path: str | Path) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._history: List[Tuple[str, str]] = []

        # Default student profile and academic state
        self.profile: Dict[str, Any] = {
            "name": "Tamizh",
            "learning_style": "Short explanations and interactive MCQs",
            "preferred_duration_mins": 25,
            "target_exams": [
                {"subject": "Operating Systems", "exam": "End-Semester OS Exam", "days_left": 2, "date": "In 2 days"},
                {"subject": "DBMS", "exam": "Relational DB Midterm", "days_left": 5, "date": "In 5 days"},
                {"subject": "Computer Networks", "exam": "Computer Networks Final", "days_left": 9, "date": "In 9 days"},
            ],
        }

        self.weak_topics: List[Dict[str, Any]] = [
            {"topic": "Deadlocks", "subject": "Operating Systems", "score": 55, "target": 80, "urgency": "High"},
            {"topic": "Normalization", "subject": "DBMS", "score": 61, "target": 85, "urgency": "Medium"},
            {"topic": "Trees", "subject": "Data Structures", "score": 68, "target": 85, "urgency": "Medium"},
        ]

        self.completed_topics: List[str] = [
            "Process Management",
            "CPU Scheduling",
            "Relational Algebra",
            "TCP 3-Way Handshake",
        ]

        self.pending_topics: List[str] = [
            "Deadlocks",
            "Memory Management",
            "Boyce-Codd Normal Form",
            "BGP Routing",
        ]

        self.today_plan: List[Dict[str, Any]] = [
            {"id": "task-1", "title": "Process Management", "completed": True, "subject": "Operating Systems"},
            {"id": "task-2", "title": "CPU Scheduling", "completed": True, "subject": "Operating Systems"},
            {"id": "task-3", "title": "Deadlocks", "completed": False, "current": True, "subject": "Operating Systems"},
            {"id": "task-4", "title": "Memory Management", "completed": False, "subject": "Operating Systems"},
        ]

        self.recent_quizzes: List[Dict[str, Any]] = [
            {"subject": "Operating Systems", "topic": "Processes & Threads", "score": 8, "total": 10, "date": "Yesterday"},
            {"subject": "DBMS", "topic": "SQL & ER Models", "score": 7, "total": 10, "date": "2 days ago"},
            {"subject": "Computer Networks", "topic": "OSI Layers", "score": 9, "total": 10, "date": "3 days ago"},
        ]

        self._load()

    def _load(self) -> None:
        if not self.storage_path.exists():
            return
        try:
            payload = json.loads(self.storage_path.read_text(encoding="utf-8"))
            if isinstance(payload, list):
                self._history = [(item.get("question", ""), item.get("answer", "")) for item in payload]
            elif isinstance(payload, dict):
                self._history = [(item["question"], item["answer"]) for item in payload.get("history", [])]
                if "profile" in payload:
                    self.profile.update(payload["profile"])
                if "weak_topics" in payload:
                    self.weak_topics = payload["weak_topics"]
                if "completed_topics" in payload:
                    self.completed_topics = payload["completed_topics"]
                if "pending_topics" in payload:
                    self.pending_topics = payload["pending_topics"]
                if "today_plan" in payload:
                    self.today_plan = payload["today_plan"]
                if "recent_quizzes" in payload:
                    self.recent_quizzes = payload["recent_quizzes"]
        except Exception:
            self._history = []

    def _save(self) -> None:
        serializable = {
            "history": [{"question": q, "answer": a} for q, a in self._history],
            "profile": self.profile,
            "weak_topics": self.weak_topics,
            "completed_topics": self.completed_topics,
            "pending_topics": self.pending_topics,
            "today_plan": self.today_plan,
            "recent_quizzes": self.recent_quizzes,
            "updated_at": datetime.now().isoformat(),
        }
        self.storage_path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")

    def add_turn(self, question: str, answer: str) -> None:
        self._history.append((question, answer))
        # Keep recent 40 turns
        if len(self._history) > 40:
            self._history = self._history[-40:]
        self._save()

    def summary(self) -> str:
        if not self._history:
            return "No prior conversation history recorded."
        lines = [f"Q: {q}\nA: {a[:160]}..." for q, a in self._history[-4:]]
        return "\n\n".join(lines)

    def get_student_context_prompt(self) -> str:
        """Concise context summary for LLM prompt grounding."""
        weak = ", ".join(f"{w['topic']} ({w['score']}%)" for w in self.weak_topics[:2])
        return (
            f"Student Context: Name: {self.profile.get('name', 'Tamizh')}. "
            f"Style Preference: {self.profile.get('learning_style')}. "
            f"Upcoming Exam: Operating Systems in 2 days. "
            f"Priority Weak Area: {weak}."
        )

    def get_next_best_action(self) -> Dict[str, Any]:
        """Determine next best learning action based on weak areas, upcoming exams, and plan."""
        # Find weakest topic
        weakest = min(self.weak_topics, key=lambda x: x.get("score", 100)) if self.weak_topics else None
        if weakest and weakest.get("score", 100) < 70:
            return {
                "action": f"Revise {weakest.get('subject')} – {weakest.get('topic')}",
                "title": f"Revise {weakest.get('topic')}",
                "subject": weakest.get("subject"),
                "topic": weakest.get("topic"),
                "score": weakest.get("score"),
                "reason": f"Your last quiz score was {weakest.get('score')}% and your {weakest.get('subject')} exam is in 2 days.",
                "type": "revision",
                "recommended_minutes": 25,
            }

        return {
            "action": "Continue Operating Systems Practice",
            "title": "Practice Deadlock Avoidance",
            "subject": "Operating Systems",
            "topic": "Deadlocks",
            "score": 65,
            "reason": "Reinforce Banker's algorithm before your upcoming exam.",
            "type": "quiz",
            "recommended_minutes": 20,
        }

    def record_quiz_score(self, topic: str, subject: str, score: int, total: int) -> None:
        percent = round((score / max(1, total)) * 100)
        # Update or add to recent quizzes
        self.recent_quizzes.insert(0, {
            "subject": subject,
            "topic": topic,
            "score": score,
            "total": total,
            "percentage": percent,
            "date": "Today",
        })
        self.recent_quizzes = self.recent_quizzes[:5]

        # Update weak topics if below 70%
        matched = False
        for item in self.weak_topics:
            if item.get("topic", "").lower() == topic.lower():
                item["score"] = percent
                matched = True
                break
        if not matched and percent < 70:
            self.weak_topics.append({
                "topic": topic,
                "subject": subject,
                "score": percent,
                "target": 80,
                "urgency": "High" if percent < 60 else "Medium",
            })
        elif percent >= 75:
            self.weak_topics = [w for w in self.weak_topics if w.get("topic", "").lower() != topic.lower()]
            if topic not in self.completed_topics:
                self.completed_topics.append(topic)

        self._save()

    def update_task_status(self, task_id: str, completed: bool) -> None:
        for task in self.today_plan:
            if task.get("id") == task_id or task.get("title") == task_id:
                task["completed"] = completed
                break
        self._save()

    def clear(self) -> None:
        self._history = []
        self._save()


__all__ = ["ConversationMemory"]
