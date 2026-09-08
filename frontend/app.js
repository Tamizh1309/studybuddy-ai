// StudyBuddy AI — Frontend Application Logic
// Features: Multi-Engine AI, Interactive Chat, Graded Quizzes, 3D Flashcards, Pomodoro, Library & Summarizer

// --- State Management ---
const state = {
  selectedEngine: localStorage.getItem('studybuddy-engine') || 'auto',
  currentQuiz: null,
  userQuizAnswers: {},
  flashcards: [],
  currentCardIndex: 0,
  cardFlipped: false,
  cardMastery: {}, // index -> 'mastered' | 'review'
  currentPlan: null,
  currentSummary: null,
  pomodoro: {
    timerId: null,
    totalSeconds: 25 * 60,
    remainingSeconds: 25 * 60,
    isRunning: false,
    mode: 'focus', // 'focus' | 'short-break' | 'long-break'
    focusDurationMinutes: 25,
    completedSessions: Number(localStorage.getItem('studybuddy-pomodoro-count') || 0),
  },
};

// --- DOM References ---
const aiEngineSelect = document.getElementById('ai-engine-select');
const navStatus = document.getElementById('nav-status');
const ollamaStatus = document.getElementById('ollama-status');
const themeButton = document.getElementById('theme-button');

// Stats Bar
const statTopics = document.getElementById('stat-topics');
const statHours = document.getElementById('stat-hours');
const statQuizzes = document.getElementById('stat-quizzes');
const statFocusSessions = document.getElementById('stat-focus-sessions');

// Tabs
const tabButtons = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

// Chat / Tutor
const chatViewport = document.getElementById('chat-viewport');
const questionForm = document.getElementById('question-form');
const questionInput = document.getElementById('question-input');
const subjectInput = document.getElementById('subject-input');
const modeInput = document.getElementById('mode-input');
const sendBtn = document.getElementById('send-btn');
const clearChatBtn = document.getElementById('clear-chat-btn');

// Study Planner
const planForm = document.getElementById('plan-form');
const planTopicInput = document.getElementById('plan-topic');
const planDaysInput = document.getElementById('plan-days');
const planStatusMsg = document.getElementById('plan-status-msg');
const planContainer = document.getElementById('plan-container');
const exportPlanBtn = document.getElementById('export-plan-btn');

// Interactive Quiz
const quizForm = document.getElementById('quiz-form');
const quizTopicInput = document.getElementById('quiz-topic');
const quizCountInput = document.getElementById('quiz-count');
const quizLoading = document.getElementById('quiz-loading');
const quizRunner = document.getElementById('quiz-runner');
const quizTopicDisplay = document.getElementById('quiz-topic-display');
const quizProgressDisplay = document.getElementById('quiz-progress-display');
const quizQuestionsList = document.getElementById('quiz-questions-list');
const submitQuizBtn = document.getElementById('submit-quiz-btn');
const quizResultsCard = document.getElementById('quiz-results-card');
const exportQuizBtn = document.getElementById('export-quiz-btn');

// 3D Flashcards
const flashcardForm = document.getElementById('flashcard-form');
const flashcardTopicInput = document.getElementById('flashcard-topic');
const flashcardCountInput = document.getElementById('flashcard-count');
const flashcardStatus = document.getElementById('flashcard-status');
const flashcardElement = document.getElementById('flashcard-element');
const cardTag = document.getElementById('card-tag');
const cardFrontText = document.getElementById('card-front-text');
const cardBackText = document.getElementById('card-back-text');
const prevCardBtn = document.getElementById('prev-card-btn');
const nextCardBtn = document.getElementById('next-card-btn');
const deckCounter = document.getElementById('deck-counter');
const shuffleCardsBtn = document.getElementById('shuffle-cards-btn');
const exportCardsBtn = document.getElementById('export-cards-btn');
const markReviewBtn = document.getElementById('mark-review-btn');
const markMasteredBtn = document.getElementById('mark-mastered-btn');

// Pomodoro Timer
const timerModeBtns = document.querySelectorAll('.timer-mode-btn');
const timerDigits = document.getElementById('timer-digits');
const timerLabel = document.getElementById('timer-label');
const timerToggleBtn = document.getElementById('timer-toggle-btn');
const timerResetBtn = document.getElementById('timer-reset-btn');
const timerProgressCircle = document.getElementById('timer-progress-circle');
const pomodoroLogFeedback = document.getElementById('pomodoro-log-feedback');

// Library & Summarizer
const uploadForm = document.getElementById('upload-form');
const materialFileInput = document.getElementById('material-file');
const uploadResult = document.getElementById('upload-result');
const materialsResult = document.getElementById('materials-result');
const materialsCount = document.getElementById('materials-count');
const refreshMaterialsBtn = document.getElementById('refresh-materials-btn');
const summaryForm = document.getElementById('summary-form');
const summaryTopicInput = document.getElementById('summary-topic-input');
const summaryLoading = document.getElementById('summary-loading');
const summaryOutput = document.getElementById('summary-output');
const exportSummaryBtn = document.getElementById('export-summary-btn');

// Memory Drawer
const memoryButton = document.getElementById('memory-button');
const clearMemoryButton = document.getElementById('clear-memory-button');
const memoryResult = document.getElementById('memory-result');

// --- Helper Utilities ---
async function postJson(url, payload) {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || `Request failed (${response.status})`);
  }
  return data;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatMarkdown(text) {
  if (!text) return '';
  let parsed = escapeHtml(text);
  // Code blocks: ```lang ... ```
  parsed = parsed.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
  // Inline code: `code`
  parsed = parsed.replace(/`([^`]+)`/g, '<code>$1</code>');
  // Bold: **text**
  parsed = parsed.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  // Italic: *text*
  parsed = parsed.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  // Headings: ### Topic
  parsed = parsed.replace(/^### (.*$)/gim, '<h4>$1</h4>');
  parsed = parsed.replace(/^## (.*$)/gim, '<h3>$1</h3>');
  parsed = parsed.replace(/^# (.*$)/gim, '<h2>$1</h2>');
  // Bullet lists
  parsed = parsed.replace(/^\s*[-*]\s+(.*$)/gim, '<li>$1</li>');
  parsed = parsed.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
  // Line breaks to <br /> if not wrapped in tags
  parsed = parsed.replace(/\n\n/g, '<br/><br/>');
  return parsed;
}

function downloadFile(filename, content, mimeType = 'text/markdown') {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// --- Sound Synthesizer for Timers and Actions ---
function playNotificationChime(type = 'success') {
  try {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);

    if (type === 'success') {
      osc.frequency.setValueAtTime(523.25, audioCtx.currentTime); // C5
      osc.frequency.exponentialRampToValueAtTime(659.25, audioCtx.currentTime + 0.15); // E5
      osc.frequency.exponentialRampToValueAtTime(783.99, audioCtx.currentTime + 0.3); // G5
      gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.5);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.5);
    } else if (type === 'quiz') {
      osc.frequency.setValueAtTime(440, audioCtx.currentTime); // A4
      osc.frequency.exponentialRampToValueAtTime(880, audioCtx.currentTime + 0.2); // A5
      gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.35);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.35);
    }
  } catch (e) {
    // AudioContext blocked or not supported
  }
}

// --- Engine Selection & Status ---
if (aiEngineSelect) {
  aiEngineSelect.value = state.selectedEngine;
  aiEngineSelect.addEventListener('change', (e) => {
    state.selectedEngine = e.target.value;
    localStorage.setItem('studybuddy-engine', state.selectedEngine);
    updateEngineDisplay();
  });
}

async function loadAiStatus() {
  try {
    const response = await fetch('/api/ai-status');
    const data = await response.json();
    let statusText = 'RAG Fallback';
    let detailText = 'Local pattern matcher active';

    if (data.gemini_available && (state.selectedEngine === 'auto' || state.selectedEngine === 'gemini')) {
      statusText = 'Gemini Online';
      detailText = `Gemini Flash (${data.gemini_model || 'gemini-1.5-flash'}) connected`;
    } else if (data.groq_available && (state.selectedEngine === 'auto' || state.selectedEngine === 'groq')) {
      statusText = 'Groq Online';
      detailText = `Groq Cloud (${data.groq_model || 'llama-3.3-70b-versatile'}) connected`;
    } else if (data.ollama_available && (state.selectedEngine === 'auto' || state.selectedEngine === 'ollama')) {
      statusText = 'Ollama Online';
      detailText = `Ollama Local (${data.ollama_model || 'llama3'}) connected`;
    }

    if (navStatus) navStatus.textContent = statusText;
    if (ollamaStatus) ollamaStatus.textContent = detailText;
  } catch (error) {
    if (navStatus) navStatus.textContent = 'Offline';
    if (ollamaStatus) ollamaStatus.textContent = 'Server unavailable';
  }
}

function updateEngineDisplay() {
  loadAiStatus();
}

// --- Tabs Management ---
tabButtons.forEach((btn) => {
  btn.addEventListener('click', () => {
    tabButtons.forEach((b) => b.classList.remove('active'));
    tabContents.forEach((c) => c.classList.remove('active'));

    btn.classList.add('active');
    const tabId = btn.dataset.tab;
    const targetContent = document.getElementById(tabId);
    if (targetContent) {
      targetContent.classList.add('active');
    }
  });
});

// --- Progress & Momentum Bar ---
async function loadProgress() {
  try {
    const response = await fetch('/api/progress');
    const data = await response.json();
    if (statTopics) statTopics.textContent = data.completed_topics || 0;
    if (statHours) statHours.textContent = Number(data.study_hours || 0).toFixed(1);
    if (statQuizzes) statQuizzes.textContent = data.quizzes_completed || 0;
    if (statFocusSessions) statFocusSessions.textContent = state.pomodoro.completedSessions;
  } catch (e) {
    // fallback
  }
}

// --- Tab 1: AI Tutor (Chat) ---
function appendChatMessage(sender, text, isMarkdown = true) {
  const isBot = sender === 'bot';
  const messageDiv = document.createElement('div');
  messageDiv.className = `chat-message ${isBot ? 'bot-message' : 'user-message'}`;

  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.textContent = isBot ? '✦' : '👤';

  const body = document.createElement('div');
  body.className = 'msg-body';

  const header = document.createElement('div');
  header.className = 'msg-header';
  header.innerHTML = `<strong>${isBot ? 'StudyBuddy AI' : 'You'}</strong> <span class="msg-time">Just now</span>`;

  const content = document.createElement('div');
  content.className = 'msg-content';
  if (isBot && isMarkdown) {
    content.innerHTML = formatMarkdown(text);
  } else {
    content.textContent = text;
  }

  body.appendChild(header);
  body.appendChild(content);

  // If bot, add Speak & Copy action buttons
  if (isBot) {
    const actions = document.createElement('div');
    actions.className = 'msg-actions';
    actions.style.marginTop = '0.5rem';
    actions.style.display = 'flex';
    actions.style.gap = '0.5rem';

    const copyBtn = document.createElement('button');
    copyBtn.className = 'icon-link-btn';
    copyBtn.type = 'button';
    copyBtn.innerHTML = '📋 Copy';
    copyBtn.addEventListener('click', () => {
      navigator.clipboard.writeText(text);
      copyBtn.textContent = '✓ Copied!';
      setTimeout(() => (copyBtn.innerHTML = '📋 Copy'), 2000);
    });

    const speakBtn = document.createElement('button');
    speakBtn.className = 'icon-link-btn';
    speakBtn.type = 'button';
    speakBtn.innerHTML = '🔊 Listen';
    speakBtn.addEventListener('click', () => {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utter = new SpeechSynthesisUtterance(text);
        utter.rate = 1.05;
        window.speechSynthesis.speak(utter);
      }
    });

    actions.appendChild(copyBtn);
    actions.appendChild(speakBtn);
    body.appendChild(actions);
  }

  messageDiv.appendChild(avatar);
  messageDiv.appendChild(body);
  chatViewport.appendChild(messageDiv);
  chatViewport.scrollTop = chatViewport.scrollHeight;
}

if (questionForm) {
  questionForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const question = questionInput.value.trim();
    const subject = subjectInput.value;
    const mode = modeInput.value;

    if (!question) return;

    // Add user message to chat
    appendChatMessage('user', question, false);
    questionInput.value = '';

    // Show typing placeholder
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'chat-message bot-message typing-indicator';
    typingIndicator.innerHTML = `
      <div class="msg-avatar">✦</div>
      <div class="msg-body"><div class="msg-content"><em>Thinking & consulting knowledge base...</em></div></div>
    `;
    chatViewport.appendChild(typingIndicator);
    chatViewport.scrollTop = chatViewport.scrollHeight;

    sendBtn.disabled = true;

    try {
      const data = await postJson('/api/answer', {
        question,
        subject,
        mode,
        engine: state.selectedEngine,
      });

      typingIndicator.remove();
      appendChatMessage('bot', data.answer);
      loadMemory();
    } catch (error) {
      typingIndicator.remove();
      appendChatMessage('bot', `⚠️ **Error**: ${error.message}\nPlease check your network or try changing the AI engine dropdown at the top.`);
    } finally {
      sendBtn.disabled = false;
      questionInput.focus();
    }
  });

  // Enter sends, Shift+Enter new line
  questionInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      questionForm.dispatchEvent(new Event('submit'));
    }
  });
}

// Chips click
document.querySelectorAll('.chip').forEach((chip) => {
  chip.addEventListener('click', () => {
    if (questionInput) {
      questionInput.value = chip.dataset.prompt;
      questionInput.focus();
    }
  });
});

if (clearChatBtn) {
  clearChatBtn.addEventListener('click', () => {
    chatViewport.innerHTML = `
      <div class="chat-message bot-message">
        <div class="msg-avatar">✦</div>
        <div class="msg-body">
          <div class="msg-header">
            <strong>StudyBuddy AI</strong>
            <span class="msg-time">Just now</span>
          </div>
          <div class="msg-content">
            Chat cleared. What topic or concept would you like to explore next?
          </div>
        </div>
      </div>
    `;
  });
}

// --- Tab 2: Study Planner ---
if (planForm) {
  planForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const topic = planTopicInput.value.trim();
    const days = Number(planDaysInput.value || 5);

    if (!topic) return;

    planStatusMsg.style.display = 'block';
    planStatusMsg.className = 'status-msg info-msg';
    planStatusMsg.textContent = `Structuring customized ${days}-day learning roadmap for "${topic}"...`;
    planContainer.innerHTML = '';
    if (exportPlanBtn) exportPlanBtn.style.display = 'none';

    try {
      const data = await postJson('/api/plan', { topic, days, engine: state.selectedEngine });
      const planItems = data.plan || [];

      state.currentPlan = { topic, days, items: planItems };
      planStatusMsg.style.display = 'none';

      let html = '';
      planItems.forEach((item, idx) => {
        html += `
          <div class="plan-card">
            <div class="plan-day-badge">Day ${idx + 1}</div>
            <div class="plan-details">
              <label class="plan-checkbox-label">
                <input type="checkbox" class="plan-check" data-day="${idx + 1}" />
                <span class="plan-text">${escapeHtml(item)}</span>
              </label>
            </div>
          </div>
        `;
      });
      planContainer.innerHTML = html;

      if (exportPlanBtn) exportPlanBtn.style.display = 'inline-block';

      // Attach checkbox listener to update completed topics
      document.querySelectorAll('.plan-check').forEach((chk) => {
        chk.addEventListener('change', async () => {
          if (chk.checked) {
            playNotificationChime('success');
            // update completed topics
            const curr = Number(statTopics.textContent || 0);
            await postJson('/api/progress', { completed_topics: curr + 1 });
            loadProgress();
          }
        });
      });
    } catch (err) {
      planStatusMsg.className = 'status-msg error-msg';
      planStatusMsg.textContent = `Failed to generate plan: ${err.message}`;
    }
  });
}

if (exportPlanBtn) {
  exportPlanBtn.addEventListener('click', async () => {
    if (!state.currentPlan) return;
    const { topic, days, items } = state.currentPlan;
    const content = `# Study Plan: ${topic} (${days} Days)\n\nGenerated by StudyBuddy AI\n\n` +
      items.map((it, idx) => `### Day ${idx + 1}\n- [ ] ${it}\n`).join('\n');

    try {
      const res = await postJson('/api/export', { type: 'plan', content, topic });
      downloadFile(res.filename || `study_plan_${topic}.md`, content);
    } catch (e) {
      downloadFile(`study_plan_${topic}.md`, content);
    }
  });
}

// --- Tab 3: Interactive Practice Quiz ---
if (quizForm) {
  quizForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const topic = quizTopicInput.value.trim();
    const count = Number(quizCountInput.value || 3);

    if (!topic) return;

    quizLoading.style.display = 'block';
    quizLoading.className = 'status-msg info-msg';
    quizLoading.textContent = `Drafting ${count} quiz questions grounded in "${topic}"...`;
    quizRunner.style.display = 'none';
    quizResultsCard.style.display = 'none';
    if (exportQuizBtn) exportQuizBtn.style.display = 'none';

    try {
      const data = await postJson('/api/quiz', { topic, count, engine: state.selectedEngine });
      const questions = data.quiz || [];

      if (!questions.length) {
        throw new Error('No questions returned for this topic.');
      }

      state.currentQuiz = { topic, questions };
      state.userQuizAnswers = {};

      quizTopicDisplay.textContent = `Topic: ${topic}`;
      quizProgressDisplay.textContent = `${questions.length} Questions`;

      renderQuizQuestions(questions);

      quizLoading.style.display = 'none';
      quizRunner.style.display = 'block';
      if (exportQuizBtn) exportQuizBtn.style.display = 'inline-block';
    } catch (err) {
      quizLoading.className = 'status-msg error-msg';
      quizLoading.textContent = `Quiz error: ${err.message}`;
    }
  });
}

function renderQuizQuestions(questions) {
  quizQuestionsList.innerHTML = '';

  questions.forEach((q, idx) => {
    const card = document.createElement('div');
    card.className = 'quiz-question-card';

    const qNum = idx + 1;
    let optionsHtml = '';

    if (Array.isArray(q.options) && q.options.length > 0) {
      optionsHtml = `
        <div class="quiz-options-grid">
          ${q.options
            .map(
              (opt, oIdx) => `
            <label class="quiz-option-label">
              <input type="radio" name="quiz_q_${idx}" value="${escapeHtml(opt)}" data-q-idx="${idx}" />
              <span class="opt-indicator">${String.fromCharCode(65 + oIdx)}</span>
              <span class="opt-text">${escapeHtml(opt)}</span>
            </label>
          `,
            )
            .join('')}
        </div>
      `;
    } else {
      optionsHtml = `
        <div class="quiz-text-answer-box">
          <input type="text" class="quiz-answer-input" placeholder="Type your answer here..." data-q-idx="${idx}" />
        </div>
      `;
    }

    card.innerHTML = `
      <div class="quiz-question-header">
        <span class="quiz-num">Q${qNum}</span>
        <span class="quiz-q-text">${escapeHtml(q.question)}</span>
      </div>
      ${optionsHtml}
    `;

    quizQuestionsList.appendChild(card);
  });

  // Track answers
  quizQuestionsList.querySelectorAll('input[type="radio"]').forEach((radio) => {
    radio.addEventListener('change', (e) => {
      const qIdx = e.target.dataset.qIdx;
      state.userQuizAnswers[qIdx] = e.target.value;
    });
  });

  quizQuestionsList.querySelectorAll('.quiz-answer-input').forEach((input) => {
    input.addEventListener('input', (e) => {
      const qIdx = e.target.dataset.qIdx;
      state.userQuizAnswers[qIdx] = e.target.value.trim();
    });
  });
}

if (submitQuizBtn) {
  submitQuizBtn.addEventListener('click', async () => {
    if (!state.currentQuiz) return;
    const { topic, questions } = state.currentQuiz;

    // Convert dictionary answers to array
    const userAnswersList = questions.map((_, idx) => state.userQuizAnswers[idx] || '');

    submitQuizBtn.disabled = true;
    submitQuizBtn.textContent = 'Grading Answers with AI...';

    try {
      const evalData = await postJson('/api/quiz/evaluate', {
        topic,
        questions,
        answers: userAnswersList,
        engine: state.selectedEngine,
      });

      playNotificationChime('quiz');
      displayQuizResults(evalData, questions, userAnswersList);

      // Increment progress quizzes count
      const curr = Number(statQuizzes.textContent || 0);
      await postJson('/api/progress', { quizzes_completed: curr + 1 });
      loadProgress();
    } catch (err) {
      alert(`Could not evaluate quiz: ${err.message}`);
    } finally {
      submitQuizBtn.disabled = false;
      submitQuizBtn.textContent = 'Submit Answers & Grade Quiz ✓';
    }
  });
}

function displayQuizResults(evalData, questions, userAnswers) {
  const percentage = evalData.percentage ?? 0;
  const score = evalData.score ?? 0;
  const total = evalData.total ?? questions.length;
  const breakdown = evalData.breakdown || [];

  let badgeEmoji = '🎉';
  let badgeTitle = 'Outstanding Mastery!';
  if (percentage < 50) {
    badgeEmoji = '📚';
    badgeTitle = 'Keep Practicing!';
  } else if (percentage < 80) {
    badgeEmoji = '⭐';
    badgeTitle = 'Solid Understanding!';
  }

  let breakdownHtml = '';
  breakdown.forEach((item, idx) => {
    const isCorrect = item.correct;
    breakdownHtml += `
      <div class="result-breakdown-item ${isCorrect ? 'item-correct' : 'item-incorrect'}">
        <div class="item-status-bar">
          <span class="status-tag ${isCorrect ? 'correct-tag' : 'incorrect-tag'}">
            ${isCorrect ? '✓ Correct' : '✗ Review Needed'}
          </span>
          <strong>Question ${idx + 1}</strong>
        </div>
        <div class="item-question"><strong>Q:</strong> ${escapeHtml(item.question)}</div>
        <div class="item-answers-comparison">
          <div class="user-ans">Your Answer: <span class="ans-value">${escapeHtml(item.user_answer || '(None given)')}</span></div>
          <div class="correct-ans">Expected Answer: <span class="ans-value">${escapeHtml(item.expected_answer)}</span></div>
        </div>
        ${item.explanation ? `<div class="item-explanation">💡 ${escapeHtml(item.explanation)}</div>` : ''}
      </div>
    `;
  });

  quizResultsCard.innerHTML = `
    <div class="results-header">
      <div class="results-badge">${badgeEmoji}</div>
      <h3>${badgeTitle}</h3>
      <div class="score-display">
        <span class="score-number">${score}/${total}</span>
        <span class="score-percent">(${percentage}%)</span>
      </div>
    </div>
    <div class="results-breakdown-list">
      ${breakdownHtml}
    </div>
  `;

  quizResultsCard.style.display = 'block';
  quizResultsCard.scrollIntoView({ behavior: 'smooth' });
}

if (exportQuizBtn) {
  exportQuizBtn.addEventListener('click', async () => {
    if (!state.currentQuiz) return;
    const { topic, questions } = state.currentQuiz;
    const content = `# Practice Quiz: ${topic}\n\nGenerated by StudyBuddy AI\n\n` +
      questions.map((q, idx) => {
        let text = `### Q${idx + 1}: ${q.question}\n`;
        if (q.options) {
          text += q.options.map((opt, oIdx) => `- ${String.fromCharCode(65 + oIdx)}) ${opt}`).join('\n') + '\n';
        }
        text += `\n**Answer:** ${q.answer}\n`;
        return text;
      }).join('\n');

    try {
      const res = await postJson('/api/export', { type: 'quiz', content, topic });
      downloadFile(res.filename || `quiz_${topic}.md`, content);
    } catch (e) {
      downloadFile(`quiz_${topic}.md`, content);
    }
  });
}

// --- Tab 4: 3D Flashcards ---
if (flashcardForm) {
  flashcardForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const topic = flashcardTopicInput.value.trim();
    const count = Number(flashcardCountInput.value || 6);

    if (!topic) return;

    flashcardStatus.style.display = 'block';
    flashcardStatus.className = 'status-msg info-msg';
    flashcardStatus.textContent = `Synthesizing ${count} active-recall flashcards for "${topic}"...`;

    try {
      const data = await postJson('/api/flashcards', { topic, count, engine: state.selectedEngine });
      const cards = data.flashcards || [];

      if (!cards.length) throw new Error('Could not generate cards for this topic.');

      state.flashcards = cards;
      state.currentCardIndex = 0;
      state.cardFlipped = false;
      state.cardMastery = {};

      flashcardStatus.style.display = 'none';
      renderCurrentFlashcard();
    } catch (err) {
      flashcardStatus.className = 'status-msg error-msg';
      flashcardStatus.textContent = `Flashcard error: ${err.message}`;
    }
  });
}

function renderCurrentFlashcard() {
  if (!state.flashcards.length) {
    cardFrontText.textContent = 'Generate a deck above to start studying!';
    cardBackText.textContent = 'Answer will appear here.';
    deckCounter.textContent = '0 / 0';
    return;
  }

  const card = state.flashcards[state.currentCardIndex];
  state.cardFlipped = false;
  flashcardElement.classList.remove('is-flipped');

  cardTag.textContent = card.tag || flashcardTopicInput.value || 'Key Concept';
  cardFrontText.textContent = card.front || card.question;
  cardBackText.textContent = card.back || card.answer;
  deckCounter.textContent = `${state.currentCardIndex + 1} / ${state.flashcards.length}`;

  // Mastery visual indicator
  const mastery = state.cardMastery[state.currentCardIndex];
  flashcardElement.classList.remove('status-mastered', 'status-review');
  if (mastery === 'mastered') {
    flashcardElement.classList.add('status-mastered');
  } else if (mastery === 'review') {
    flashcardElement.classList.add('status-review');
  }
}

function flipCard() {
  if (!state.flashcards.length) return;
  state.cardFlipped = !state.cardFlipped;
  flashcardElement.classList.toggle('is-flipped', state.cardFlipped);
}

if (flashcardElement) {
  flashcardElement.addEventListener('click', flipCard);
  flashcardElement.addEventListener('keydown', (e) => {
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      flipCard();
    }
  });
}

if (prevCardBtn) {
  prevCardBtn.addEventListener('click', () => {
    if (!state.flashcards.length) return;
    state.currentCardIndex = (state.currentCardIndex - 1 + state.flashcards.length) % state.flashcards.length;
    renderCurrentFlashcard();
  });
}

if (nextCardBtn) {
  nextCardBtn.addEventListener('click', () => {
    if (!state.flashcards.length) return;
    state.currentCardIndex = (state.currentCardIndex + 1) % state.flashcards.length;
    renderCurrentFlashcard();
  });
}

// Arrow key navigation
window.addEventListener('keydown', (e) => {
  // Only if flashcard tab is active and not focused inside an input/textarea
  const activeTab = document.querySelector('.tab-content.active');
  if (activeTab && activeTab.id === 'tab-flashcards' && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
    if (e.key === 'ArrowLeft') {
      prevCardBtn.click();
    } else if (e.key === 'ArrowRight') {
      nextCardBtn.click();
    } else if (e.key === ' ' && document.activeElement !== flashcardElement) {
      e.preventDefault();
      flipCard();
    }
  }
});

if (shuffleCardsBtn) {
  shuffleCardsBtn.addEventListener('click', () => {
    if (state.flashcards.length < 2) return;
    // Fisher-Yates shuffle
    for (let i = state.flashcards.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [state.flashcards[i], state.flashcards[j]] = [state.flashcards[j], state.flashcards[i]];
    }
    state.currentCardIndex = 0;
    renderCurrentFlashcard();
  });
}

if (markMasteredBtn) {
  markMasteredBtn.addEventListener('click', () => {
    if (!state.flashcards.length) return;
    state.cardMastery[state.currentCardIndex] = 'mastered';
    renderCurrentFlashcard();
    playNotificationChime('success');
    // auto advance
    setTimeout(() => nextCardBtn.click(), 400);
  });
}

if (markReviewBtn) {
  markReviewBtn.addEventListener('click', () => {
    if (!state.flashcards.length) return;
    state.cardMastery[state.currentCardIndex] = 'review';
    renderCurrentFlashcard();
    setTimeout(() => nextCardBtn.click(), 400);
  });
}

if (exportCardsBtn) {
  exportCardsBtn.addEventListener('click', async () => {
    if (!state.flashcards.length) return;
    const topic = flashcardTopicInput.value || 'Flashcards';
    const content = `# Flashcard Deck: ${topic}\n\nGenerated by StudyBuddy AI\n\n` +
      state.flashcards.map((c, idx) => `### Card ${idx + 1}\n**Front:** ${c.front || c.question}\n**Back:** ${c.back || c.answer}\n`).join('\n');

    try {
      const res = await postJson('/api/export', { type: 'flashcards', content, topic });
      downloadFile(res.filename || `deck_${topic}.md`, content);
    } catch (e) {
      downloadFile(`deck_${topic}.md`, content);
    }
  });
}

// --- Tab 5: Pomodoro Focus Timer ---
function updateTimerDisplay() {
  const mins = Math.floor(state.pomodoro.remainingSeconds / 60);
  const secs = state.pomodoro.remainingSeconds % 60;
  timerDigits.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;

  // SVG ring circumference = 2 * PI * r = 2 * PI * 115 ≈ 722.56
  const totalCircumference = 2 * Math.PI * 115;
  const progressRatio = state.pomodoro.remainingSeconds / state.pomodoro.totalSeconds;
  const strokeDashoffset = totalCircumference * (1 - progressRatio);

  if (timerProgressCircle) {
    timerProgressCircle.style.strokeDasharray = `${totalCircumference}`;
    timerProgressCircle.style.strokeDashoffset = `${strokeDashoffset}`;
  }
}

timerModeBtns.forEach((btn) => {
  btn.addEventListener('click', () => {
    timerModeBtns.forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');

    const mode = btn.dataset.mode;
    const minutes = Number(btn.dataset.minutes);

    state.pomodoro.mode = mode;
    state.pomodoro.totalSeconds = minutes * 60;
    state.pomodoro.remainingSeconds = minutes * 60;
    if (mode === 'focus') {
      state.pomodoro.focusDurationMinutes = minutes;
      timerLabel.textContent = 'Deep Focus';
    } else if (mode === 'short-break') {
      timerLabel.textContent = 'Short Break';
    } else {
      timerLabel.textContent = 'Long Break';
    }

    pauseTimer();
    updateTimerDisplay();
  });
});

function startTimer() {
  if (state.pomodoro.isRunning) return;
  state.pomodoro.isRunning = true;
  timerToggleBtn.textContent = 'Pause Session';
  timerToggleBtn.classList.remove('primary-btn');
  timerToggleBtn.classList.add('secondary-btn');

  state.pomodoro.timerId = setInterval(async () => {
    if (state.pomodoro.remainingSeconds > 0) {
      state.pomodoro.remainingSeconds--;
      updateTimerDisplay();
    } else {
      // Completed session
      pauseTimer();
      playNotificationChime('success');

      if (state.pomodoro.mode === 'focus') {
        state.pomodoro.completedSessions++;
        localStorage.setItem('studybuddy-pomodoro-count', state.pomodoro.completedSessions);

        // Auto-log to backend progress
        try {
          const res = await postJson('/api/pomodoro', {
            duration_minutes: state.pomodoro.focusDurationMinutes,
          });

          if (pomodoroLogFeedback) {
            pomodoroLogFeedback.textContent = `🎉 Focus session complete! Logged ${state.pomodoro.focusDurationMinutes} minutes to your study progress. Total study hours: ${res.study_hours}`;
            pomodoroLogFeedback.style.display = 'block';
            setTimeout(() => (pomodoroLogFeedback.style.display = 'none'), 6000);
          }

          loadProgress();
        } catch (e) {
          // log error
        }
      } else {
        if (pomodoroLogFeedback) {
          pomodoroLogFeedback.textContent = '🔔 Break over! Ready for another productive focus round?';
          pomodoroLogFeedback.style.display = 'block';
          setTimeout(() => (pomodoroLogFeedback.style.display = 'none'), 5000);
        }
      }
    }
  }, 1000);
}

function pauseTimer() {
  state.pomodoro.isRunning = false;
  if (state.pomodoro.timerId) {
    clearInterval(state.pomodoro.timerId);
    state.pomodoro.timerId = null;
  }
  timerToggleBtn.textContent = 'Start Session';
  timerToggleBtn.classList.remove('secondary-btn');
  timerToggleBtn.classList.add('primary-btn');
}

if (timerToggleBtn) {
  timerToggleBtn.addEventListener('click', () => {
    if (state.pomodoro.isRunning) {
      pauseTimer();
    } else {
      startTimer();
    }
  });
}

if (timerResetBtn) {
  timerResetBtn.addEventListener('click', () => {
    pauseTimer();
    state.pomodoro.remainingSeconds = state.pomodoro.totalSeconds;
    updateTimerDisplay();
  });
}

// Initial timer display setup
updateTimerDisplay();

// --- Tab 6: Course Materials Library & AI Summarizer ---
async function loadMaterials() {
  try {
    const response = await fetch('/api/materials');
    const data = await response.json();
    const list = data.materials || [];

    if (materialsCount) materialsCount.textContent = list.length;
    if (materialsResult) {
      materialsResult.innerHTML = list.length
        ? list.map((name) => `<li><span class="file-icon">📄</span> <span class="file-name">${escapeHtml(name)}</span></li>`).join('')
        : '<li class="empty-list">No course documents ingested yet. Drop your first notes above!</li>';
    }
  } catch (e) {
    //
  }
}

if (refreshMaterialsBtn) {
  refreshMaterialsBtn.addEventListener('click', loadMaterials);
}

if (uploadForm) {
  uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const file = materialFileInput.files[0];
    if (!file) {
      uploadResult.style.display = 'block';
      uploadResult.className = 'status-msg error-msg';
      uploadResult.textContent = 'Please select a TXT, MD, PDF, DOCX, or PPTX file.';
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    uploadResult.style.display = 'block';
    uploadResult.className = 'status-msg info-msg';
    uploadResult.textContent = `Ingesting and indexing "${file.name}" into RAG memory...`;

    try {
      const response = await fetch('/api/upload', { method: 'POST', body: formData });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Upload failed');

      uploadResult.className = 'status-msg success-msg';
      uploadResult.textContent = `✓ Ingested "${data.filename}" (${data.chunks} semantic chunks indexed).`;
      materialFileInput.value = '';
      await loadMaterials();
    } catch (err) {
      uploadResult.className = 'status-msg error-msg';
      uploadResult.textContent = `Error: ${err.message}`;
    }
  });
}

// Document Summarizer
if (summaryForm) {
  summaryForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const topic = summaryTopicInput.value.trim();

    summaryLoading.style.display = 'block';
    summaryLoading.className = 'status-msg info-msg';
    summaryLoading.textContent = `Synthesizing executive summary and glossary${topic ? ` on "${topic}"` : ''}...`;
    if (exportSummaryBtn) exportSummaryBtn.style.display = 'none';

    try {
      const data = await postJson('/api/summarize', { topic, engine: state.selectedEngine });
      state.currentSummary = data;

      summaryLoading.style.display = 'none';

      let keyTermsHtml = '';
      if (Array.isArray(data.key_terms) && data.key_terms.length > 0) {
        keyTermsHtml = `
          <div class="summary-terms-card">
            <h4>🔑 Key Academic Concepts & Glossary</h4>
            <ul class="key-terms-list">
              ${data.key_terms
                .map(
                  (term) => `
                <li>
                  <strong>${escapeHtml(term.term || term.concept || 'Concept')}:</strong>
                  <span>${escapeHtml(term.definition || term.explanation || '')}</span>
                </li>
              `,
                )
                .join('')}
            </ul>
          </div>
        `;
      }

      summaryOutput.innerHTML = `
        <div class="summary-content-rendered">
          <div class="summary-body">
            <h3>Executive Summary: ${escapeHtml(data.topic || topic || 'Course Knowledge')}</h3>
            <div class="summary-text">${formatMarkdown(data.summary)}</div>
          </div>
          ${keyTermsHtml}
        </div>
      `;

      if (exportSummaryBtn) exportSummaryBtn.style.display = 'inline-block';
    } catch (err) {
      summaryLoading.className = 'status-msg error-msg';
      summaryLoading.textContent = `Summarizer error: ${err.message}`;
    }
  });
}

if (exportSummaryBtn) {
  exportSummaryBtn.addEventListener('click', async () => {
    if (!state.currentSummary) return;
    const { topic, summary, key_terms } = state.currentSummary;
    let content = `# Document Summary: ${topic || 'Course Notes'}\n\nGenerated by StudyBuddy AI\n\n${summary}\n\n`;

    if (key_terms && key_terms.length) {
      content += `## Key Concepts & Glossary\n\n`;
      key_terms.forEach((t) => {
        content += `- **${t.term || t.concept}**: ${t.definition || t.explanation}\n`;
      });
    }

    try {
      const res = await postJson('/api/export', { type: 'summary', content, topic: topic || 'Summary' });
      downloadFile(res.filename || `summary_${topic || 'notes'}.md`, content);
    } catch (e) {
      downloadFile(`summary_${topic || 'notes'}.md`, content);
    }
  });
}

// --- Memory Drawer ---
async function loadMemory() {
  try {
    const response = await fetch('/api/memory');
    const data = await response.json();
    if (memoryResult) {
      memoryResult.textContent = data.summary || 'No conversation history recorded yet.';
    }
  } catch (e) {
    //
  }
}

if (memoryButton) memoryButton.addEventListener('click', loadMemory);

if (clearMemoryButton) {
  clearMemoryButton.addEventListener('click', async () => {
    if (!window.confirm('Clear all conversation history from agent memory?')) return;
    try {
      const response = await fetch('/api/memory', { method: 'DELETE' });
      const data = await response.json();
      if (memoryResult) memoryResult.textContent = data.message || 'Memory cleared.';
    } catch (err) {
      alert(`Could not clear memory: ${err.message}`);
    }
  });
}

// --- Theme Toggling ---
if (themeButton) {
  themeButton.addEventListener('click', () => {
    document.body.classList.toggle('light-theme');
    const isLight = document.body.classList.contains('light-theme');
    localStorage.setItem('studybuddy-theme', isLight ? 'light' : 'dark');
    themeButton.querySelector('.theme-icon').textContent = isLight ? '☾' : '☼';
  });
}

if (localStorage.getItem('studybuddy-theme') === 'light') {
  document.body.classList.add('light-theme');
  if (themeButton) {
    const icon = themeButton.querySelector('.theme-icon');
    if (icon) icon.textContent = '☾';
  }
}

// --- Initialization ---
loadAiStatus();
loadProgress();
loadMaterials();
loadMemory();

// Service worker
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/static/service-worker.js').catch(() => {});
}
