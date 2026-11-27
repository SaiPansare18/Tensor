/* ==========================================================================
   RolePrompt AI: Models page (Iteration 9)
   1. Loads provider status and models from GET /api/models.
   2. Runs a connection test for one provider with POST /api/models/connect.
   3. Shows status honestly: a key alone is "configured", not "connected".
   All requests go through api.js. Text is set with textContent.
   ========================================================================== */

const STATUS_LABELS = {
    not_configured: "Not configured",
    configured: "Configured (not tested)",
    connected: "Connected",
    connection_failed: "Connection failed",
};

async function loadModels() {
    const list = document.getElementById("models-list");
    const message = document.getElementById("models-message");
    if (!list) {
        return;
    }

    message.hidden = true;
    try {
        const data = await getJson("/models");
        renderModels(data);
    } catch (error) {
        message.textContent = error.message;
        message.hidden = false;
    }
}

function renderModels(data) {
    const list = document.getElementById("models-list");
    list.replaceChildren();

    data.providers.forEach((provider) => {
        const card = document.createElement("article");
        card.className = "card model-card";

        const head = document.createElement("div");
        head.className = "model-card-head";

        const title = document.createElement("h2");
        title.textContent = provider.display_name;

        const badge = document.createElement("span");
        badge.className = "badge";
        badge.textContent = STATUS_LABELS[provider.status] || provider.status;

        head.append(title, badge);

        const details = document.createElement("p");
        details.className = "muted";
        details.textContent =
            `Model: ${provider.configured_model}. Supported: ${provider.supported_models.join(", ")}.` +
            (data.default_provider === provider.id ? " This is the default provider." : "");

        const note = document.createElement("p");
        note.className = "muted";
        note.textContent = provider.last_check_message || "No connection test has been run yet.";

        const button = document.createElement("button");
        button.type = "button";
        button.className = "btn btn-secondary btn-small";
        button.textContent = "Test connection";
        button.disabled = provider.status === "not_configured";
        button.addEventListener("click", () => testConnection(provider.id));

        card.append(head, details, note, button);
        list.append(card);
    });
}

async function testConnection(providerId) {
    const message = document.getElementById("models-message");
    message.hidden = true;
    try {
        await postJson("/models/connect", { provider: providerId });
    } catch (error) {
        message.textContent = error.message;
        message.hidden = false;
    }
    await loadModels();
}

function initModels() {
    if (!document.getElementById("models-list")) {
        return;
    }
    window.addEventListener("hashchange", () => {
        if (window.location.hash === "#models") {
            loadModels();
        }
    });
    if (window.location.hash === "#models") {
        loadModels();
    }
}

document.addEventListener("DOMContentLoaded", initModels);