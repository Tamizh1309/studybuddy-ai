# PROJECT REPORT: STUDY BUDDY AI – AGENTIC LEARNING & STUDY ASSISTANT

---

## 1. Project Overview

### 1.1 Project Title
**STUDY BUDDY AI – Intelligent Personal AI Learning Assistant for College Students**

### 1.2 Problem Statement
Undergraduate students preparing for demanding university examinations face persistent challenges in synthesising voluminous lecture notes, textbooks, and problem sets. Traditional study methods suffer from:
1. **Unstructured Revision**: Students struggle to budget revision time across multiple complex subjects like Operating Systems, DBMS, and Computer Networks.
2. **Passive Study Inefficiencies**: Reading slides or notes passively leads to low retention; diagnostic testing and active recall are rarely structured effectively.
3. **Context-Blind AI Chatbots**: Standard generative AI interfaces do not remember student test scores, upcoming exam deadlines, or specific course curriculum nuances, often hallucinating generic or unverified answers.
4. **Lack of Guided Direction**: Students frequently ask *"What should I study next?"* without data-driven guidance on their individual mastery gaps.

### 1.3 Brief Description
Study Buddy AI is an end-to-end, full-stack educational web application designed as an autonomous Agentic AI learning assistant. Built with an architecture centered on **RAG + MEMORY + TOOLS**, the system acts as a proactive personal tutor. Rather than passively awaiting questions, Study Buddy AI analyzes the student's academic profile, computes their **Next Best Action**, formulates tailored multi-day study plans, generates diagnostic quizzes grounded strictly in uploaded course documents, and transparently logs every execution step.

---

## 2. Objectives & Proposed Solution

### 2.1 Project Objectives
1. **Autonomous Multi-Intent Planning**: Develop a Master Agent capable of decomposing complex, multi-step student instructions into coordinated tool workflows.
2. **Grounded Course Document RAG**: Implement a high-accuracy Retrieval-Augmented Generation pipeline to index and query course notes (.pdf, .md, .txt, .docx, .pptx) without hallucinations.
3. **Dynamic Student Memory**: Maintain persistent state regarding student exam dates, weak topics, preferred study styles, and historical quiz scores.
4. **Data-Driven Recommendations**: Continuously evaluate student performance to spotlight the Next Best Action for exam success.
5. **Full-Spectrum Study Suite**: Deliver an engaging, responsive UI featuring an interactive Dashboard, AI Tutor Chat, 3D Active Recall Flashcards, Interactive Quizzes, Concept Mind Maps, Code Explainer, and a Pomodoro Focus Timer.

### 2.2 Agentic AI Solution
The core innovation of Study Buddy AI is its transition from a reactive chatbot to an active Agentic AI workflow:
$$\text{Understand} \longrightarrow \text{Plan} \longrightarrow \text{Retrieve} \longrightarrow \text{Act} \longrightarrow \text{Respond} \longrightarrow \text{Remember} \longrightarrow \text{Improve}$$

The Master Agent coordinates specialized sub-agents:
* **Intent Detection Engine**: Categorizes user queries across multi-step prep, single-subject revisions, quizzes, memory lookups, or concept explanations.
* **Task Planner**: Decomposes urgent exam requests into synchronized plan creation and topic-specific assessment.
* **RAG Retrieval Agent**: Conducts dense vector similarity search across chunked course documents.
* **Study Planner Tool**: Generates structured, day-by-day learning agendas with interactive checkboxes.
* **Quiz Generator Tool**: Constructs randomized diagnostic MCQs with immediate scoring and explanations.
* **Progress & Memory Agent**: Tracks learning momentum, awards achievement badges, and dynamically prioritizes weak topics.

### 2.3 Key Features
* **Student Dashboard**: Real-time study streak, completed topics, Next Best Action card, interactive checklist, upcoming exam countdowns, and weak topic progress bars.
* **Master Agent Transparency**: User-facing "AI Agent Activity" trace showing each high-level action executed during the response.
* **RAG Citation Drawer**: Expandable source citations displaying document name, relevance score, and verified passage excerpts.
* **Multi-Engine AI**: Seamless switching between Google Gemini Flash, Groq Cloud (Llama 3.3), Local Ollama, and offline Local RAG.
* **Multi-Format Ingestion**: Live file uploads with 4-phase animated status indicators (`Uploading` $\rightarrow$ `Processing` $\rightarrow$ `Chunking` $\rightarrow$ `Embedding` $\rightarrow$ `Ready ✓`).
* **Active Recall 3D Flashcards**: Flashcards with flip animations and Leitner-style spaced review tracking.
* **Concept Mind Map**: Dynamic tree visualization and exportable Mermaid graph syntax.
* **Algorithmic Code Explainer**: Line-by-line code dissection with Big-O time and space complexity metrics.
* **Deep Focus Pomodoro Timer**: Integrated focus rounds with browser-native notification audio and auto-logged study hours.

---

## 3. Implementation & Results

### 3.1 Technologies & Tools Used
* **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism & CSS custom properties), Modern ES6+ JavaScript, Web Speech API (Speech-to-Text & Text-to-Speech), Service Worker (PWA).
* **Backend**: Python 3.10+, Flask RESTful API architecture.
* **AI & Language Models**: Google Gemini (`gemini-1.5-flash`), Groq API (`llama-3.3-70b-versatile`), Ollama local runtime (`llama3`).
* **Vector Store & RAG**: Semantic sliding-window chunking, Dense vector bag-of-words & TF-IDF indexing, Cosine similarity ranking.
* **Testing & CI**: Pytest suite comprising 30 comprehensive unit and API test cases.
* **Cloud Deployment**: Hosted on Render PaaS with automated blueprint orchestration (`render.yaml`).

### 3.2 Working Process
1. **User Goal Submission**: The student submits a goal via the Dashboard quick-ask input or AI Tutor chat (e.g. *"Tomorrow I have OS exam. Give me a revision plan and then quiz me on deadlocks."*).
2. **Master Agent Classification**: The agent recognizes the `MULTI_PLAN_AND_QUIZ` intent, recognizing the academic subject as Operating Systems and the core focus as Deadlocks.
3. **RAG Vector Search**: The RAG engine scans `materials/Operating_Systems_Deadlocks.md`, extracting concepts including Coffman conditions, safe states, and Banker's Algorithm.
4. **Autonomous Tool Execution**:
   * Study Planner constructs an accelerated 1-day revision timetable.
   * Quiz Tool generates 4 diagnostic MCQs with plausible distractors.
5. **Context Memory Update**: The student's upcoming exam deadline is recorded, and the Next Best Action is recalculated based on their 55% deadlock baseline.
6. **Interface Rendering**: The UI displays the AI Agent Activity execution trace, revision plan, and direct interactive action buttons.

### 3.3 Results Achieved
* **100% Test Pass Rate**: All 30 automated tests in `tests/test_api.py` and `tests/test_assistant.py` passed successfully.
* **Sub-Second Offline Retrieval**: Local RAG vector search completes in $<15\text{ms}$ over course material indices.
* **Complete Demo Scenario Execution**: Verified seamless end-to-end execution of the multi-step examination cram flow.
* **Zero Critical Vulnerabilities**: Secure environment variable handling with no hardcoded API credentials.

---

## 4. Conclusion & Future Scope

### 4.1 Conclusion
Study Buddy AI demonstrates that modern LLMs, when coupled with an Agentic AI architecture, RAG vector retrieval, and long-term memory, can deliver a transformative educational experience. By automating curriculum planning, diagnostic testing, and mastery gap tracking, Study Buddy AI empowers students to study smarter and achieve academic excellence.

### 4.2 Challenges Faced & Solutions
1. **Windows Console Encoding**: PowerShell default `cp1252` encoding caused `UnicodeEncodeError` when logging emojis; resolved by encoding and sanitizing stdout streams.
2. **Multi-Step Tool Orchestration**: Synchronizing study plan generation, RAG document search, and quiz drafting in a single turn without latency; solved via modular tool design in `study_assistant/agent.py`.
3. **Graceful Fallbacks**: Cloud AI rate limits or network failures could disrupt learning; solved by creating a resilient fallback pipeline (Gemini $\rightarrow$ Groq $\rightarrow$ Ollama $\rightarrow$ Local Grounded RAG).

### 4.3 Future Enhancements
* **Voice-First Interaction**: Full duplex real-time speech tutoring using WebSocket audio streaming.
* **LMS Integration**: Automatic syllabus and assignment sync via Canvas and Blackboard REST APIs.
* **Peer Learning Rooms**: Collaborative multiplayer quiz competitions with live student leaderboards.
* **Mathematical Formula Rendering**: Native KaTeX / LaTeX mathematical rendering for advanced engineering and physics coursework.

### 4.4 References
* Lewis, P., et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. Advances in Neural Information Processing Systems (NeurIPS).
* Vaswani, A., et al. (2017). *Attention Is All You Need*. Neural Information Processing Systems.
* Roediger, H. L., & Karpicke, J. D. (2006). *The Power of Testing Memory: Basic Research and Implications for Educational Practice*. Perspectives on Psychological Science.
* Flask Documentation: https://flask.palletsprojects.com/
* Google Gemini API Documentation: https://ai.google.dev/
