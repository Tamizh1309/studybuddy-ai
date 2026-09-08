// StudyBuddy AI — Frontend Application Logic (Next-Gen Agentic Architecture)
// Features: Multi-Engine AI, Agent Architect, Concept Mind Map, Code Explainer, Voice Input, 3D Flashcards, Graded Quizzes, Pomodoro, Document Viewer, Streaks & Badges

// --- State Management ---
const state = {
  selectedEngine: localStorage.getItem('studybuddy-engine') || 'auto',
  selectedRagMode: localStorage.getItem('studybuddy-rag-mode') || 'hybrid',
  currentQuiz: null,
  userQuizAnswers: {},
  flashcards: [],
  currentCardIndex: 0,
  cardFlipped: false,
  cardMastery: {}, // index -> 'mastered' | 'review'
  currentPlan: null,
  currentSummary: null,
  architectData: null,
  activeDoc: null,
  pomodoro: {
    timerId: null,
    totalSeconds: 25 * 60,
    remainingSeconds: 25 * 60,
    isRunning: false,
    mode: 'focus', // 'focus' | 'short-break' | 'long-break'
    focusDurationMinutes: 25,
    completedSessions: Number(localStorage.getItem('studybuddy-pomodoro-count') || 0),
  },
  voice: {
    recognition: null,
    isRecording: false,
  },
};

// --- DOM References ---
const aiEngineSelect = document.getElementById('ai-engine-select');
const ragModeSelect = document.getElementById('rag-mode-select');
const navStatus = document.getElementById('nav-status');
const ollamaStatus = document.getElementById('ollama-status');
const themeButton = document.getElementById('theme-button');

// Stats Bar
const statStreak = document.getElementById('stat-streak');
const statTopics = document.getElementById('stat-topics');
const statHours = document.getElementById('stat-hours');
const statQuizzes = document.getElementById('stat-quizzes');
const statFocusSessions = document.getElementById('stat-focus-sessions');
const statBadgesCount = document.getElementById('stat-badges-count');
const viewBadgesCard = document.getElementById('view-badges-card');

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
const voiceMicBtn = document.getElementById('voice-mic-btn');
const voiceStatusIndicator = document.getElementById('voice-status-indicator');
const voiceStatusText = document.getElementById('voice-status-text');

// Agent Architect
const architectForm = document.getElementById('architect-form');
const architectGoalInput = document.getElementById('architect-goal');
const architectDaysInput = document.getElementById('architect-days');
const architectStatus = document.getElementById('architect-status');
const architectTraceBox = document.getElementById('architect-trace-box');
const architectStepsList = document.getElementById('architect-steps-list');
const architectResultsBox = document.getElementById('architect-results-box');
const archCurriculumList = document.getElementById('arch-curriculum-list');
const archQuizList = document.getElementById('arch-quiz-list');
const archCardsList = document.getElementById('arch-cards-list');
const archQuizCount = document.getElementById('arch-quiz-count');
const archCardsCount = document.getElementById('arch-cards-count');
const sendToQuizTabBtn = document.getElementById('send-to-quiz-tab-btn');
const sendToCardsTabBtn = document.getElementById('send-to-cards-tab-btn');

// Concept Mind Map
const conceptmapForm = document.getElementById('conceptmap-form');
const conceptmapTopic = document.getElementById('conceptmap-topic');
const conceptmapStatus = document.getElementById('conceptmap-status');
const conceptmapCanvas = document.getElementById('conceptmap-canvas');
const conceptRoot = document.getElementById('concept-root');
const conceptBranches = document.getElementById('concept-branches');
const copyMermaidBtn = document.getElementById('copy-mermaid-btn');
const conceptmapMermaidBox = document.getElementById('conceptmap-mermaid-box');
const conceptmapMermaidCode = document.getElementById('conceptmap-mermaid-code');

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

// Code Explainer
const codeForm = document.getElementById('code-form');
const codeLangSelect = document.getElementById('code-lang-select');
const codeModeSelect = document.getElementById('code-mode-select');
const codeInput = document.getElementById('code-input');
const codeLoading = document.getElementById('code-loading');
const codeResults = document.getElementById('code-results');
const metricTimeComp = document.getElementById('metric-time-comp');
const metricSpaceComp = document.getElementById('metric-space-comp');
const codeSummaryText = document.getElementById('code-summary-text');
const codeLinesTable = document.getElementById('code-lines-table');
const codeSuggestionsList = document.getElementById('code-suggestions-list');

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

// Modals
const docModal = document.getElementById('doc-modal');
const docModalTitle = document.getElementById('doc-modal-title');
const docModalContent = document.getElementById('doc-modal-content');
const closeDocModalBtn = document.getElementById('close-doc-modal-btn');
const docQuickSummarize = document.getElementById('doc-quick-summarize');
const docQuickCards = document.getElementById('doc-quick-cards');
const docQuickQuiz = document.getElementById('doc-quick-quiz');

const badgesModal = document.getElementById('badges-modal');
const closeBadgesModalBtn = document.getElementById('close-badges-modal-btn');
const badgesGrid = document.getElementById('badges-grid');

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
  parsed = parsed.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
  parsed = parsed.replace(/`([^`]+)`/g, '<code>$1</code>');
  parsed = parsed.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  parsed = parsed.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  parsed = parsed.replace(/^### (.*$)/gim, '<h4>$1</h4>');
  parsed = parsed.replace(/^## (.*$)/gim, '<h3>$1</h3>');
  parsed = parsed.replace(/^# (.*$)/gim, '<h2>$1</h2>');
  parsed = parsed.replace(/^\s*[-*]\s+(.*$)/gim, '<li>$1</li>');
  parsed = parsed.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
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

function switchTab(tabId) {
  tabButtons.forEach((b) => b.classList.remove('active'));
  tabContents.forEach((c) => c.classList.remove('active'));

  const btn = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
  const content = document.getElementById(tabId);
  if (btn) btn.classList.add('active');
  if (content) {
    content.classList.add('active');
    content.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  if (tabId === 'tab-dashboard') {
    loadDashboard();
  } else if (tabId === 'tab-memory') {
    loadMemory();
  }
}

// Sound Synthesizer
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
  } catch (e) {}
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

if (ragModeSelect) {
  ragModeSelect.value = state.selectedRagMode;
  ragModeSelect.addEventListener('change', (e) => {
    state.selectedRagMode = e.target.value;
    localStorage.setItem('studybuddy-rag-mode', state.selectedRagMode);
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
    switchTab(btn.dataset.tab);
  });
});

// --- Progress, Streaks & Badges ---
const ALL_BADGES = [
  { id: 'First Steps', name: 'First Steps', icon: '🎓', desc: 'Started your AI learning journey' },
  { id: 'Curriculum Explorer', name: 'Curriculum Explorer', icon: '🗺️', desc: 'Completed your first study topic' },
  { id: 'Focus Titan', name: 'Focus Titan', icon: '⏱️', desc: 'Completed a 25-minute Pomodoro focus round' },
  { id: 'Quiz Ace', name: 'Quiz Ace', icon: '🎯', desc: 'Completed and graded an interactive practice quiz' },
  { id: 'Agent Architect', name: 'Agent Architect', icon: '🤖', desc: 'Generated an autonomous multi-step study plan' },
  { id: 'Recall Master', name: 'Recall Master', icon: '🗂️', desc: 'Mastered concepts using 3D Active Recall flashcards' },
];

async function loadProgress() {
  try {
    const response = await fetch('/api/progress');
    const data = await response.json();
    if (statStreak) statStreak.textContent = data.streak_days || 1;
    if (statTopics) statTopics.textContent = data.completed_topics || 0;
    if (statHours) statHours.textContent = Number(data.study_hours || 0).toFixed(1);
    if (statQuizzes) statQuizzes.textContent = data.quizzes_completed || 0;
    if (statFocusSessions) statFocusSessions.textContent = state.pomodoro.completedSessions;

    const userBadges = data.badges || ['First Steps'];
    if (statBadgesCount) statBadgesCount.textContent = userBadges.length;

    renderBadgesModal(userBadges);
  } catch (e) {}
}

function renderBadgesModal(unlockedBadges = []) {
  if (!badgesGrid) return;
  badgesGrid.innerHTML = ALL_BADGES.map((b) => {
    const isUnlocked = unlockedBadges.includes(b.id);
    return `
      <div class="badge-item-card ${isUnlocked ? 'unlocked' : 'locked'}">
        <div class="badge-icon">${b.icon}</div>
        <div class="badge-title">${b.name}</div>
        <div class="badge-desc">${b.desc}</div>
        <span class="badge-status-tag ${isUnlocked ? 'badge-unlocked-tag' : 'badge-locked-tag'}">
          ${isUnlocked ? '✓ Unlocked' : '🔒 In Progress'}
        </span>
      </div>
    `;
  }).join('');
}

if (viewBadgesCard) {
  viewBadgesCard.addEventListener('click', () => {
    if (badgesModal) badgesModal.style.display = 'flex';
  });
}
if (closeBadgesModalBtn) {
  closeBadgesModalBtn.addEventListener('click', () => {
    if (badgesModal) badgesModal.style.display = 'none';
  });
}

// --- Student Dashboard ---
async function loadDashboard() {
  try {
    const res = await fetch('/api/dashboard');
    const data = await res.json();
    if (!data) return;

    // Greeting
    const greetingEl = document.getElementById('dash-greeting');
    if (greetingEl) greetingEl.textContent = data.greeting || 'Good Evening, Tamizh 👋';

    // Spotlight: Next Best Action
    const nba = data.next_best_action;
    if (nba) {
      const nbaTitle = document.getElementById('nba-action-title');
      const nbaDesc = document.getElementById('nba-action-desc');
      const nbaSubReason = document.getElementById('nba-sub-reason');
      const nbaBtn = document.getElementById('nba-action-btn');

      if (nbaTitle) nbaTitle.textContent = nba.action || 'Revise Operating Systems – Deadlocks';
      if (nbaDesc) nbaDesc.textContent = nba.reason || 'Your last quiz score was 55% and your exam is in 2 days.';
      if (nbaSubReason) nbaSubReason.textContent = `Priority Focus • Based on recent 55% score`;
      if (nbaBtn) {
        nbaBtn.textContent = nba.button_label || 'Start Revision →';
        nbaBtn.onclick = () => {
          triggerMasterAgent(
            `Tomorrow I have ${nba.subject || 'OS'} exam. Give me a revision plan and then quiz me on ${nba.topic || 'deadlocks'}.`
          );
        };
      }
    }

    // Today's Study Plan Tasks
    const tasksContainer = document.getElementById('dash-tasks-container');
    const planRatio = document.getElementById('dash-plan-ratio');
    if (tasksContainer && data.today_plan) {
      const completedCount = data.today_plan.filter(t => t.completed).length;
      if (planRatio) planRatio.textContent = `${completedCount}/${data.today_plan.length} Done`;

      tasksContainer.innerHTML = data.today_plan.map(task => `
        <div class="dash-task-item ${task.completed ? 'completed' : ''} ${task.current ? 'current' : ''}">
          <label class="task-checkbox-label">
            <input type="checkbox" class="dash-task-checkbox" data-id="${task.id}" ${task.completed ? 'checked' : ''} />
            <span class="task-custom-checkbox"></span>
          </label>
          <div class="task-content">
            <span class="task-name">${task.current ? '➔ ' : ''}${escapeHtml(task.title)}</span>
            <span class="task-duration">${task.duration || '45m'}</span>
          </div>
          ${task.completed ? '<span class="task-badge done-badge">✓ Done</span>' : task.current ? '<span class="task-badge current-badge">In Progress</span>' : '<span class="task-badge pending-badge">Pending</span>'}
        </div>
      `).join('');

      tasksContainer.querySelectorAll('.dash-task-checkbox').forEach(cb => {
        cb.addEventListener('change', async (e) => {
          const taskId = e.target.dataset.id;
          try {
            await postJson('/api/dashboard/plan/toggle', { task_id: taskId });
            loadDashboard();
          } catch (err) {}
        });
      });
    }

    // Upcoming Exams
    const examsContainer = document.getElementById('dash-exams-container');
    if (examsContainer && data.upcoming_exams) {
      examsContainer.innerHTML = data.upcoming_exams.map(ex => `
        <div class="exam-item-card">
          <div class="exam-info">
            <span class="exam-subject">📚 ${escapeHtml(ex.subject)}</span>
            <span class="exam-status-tag">${escapeHtml(ex.status)}</span>
          </div>
          <div class="exam-days-tag">${escapeHtml(ex.date)}</div>
        </div>
      `).join('');
    }

    // Weak Topics
    const weakContainer = document.getElementById('dash-weak-container');
    if (weakContainer && data.weak_topics) {
      weakContainer.innerHTML = data.weak_topics.map(w => `
        <div class="weak-topic-row">
          <div class="weak-topic-header">
            <span class="weak-topic-name">⚠️ ${escapeHtml(w.topic)} <small style="color:var(--text-muted);">(${escapeHtml(w.subject)})</small></span>
            <span class="weak-topic-score">${w.score}%</span>
          </div>
          <div class="weak-topic-bar-bg">
            <div class="weak-topic-bar-fill" style="width: ${w.score}%"></div>
          </div>
        </div>
      `).join('');
    }

    // Recent Quizzes
    const quizHistoryContainer = document.getElementById('dash-quiz-history-container');
    if (quizHistoryContainer && data.recent_quizzes) {
      quizHistoryContainer.innerHTML = data.recent_quizzes.map(q => `
        <div class="recent-quiz-pill">
          <span class="quiz-subject">🎯 ${escapeHtml(q.subject)}</span>
          <span class="quiz-score-badge">${escapeHtml(q.score)} (${q.percent}%)</span>
        </div>
      `).join('');
    }
  } catch (err) {
    console.error('Failed to load dashboard data:', err);
  }
}

// Dashboard Quick-Ask & Quick Goal Chips
const dashAskForm = document.getElementById('dash-ask-form');
const dashAskInput = document.getElementById('dash-ask-input');

if (dashAskForm) {
  dashAskForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const query = dashAskInput.value.trim();
    if (!query) return;
    dashAskInput.value = '';
    triggerMasterAgent(query);
  });
}

document.querySelectorAll('.quick-goal-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    const goal = btn.dataset.goal;
    if (goal) triggerMasterAgent(goal);
  });
});

// --- Voice Input (Speech-to-Text) ---
function initSpeechRecognition() {
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRec) {
    if (voiceMicBtn) {
      voiceMicBtn.title = 'Speech-to-text is not supported in this browser';
      voiceMicBtn.style.opacity = '0.5';
    }
    return;
  }

  state.voice.recognition = new SpeechRec();
  state.voice.recognition.continuous = false;
  state.voice.recognition.interimResults = true;
  state.voice.recognition.lang = 'en-US';

  state.voice.recognition.onstart = () => {
    state.voice.isRecording = true;
    if (voiceMicBtn) voiceMicBtn.classList.add('recording');
    if (voiceStatusIndicator) voiceStatusIndicator.style.display = 'flex';
    if (voiceStatusText) voiceStatusText.textContent = 'Listening... Speak your academic question clearly';
  };

  state.voice.recognition.onresult = (event) => {
    const transcript = Array.from(event.results)
      .map((res) => res[0].transcript)
      .join('');
    if (questionInput) questionInput.value = transcript;
  };

  state.voice.recognition.onerror = (event) => {
    if (voiceStatusText) voiceStatusText.textContent = `Microphone error: ${event.error}`;
    stopVoiceRecording();
  };

  state.voice.recognition.onend = () => {
    stopVoiceRecording();
    if (questionInput && questionInput.value.trim().length > 0) {
      questionInput.focus();
    }
  };
}

function stopVoiceRecording() {
  state.voice.isRecording = false;
  if (voiceMicBtn) voiceMicBtn.classList.remove('recording');
  if (voiceStatusIndicator) voiceStatusIndicator.style.display = 'none';
}

if (voiceMicBtn) {
  initSpeechRecognition();
  voiceMicBtn.addEventListener('click', () => {
    if (!state.voice.recognition) {
      alert('Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari.');
      return;
    }
    if (state.voice.isRecording) {
      state.voice.recognition.stop();
      stopVoiceRecording();
    } else {
      try {
        state.voice.recognition.start();
      } catch (e) {
        stopVoiceRecording();
      }
    }
  });
}

function escapeHtml(str) {
  return String(str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// --- Master Agent Bridge & Helpers ---
function triggerMasterAgent(userGoal) {
  switchTab('tab-tutor');
  if (questionInput) questionInput.value = userGoal;
  if (questionForm) questionForm.dispatchEvent(new Event('submit'));
}

function renderActiveQuiz(quizData) {
  if (!quizData) return;
  const topic = quizData.topic || 'Assessment';
  const questions = quizData.questions || [];
  if (!questions.length) return;

  state.currentQuiz = { topic, questions };
  state.userQuizAnswers = {};

  if (quizTopicDisplay) quizTopicDisplay.textContent = `Topic: ${topic}`;
  if (quizProgressDisplay) quizProgressDisplay.textContent = `${questions.length} Questions`;
  renderQuizQuestions(questions);
  if (quizLoading) quizLoading.style.display = 'none';
  if (quizRunner) quizRunner.style.display = 'block';
  if (quizResultsCard) quizResultsCard.style.display = 'none';
  if (exportQuizBtn) exportQuizBtn.style.display = 'inline-block';
}

function renderStudyPlan(planData) {
  if (!planData) return;
  const topic = planData.topic || 'Revision Schedule';
  const planItems = planData.plan || [];
  const days = planData.days || planItems.length || 3;
  state.currentPlan = { topic, days, items: planItems };
  if (planStatusMsg) planStatusMsg.style.display = 'none';

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
  if (planContainer) planContainer.innerHTML = html;
  if (exportPlanBtn) exportPlanBtn.style.display = 'inline-block';

  document.querySelectorAll('.plan-check').forEach((chk) => {
    chk.addEventListener('change', async () => {
      if (chk.checked) {
        playNotificationChime('success');
        const curr = Number(statTopics.textContent || 0);
        await postJson('/api/progress', { completed_topics: curr + 1 });
        loadProgress();
      }
    });
  });
}

// --- Tab 1: AI Tutor (Chat with Master Agent Trace) ---
function appendChatMessage(sender, text, isMarkdown = true, sources = [], retrievedChunks = [], ragMode = 'hybrid', agentTrace = null, actionButtons = null) {
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

  // Render Transparent Master Agent Execution Trace Card
  if (isBot && agentTrace && agentTrace.actions && agentTrace.actions.length > 0) {
    const traceBox = document.createElement('div');
    traceBox.className = 'agent-trace-card';
    traceBox.innerHTML = `
      <div class="agent-trace-header">
        <span class="agent-trace-title">🤖 AI Agent Activity & Execution Plan</span>
        <span class="agent-trace-badge">Master Agent • ${escapeHtml(agentTrace.intent || 'Active')}</span>
      </div>
      <div class="agent-trace-steps">
        ${agentTrace.actions.map(act => `
          <div class="agent-step-item">
            <span class="step-check">✓</span>
            <span class="step-text">${escapeHtml(act.label || act.action)}</span>
          </div>
        `).join('')}
      </div>
    `;
    body.appendChild(traceBox);
  }

  const content = document.createElement('div');
  content.className = 'msg-content';
  if (isBot && isMarkdown) {
    content.innerHTML = formatMarkdown(text);
  } else {
    content.textContent = text;
  }

  body.appendChild(header);
  body.appendChild(content);

  // Render Interactive RAG Citations Drawer
  if (isBot && retrievedChunks && retrievedChunks.length > 0) {
    const citationBox = document.createElement('div');
    citationBox.className = 'rag-citation-box';

    const citationHeader = document.createElement('div');
    citationHeader.className = 'rag-citation-header';
    citationHeader.innerHTML = `
      <span class="rag-badge ${ragMode === 'strict' ? 'strict' : 'hybrid'}">
        ${ragMode === 'strict' ? '🛡️ Strict RAG' : '⚡ Grounded RAG'}
      </span>
      <span class="rag-sources-label">📚 Grounded in ${retrievedChunks.length} course passage${retrievedChunks.length > 1 ? 's' : ''}</span>
    `;
    citationBox.appendChild(citationHeader);

    const pillsList = document.createElement('div');
    pillsList.className = 'rag-citation-pills';

    retrievedChunks.forEach((chunk) => {
      const item = document.createElement('div');
      item.className = 'citation-pill-item';

      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'citation-pill-btn';
      btn.innerHTML = `
        <span class="citation-doc-name">📄 ${escapeHtml(chunk.source)}</span>
        <span class="citation-match-tag">${chunk.relevance_percent || 85}% match ▾</span>
      `;

      const drawer = document.createElement('div');
      drawer.className = 'citation-snippet-drawer';
      drawer.textContent = chunk.snippet || chunk.full_text || 'Course content indexed.';

      btn.addEventListener('click', () => {
        drawer.classList.toggle('open');
        const tag = btn.querySelector('.citation-match-tag');
        if (tag) {
          tag.textContent = drawer.classList.contains('open')
            ? `${chunk.relevance_percent || 85}% match ▴`
            : `${chunk.relevance_percent || 85}% match ▾`;
        }
      });

      item.appendChild(btn);
      item.appendChild(drawer);
      pillsList.appendChild(item);
    });

    citationBox.appendChild(pillsList);
    body.appendChild(citationBox);
  }

  // Render Quick Interactive Action Buttons (e.g. Launch Quiz, Open Study Plan)
  if (isBot && actionButtons && actionButtons.length > 0) {
    const btnRow = document.createElement('div');
    btnRow.style.display = 'flex';
    btnRow.style.gap = '0.6rem';
    btnRow.style.marginTop = '0.85rem';
    btnRow.style.flexWrap = 'wrap';

    actionButtons.forEach(btnConfig => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = btnConfig.className || 'action-btn small-btn';
      b.textContent = btnConfig.label;
      b.addEventListener('click', btnConfig.onClick);
      btnRow.appendChild(b);
    });
    body.appendChild(btnRow);
  }

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

    appendChatMessage('user', question, false);
    questionInput.value = '';

    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'chat-message bot-message typing-indicator';
    typingIndicator.innerHTML = `
      <div class="msg-avatar">✦</div>
      <div class="msg-body"><div class="msg-content"><em>Master Agent: Detecting intent & orchestrating RAG, Memory, and Tools...</em></div></div>
    `;
    chatViewport.appendChild(typingIndicator);
    chatViewport.scrollTop = chatViewport.scrollHeight;

    sendBtn.disabled = true;

    try {
      // Call Master Agent endpoint
      const data = await postJson('/api/agent/chat', {
        query: question,
        subject: subject,
        mode: mode,
        engine: state.selectedEngine,
        rag_mode: state.selectedRagMode,
      });

      typingIndicator.remove();

      const agentTrace = (data.actions_taken && data.actions_taken.length > 0)
        ? { intent: data.intent, actions: data.actions_taken }
        : null;

      const actionButtons = [];
      if (data.quiz && data.quiz.questions && data.quiz.questions.length > 0) {
        actionButtons.push({
          label: `🚀 Launch ${data.quiz.topic || 'Deadlocks'} Quiz in Quiz Center`,
          className: 'action-btn small-btn glow-btn',
          onClick: () => {
            switchTab('tab-quiz');
            renderActiveQuiz(data.quiz);
          }
        });
      }
      if (data.study_plan) {
        actionButtons.push({
          label: '📅 View Plan in Study Planner',
          className: 'secondary-btn small-btn',
          onClick: () => {
            switchTab('tab-planner');
            renderStudyPlan(data.study_plan);
          }
        });
      }

      appendChatMessage(
        'bot',
        data.response || data.answer || 'Response generated.',
        true,
        data.sources || [],
        data.retrieved_chunks || [],
        data.rag_mode || state.selectedRagMode,
        agentTrace,
        actionButtons
      );

      loadMemory();
      loadDashboard();
      loadProgress();
    } catch (error) {
      typingIndicator.remove();
      appendChatMessage('bot', `⚠️ **Error**: ${error.message}\nPlease check your connection or switch the AI engine.`);
    } finally {
      sendBtn.disabled = false;
      questionInput.focus();
    }
  });

  questionInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      questionForm.dispatchEvent(new Event('submit'));
    }
  });
}

document.querySelectorAll('.chip').forEach((chip) => {
  chip.addEventListener('click', () => {
    if (questionInput) {
      questionInput.value = chip.dataset.prompt;
      questionInput.focus();
    }
  });
});

if (clearChatBtn) {
  clearChatBtn.addEventListener('click', async () => {
    try {
      await fetch('/api/memory', { method: 'DELETE' });
    } catch (e) {}
    chatViewport.innerHTML = `
      <div class="chat-message bot-message">
        <div class="msg-avatar">✦</div>
        <div class="msg-body">
          <div class="msg-header">
            <strong>StudyBuddy AI</strong>
            <span class="msg-time">Just now</span>
          </div>
          <div class="msg-content">
            Chat & conversation memory cleared. What topic or concept would you like to explore next?
          </div>
        </div>
      </div>
    `;
    loadMemory();
  });
}

// --- Tab: Agent Architect ---
if (architectForm) {
  architectForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const goal = architectGoalInput.value.trim();
    const days = Number(architectDaysInput.value || 5);

    if (!goal) return;

    architectStatus.style.display = 'block';
    architectStatus.className = 'status-msg info-msg';
    architectStatus.textContent = `Autonomous Agent initializing for goal: "${goal}"...`;
    architectTraceBox.style.display = 'block';
    architectResultsBox.style.display = 'none';

    // Show dynamic simulated steps while backend executes
    architectStepsList.innerHTML = `
      <div class="trace-step-item">
        <span class="trace-step-num">Step 1:</span>
        <div><span class="trace-step-phase">Scanning RAG Knowledge Base...</span> Checking uploaded documents and syllabus.</div>
      </div>
    `;

    try {
      const data = await postJson('/api/agent/architect', {
        goal,
        days,
        engine: state.selectedEngine,
      });

      state.architectData = data;
      playNotificationChime('success');

      architectStatus.style.display = 'none';

      // Render Completed Execution Trace
      if (data.reasoning_trace) {
        architectStepsList.innerHTML = data.reasoning_trace
          .map(
            (st) => `
          <div class="trace-step-item">
            <span class="trace-step-num">Step ${st.step}:</span>
            <div><span class="trace-step-phase">${escapeHtml(st.phase)}</span> — ${escapeHtml(st.detail)}</div>
          </div>
        `,
          )
          .join('');
      }

      // Render Curriculum
      if (archCurriculumList && Array.isArray(data.curriculum)) {
        archCurriculumList.innerHTML = data.curriculum
          .map(
            (item, idx) => `
          <div class="plan-card">
            <div class="plan-day-badge">Day ${idx + 1}</div>
            <div class="plan-details"><span class="plan-text">${escapeHtml(item)}</span></div>
          </div>
        `,
          )
          .join('');
      }

      // Render Diagnostic Quiz
      const quizItems = data.diagnostic_quiz || [];
      if (archQuizCount) archQuizCount.textContent = quizItems.length;
      if (archQuizList) {
        archQuizList.innerHTML = quizItems
          .map(
            (q, idx) => `
          <div class="quiz-question-card">
            <div class="quiz-question-header"><span class="quiz-num">Q${idx + 1}</span> <span>${escapeHtml(q.question)}</span></div>
            <div style="margin-top: 8px; color: var(--text-secondary); font-size: 0.85rem;"><strong>Answer:</strong> ${escapeHtml(q.answer)}</div>
          </div>
        `,
          )
          .join('');
      }

      // Render Flashcards
      const cardItems = data.flashcards || [];
      if (archCardsCount) archCardsCount.textContent = cardItems.length;
      if (archCardsList) {
        archCardsList.innerHTML = cardItems
          .map(
            (c) => `
          <div class="mini-card-item">
            <div class="card-q">Q: ${escapeHtml(c.front || c.question)}</div>
            <div class="card-a">A: ${escapeHtml(c.back || c.answer)}</div>
          </div>
        `,
          )
          .join('');
      }

      architectResultsBox.style.display = 'block';
      loadProgress();
    } catch (err) {
      architectStatus.className = 'status-msg error-msg';
      architectStatus.textContent = `Agent pipeline error: ${err.message}`;
    }
  });
}

// Subtab buttons inside Architect results
document.querySelectorAll('.results-subtabs .subtab-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.results-subtabs .subtab-btn').forEach((b) => b.classList.remove('active'));
    document.querySelectorAll('.architect-results .subtab-view').forEach((v) => v.classList.remove('active'));
    btn.classList.add('active');
    const target = document.getElementById(btn.dataset.sub);
    if (target) target.classList.add('active');
  });
});

if (sendToQuizTabBtn) {
  sendToQuizTabBtn.addEventListener('click', () => {
    if (!state.architectData || !state.architectData.diagnostic_quiz) return;
    state.currentQuiz = {
      topic: state.architectData.topic,
      questions: state.architectData.diagnostic_quiz,
    };
    state.userQuizAnswers = {};
    if (quizTopicDisplay) quizTopicDisplay.textContent = `Topic: ${state.architectData.topic}`;
    if (quizProgressDisplay) quizProgressDisplay.textContent = `${state.currentQuiz.questions.length} Questions`;
    renderQuizQuestions(state.currentQuiz.questions);
    quizRunner.style.display = 'block';
    quizResultsCard.style.display = 'none';
    switchTab('tab-quiz');
  });
}

if (sendToCardsTabBtn) {
  sendToCardsTabBtn.addEventListener('click', () => {
    if (!state.architectData || !state.architectData.flashcards) return;
    state.flashcards = state.architectData.flashcards;
    state.currentCardIndex = 0;
    state.cardFlipped = false;
    state.cardMastery = {};
    renderCurrentFlashcard();
    switchTab('tab-flashcards');
  });
}

// --- Tab: Concept Mind Map ---
if (conceptmapForm) {
  conceptmapForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const topic = conceptmapTopic.value.trim();
    if (!topic) return;

    conceptmapStatus.style.display = 'block';
    conceptmapStatus.className = 'status-msg info-msg';
    conceptmapStatus.textContent = `Synthesizing conceptual knowledge graph for "${topic}"...`;
    conceptmapCanvas.style.display = 'none';
    conceptmapMermaidBox.style.display = 'none';

    try {
      const data = await postJson('/api/concept-map', { topic, engine: state.selectedEngine });
      state.currentConceptMap = data;

      conceptmapStatus.style.display = 'none';
      conceptRoot.textContent = `✦ ${data.root?.label || topic}`;

      conceptBranches.innerHTML = (data.branches || [])
        .map(
          (b) => `
        <div class="concept-branch-card">
          <h4>${escapeHtml(b.name)}</h4>
          <p>${escapeHtml(b.desc)}</p>
          <div class="leaf-pill-container">
            ${(b.leaves || [])
              .map(
                (l) => `
              <div class="concept-leaf-pill">
                <strong>${escapeHtml(l.name)}:</strong> ${escapeHtml(l.desc)}
              </div>
            `,
              )
              .join('')}
          </div>
        </div>
      `,
        )
        .join('');

      conceptmapCanvas.style.display = 'flex';

      if (conceptmapMermaidCode && data.mermaid) {
        conceptmapMermaidCode.textContent = data.mermaid;
        conceptmapMermaidBox.style.display = 'block';
        if (copyMermaidBtn) copyMermaidBtn.style.display = 'inline-block';
      }
    } catch (err) {
      conceptmapStatus.className = 'status-msg error-msg';
      conceptmapStatus.textContent = `Mind map error: ${err.message}`;
    }
  });
}

if (copyMermaidBtn) {
  copyMermaidBtn.addEventListener('click', () => {
    if (conceptmapMermaidCode) {
      navigator.clipboard.writeText(conceptmapMermaidCode.textContent);
      copyMermaidBtn.textContent = '✓ Copied Mermaid Code!';
      setTimeout(() => (copyMermaidBtn.innerHTML = '📋 Copy Mermaid Syntax'), 2000);
    }
  });
}

// --- Tab: Code Explainer ---
if (codeForm) {
  codeForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const code = codeInput.value.trim();
    const language = codeLangSelect.value;
    const analysis_type = codeModeSelect.value;

    if (!code) return;

    codeLoading.style.display = 'block';
    codeLoading.className = 'status-msg info-msg';
    codeLoading.textContent = `Analyzing ${language} code complexity and structure...`;
    codeResults.style.display = 'none';

    try {
      const data = await postJson('/api/code-explain', {
        code,
        language,
        analysis_type,
        engine: state.selectedEngine,
      });

      codeLoading.style.display = 'none';

      if (metricTimeComp) metricTimeComp.textContent = data.complexity?.time || 'O(n)';
      if (metricSpaceComp) metricSpaceComp.textContent = data.complexity?.space || 'O(1)';
      if (codeSummaryText) codeSummaryText.innerHTML = formatMarkdown(data.summary);

      if (codeLinesTable && Array.isArray(data.breakdown)) {
        codeLinesTable.innerHTML = data.breakdown
          .map(
            (row) => `
          <div class="code-line-row">
            <span class="line-num-cell">L${row.line_number}</span>
            <span class="line-code-cell">${escapeHtml(row.code)}</span>
            <span class="line-expl-cell">${escapeHtml(row.explanation)}</span>
          </div>
        `,
          )
          .join('');
      }

      if (codeSuggestionsList && Array.isArray(data.suggestions)) {
        codeSuggestionsList.innerHTML = data.suggestions
          .map((s) => `<li>${escapeHtml(s)}</li>`)
          .join('');
      }

      codeResults.style.display = 'block';
    } catch (err) {
      codeLoading.className = 'status-msg error-msg';
      codeLoading.textContent = `Analysis error: ${err.message}`;
    }
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

      document.querySelectorAll('.plan-check').forEach((chk) => {
        chk.addEventListener('change', async () => {
          if (chk.checked) {
            playNotificationChime('success');
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
    const isCorrect = item.correct || item.is_correct;
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
          <div class="correct-ans">Expected Answer: <span class="ans-value">${escapeHtml(item.correct_answer || item.expected_answer)}</span></div>
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

window.addEventListener('keydown', (e) => {
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
      pauseTimer();
      playNotificationChime('success');

      if (state.pomodoro.mode === 'focus') {
        state.pomodoro.completedSessions++;
        localStorage.setItem('studybuddy-pomodoro-count', state.pomodoro.completedSessions);

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
        } catch (e) {}
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

updateTimerDisplay();

// --- Tab 6: Course Materials Library & Document Viewer Modal ---
async function loadMaterials() {
  try {
    const response = await fetch('/api/materials');
    const data = await response.json();
    const list = data.materials || [];

    if (materialsCount) materialsCount.textContent = list.length;
    if (materialsResult) {
      materialsResult.innerHTML = list.length
        ? list
            .map(
              (name) => `
          <li class="material-list-item" style="padding: 0.75rem; border-bottom: 1px solid var(--border);">
            <div style="display:flex; justify-content:space-between; align-items:center; width:100%; gap: 0.5rem; flex-wrap: wrap;">
              <span><span class="file-icon">📄</span> <strong class="file-name">${escapeHtml(name)}</strong></span>
              <div style="display: flex; gap: 0.4rem; align-items: center;">
                <span class="badge-status-tag badge-unlocked-tag" style="font-size:0.75rem; padding: 0.2rem 0.5rem;">Ready ✓</span>
                <button type="button" class="icon-link-btn view-doc-btn" data-doc="${escapeHtml(name)}">👁 View</button>
                <button type="button" class="icon-link-btn delete-doc-btn" data-doc="${escapeHtml(name)}" style="color:var(--danger, #ef4444);">🗑 Delete</button>
              </div>
            </div>
          </li>
        `,
            )
            .join('')
        : '<li class="empty-list">No course documents ingested yet. Drop your first notes above!</li>';

      // Attach click listeners to view doc buttons
      document.querySelectorAll('.view-doc-btn').forEach((btn) => {
        btn.addEventListener('click', async () => {
          const docName = btn.dataset.doc;
          openDocumentModal(docName);
        });
      });

      // Attach click listeners to delete doc buttons
      document.querySelectorAll('.delete-doc-btn').forEach((btn) => {
        btn.addEventListener('click', async () => {
          const docName = btn.dataset.doc;
          if (!window.confirm(`Are you sure you want to delete "${docName}" from course materials and update RAG index?`)) return;
          try {
            const res = await fetch(`/api/materials/${encodeURIComponent(docName)}`, { method: 'DELETE' });
            const d = await res.json();
            if (!res.ok) throw new Error(d.error || 'Failed to delete');
            await loadMaterials();
            await loadDashboard();
          } catch (err) {
            alert(`Could not delete document: ${err.message}`);
          }
        });
      });
    }
  } catch (e) {}
}

async function openDocumentModal(docName) {
  if (!docModal) return;
  state.activeDoc = docName;
  docModalTitle.textContent = docName;
  docModalContent.textContent = 'Fetching document content...';
  docModal.style.display = 'flex';

  try {
    const res = await fetch(`/api/materials/${encodeURIComponent(docName)}/content`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Failed to read document');
    docModalContent.textContent = data.content || '(Empty document)';
  } catch (err) {
    docModalContent.textContent = `Error loading document: ${err.message}`;
  }
}

if (closeDocModalBtn) {
  closeDocModalBtn.addEventListener('click', () => {
    if (docModal) docModal.style.display = 'none';
  });
}

// Quick Actions inside Document Modal
if (docQuickSummarize) {
  docQuickSummarize.addEventListener('click', () => {
    if (!state.activeDoc) return;
    docModal.style.display = 'none';
    summaryTopicInput.value = state.activeDoc.replace(/\.(md|txt|pdf|docx|pptx)$/i, '');
    switchTab('tab-library');
    summaryForm.dispatchEvent(new Event('submit'));
  });
}

if (docQuickCards) {
  docQuickCards.addEventListener('click', () => {
    if (!state.activeDoc) return;
    docModal.style.display = 'none';
    flashcardTopicInput.value = state.activeDoc.replace(/\.(md|txt|pdf|docx|pptx)$/i, '');
    switchTab('tab-flashcards');
    flashcardForm.dispatchEvent(new Event('submit'));
  });
}

if (docQuickQuiz) {
  docQuickQuiz.addEventListener('click', () => {
    if (!state.activeDoc) return;
    docModal.style.display = 'none';
    quizTopicInput.value = state.activeDoc.replace(/\.(md|txt|pdf|docx|pptx)$/i, '');
    switchTab('tab-quiz');
    quizForm.dispatchEvent(new Event('submit'));
  });
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

    // Animated upload phases
    uploadResult.textContent = `⏳ 1/4 Uploading "${file.name}" to server...`;
    const t1 = setTimeout(() => {
      uploadResult.textContent = `⚙️ 2/4 Processing text extraction & cleaning...`;
    }, 450);
    const t2 = setTimeout(() => {
      uploadResult.textContent = `✂️ 3/4 Chunking text into semantically aware passages...`;
    }, 950);
    const t3 = setTimeout(() => {
      uploadResult.textContent = `🧠 4/4 Computing dense embeddings & updating FAISS vector index...`;
    }, 1450);

    try {
      const response = await fetch('/api/upload', { method: 'POST', body: formData });
      clearTimeout(t1); clearTimeout(t2); clearTimeout(t3);
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Upload failed');

      uploadResult.className = 'status-msg success-msg';
      uploadResult.textContent = `✓ Ready! "${data.filename || file.name}" ingested into RAG vector index.`;
      materialFileInput.value = '';
      await loadMaterials();
      await loadDashboard();
    } catch (err) {
      clearTimeout(t1); clearTimeout(t2); clearTimeout(t3);
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
      const termsList = data.key_terms || data.key_concepts || [];
      if (Array.isArray(termsList) && termsList.length > 0) {
        keyTermsHtml = `
          <div class="summary-terms-card">
            <h4>🔑 Key Academic Concepts & Glossary</h4>
            <ul class="key-terms-list">
              ${termsList
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
    const { topic, summary, key_terms, key_concepts } = state.currentSummary;
    let content = `# Document Summary: ${topic || 'Course Notes'}\n\nGenerated by StudyBuddy AI\n\n${summary}\n\n`;

    const terms = key_terms || key_concepts || [];
    if (terms && terms.length) {
      content += `## Key Concepts & Glossary\n\n`;
      terms.forEach((t) => {
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

// --- Learning Memory Tab ---
async function loadMemory() {
  try {
    const response = await fetch('/api/memory');
    const data = await response.json();

    const memProfile = data.profile || {};
    const nameEl = document.getElementById('mem-val-name');
    if (nameEl && memProfile.name) nameEl.textContent = memProfile.name;

    const styleEl = document.getElementById('mem-style-display');
    if (styleEl && memProfile.preferred_style) {
      styleEl.textContent = `"${memProfile.preferred_style}"`;
    }

    if (memoryResult) {
      if (data.recent_turns && data.recent_turns.length > 0) {
        memoryResult.textContent = data.recent_turns.map((t, idx) =>
          `[Session Turn ${idx + 1}]\nStudent: ${t.user}\nStudyBuddy: ${t.assistant}\n`
        ).join('\n---\n');
      } else {
        memoryResult.textContent = data.summary || 'No conversation history recorded yet. Start interacting with the AI Tutor to build persistent context!';
      }
    }
  } catch (e) {}
}

if (memoryButton) memoryButton.addEventListener('click', loadMemory);

async function handleClearMemory() {
  if (!window.confirm('Clear all conversation history from agent memory?')) return;
  try {
    const response = await fetch('/api/memory', { method: 'DELETE' });
    const data = await response.json();
    if (memoryResult) memoryResult.textContent = data.message || 'Memory cleared.';
    await loadMemory();
    await loadDashboard();
  } catch (err) {
    alert(`Could not clear memory: ${err.message}`);
  }
}

if (clearMemoryButton) clearMemoryButton.addEventListener('click', handleClearMemory);

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

// --- Close Modals on Backdrop Click ---
window.addEventListener('click', (e) => {
  if (e.target === docModal) docModal.style.display = 'none';
  if (e.target === badgesModal) badgesModal.style.display = 'none';
});

// --- Initialization ---
loadDashboard();
loadAiStatus();
loadProgress();
loadMaterials();
loadMemory();

// Service worker
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/static/service-worker.js').catch(() => {});
}
