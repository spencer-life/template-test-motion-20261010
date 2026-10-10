import "@fontsource-variable/inter/index.css";
import "./style.css";
import { formatClock, progressPercent, remainingSeconds } from "./timer";

type Session = {
  id: string;
  title: string;
  durationMinutes: number;
  remainingSeconds: number;
  completed: boolean;
};

const sessions: Session[] = [
  {
    id: "session-1",
    title: "Shape the next idea",
    durationMinutes: 25,
    remainingSeconds: 25 * 60,
    completed: false,
  },
  {
    id: "session-2",
    title: "Sort the working notes",
    durationMinutes: 15,
    remainingSeconds: 15 * 60,
    completed: false,
  },
  {
    id: "session-3",
    title: "Read with intention",
    durationMinutes: 45,
    remainingSeconds: 45 * 60,
    completed: false,
  },
];

const app = document.querySelector<HTMLDivElement>("#app");
if (!app) throw new Error("Tempo Board needs an #app element.");
const appRoot = app;

app.innerHTML = `
  <div class="app-shell">
    <header class="site-header">
      <a class="brand" href="/" aria-label="Tempo Board home">
        <span class="brand-mark" aria-hidden="true"><span></span><span></span><span></span></span>
        <span>tempo <span class="brand-light">board</span></span>
      </a>
      <p class="header-note">A little structure for your next stretch of focus.</p>
    </header>

    <main class="workspace" id="workspace">
      <section class="focus-section" aria-labelledby="page-title">
        <header class="page-intro">
          <p class="date-line" id="today-label"></p>
          <h1 id="page-title">Make room for focus.</h1>
          <p>Choose a session, then settle into one thing at a time.</p>
        </header>

        <article class="timer-card" aria-labelledby="session-title">
          <div class="timer-topline">
            <p id="timer-status" class="timer-status" role="status">Ready to begin</p>
            <p id="timer-length" class="timer-length">25 minute session</p>
          </div>
          <div class="timer-copy">
            <h2 id="session-title">Shape the next idea</h2>
            <p id="timer-hint">Take a breath. Then begin.</p>
          </div>
          <time
            class="timer-display"
            id="timer-display"
            role="timer"
            aria-live="off"
            datetime="PT1500S"
            aria-label="25 minutes remaining"
          >25:00</time>
          <div
            class="progress-track"
            id="progress-track"
            role="progressbar"
            aria-label="Session progress"
            aria-valuemin="0"
            aria-valuemax="100"
            aria-valuenow="0"
            aria-valuetext="0% complete"
          >
            <span class="progress-fill" id="progress-fill" aria-hidden="true"></span>
          </div>
          <div class="timer-footer">
            <p class="timer-footnote">One thing at a time.</p>
            <div class="timer-actions">
              <button class="button-primary" id="start-button" type="button">Start session</button>
              <button class="button-quiet" id="reset-button" type="button" disabled>Reset</button>
            </div>
          </div>
        </article>

        <p class="privacy-note"><span aria-hidden="true"></span> No account or sync; your plan stays in this tab.</p>
      </section>

      <aside class="plan-panel" aria-labelledby="plan-title">
        <header class="plan-heading">
          <div>
            <h2 id="plan-title">Your sessions</h2>
            <p>Keep the next step small.</p>
          </div>
          <span class="queue-count" id="queue-count">3 sessions left</span>
        </header>

        <ol class="session-list" id="session-list" aria-label="Focus session queue"></ol>
        <div class="empty-queue" id="empty-queue" hidden>
          <p class="empty-title">Nothing on the plan yet.</p>
          <p>Add one small session to get started.</p>
        </div>

        <form class="session-form" id="session-form" action="/" method="get">
          <h3>Add to your plan</h3>
          <div class="field-group">
            <label for="session-name">Session name</label>
            <input
              id="session-name"
              name="session-name"
              type="text"
              required
              minlength="1"
              maxlength="48"
              autocomplete="off"
              aria-describedby="session-name-help session-name-error"
              aria-errormessage="session-name-error"
              placeholder="What will you focus on?"
            />
            <p class="field-help" id="session-name-help">A few words is plenty.</p>
            <p class="field-error" id="session-name-error" hidden></p>
          </div>
          <fieldset class="duration-fieldset">
            <legend>Choose a length</legend>
            <div class="duration-options">
              <label class="duration-choice">
                <input type="radio" name="duration" value="15" required />
                <span>15 <small>min</small></span>
              </label>
              <label class="duration-choice">
                <input type="radio" name="duration" value="25" checked required />
                <span>25 <small>min</small></span>
              </label>
              <label class="duration-choice">
                <input type="radio" name="duration" value="45" required />
                <span>45 <small>min</small></span>
              </label>
            </div>
          </fieldset>
          <button class="button-add" type="submit">Add session</button>
        </form>

      </aside>
    </main>
    <p class="sr-only" id="live-announcement" role="status" aria-live="polite"></p>
  </div>
`;

function element<T extends Element>(selector: string): T {
  const result = appRoot.querySelector<T>(selector);
  if (!result) throw new Error(`Missing Tempo Board element: ${selector}`);
  return result;
}

const sessionList = element<HTMLOListElement>("#session-list");
const emptyQueue = element<HTMLDivElement>("#empty-queue");
const queueCount = element<HTMLSpanElement>("#queue-count");
const timerStatus = element<HTMLParagraphElement>("#timer-status");
const timerLength = element<HTMLParagraphElement>("#timer-length");
const timerTitle = element<HTMLHeadingElement>("#session-title");
const timerHint = element<HTMLParagraphElement>("#timer-hint");
const timerDisplay = element<HTMLTimeElement>("#timer-display");
const progressTrack = element<HTMLDivElement>("#progress-track");
const progressFill = element<HTMLSpanElement>("#progress-fill");
const startButton = element<HTMLButtonElement>("#start-button");
const resetButton = element<HTMLButtonElement>("#reset-button");
const sessionForm = element<HTMLFormElement>("#session-form");
const sessionName = element<HTMLInputElement>("#session-name");
const sessionNameError = element<HTMLParagraphElement>("#session-name-error");
const liveAnnouncement = element<HTMLParagraphElement>("#live-announcement");
const todayLabel = element<HTMLParagraphElement>("#today-label");

let selectedId: string | null = sessions[0]?.id ?? null;
let isRunning = false;
let timerEndAt: number | null = null;
let timerInterval: number | undefined;
let sessionSequence = sessions.length;
let titleAnimation: Animation | undefined;

todayLabel.textContent = new Intl.DateTimeFormat(undefined, {
  weekday: "long",
  month: "long",
  day: "numeric",
}).format(new Date());

function selectedSession(): Session | undefined {
  return sessions.find((session) => session.id === selectedId);
}

function escapeHtml(value: string): string {
  return value.replace(/[&<>"']/g, (character) => {
    const entities: Record<string, string> = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    };
    return entities[character] ?? character;
  });
}

function queueState(session: Session): string {
  if (session.completed) return "Complete";
  if (session.id === selectedId && isRunning) return "In focus";
  if (session.id === selectedId && session.remainingSeconds < session.durationMinutes * 60) {
    return "Paused";
  }
  return "Up next";
}

function renderQueue(): void {
  const unfinished = sessions.filter((session) => !session.completed).length;
  queueCount.textContent =
    unfinished === 0
      ? "All done"
      : `${unfinished} ${unfinished === 1 ? "session" : "sessions"} left`;
  emptyQueue.hidden = sessions.length !== 0;
  sessionList.hidden = sessions.length === 0;

  sessionList.innerHTML = sessions
    .map((session) => {
      const selected = session.id === selectedId;
      const safeTitle = escapeHtml(session.title);
      const state = queueState(session);
      return `
        <li class="session-item${selected ? " is-selected" : ""}${session.completed ? " is-complete" : ""}">
          <button
            class="session-select"
            type="button"
            data-session-id="${session.id}"
            aria-pressed="${selected}"
            aria-label="Select ${safeTitle}, ${session.durationMinutes} minutes"
          >
            <span class="session-marker" aria-hidden="true"></span>
            <span class="session-details">
              <span class="session-name">${safeTitle}</span>
              <span class="session-meta">${session.durationMinutes} min <span aria-hidden="true">·</span> ${state}</span>
            </span>
          </button>
          <button
            class="remove-session"
            type="button"
            data-remove-id="${session.id}"
            aria-label="Remove ${safeTitle}"
          >Remove</button>
        </li>
      `;
    })
    .join("");
}

function animateSessionTitle(): void {
  titleAnimation?.cancel();
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  titleAnimation = timerTitle.animate(
    reduceMotion
      ? [{ opacity: 0.78 }, { opacity: 1 }]
      : [
          { opacity: 0.78, transform: "translateY(3px)" },
          { opacity: 1, transform: "translateY(0)" },
        ],
    {
      duration: reduceMotion ? 140 : 180,
      easing: "cubic-bezier(0.23, 1, 0.32, 1)",
    },
  );
}

function renderTimer(): void {
  const session = selectedSession();
  startButton.disabled = !session;

  if (!session) {
    timerStatus.textContent = "No session selected";
    timerLength.textContent = "Add a session to begin";
    timerTitle.textContent = "Your next session will land here.";
    timerHint.textContent = "Add one small step to get started.";
    timerDisplay.textContent = "00:00";
    timerDisplay.dateTime = "PT0S";
    timerDisplay.setAttribute("aria-label", "No session selected");
    progressTrack.setAttribute("aria-valuenow", "0");
    progressTrack.setAttribute("aria-valuetext", "No session selected");
    progressFill.style.transform = "scaleX(0)";
    startButton.textContent = "Start session";
    resetButton.disabled = true;
    return;
  }

  const durationSeconds = session.durationMinutes * 60;
  const percentage = progressPercent(durationSeconds, session.remainingSeconds);
  const minutesLeft = Math.ceil(session.remainingSeconds / 60);
  const status = isRunning
    ? "In focus"
    : session.completed
      ? "Session complete"
      : session.remainingSeconds < durationSeconds
        ? "Paused"
        : "Ready to begin";
  if (timerStatus.textContent !== status) timerStatus.textContent = status;
  timerLength.textContent = `${session.durationMinutes} minute${session.durationMinutes === 1 ? "" : "s"} session`;
  timerTitle.textContent = session.title;
  timerHint.textContent = isRunning
    ? "Stay with this one small step."
    : session.completed
      ? "You gave this one your time. Well done."
      : session.remainingSeconds < durationSeconds
        ? "Paused. Continue when you’re ready."
        : "Take a breath. Then begin.";
  timerDisplay.textContent = formatClock(session.remainingSeconds);
  timerDisplay.dateTime = `PT${session.remainingSeconds}S`;
  timerDisplay.setAttribute(
    "aria-label",
    `${minutesLeft} ${minutesLeft === 1 ? "minute" : "minutes"} remaining`,
  );
  progressTrack.setAttribute("aria-valuenow", String(Math.round(percentage)));
  progressTrack.setAttribute("aria-valuetext", `${Math.round(percentage)}% complete`);
  progressFill.style.transform = `scaleX(${percentage / 100})`;
  startButton.textContent = isRunning
    ? "Pause session"
    : session.completed
      ? "Start again"
      : session.remainingSeconds < durationSeconds
        ? "Continue session"
        : "Start session";
  resetButton.disabled =
    !isRunning && !session.completed && session.remainingSeconds === durationSeconds;
}

function render(): void {
  renderQueue();
  renderTimer();
}

function stopTicker(): void {
  if (timerInterval !== undefined) window.clearInterval(timerInterval);
  timerInterval = undefined;
}

function pauseTimer(): void {
  const session = selectedSession();
  if (!session || !isRunning || timerEndAt === null) return;

  session.remainingSeconds = remainingSeconds(timerEndAt, Date.now());
  isRunning = false;
  timerEndAt = null;
  stopTicker();
}

function tick(): void {
  const session = selectedSession();
  if (!session || !isRunning || timerEndAt === null) return;

  const next = remainingSeconds(timerEndAt, Date.now());
  if (next !== session.remainingSeconds) {
    session.remainingSeconds = next;
    renderTimer();
  }
  if (next === 0) {
    session.completed = true;
    isRunning = false;
    timerEndAt = null;
    stopTicker();
    liveAnnouncement.textContent = `${session.title} is complete.`;
    render();
  }
}

function startTimer(): void {
  const session = selectedSession();
  if (!session) return;

  if (session.completed) {
    session.completed = false;
    session.remainingSeconds = session.durationMinutes * 60;
  }
  if (session.remainingSeconds <= 0) return;

  isRunning = true;
  timerEndAt = Date.now() + session.remainingSeconds * 1000;
  stopTicker();
  timerInterval = window.setInterval(tick, 250);
  liveAnnouncement.textContent = `Started ${session.title}.`;
  render();
}

function updateInputError(): void {
  const emptyAfterTrim = sessionName.value.trim().length === 0;
  sessionName.setCustomValidity(emptyAfterTrim ? "Enter a short name for this session." : "");
}

sessionName.addEventListener("invalid", () => {
  sessionName.setAttribute("aria-invalid", "true");
  sessionNameError.textContent = sessionName.validationMessage;
  sessionNameError.hidden = false;
});

sessionName.addEventListener("input", () => {
  updateInputError();
  if (sessionName.validity.valid) {
    sessionName.removeAttribute("aria-invalid");
    sessionNameError.hidden = true;
  }
});

sessionForm.addEventListener("submit", (event) => {
  event.preventDefault();
  updateInputError();
  if (!sessionForm.reportValidity()) return;

  const title = sessionName.value.trim();
  const duration = Number(new FormData(sessionForm).get("duration"));
  const session: Session = {
    id: `session-${++sessionSequence}`,
    title,
    durationMinutes: duration,
    remainingSeconds: duration * 60,
    completed: false,
  };
  sessions.push(session);

  if (selectedId === null) {
    selectedId = session.id;
    timerTitle.textContent = session.title;
    animateSessionTitle();
  }

  sessionName.value = "";
  sessionName.removeAttribute("aria-invalid");
  sessionNameError.hidden = true;
  liveAnnouncement.textContent = `Added ${session.title} to your plan.`;
  render();
  sessionName.focus();
});

sessionList.addEventListener("click", (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) return;

  const removeButton = target.closest<HTMLButtonElement>("[data-remove-id]");
  if (removeButton) {
    const index = sessions.findIndex((session) => session.id === removeButton.dataset.removeId);
    if (index < 0) return;
    const isSelected = sessions[index]?.id === selectedId;
    if (isSelected && isRunning) {
      tick();
      pauseTimer();
    }
    const [removed] = sessions.splice(index, 1);
    if (!removed) return;

    if (isSelected) {
      selectedId = sessions[index]?.id ?? sessions[index - 1]?.id ?? null;
      if (selectedId) {
        const next = selectedSession();
        if (next) timerTitle.textContent = next.title;
        animateSessionTitle();
      }
    }
    liveAnnouncement.textContent = `Removed ${removed.title} from your plan.`;
    render();
    return;
  }

  const selectButton = target.closest<HTMLButtonElement>("[data-session-id]");
  const nextId = selectButton?.dataset.sessionId;
  if (!nextId || nextId === selectedId) return;

  tick();
  pauseTimer();
  selectedId = nextId;
  const session = selectedSession();
  if (session) timerTitle.textContent = session.title;
  animateSessionTitle();
  liveAnnouncement.textContent = session ? `Selected ${session.title}.` : "Session selected.";
  render();
});

startButton.addEventListener("click", () => {
  if (isRunning) {
    tick();
    pauseTimer();
    const session = selectedSession();
    if (session) liveAnnouncement.textContent = `Paused ${session.title}.`;
    render();
    return;
  }
  startTimer();
});

resetButton.addEventListener("click", () => {
  const session = selectedSession();
  if (!session) return;
  stopTicker();
  isRunning = false;
  timerEndAt = null;
  session.completed = false;
  session.remainingSeconds = session.durationMinutes * 60;
  liveAnnouncement.textContent = `Reset ${session.title}.`;
  render();
});

render();
