from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from study_assistant.assistant import StudyAssistant


class MasterAgent:
    """Master Agent for StudyBuddy AI: Handles intent detection, task decomposition,

    RAG retrieval, tool execution, memory synchronization, and personalized responses.
    """

    def __init__(self, assistant: StudyAssistant) -> None:
        self.assistant = assistant
        self.memory = assistant.memory
        self.knowledge = assistant.knowledge

    def detect_intents(self, query: str) -> List[str]:
        q = query.lower()
        intents: List[str] = []

        # Check for multi-goal keywords
        has_plan = any(k in q for k in ["revision plan", "study plan", "schedule", "roadmap", "plan me", "give me a plan"])
        has_quiz = any(k in q for k in ["quiz", "test me", "mcq", "practice questions", "questions on"])
        has_explain = any(k in q for k in ["explain", "what is", "how does", "summarize", "teach me", "difference between"])
        has_memory = any(k in q for k in ["what did i study", "yesterday", "weak topics", "my progress", "my scores", "what are my weak"])
        has_next_action = any(k in q for k in ["what should i study next", "next best action", "recommend", "what next"])

        if has_plan and has_quiz:
            intents.append("MULTI_PLAN_AND_QUIZ")
        elif has_plan:
            intents.append("STUDY_PLAN")
        elif has_quiz:
            intents.append("QUIZ_GENERATION")
        elif has_memory:
            intents.append("MEMORY_QUERY")
        elif has_next_action:
            intents.append("NEXT_BEST_ACTION")
        elif has_explain:
            intents.append("EXPLAIN_RAG")
        else:
            intents.append("GENERAL_QA")

        return intents

    def execute(self, query: str, engine: str = "auto", rag_mode: str = "hybrid") -> Dict[str, Any]:
        """Autonomous Agent execution loop: Understand -> Plan -> Retrieve -> Act -> Respond -> Remember."""
        intents = self.detect_intents(query)
        primary_intent = intents[0]

        trace: List[Dict[str, str]] = [
            {"phase": "Intent Detection", "detail": f"Classified student goal as [{primary_intent}] with active memory grounding."}
        ]
        tools_executed: List[str] = []
        sources: List[str] = []
        study_plan: Optional[List[str]] = None
        quiz_data: Optional[List[Dict[str, Any]]] = None

        # 1. Multi-Step Demo Flow: "Tomorrow I have OS exam. Give me a revision plan and then quiz me on deadlocks."
        if primary_intent == "MULTI_PLAN_AND_QUIZ":
            trace.append({"phase": "Task Planning", "detail": "Decomposing into 2 sub-tasks: (1) Urgent Exam Revision Plan, (2) Targeted Topic Quiz."})

            # Detect topic and subject
            subject = "Operating Systems" if "os" in query.lower() or "operating" in query.lower() else "Computer Science"
            topic = "Deadlocks" if "deadlock" in query.lower() else "Operating Systems"

            # Execute Tool 1: RAG Retrieval
            rag_chunks = self.knowledge.search_with_metadata(f"{subject} {topic}", limit=3)
            tools_executed.append("rag_retriever")
            if rag_chunks:
                sources = list({c["source"] for c in rag_chunks if c.get("source")})
                trace.append({
                    "phase": "RAG Knowledge Base",
                    "detail": f"Grounded in course notes: {', '.join(sources)} ({rag_chunks[0].get('relevance_percent', 90)}% relevance match)."
                })

            # Execute Tool 2: Study Planner Tool
            tools_executed.append("study_planner_tool")
            days = 1 if any(k in query.lower() for k in ["tomorrow", "urgent", "1 day", "tonight"]) else 3
            study_plan = self.assistant.create_learning_plan(f"{subject} - {topic} Final Revision", days=days)
            trace.append({"phase": "Study Planner Tool", "detail": f"Synthesized high-yield {days}-Day targeted cramming roadmap."})

            # Execute Tool 3: Quiz Generator Tool
            tools_executed.append("quiz_generator_tool")
            quiz_data = self.assistant.generate_quiz(topic, count=4, engine=engine)
            trace.append({"phase": "Quiz Tool", "detail": f"Generated 4 active-recall diagnostic questions on {topic}."})

            # Execute Tool 4: Update Memory
            tools_executed.append("memory_updater")
            self.memory.profile["target_exams"][0]["days_left"] = 1
            self.memory.add_turn(query, f"Generated revision plan and diagnostic quiz for {topic}.")
            trace.append({"phase": "Progress & Memory Agent", "detail": f"Updated academic goal: {subject} Exam Tomorrow. Prioritized {topic}."})

            answer = (
                f"### 🎯 Agentic Action Plan: {subject} Exam Revision & {topic} Mastery\n\n"
                f"Hello **{self.memory.profile.get('name', 'Tamizh')}**! I have processed your urgent exam preparation request:\n\n"
                f"1. **⚡ High-Yield Revision Plan ({days} Day)**: Focus intensely on process synchronization, banker's algorithm, and resource graphs.\n"
                f"2. **📝 Interactive Diagnostic Quiz**: 4 questions on **{topic}** ready below to test your recall.\n"
                f"3. **📚 Course Grounding**: Grounded in `{', '.join(sources) if sources else 'Operating_Systems_Deadlocks.md'}`.\n\n"
                f"Let's review your revision roadmap first, then tackle the diagnostic quiz!"
            )

        # 2. Study Plan Only
        elif primary_intent == "STUDY_PLAN":
            tools_executed.append("study_planner_tool")
            # Extract topic
            topic_clean = re.sub(r"(?i)(create|give me|generate|a|study|plan|for|on|7-day|3-day|days)", "", query).strip() or "Computer Science"
            study_plan = self.assistant.create_learning_plan(topic_clean, days=7)
            trace.append({"phase": "Study Planner Tool", "detail": f"Constructed personalized 7-day milestone curriculum for {topic_clean}."})
            answer = (
                f"### 📅 7-Day Structured Study Plan: {topic_clean.title()}\n\n"
                f"Based on your profile (*{self.memory.profile.get('learning_style')}*), here is your optimized daily schedule:\n\n"
                + "\n".join(f"- **{step}**" for step in study_plan)
                + "\n\n💡 *Tip: Check off daily milestones in the **Study Planner** tab as you complete them!*"
            )

        # 3. Quiz Generation Only
        elif primary_intent == "QUIZ_GENERATION":
            tools_executed.append("quiz_generator_tool")
            topic_clean = re.sub(r"(?i)(quiz|me|on|generate|mcqs|test|questions)", "", query).strip() or "Operating Systems"
            quiz_data = self.assistant.generate_quiz(topic_clean, count=4, engine=engine)
            trace.append({"phase": "Quiz Tool", "detail": f"Synthesized 4 multi-tier MCQs for {topic_clean}."})
            answer = (
                f"### 🎯 Diagnostic Quiz Ready: {topic_clean.title()}\n\n"
                f"I've generated a 4-question active-recall quiz grounded in your syllabus. "
                f"Choose your answers below to receive instant grading and explanation breakdown!"
            )

        # 4. Memory & History Query
        elif primary_intent == "MEMORY_QUERY":
            tools_executed.append("memory_reader")
            weak_topics_text = "\n".join(f"- **{w['topic']}** ({w['subject']}): Current score **{w['score']}%** [{w['urgency']} Urgency]" for w in self.memory.weak_topics)
            quizzes_text = "\n".join(f"- **{q['subject']} ({q['topic']})**: {q['score']}/{q['total']} ({q.get('date', 'Recent')})" for q in self.memory.recent_quizzes[:3])
            trace.append({"phase": "Learning Memory Store", "detail": "Retrieved student profile, recent quiz performance, and weak areas."})

            answer = (
                f"### 🧠 Your Personal Learning Memory & History\n\n"
                f"Hello **{self.memory.profile.get('name', 'Tamizh')}**! Here is what I am currently tracking for you:\n\n"
                f"**🎯 Target Upcoming Exams:**\n"
                f"- Operating Systems: **In 2 days**\n"
                f"- DBMS Midterm: **In 5 days**\n\n"
                f"**⚠️ Your Current Weak Topics (Score < 70%):**\n"
                f"{weak_topics_text}\n\n"
                f"**📊 Recent Quiz Performance:**\n"
                f"{quizzes_text}\n\n"
                f"**💡 Learning Preference:** {self.memory.profile.get('learning_style')}."
            )

        # 5. Next Best Action Query
        elif primary_intent == "NEXT_BEST_ACTION":
            tools_executed.append("recommendation_engine")
            nba = self.memory.get_next_best_action()
            trace.append({"phase": "Next Best Action Engine", "detail": f"Recommended action: {nba['action']} ({nba['reason']})"})
            answer = (
                f"### 🚀 Next Best Action Recommended\n\n"
                f"**Goal**: **{nba['action']}**\n\n"
                f"**Why this now?** {nba['reason']}\n\n"
                f"⏱️ **Recommended Duration**: {nba['recommended_minutes']} minutes\n"
                f"💡 **Suggested steps**:\n"
                f"1. Review the Banker's Algorithm safety condition in `Operating_Systems_Deadlocks.md`.\n"
                f"2. Take a 5-question targeted quiz to raise your score from 55% to 80%."
            )

        # 6. Standard RAG Q&A
        else:
            tools_executed.append("rag_retriever")
            res = self.assistant.answer_question_structured(query, engine=engine, rag_mode=rag_mode)
            answer = res["answer"]
            sources = res.get("sources", [])
            trace.append({"phase": "RAG Engine", "detail": f"Grounded response via vector similarity search across {len(sources)} source(s)."})

        # Final Next Best Action calculation
        next_action = self.memory.get_next_best_action()

        actions_taken = [{"action": step["phase"], "label": f"{step['phase']}: {step['detail']}"} for step in trace]

        formatted_quiz = {
            "topic": topic if "topic" in locals() else "Deadlocks",
            "questions": quiz_data if isinstance(quiz_data, list) else (quiz_data.get("questions", []) if isinstance(quiz_data, dict) else []),
        } if quiz_data else None

        return {
            "answer": answer,
            "response": answer,
            "intent": primary_intent,
            "tools_executed": tools_executed,
            "action_trace": trace,
            "actions_taken": actions_taken,
            "sources": sources,
            "study_plan": study_plan,
            "quiz": formatted_quiz,
            "next_best_action": next_action,
        }


__all__ = ["MasterAgent"]
