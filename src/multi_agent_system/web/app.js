(function () {
  const STORAGE_KEY = "multi-agent-chat.sessions.v1";

  const conversation = document.getElementById("conversation");
  const chatForm = document.getElementById("chatForm");
  const messageInput = document.getElementById("messageInput");
  const sendButton = document.getElementById("sendButton");
  const statusLine = document.getElementById("statusLine");
  const threadLabel = document.getElementById("threadLabel");
  const runStatus = document.getElementById("runStatus");
  const stepList = document.getElementById("stepList");
  const evidenceList = document.getElementById("evidenceList");
  const sessionList = document.getElementById("sessionList");
  const newChatButton = document.getElementById("newChatButton");
  const menuButton = document.getElementById("menuButton");
  const sidebar = document.getElementById("sidebar");

  let sessions = loadSessions();
  let activeSessionId = sessions[0]?.id || createSession().id;
  let isSending = false;

  render();

  chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const text = messageInput.value.trim();
    if (!text || isSending) return;
    await sendMessage(text);
  });

  messageInput.addEventListener("input", () => {
    messageInput.style.height = "auto";
    messageInput.style.height = `${Math.min(messageInput.scrollHeight, 180)}px`;
  });

  messageInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      chatForm.requestSubmit();
    }
  });

  newChatButton.addEventListener("click", () => {
    activeSessionId = createSession().id;
    saveSessions();
    render();
    messageInput.focus();
  });

  menuButton.addEventListener("click", () => {
    sidebar.classList.toggle("open");
  });

  document.querySelectorAll("[data-prompt]").forEach((button) => {
    button.addEventListener("click", () => {
      messageInput.value = button.dataset.prompt || "";
      messageInput.dispatchEvent(new Event("input"));
      messageInput.focus();
      sidebar.classList.remove("open");
    });
  });

  async function sendMessage(text) {
    const session = getActiveSession();
    const userMessage = createMessage("user", text);
    session.messages.push(userMessage);
    session.title = session.title || makeTitle(text);
    session.updatedAt = Date.now();
    session.lastResult = null;
    saveSessions();
    render();

    const loadingId = `loading-${Date.now()}`;
    session.messages.push({
      id: loadingId,
      role: "assistant",
      content: "",
      createdAt: Date.now(),
      loading: true,
    });
    setSending(true, "Running planner workflow...");
    setRunStatus("running", "Running");
    renderConversation();

    try {
      const response = await fetch("/planner/invoke", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_input: text,
          thread_id: session.threadId,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Request failed with HTTP ${response.status}`);
      }

      const result = await response.json();
      session.threadId = result.thread_id || session.threadId;
      session.lastResult = result;
      replaceLoadingMessage(session, loadingId, {
        role: "assistant",
        content: responseText(result),
        status: result.status,
      });
      session.updatedAt = Date.now();
      setRunStatus(result.status === "failed" ? "failed" : "completed", result.status || "Completed");
      setSending(false, result.needs_resume ? "Waiting for your reply" : "Ready");
    } catch (error) {
      replaceLoadingMessage(session, loadingId, {
        role: "assistant",
        content: `System error: ${error.message}`,
        status: "failed",
      });
      session.updatedAt = Date.now();
      setRunStatus("failed", "Failed");
      setSending(false, "Request failed");
    }

    saveSessions();
    render();
    messageInput.focus();
  }

  function responseText(result) {
    if (result.status === "interrupted") {
      return result.interrupt_message || result.final_answer || "Could you provide the missing information?";
    }
    return result.final_answer || result.interrupt_message || "I could not complete the request.";
  }

  function replaceLoadingMessage(session, loadingId, next) {
    const index = session.messages.findIndex((message) => message.id === loadingId);
    const message = createMessage(next.role, next.content);
    message.status = next.status;
    if (index >= 0) {
      session.messages.splice(index, 1, message);
      return;
    }
    session.messages.push(message);
  }

  function render() {
    renderSessionList();
    renderConversation();
    renderExecution();
    const session = getActiveSession();
    threadLabel.textContent = session.threadId ? `Thread ${session.threadId}` : "New thread";
  }

  function renderSessionList() {
    sessionList.innerHTML = "";
    const sorted = [...sessions].sort((a, b) => b.updatedAt - a.updatedAt);

    if (!sorted.length) {
      sessionList.innerHTML = '<div class="placeholder">No recent chats.</div>';
      return;
    }

    sorted.forEach((session) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = `session-button${session.id === activeSessionId ? " active" : ""}`;
      button.innerHTML = `
        <div class="session-title">${escapeHtml(session.title || "New chat")}</div>
        <div class="session-meta">${session.messages.length} messages</div>
      `;
      button.addEventListener("click", () => {
        activeSessionId = session.id;
        sidebar.classList.remove("open");
        render();
      });
      sessionList.appendChild(button);
    });
  }

  function renderConversation() {
    const session = getActiveSession();
    conversation.innerHTML = "";

    if (!session.messages.length) {
      conversation.innerHTML = `
        <div class="empty-state">
          <h2>Start a multi-agent conversation</h2>
          <p>Ask about invoices, music, or a request that needs both agents. The planner will keep the same thread for follow-up questions.</p>
        </div>
      `;
      return;
    }

    session.messages.forEach((message) => {
      conversation.appendChild(renderMessage(message));
    });
    conversation.scrollTop = conversation.scrollHeight;
  }

  function renderMessage(message) {
    const row = document.createElement("article");
    row.className = `message-row ${message.role}`;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = message.role === "user" ? "You" : "AI";

    const bubble = document.createElement("div");
    bubble.className = "message";
    bubble.innerHTML = `
      <div class="message-header">
        <span>${message.role === "user" ? "You" : "Assistant"}</span>
        <span>${formatTime(message.createdAt)}</span>
      </div>
      <div class="message-content">
        ${
          message.loading
            ? '<span class="typing"><span></span><span></span><span></span></span>'
            : renderMarkdownLite(message.content)
        }
      </div>
    `;

    row.appendChild(avatar);
    row.appendChild(bubble);
    return row;
  }

  function renderExecution() {
    const session = getActiveSession();
    const result = session.lastResult;
    const steps = buildSteps(result);
    stepList.innerHTML = "";
    evidenceList.innerHTML = "";

    if (!result) {
      setRunStatus(isSending ? "running" : "idle", isSending ? "Running" : "Idle");
      stepList.innerHTML = '<div class="placeholder">Execution steps will appear after a request completes.</div>';
      return;
    }

    steps.forEach((step, index) => {
      const item = document.createElement("div");
      item.className = `step ${step.status}`;
      item.innerHTML = `
        <div class="step-dot">${index + 1}</div>
        <div>
          <div class="step-title">${escapeHtml(step.title)}</div>
          <div class="step-detail">${escapeHtml(step.detail)}</div>
        </div>
      `;
      stepList.appendChild(item);
    });

    const evidence = result.raw_result?.execution_evidence || [];
    if (!Array.isArray(evidence) || evidence.length === 0) {
      evidenceList.innerHTML = '<div class="placeholder">No execution evidence returned for this run.</div>';
      return;
    }

    evidence.slice(-5).forEach((entry) => {
      const card = document.createElement("div");
      card.className = "evidence-card";
      card.textContent = evidenceLabel(entry);
      evidenceList.appendChild(card);
    });
  }

  function buildSteps(result) {
    if (!result) {
      return [
        { title: "Planner", status: "idle", detail: "Waiting for a request." },
        { title: "Domain agents", status: "idle", detail: "Invoice and music agents run when needed." },
        { title: "Final response", status: "idle", detail: "Aggregator formats the answer." },
      ];
    }

    const tasks = result.raw_result?.planner_output?.tasks || [];
    const steps = [
      {
        title: "Planner",
        status: result.status === "failed" ? "failed" : "completed",
        detail: tasks.length ? `${tasks.length} task${tasks.length === 1 ? "" : "s"} planned.` : "No domain task needed.",
      },
    ];

    if (Array.isArray(tasks) && tasks.length) {
      tasks.forEach((task) => {
        steps.push({
          title: `${capitalize(task.agent || "agent")} agent`,
          status: normalizeStatus(task.status),
          detail: task.instruction || "Executed planned task.",
        });
      });
    } else {
      steps.push({
        title: "Domain agents",
        status: "completed",
        detail: "Skipped because the planner answered directly.",
      });
    }

    steps.push({
      title: "Final response",
      status: result.status === "failed" ? "failed" : "completed",
      detail: result.needs_resume ? "Waiting for more information." : "Answer returned to the conversation.",
    });

    return steps;
  }

  function evidenceLabel(entry) {
    const parts = [
      entry.kind,
      entry.agent,
      entry.operation,
      entry.status,
    ].filter(Boolean);
    const summary = entry.summary ? `: ${entry.summary}` : "";
    return `${parts.join(" / ") || "Evidence"}${summary}`;
  }

  function normalizeStatus(status) {
    if (status === "completed") return "completed";
    if (status === "failed" || status === "error") return "failed";
    if (status === "running") return "running";
    return "idle";
  }

  function setSending(next, line) {
    isSending = next;
    sendButton.disabled = next;
    messageInput.disabled = next;
    statusLine.textContent = line;
  }

  function setRunStatus(status, label) {
    runStatus.className = `status-pill ${status}`;
    runStatus.textContent = capitalize(label);
  }

  function createSession() {
    const session = {
      id: crypto.randomUUID ? crypto.randomUUID() : `session-${Date.now()}`,
      title: "",
      threadId: null,
      messages: [],
      lastResult: null,
      updatedAt: Date.now(),
    };
    sessions.unshift(session);
    return session;
  }

  function getActiveSession() {
    let session = sessions.find((item) => item.id === activeSessionId);
    if (!session) {
      session = createSession();
      activeSessionId = session.id;
    }
    return session;
  }

  function createMessage(role, content) {
    return {
      id: crypto.randomUUID ? crypto.randomUUID() : `message-${Date.now()}-${Math.random()}`,
      role,
      content,
      createdAt: Date.now(),
    };
  }

  function loadSessions() {
    try {
      const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
      return Array.isArray(parsed) ? parsed : [];
    } catch (_error) {
      return [];
    }
  }

  function saveSessions() {
    const trimmed = sessions
      .sort((a, b) => b.updatedAt - a.updatedAt)
      .slice(0, 20);
    sessions = trimmed;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
  }

  function makeTitle(text) {
    return text.length > 42 ? `${text.slice(0, 39)}...` : text;
  }

  function formatTime(timestamp) {
    return new Intl.DateTimeFormat(undefined, {
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(timestamp));
  }

  function renderMarkdownLite(text) {
    const escaped = escapeHtml(text || "");
    const withCodeBlocks = escaped.replace(/```([\s\S]*?)```/g, (_match, code) => {
      return `<pre><code>${code.trim()}</code></pre>`;
    });
    return withCodeBlocks
      .split(/\n{2,}/)
      .map((paragraph) => {
        const lineFormatted = paragraph
          .replace(/`([^`]+)`/g, "<code>$1</code>")
          .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
          .replace(/\n/g, "<br />");
        return `<p>${lineFormatted}</p>`;
      })
      .join("");
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function capitalize(value) {
    const text = String(value || "");
    return text ? text.charAt(0).toUpperCase() + text.slice(1) : "";
  }
})();
