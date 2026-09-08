const questionForm = document.getElementById('question-form');
const planForm = document.getElementById('plan-form');
const quizForm = document.getElementById('quiz-form');
const memoryButton = document.getElementById('memory-button');
const clearMemoryButton = document.getElementById('clear-memory-button');
const uploadForm = document.getElementById('upload-form');
const progressForm = document.getElementById('progress-form');

const questionResult = document.getElementById('question-result');
const planResult = document.getElementById('plan-result');
const quizResult = document.getElementById('quiz-result');
const memoryResult = document.getElementById('memory-result');
const uploadResult = document.getElementById('upload-result');
const progressResult = document.getElementById('progress-result');
const ollamaStatus = document.getElementById('ollama-status');
const navStatus = document.getElementById('nav-status');

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || 'Request failed');
  }

  return data;
}

async function loadMemory() {
  const response = await fetch('/api/memory');
  const data = await response.json();
  memoryResult.textContent = data.summary || 'No conversation history yet.';
}

async function loadProgress() {
  const response = await fetch('/api/progress');
  const data = await response.json();
  progressResult.textContent =
    `Completed topics: ${data.completed_topics}\n` +
    `Study hours: ${data.study_hours}\n` +
    `Quizzes completed: ${data.quizzes_completed}`;
  document.getElementById('stat-topics').textContent = data.completed_topics;
  document.getElementById('stat-hours').textContent = data.study_hours;
  document.getElementById('stat-quizzes').textContent = data.quizzes_completed;
}

async function loadOllamaStatus() {
  const response = await fetch('/api/ollama-status');
  const data = await response.json();
  if (data.gemini_available) {
    ollamaStatus.textContent = `Gemini connected - model: ${data.gemini_model}`;
    navStatus.textContent = 'Gemini online';
  } else if (data.available) {
    ollamaStatus.textContent = `Ollama connected - model: ${data.model}`;
    navStatus.textContent = 'Ollama online';
  } else {
    ollamaStatus.textContent = `AI providers offline - using local RAG fallback`;
    navStatus.textContent = 'RAG fallback';
  }
}

questionForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const question = document.getElementById('question-input').value.trim();
  if (!question) {
    questionResult.textContent = 'Please type a question first.';
    return;
  }

  questionResult.textContent = 'Thinking...';
  try {
    const data = await postJson('/api/answer', { question });
    questionResult.textContent = data.answer;
    await loadMemory();
  } catch (error) {
    questionResult.textContent = `Error: ${error.message}`;
  }
});

planForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const topic = document.getElementById('plan-topic').value.trim();
  const days = Number(document.getElementById('plan-days').value || 5);

  planResult.innerHTML = '';
  try {
    const data = await postJson('/api/plan', { topic, days });
    const items = data.plan || [];
    planResult.innerHTML = items.map((item) => `<li>${item}</li>`).join('');
  } catch (error) {
    planResult.innerHTML = `<li>Error: ${error.message}</li>`;
  }
});

quizForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const topic = document.getElementById('quiz-topic').value.trim();
  const count = Number(document.getElementById('quiz-count').value || 3);

  quizResult.innerHTML = 'Generating quiz...';
  try {
    const data = await postJson('/api/quiz', { topic, count });
    const quiz = data.quiz || [];
    quizResult.innerHTML = quiz
      .map(
        (item, index) => `
          <div class="quiz-item">
            <strong>Q${index + 1}:</strong> ${item.question}<br />
            <strong>Answer:</strong> ${item.answer}
          </div>
        `,
      )
      .join('');
  } catch (error) {
    quizResult.innerHTML = `Error: ${error.message}`;
  }
});

memoryButton.addEventListener('click', loadMemory);
clearMemoryButton.addEventListener('click', async () => {
  if (!window.confirm('Clear all saved conversation memory?')) return;
  const response = await fetch('/api/memory', { method: 'DELETE' });
  const data = await response.json();
  memoryResult.textContent = data.message || 'Memory cleared.';
});
uploadForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const file = document.getElementById('material-file').files[0];
  if (!file) {
    uploadResult.textContent = 'Choose a .txt or .md file first.';
    return;
  }
  const formData = new FormData();
  formData.append('file', file);
  uploadResult.textContent = 'Uploading...';
  try {
    const response = await fetch('/api/upload', { method: 'POST', body: formData });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Upload failed');
    uploadResult.textContent = data.message;
  } catch (error) {
    uploadResult.textContent = `Error: ${error.message}`;
  }
});

progressForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const payload = {
    completed_topics: Number(document.getElementById('completed-topics').value || 0),
    study_hours: Number(document.getElementById('study-hours').value || 0),
    quizzes_completed: Number(document.getElementById('quizzes-completed').value || 0),
  };
  const response = await fetch('/api/progress', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  progressResult.textContent =
    `Completed topics: ${data.completed_topics}\n` +
    `Study hours: ${data.study_hours}\n` +
    `Quizzes completed: ${data.quizzes_completed}`;
  await loadProgress();
});

document.querySelectorAll('.chip').forEach((chip) => {
  chip.addEventListener('click', () => {
    document.getElementById('question-input').value = chip.dataset.prompt;
    document.getElementById('question-input').focus();
  });
});

loadMemory();
loadProgress();
loadOllamaStatus();
