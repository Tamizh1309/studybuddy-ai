# StudyBuddy AI

## Live Demo

[Open StudyBuddy AI](https://studybuddy-ai-dlin.onrender.com/)

A lightweight AI-powered learning assistant that combines:

- RAG-style retrieval over course materials
- Persistent conversation memory
- Study planning and quiz generation tools
- A modern frontend and Python backend for real web usage

## Features

- Ask questions about course notes and get answers grounded in the available material
- Generate a multi-day learning plan around a topic of interest
- Create quizzes for revision and self-assessment
- Retain conversation history in memory for follow-up interactions
- Access the system through both CLI and browser UI
- Optional local Ollama chat using the `nemotron-3-nano:30b` model
- Optional Gemini API chat using the `gemini-2.5-flash` model
- General-purpose Q&A for academic, technical, planning, and everyday questions
- Subject selector and response modes: explain, step-by-step, summary, examples, exam answer
- Upload `.txt`, `.md`, `.pdf`, `.docx`, and `.pptx` course notes from the browser (10 MB max)
- Track completed topics, study hours, and quizzes
- Installable PWA shell with browser-native text-to-speech and dark/light theme toggle

## Project layout

- `study_assistant/knowledge.py` — document indexing and retrieval
- `study_assistant/memory.py` — persistent conversation history
- `study_assistant/assistant.py` — study assistant logic
- `study_assistant/tools.py` — reusable helper tools
- `materials/` — sample course content
- `main.py` — CLI entry point
- `backend/app.py` — Flask backend API
- `frontend/` — browser-based user interface
- `tests/` — validation tests

## Run the backend and frontend

1. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

2. Start the web app:

```bash
python backend/app.py
```

3. Open your browser at:

```text
http://localhost:5000
```

## Deploy on Render

The repository includes `render.yaml` for one-click Render deployment:

1. Open [Render](https://render.com) and sign in with GitHub.
2. Select **New +** → **Blueprint**.
3. Choose `Tamizh1309/studybuddy-ai`.
4. Add `GEMINI_API_KEY` in the Render environment settings if Gemini is enabled.
5. Deploy. Render provides a public HTTPS URL such as:
   `https://studybuddy-ai.onrender.com`

The free service may sleep when idle. The app still works with local RAG when no cloud
AI provider key is configured.

## Ollama setup

Ollama runs locally and normally does not require an API key. Install Ollama, then download
the default model:

```bash
ollama pull nemotron-3-nano:30b
```

Optional configuration:

```powershell
$env:OLLAMA_BASE_URL = "http://127.0.0.1:11434"
$env:OLLAMA_MODEL = "nemotron-3-nano:30b"
python backend/app.py
```

For Ollama Cloud or a secured Ollama gateway, set the key without placing it in source code:

```powershell
$env:OLLAMA_API_KEY = "your-key"
```

If Ollama is offline, StudyBuddy AI automatically uses the built-in local RAG response.

## Gemini setup

Create a Gemini API key in Google AI Studio and set it as an environment variable.
Never commit the key to source code:

```powershell
$env:GEMINI_API_KEY = "your-gemini-api-key"
$env:GEMINI_MODEL = "gemini-2.5-flash"
python backend/app.py
```

Provider priority is Gemini, then local Ollama, then the built-in RAG fallback.

## CLI usage

```bash
python main.py --question "What is machine learning?"
python main.py --plan --topic "artificial intelligence" --days 5
python main.py --quiz --topic "artificial intelligence" --count 3
```

## API endpoints

- `POST /api/answer` with JSON: `{ "question": "What is machine learning?" }`
- `POST /api/plan` with JSON: `{ "topic": "artificial intelligence", "days": 5 }`
- `POST /api/quiz` with JSON: `{ "topic": "artificial intelligence", "count": 3 }`
- `GET /api/memory`
- `GET /api/health`
- `GET /api/materials`
- `GET /api/ollama-status`
- `POST /api/upload` with a multipart `.txt`, `.md`, `.pdf`, `.docx`, or `.pptx` file
- `GET/POST /api/progress`

## Running tests

```bash
python -m pytest -q
```
