/* ==========================================================================
   Tensor: Prompt optimizer form
   Same behavior as the Iteration 9 version. Adds label cycling while the
   loading orb is visible. No backend or API changes.
   ========================================================================== */

const LIMITS = {
    originalPromptMin: 10,
    originalPromptMax: 4000,
    contextMax: 1500,
    constraintsMax: 1000,
};

const ENABLED_TARGET_MODELS = ["generic", "gemini", "openai", "claude"];
const OPTIMIZATION_LEVELS = ["light", "standard", "deep"];

// Labels shown in the orb while the request is pending. Display only.
const ORB_LABELS = ["Thinking", "Searching", "Analyzing", "Composing"];
const ORB_LABEL_INTERVAL_MS = 1800;

const FIELD_CONFIG = [
    { name: "role", inputId: "role-select", errorId: "error-role" },
    { name: "task", inputId: "task-select", errorId: "error-task" },
    {
        name: "originalPrompt",
        inputId: "original-prompt",
        errorId: "error-original-prompt",
        countId: "count-original-prompt",
        maxLength: LIMITS.originalPromptMax,
    },
    {
        name: "additionalContext",
        inputId: "additional-context",
        errorId: "error-additional-context",
        countId: "count-additional-context",
        maxLength: LIMITS.contextMax,
    },
    {
        name: "constraints",
        inputId: "constraints",
        errorId: "error-constraints",
        countId: "count-constraints",
        maxLength: LIMITS.constraintsMax,
    },
    { name: "outputFormat", inputId: "output-format", errorId: "error-output-format" },
    { name: "targetModel", inputId: "target-model", errorId: "error-target-model" },
    {
        name: "optimizationLevel",
        inputId: null,
        groupId: "optimization-level-group",
        errorId: "error-optimization-level",
    },
];

function getFieldConfig(name) {
    return FIELD_CONFIG.find((config) => config.name === name);
}

function readFormValues() {
    const readText = (id) => document.getElementById(id).value.trim();
    const checkedLevel = document.querySelector('input[name="optimizationLevel"]:checked');

    return {
        role: readText("role-select"),
        task: readText("task-select"),
        originalPrompt: readText("original-prompt"),
        additionalContext: readText("additional-context"),
        constraints: readText("constraints"),
        outputFormat: readText("output-format"),
        targetModel: readText("target-model"),
        optimizationLevel: checkedLevel ? checkedLevel.value : "",
    };
}

function validateValues(values) {
    const errors = {};

    if (!values.role) {
        errors.role = "Choose a professional role.";
    }

    if (!values.task) {
        errors.task = values.role
            ? "Choose a task category for this role."
            : "Choose a role first, then a task category.";
    }

    const promptLength = values.originalPrompt.length;
    if (promptLength === 0) {
        errors.originalPrompt = "Enter the instruction you want optimized.";
    } else if (promptLength < LIMITS.originalPromptMin) {
        errors.originalPrompt = `Add more detail. Use at least ${LIMITS.originalPromptMin} characters.`;
    } else if (promptLength > LIMITS.originalPromptMax) {
        errors.originalPrompt = `Shorten this to ${LIMITS.originalPromptMax} characters or fewer.`;
    }

    if (values.additionalContext.length > LIMITS.contextMax) {
        errors.additionalContext = `Shorten the context to ${LIMITS.contextMax} characters or fewer.`;
    }

    if (values.constraints.length > LIMITS.constraintsMax) {
        errors.constraints = `Shorten the constraints to ${LIMITS.constraintsMax} characters or fewer.`;
    }

    if (!values.outputFormat) {
        errors.outputFormat = "Choose an expected output format.";
    }

    if (!ENABLED_TARGET_MODELS.includes(values.targetModel)) {
        errors.targetModel = "Choose an available target LLM.";
    }

    if (!OPTIMIZATION_LEVELS.includes(values.optimizationLevel)) {
        errors.optimizationLevel = "Choose an optimization level.";
    }

    return errors;
}

function renderFieldError(config, message) {
    const errorElement = document.getElementById(config.errorId);
    errorElement.textContent = message;
    errorElement.hidden = !message;

    const target = config.inputId
        ? document.getElementById(config.inputId)
        : document.getElementById(config.groupId);

    target.classList.toggle("is-invalid", Boolean(message));
    target.setAttribute("aria-invalid", message ? "true" : "false");
}

function showAllErrors(errors) {
    FIELD_CONFIG.forEach((config) => {
        renderFieldError(config, errors[config.name] || "");
    });
}

function refreshFieldError(name) {
    const errors = validateValues(readFormValues());
    renderFieldError(getFieldConfig(name), errors[name] || "");
}

function showNotice(type, message) {
    const notice = document.getElementById("form-notice");
    notice.className = `notice notice-${type}`;
    notice.textContent = message;
    notice.hidden = !message;
}

function focusFirstInvalidField(errors) {
    const firstInvalid = FIELD_CONFIG.find((config) => errors[config.name]);
    if (!firstInvalid) {
        return;
    }

    const target = firstInvalid.inputId
        ? document.getElementById(firstInvalid.inputId)
        : document.querySelector('input[name="optimizationLevel"]');

    target.focus();
}

function updateCounter(config) {
    if (!config.countId) {
        return;
    }

    const length = document.getElementById(config.inputId).value.length;
    const counter = document.getElementById(config.countId);
    counter.textContent = `${length} / ${config.maxLength}`;
    counter.classList.toggle("is-over", length > config.maxLength);
}

function updateAllCounters() {
    FIELD_CONFIG.forEach(updateCounter);
}

function updateTaskOptions(roleId) {
    const taskSelect = document.getElementById("task-select");
    populateTaskSelect(taskSelect, roleId);
    taskSelect.disabled = !roleId;

    document.getElementById("task-hint").textContent = roleId
        ? "Tasks available for this role."
        : "Task options depend on the selected role.";
}

function buildOptimizationPayload(values) {
    return {
        role: values.role,
        task: values.task,
        original_prompt: values.originalPrompt,
        context: values.additionalContext,
        constraints: values.constraints,
        output_format: values.outputFormat,
        target_model: values.targetModel,
        optimization_level: values.optimizationLevel,
    };
}

function buildContextWithAnswers(context, questions, answers) {
    const answerBlock = questions
        .map((question, index) => `Q: ${question}\nA: ${answers[index]}`)
        .join("\n");

    return [context, `Answers to clarification questions:\n${answerBlock}`]
        .filter(Boolean)
        .join("\n\n");
}

function showPayloadPreview(payload) {
    document.getElementById("payload-preview").textContent = JSON.stringify(payload, null, 2);
    document.getElementById("payload-preview-wrap").hidden = false;
}

function hidePayloadPreview() {
    document.getElementById("payload-preview").textContent = "";
    document.getElementById("payload-preview-wrap").hidden = true;
}

function setSubmitting(isSubmitting) {
    setOptimizerSubmitting(isSubmitting);

    const form = document.getElementById("optimizer-form");
    const submitButton = document.getElementById("optimize-submit");
    const clearButton = document.getElementById("clear-form");

    form.setAttribute("aria-busy", String(isSubmitting));
    submitButton.disabled = isSubmitting;
    submitButton.classList.toggle("is-loading", isSubmitting);
    submitButton.querySelector(".btn-label").textContent = isSubmitting
        ? "Optimizing..."
        : "Optimize Prompt";
    clearButton.disabled = isSubmitting;
}

/* --------------------------------------------------------------------------
   Orb label cycling. Starts when a request is pending, stops when it settles.
   Only changes display text; it does not affect the request.
   -------------------------------------------------------------------------- */
let orbLabelTimer = null;

function startOrbLabels() {
    const label = document.getElementById("orb-label");
    if (!label) {
        return;
    }

    let index = 0;
    label.textContent = ORB_LABELS[index];

    stopOrbLabels();
    orbLabelTimer = window.setInterval(() => {
        label.classList.add("is-changing");
        window.setTimeout(() => {
            index = (index + 1) % ORB_LABELS.length;
            label.textContent = ORB_LABELS[index];
            label.classList.remove("is-changing");
        }, 200);
    }, ORB_LABEL_INTERVAL_MS);
}

function stopOrbLabels() {
    if (orbLabelTimer !== null) {
        window.clearInterval(orbLabelTimer);
        orbLabelTimer = null;
    }
}

async function sendPayload(payload) {
    setOptimizerLastPayload(payload);
    showPayloadPreview(payload);
    setSubmitting(true);
    showResultsLoading();
    startOrbLabels();

    try {
        const result = await requestOptimization(payload);

        if (result.status === "clarification_needed") {
            setPendingQuestions(result.clarification_questions || []);
        } else {
            clearPendingQuestions();
        }

        showOptimizationResult(result);
    } catch (error) {
        clearPendingQuestions();
        const message = error instanceof Error
            ? error.message
            : "An unexpected error occurred. No prompt was generated.";
        showResultsError(message);
    } finally {
        stopOrbLabels();
        setSubmitting(false);
    }
}

function handleFieldChange(name) {
    const config = getFieldConfig(name);
    updateCounter(config);
    setOptimizerDraft(readFormValues());

    if (getOptimizerState().hasAttemptedSubmit) {
        refreshFieldError(name);

        if (name === "role") {
            refreshFieldError("task");
        }
    }
}

async function handleSubmit(event) {
    event.preventDefault();

    if (getOptimizerState().isSubmitting) {
        return;
    }

    setOptimizerAttempted(true);
    const values = readFormValues();
    setOptimizerDraft(values);

    const errors = validateValues(values);
    showAllErrors(errors);

    if (Object.keys(errors).length > 0) {
        showNotice("error", "Please correct the highlighted fields before continuing.");
        hidePayloadPreview();
        clearResults();
        clearPendingQuestions();
        focusFirstInvalidField(errors);
        return;
    }

    showNotice("info", "");
    await sendPayload(buildOptimizationPayload(values));
}

async function handleClarificationAnswers(questions, answers) {
    if (getOptimizerState().isSubmitting) {
        return;
    }

    const values = readFormValues();
    const errors = validateValues(values);
    if (Object.keys(errors).length > 0) {
        showAllErrors(errors);
        showNotice("error", "Please correct the highlighted fields before submitting your answers.");
        showResultsError("Your form has errors, so the answers were not sent. Fix the fields above first.");
        return;
    }

    const context = buildContextWithAnswers(values.additionalContext, questions, answers);
    if (context.length > LIMITS.contextMax) {
        showResultsError(
            `Your context and answers total ${context.length} characters, but the limit is ${LIMITS.contextMax}. ` +
            "Shorten the answers or the context field."
        );
        return;
    }

    showNotice("info", "");
    await sendPayload({ ...buildOptimizationPayload(values), context });
}

function handleClear() {
    document.getElementById("optimizer-form").reset();
    resetOptimizerState();
    updateTaskOptions("");
    showAllErrors({});
    showNotice("info", "");
    hidePayloadPreview();
    clearResults();
    updateAllCounters();
}

function initOptimizer() {
    const form = document.getElementById("optimizer-form");

    if (!form) {
        return;
    }

    populateRoleSelect(document.getElementById("role-select"));
    updateTaskOptions("");
    updateAllCounters();
    setOptimizerDraft(readFormValues());

    form.addEventListener("submit", handleSubmit);
    document.getElementById("clear-form").addEventListener("click", handleClear);

    initResults();
    setClarificationSubmitHandler(handleClarificationAnswers);

    FIELD_CONFIG.forEach((config) => {
        if (!config.inputId) {
            return;
        }

        const input = document.getElementById(config.inputId);
        const eventName = input.tagName === "SELECT" ? "change" : "input";

        input.addEventListener(eventName, () => {
            if (config.name === "role") {
                updateTaskOptions(input.value);
            }
            handleFieldChange(config.name);
        });
    });

    form.querySelectorAll('input[name="optimizationLevel"]').forEach((radio) => {
        radio.addEventListener("change", () => handleFieldChange("optimizationLevel"));
    });
}

document.addEventListener("DOMContentLoaded", initOptimizer);