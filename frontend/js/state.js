/* ==========================================================================
   RolePrompt AI: Frontend state (Iteration 7)
   Keeps the optimizer's draft, submission flag, last payload and any pending
   clarification in one object. Nothing is persisted: browser storage is not
   used for the prompt flow.
   ========================================================================== */

const DEFAULT_OPTIMIZER_DRAFT = Object.freeze({
    role: "",
    task: "",
    originalPrompt: "",
    additionalContext: "",
    constraints: "",
    outputFormat: "",
    targetModel: "generic",
    optimizationLevel: "standard",
});

const appState = {
    optimizer: {
        draft: { ...DEFAULT_OPTIMIZER_DRAFT },
        isSubmitting: false,
        hasAttemptedSubmit: false,
        lastPayload: null,
        // Questions from the last clarification_needed response. Empty when none is pending.
        pendingQuestions: [],
    },
};

function getOptimizerState() {
    return appState.optimizer;
}

function setOptimizerDraft(values) {
    appState.optimizer.draft = { ...values };
}

function setOptimizerSubmitting(isSubmitting) {
    appState.optimizer.isSubmitting = Boolean(isSubmitting);
}

function setOptimizerAttempted(hasAttempted) {
    appState.optimizer.hasAttemptedSubmit = Boolean(hasAttempted);
}

function setOptimizerLastPayload(payload) {
    appState.optimizer.lastPayload = payload ? { ...payload } : null;
}

/** Stores the questions the agent asked, so the form knows a clarification is open. */
function setPendingQuestions(questions) {
    appState.optimizer.pendingQuestions = Array.isArray(questions) ? [...questions] : [];
}

function clearPendingQuestions() {
    appState.optimizer.pendingQuestions = [];
}

function resetOptimizerState() {
    appState.optimizer.draft = { ...DEFAULT_OPTIMIZER_DRAFT };
    appState.optimizer.isSubmitting = false;
    appState.optimizer.hasAttemptedSubmit = false;
    appState.optimizer.lastPayload = null;
    appState.optimizer.pendingQuestions = [];
}