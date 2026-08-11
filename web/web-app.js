const state = { scenarios: [], active: null, attemptId: null, attemptToken: null, step: 1, totalSteps: 1, busy: false };
const $ = (selector) => document.querySelector(selector);
const categoryClasses = {
  Cardiac: "category-cardiac", Respiratory: "category-respiratory",
  Medical: "category-medical", Neurologic: "category-neurologic",
  Toxicology: "category-toxicology", Trauma: "category-trauma",
  Pediatrics: "category-pediatrics", Environmental: "category-environmental",
  Behavioral: "category-behavioral", Obstetrics: "category-obstetrics",
};

async function api(path, options = {}) {
  const response = await fetch(`/api${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || "Request failed.");
  return body;
}

function show(view) {
  ["home-view", "trainer-view", "result-view"].forEach((id) => {
    document.getElementById(id).classList.toggle("hidden", id !== view);
  });
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function scenarioCard(scenario) {
  const score = scenario.attempted
    ? `<strong class="score-badge">${scenario.score}% score</strong>`
    : "<strong>Start call →</strong>";
  return `
    <button class="scenario-card ${categoryClasses[scenario.category] || "category-medical"}" data-start="${scenario.key}">
      <span class="card-category">${scenario.category.toUpperCase()}</span>
      <h3>${escapeHtml(scenario.title)}</h3>
      <p>Independent ${escapeHtml(scenario.category.toLowerCase())} training scenario</p>
      <span class="card-footer"><span>${escapeHtml(scenario.difficulty)}</span>${score}</span>
    </button>`;
}

function renderScenarios(filter = "") {
  const term = filter.trim().toLowerCase();
  const filtered = state.scenarios.filter((s) =>
    `${s.title} ${s.category} ${s.difficulty}`.toLowerCase().includes(term)
  );
  $("#scenario-grid").innerHTML = filtered.length
    ? filtered.map(scenarioCard).join("")
    : '<div class="loading-card">No matching scenarios. Try another search.</div>';
}

async function loadScenarios() {
  try {
    const data = await api("/scenarios/");
    state.scenarios = data.scenarios;
    $("#disclaimer").textContent = data.disclaimer;
    renderScenarios($("#search").value);
  } catch (error) {
    $("#scenario-grid").innerHTML = `<div class="loading-card">Could not load scenarios: ${escapeHtml(error.message)}</div>`;
  }
}

function addMessage(role, text, extra = "") {
  const message = document.createElement("div");
  message.className = `message ${role} ${extra}`;
  message.textContent = text;
  $("#chat").appendChild(message);
  $("#chat").scrollTop = $("#chat").scrollHeight;
}

function updateProgress() {
  $("#step-label").textContent = `Step ${state.step} of ${state.totalSteps}`;
  $("#progress-bar").style.width = `${(state.step / state.totalSteps) * 100}%`;
}

async function startScenario(key) {
  if (state.busy) return;
  const scenario = state.scenarios.find((s) => s.key === key);
  if (!scenario) return;
  state.busy = true;
  try {
    const data = await api(`/scenarios/${key}/start/`, { method: "POST" });
    state.active = scenario;
    state.attemptId = data.attempt_id;
    state.attemptToken = data.attempt_token;
    state.step = data.step;
    state.totalSteps = data.total_steps;
    $("#trainer-title").textContent = scenario.title;
    $("#trainer-protocol").textContent = `${scenario.category} · ${scenario.difficulty}`;
    $("#chat").innerHTML = "";
    $("#completion-toast").classList.add("hidden");
    $("#response-form").classList.remove("composer-disabled");
    $("#response-input").disabled = false;
    $("#send-response").disabled = false;
    addMessage("trainer", `DISPATCH\n${data.dispatch}`, "dispatch");
    addMessage("trainer", data.prompt);
    updateProgress();
    show("trainer-view");
    $("#response-input").focus();
  } catch (error) {
    alert(error.message);
  } finally {
    state.busy = false;
  }
}

async function submitResponse(event) {
  event.preventDefault();
  const input = $("#response-input");
  const answer = input.value.trim();
  if (!answer || state.busy) return;
  state.busy = true;
  input.value = "";
  addMessage("student", answer);
  $("#send-response").disabled = true;
  try {
    const data = await api(`/attempts/${state.attemptId}/respond/`, {
      method: "POST",
      headers: { "X-Attempt-Token": state.attemptToken },
      body: JSON.stringify({ response: answer }),
    });
    addMessage("feedback", data.feedback);
    if (data.completed) {
      state.step = state.totalSteps;
      updateProgress();
      $("#completion-score").textContent = data.overall_score;
      $("#completion-evaluation").textContent = data.evaluation;
      $("#completion-toast").classList.remove("hidden");
      $("#response-form").classList.add("composer-disabled");
      $("#response-input").disabled = true;
      $("#send-response").disabled = true;
      await loadScenarios();
    } else {
      state.step = data.step;
      state.totalSteps = data.total_steps;
      updateProgress();
      addMessage("trainer", data.prompt);
    }
  } catch (error) {
    addMessage("feedback", `Your response was not saved: ${error.message}`);
    input.value = answer;
  } finally {
    state.busy = false;
    if ($("#completion-toast").classList.contains("hidden")) {
      $("#send-response").disabled = false;
      input.focus();
    }
  }
}

function escapeHtml(value) {
  const node = document.createElement("span");
  node.textContent = value;
  return node.innerHTML;
}

document.addEventListener("click", (event) => {
  const start = event.target.closest("[data-start]");
  if (start) startScenario(start.dataset.start);
});
$("#search").addEventListener("input", (event) => renderScenarios(event.target.value));
$("#response-form").addEventListener("submit", submitResponse);
$("#back-home").addEventListener("click", () => show("home-view"));
$("#result-home").addEventListener("click", () => show("home-view"));
$("#retry-call").addEventListener("click", () => startScenario(state.active.key));
$("#completion-retry").addEventListener("click", () => startScenario(state.active.key));
$("#completion-home").addEventListener("click", () => show("home-view"));
$("#dismiss-completion").addEventListener("click", () => {
  $("#completion-toast").classList.add("hidden");
});
loadScenarios();
