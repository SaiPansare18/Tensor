/* ==========================================================================
   RolePrompt AI: Prompt history (Iteration 8, corrected)
   Responsibilities:
   1. List saved sessions, newest first, with pagination.
   2. Open a saved session. The result comes from the database, so no model is called.
   3. Delete a session after confirmation.

   All requests go through api.js. Text from the server is set with textContent.
   ========================================================================== */

const HISTORY_PAGE_SIZE = 10;
let historyPage = 1;
let historyTotal = 0;

/** Reads one page of the history list through api.js. */
async function fetchHistory(page) {
    return getJson(`/history?page=${page}&page_size=${HISTORY_PAGE_SIZE}`);
}

/** Formats an ISO timestamp for display. Falls back to the raw text. */
function formatDate(isoText) {
    const date = new Date(isoText);
    return Number.isNaN(date.getTime()) ? isoText : date.toLocaleString();
}

/** Renders the session list. Empty states have their own message. */
function renderHistoryList(data) {
    const list = document.getElementById("history-list");
    const empty = document.getElementById("history-empty");
    const pager = document.getElementById("history-pager");

    list.replaceChildren();
    historyTotal = data.total;

    if (data.items.length === 0) {
        empty.hidden = false;
        pager.hidden = true;
        return;
    }

    empty.hidden = true;
    pager.hidden = false;

    data.items.forEach((item) => {
        const row = document.createElement("li");
        row.className = "history-item";

        const text = document.createElement("div");
        text.className = "history-text";

        const preview = document.createElement("p");
        preview.className = "history-preview";
        const original = item.original_prompt;
        preview.textContent = original.length > 120 ? `${original.slice(0, 120)}…` : original;

        const meta = document.createElement("p");
        meta.className = "history-meta muted";
        const scoreText = item.overall_score === null ? "no score" : `score ${item.overall_score}`;
        const statusText = item.status === "clarification_needed" ? "clarification" : "completed";
        meta.textContent = `${item.role} · ${item.task} · ${scoreText} · ${statusText} · ${formatDate(item.created_at)}`;

        text.append(preview, meta);

        const actions = document.createElement("div");
        actions.className = "history-actions";

        const openButton = document.createElement("button");
        openButton.type = "button";
        openButton.className = "btn btn-secondary btn-small";
        openButton.textContent = "Open";
        openButton.addEventListener("click", () => openSession(item.id));

        const deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.className = "btn btn-secondary btn-small";
        deleteButton.textContent = "Delete";
        deleteButton.addEventListener("click", () => confirmDelete(item.id));

        actions.append(openButton, deleteButton);
        row.append(text, actions);
        list.append(row);
    });

    const totalPages = Math.max(1, Math.ceil(historyTotal / HISTORY_PAGE_SIZE));
    document.getElementById("history-page-label").textContent = `Page ${data.page} of ${totalPages}`;
    document.getElementById("history-prev").disabled = data.page <= 1;
    document.getElementById("history-next").disabled = data.page >= totalPages;
}

/** Loads one page of the list and shows it, or shows the error message. */
async function loadHistory(page = 1) {
    const message = document.getElementById("history-message");
    message.hidden = true;

    try {
        const data = await fetchHistory(page);
        historyPage = data.page;
        renderHistoryList(data);
    } catch (error) {
        message.textContent = error.message;
        message.hidden = false;
    }
}

/** Opens a saved session in the result panel. No model is called. */
async function openSession(sessionId) {
    const message = document.getElementById("history-message");
    message.hidden = true;

    try {
        const session = await getJson(`/sessions/${encodeURIComponent(sessionId)}`);
        showSavedSession(session);
        window.location.hash = "optimize";
    } catch (error) {
        message.textContent = error.message;
        message.hidden = false;
    }
}

/** Deletes a session only after the user confirms. */
async function confirmDelete(sessionId) {
    if (!window.confirm("Delete this saved session and all its versions? This cannot be undone.")) {
        return;
    }

    const message = document.getElementById("history-message");
    try {
        await deleteJson(`/sessions/${encodeURIComponent(sessionId)}`);
        await loadHistory(historyPage);
    } catch (error) {
        message.textContent = error.message;
        message.hidden = false;
    }
}

function initHistory() {
    if (!document.getElementById("history-list")) {
        return;
    }

    document.getElementById("history-prev").addEventListener("click", () => loadHistory(historyPage - 1));
    document.getElementById("history-next").addEventListener("click", () => loadHistory(historyPage + 1));

    // Reload the list whenever the History page is opened
    window.addEventListener("hashchange", () => {
        if (window.location.hash === "#history") {
            loadHistory(1);
        }
    });

    if (window.location.hash === "#history") {
        loadHistory(1);
    }
}

document.addEventListener("DOMContentLoaded", initHistory);