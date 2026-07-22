const form = document.querySelector("#plan-form");
const nameInput = document.querySelector("#employee-name");
const emailInput = document.querySelector("#employee-email");
const profileSelect = document.querySelector("#profile-id");
const projectSelect = document.querySelector("#project-id");
const generateButton = document.querySelector("#generate-button");
const buttonLabel = document.querySelector("#button-label");
const statusMessage = document.querySelector("#status-message");
const markdownOutput = document.querySelector("#markdown-output");
const sourcePill = document.querySelector("#source-pill");

const escapeHtml = (value) =>
  value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

const inlineMarkdown = (value) =>
  escapeHtml(value).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

function renderMarkdown(markdown) {
  const lines = markdown.split(/\r?\n/);
  const html = [];
  let inList = false;
  let inCode = false;
  let codeLines = [];

  const closeList = () => {
    if (inList) {
      html.push("</ul>");
      inList = false;
    }
  };

  for (const line of lines) {
    if (line.startsWith("```")) {
      if (inCode) {
        html.push(`<pre><code>${escapeHtml(codeLines.join("\n"))}</code></pre>`);
        codeLines = [];
        inCode = false;
      } else {
        closeList();
        inCode = true;
      }
      continue;
    }

    if (inCode) {
      codeLines.push(line);
      continue;
    }

    if (!line.trim()) {
      closeList();
      continue;
    }

    if (line.startsWith("### ")) {
      closeList();
      html.push(`<h3>${inlineMarkdown(line.slice(4))}</h3>`);
      continue;
    }

    if (line.startsWith("## ")) {
      closeList();
      html.push(`<h2>${inlineMarkdown(line.slice(3))}</h2>`);
      continue;
    }

    if (line.startsWith("# ")) {
      closeList();
      html.push(`<h1>${inlineMarkdown(line.slice(2))}</h1>`);
      continue;
    }

    if (line.startsWith("- ")) {
      if (!inList) {
        html.push("<ul>");
        inList = true;
      }
      html.push(`<li>${inlineMarkdown(line.slice(2))}</li>`);
      continue;
    }

    closeList();
    html.push(`<p>${inlineMarkdown(line)}</p>`);
  }

  closeList();

  if (inCode) {
    html.push(`<pre><code>${escapeHtml(codeLines.join("\n"))}</code></pre>`);
  }

  return html.join("");
}

function setStatus(message, isError = false) {
  statusMessage.textContent = message;
  statusMessage.classList.toggle("error", isError);
}

function setLoading(isLoading) {
  generateButton.disabled = isLoading;
  buttonLabel.textContent = isLoading ? "Generating..." : "Generate plan";
}

function fillSelect(select, items, placeholder) {
  select.innerHTML = "";
  const emptyOption = document.createElement("option");
  emptyOption.value = "";
  emptyOption.textContent = placeholder;
  select.appendChild(emptyOption);

  for (const item of items) {
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = item.name || item.id;
    select.appendChild(option);
  }
}

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(payload.detail || `Request failed with status ${response.status}`);
  }

  return payload;
}

async function loadReferenceData() {
  setStatus("Loading profiles and projects...");
  try {
    const [profilesPayload, projectsPayload] = await Promise.all([
      fetchJson("/profiles"),
      fetchJson("/projects"),
    ]);

    fillSelect(profileSelect, profilesPayload.profiles, "Select a profile");
    fillSelect(projectSelect, projectsPayload.projects, "Select a project");
    setStatus("Ready.");
  } catch (error) {
    fillSelect(profileSelect, [], "Profiles unavailable");
    fillSelect(projectSelect, [], "Projects unavailable");
    setStatus(error.message, true);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  setLoading(true);
  setStatus("Calling the AI agent endpoint...");
  sourcePill.textContent = "Generating";
  sourcePill.classList.remove("ready");

  const request = {
    employee_name: nameInput.value.trim(),
    employee_email: emailInput.value.trim(),
    profile_id: profileSelect.value,
    project_id: projectSelect.value,
  };

  try {
    const payload = await fetchJson("/agent/onboarding-plans", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });

    markdownOutput.classList.remove("empty-state");
    markdownOutput.innerHTML = renderMarkdown(payload.plan_markdown || "");
    sourcePill.textContent = payload.mode === "strands" ? "Strands agent" : "Local";
    sourcePill.classList.add("ready");
    setStatus("Plan generated.");
  } catch (error) {
    setStatus(error.message, true);
    sourcePill.textContent = "Error";
  } finally {
    setLoading(false);
  }
});

loadReferenceData();
