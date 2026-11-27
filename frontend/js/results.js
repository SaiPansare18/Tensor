/* ==========================================================================
   RolePrompt AI: Result panel (Iteration 8, corrected)
   1. Shows one state at a time: hidden, loading, error, clarification, or success.
   2. Shows a saved session from history through the same code path as a live result.
   3. Stores the versions on the panel so "Compare versions" can read them.
   4. Compare, copy and return actions.
   Backend values are written with textContent, so they are never run as HTML.
   ========================================================================== */

let clarificationSubmitHandler = null;

function setClarificationSubmitHandler(handler) {
    clarificationSubmitHandler = handler;
}

function getResultElements() {
    return {
        panel: document.getElementById("results-panel"),
        loading: document.getElementById("results-loading"),
        error: document.getElementById("results-error"),
        errorMessage: document.getElementById("results-error-message"),
        content: document.getElementById("results-content"),
        status: document.getElementById("result-status"),
        optimizedPrompt: document.getElementById("optimized-prompt"),
        explanation: document.getElementById("result-explanation"),
        originalPrompt: document.getElementById("result-original"),
        copyButton: document.getElementById("copy-optimized"),
        copyFeedback: document.getElementById("copy-feedback"),
        returnButton: document.getElementById("return-to-optimizer"),
        compareButton: document.getElementById("compare-versions"),
        compareBox: document.getElementById("compare-box"),
        savedBanner: document.getElementById("saved-banner"),
    };
}

function showResultsPanel() {
    const elements = getResultElements();
    elements.panel.hidden = false;
    elements.loading.hidden = true;
    elements.error.hidden = true;
    elements.content.hidden = true;
    return elements;
}

function scrollResultsIntoView() {
    getResultElements().panel.scrollIntoView({ behavior: "smooth", block: "start" });
}

function clearResults() {
    const elements = getResultElements();
    elements.panel.hidden = true;
    elements.loading.hidden = true;
    elements.error.hidden = true;
    elements.content.hidden = true;
    elements.copyFeedback.textContent = "";
    elements.savedBanner.hidden = true;
    elements.compareBox.hidden = true;
    removeClarificationForm(elements);
}

function showResultsLoading() {
    const elements = showResultsPanel();
    elements.savedBanner.hidden = true;
    elements.loading.hidden = false;
    scrollResultsIntoView();
}

/** Fills the error card. Questions, when given, are shown as a numbered list. */
function renderErrorCard({ title, message, questions = [], footnote }) {
    const elements = getResultElements();

    elements.error.querySelector("h2").textContent = title;
    elements.errorMessage.textContent = message;
    elements.error.querySelector("p.muted").textContent = footnote;

    const previousList = elements.error.querySelector(".clarification-list");
    if (previousList) {
        previousList.remove();
    }

    if (questions.length > 0) {
        const list = document.createElement("ol");
        list.className = "clarification-list";
        questions.forEach((question) => {
            const item = document.createElement("li");
            item.textContent = question;
            list.append(item);
        });
        elements.errorMessage.after(list);
    }
}

function removeClarificationForm(elements) {
    const previous = elements.error.querySelector(".clarification-form");
    if (previous) {
        previous.remove();
    }
}

/** One answer box per question. Every answer is required before submitting. */
function renderClarificationForm(elements, questions) {
    removeClarificationForm(elements);
    if (questions.length === 0) {
        return;
    }

    const form = document.createElement("form");
    form.className = "clarification-form";
    form.noValidate = true;
    form.style.display = "flex";
    form.style.flexDirection = "column";
    form.style.gap = "1rem";
    form.style.width = "100%";
    form.style.marginTop = "0.75rem";

    const message = document.createElement("p");
    message.className = "field-error";
    message.setAttribute("role", "alert");
    message.hidden = true;

    questions.forEach((question, index) => {
        const field = document.createElement("div");
        field.className = "form-field";

        const label = document.createElement("label");
        label.htmlFor = `clarification-answer-${index}`;
        label.textContent = `${index + 1}. ${question}`;

        const textarea = document.createElement("textarea");
        textarea.id = `clarification-answer-${index}`;
        textarea.className = "form-control form-textarea";
        textarea.rows = 3;
        textarea.maxLength = 500;
        textarea.placeholder = "Your answer";

        field.append(label, textarea);
        form.append(field);
    });

    const submit = document.createElement("button");
    submit.type = "submit";
    submit.className = "btn btn-primary";
    submit.textContent = "Submit answers";

    form.append(message, submit);

    form.addEventListener("submit", (event) => {
        event.preventDefault();

        const answers = questions.map((_, index) =>
            form.querySelector(`#clarification-answer-${index}`).value.trim()
        );
        const firstEmpty = answers.findIndex((answer) => !answer);

        if (firstEmpty !== -1) {
            message.textContent = "Answer every question before submitting.";
            message.hidden = false;
            form.querySelector(`#clarification-answer-${firstEmpty}`).focus();
            return;
        }

        message.hidden = true;
        if (clarificationSubmitHandler) {
            clarificationSubmitHandler(questions, answers);
        }
    });

    (elements.error.querySelector(".clarification-list") || elements.errorMessage).after(form);
}

function showResultsError(message) {
    const elements = showResultsPanel();
    renderErrorCard({
        title: "Optimization failed",
        message,
        footnote: "No prompt was generated. Fix the issue above and try again.",
    });
    removeClarificationForm(elements);
    elements.error.hidden = false;
    scrollResultsIntoView();
}

function showClarificationNeeded(result) {
    const elements = showResultsPanel();
    const questions = result.clarification_questions || [];

    renderErrorCard({
        title: "More information needed",
        message: result.explanation,
        questions,
        footnote: "No prompt has been generated yet. Answer each question below, then submit.",
    });
    renderClarificationForm(elements, questions);
    elements.error.hidden = false;
    scrollResultsIntoView();
}

/* --------------------------------------------------------------------------
   Evaluation display
   -------------------------------------------------------------------------- */

function createTextList(items, className = "plain-bullets") {
    const list = document.createElement("ul");
    list.className = className;
    items.forEach((text) => {
        const item = document.createElement("li");
        item.textContent = text;
        list.append(item);
    });
    return list;
}

function createHeading(text) {
    const heading = document.createElement("h3");
    heading.textContent = text;
    return heading;
}

/** Score with the internal-heuristic caveat. The target is shown only when the server sent one. */
function buildScoreSummary(result) {
    const wrap = document.createElement("div");
    wrap.className = "score-summary";

    const value = document.createElement("span");
    value.className = "score-value";
    value.textContent = `${result.overall_score}/100`;

    const caveat = document.createElement("p");
    caveat.className = "score-caveat";
    const target = result.quality_threshold == null ? "" : ` Target ${result.quality_threshold}.`;
    caveat.textContent =
        `Internal heuristic score.${target} ` +
        "This is an indicator, not a validated measure of prompt quality.";

    wrap.append(value, caveat);
    return wrap;
}

function buildCriteria(details) {
    const list = document.createElement("ul");
    list.className = "criteria-list";

    details.forEach((item) => {
        const row = document.createElement("li");

        const head = document.createElement("div");
        head.className = "criterion-head";

        const name = document.createElement("span");
        name.textContent = `${item.label} (${item.weight}%)`;

        const value = document.createElement("span");
        value.textContent = `${item.score}`;

        head.append(name, value);

        const bar = document.createElement("div");
        bar.className = "criterion-bar";
        bar.setAttribute("role", "img");
        bar.setAttribute("aria-label", `${item.label}: ${item.score} out of 100`);

        const fill = document.createElement("div");
        fill.className = "criterion-fill";
        fill.style.width = `${item.score}%`;
        bar.append(fill);

        row.append(head, bar);
        if (item.weaknesses && item.weaknesses.length > 0) {
            row.append(createTextList(item.weaknesses, "criterion-notes"));
        }
        list.append(row);
    });

    return list;
}

function buildVersions(versions) {
    const wrap = document.createElement("div");
    wrap.className = "version-list";

    versions.forEach((version) => {
        const item = document.createElement("details");
        item.className = "version-item";

        const summary = document.createElement("summary");
        summary.textContent = `Version ${version.version} · score ${version.overall_score} · ${version.note}`;

        const box = document.createElement("div");
        box.className = "result-text";
        box.textContent = version.prompt;

        item.append(summary, box);
        wrap.append(item);
    });

    return wrap;
}

function removeEvaluationSection(elements) {
    const previous = elements.content.querySelector(".evaluation-section");
    if (previous) {
        previous.remove();
    }
}

function renderEvaluation(elements, result) {
    removeEvaluationSection(elements);

    if (typeof result.overall_score !== "number") {
        return;
    }

    const section = document.createElement("div");
    section.className = "evaluation-section";

    section.append(buildScoreSummary(result));

    section.append(createHeading("Evaluation by criterion"));
    section.append(buildCriteria(result.criteria_details || []));

    section.append(createHeading("Refinement history"));
    const roundsNote = document.createElement("p");
    roundsNote.className = "muted";
    const limit = result.max_refinements == null ? "" : ` of ${result.max_refinements}`;
    roundsNote.textContent = `${result.refinement_iterations}${limit} refinement rounds performed.`;
    section.append(roundsNote);

    const improvements = result.improvements || [];
    if (improvements.length > 0) {
        section.append(createTextList(improvements));
    }

    section.append(createHeading("Remaining weaknesses"));
    const weaknesses = result.remaining_weaknesses || [];
    if (weaknesses.length > 0) {
        section.append(createTextList(weaknesses));
    } else {
        const none = document.createElement("p");
        none.className = "muted";
        none.textContent = "The evaluator found no remaining weaknesses.";
        section.append(none);
    }

    section.append(createHeading("Prompt versions"));
    const versionNote = document.createElement("p");
    versionNote.className = "muted";
    versionNote.textContent = "Expand a version to read its full text.";
    section.append(versionNote);
    section.append(buildVersions(result.versions || []));

    elements.content.querySelector(".results-head").after(section);
}

/* --------------------------------------------------------------------------
   Assumptions and success result
   -------------------------------------------------------------------------- */

function renderAssumptions(elements, assumptions) {
    const previousBlock = elements.content.querySelector(".assumptions-block");
    if (previousBlock) {
        previousBlock.remove();
    }

    if (!assumptions || assumptions.length === 0) {
        return;
    }

    const block = document.createElement("div");
    block.className = "result-block assumptions-block";

    const heading = document.createElement("h3");
    heading.textContent = "Assumptions made";

    const box = document.createElement("div");
    box.className = "result-text";
    box.append(createTextList(assumptions, "assumptions-list"));

    block.append(heading, box);
    elements.originalPrompt.closest(".result-block").before(block);
}

function showOptimizationResult(result) {
    if (result.status === "clarification_needed") {
        showClarificationNeeded(result);
        return;
    }

    const elements = showResultsPanel();

    elements.status.textContent = result.status;
    elements.optimizedPrompt.textContent = result.optimized_prompt;
    elements.explanation.textContent = result.explanation;
    elements.originalPrompt.textContent = result.original_prompt;
    elements.copyFeedback.textContent = "";
    elements.savedBanner.hidden = true;

    renderEvaluation(elements, result);

    // Stored for "Compare versions". Read by toggleCompare().
    elements.content.dataset.versions = JSON.stringify(result.versions || []);

    renderAssumptions(elements, result.assumptions);

    elements.content.hidden = false;
    scrollResultsIntoView();
}

/**
 * Shows a session loaded from history through the same code path as a live result.
 * A banner marks it as saved, so it is clear that no model was called.
 */
function showSavedSession(session) {
    if (session.status === "clarification_needed") {
        const elements = showResultsPanel();
        renderErrorCard({
            title: "Saved clarification request",
            message: session.explanation,
            questions: session.clarification_questions || [],
            footnote: "This was saved earlier. Submit a new optimization to answer the questions.",
        });
        elements.error.hidden = false;
        elements.savedBanner.hidden = false;
        scrollResultsIntoView();
        return;
    }

    const result = {
        status: "success",
        original_prompt: session.original_prompt,
        optimized_prompt: session.optimized_prompt,
        explanation: session.explanation,
        assumptions: session.assumptions,
        clarification_questions: session.clarification_questions,
        overall_score: session.overall_score,
        quality_threshold: null,
        max_refinements: null,
        refinement_iterations: session.refinement_iterations,
        improvements: session.improvements,
        remaining_weaknesses: session.remaining_weaknesses,
        criteria_details: session.criteria_details,
        versions: session.versions.map((v) => ({
            version: v.version_number,
            refinement_iteration: v.refinement_iteration,
            prompt: v.prompt,
            overall_score: v.overall_score,
            note: v.note,
        })),
    };

    showOptimizationResult(result);
    getResultElements().savedBanner.hidden = false;
}

/* --------------------------------------------------------------------------
   Compare, copy and return
   -------------------------------------------------------------------------- */

/** Shows two chosen versions side by side. Text is set with textContent. */
function renderCompare(versions) {
    const box = getResultElements().compareBox;
    box.replaceChildren();

    if (versions.length < 2) {
        const note = document.createElement("p");
        note.className = "muted";
        note.textContent = "Only one version was saved, so there is nothing to compare.";
        box.append(note);
        box.hidden = false;
        return;
    }

    const makePicker = (id, selectedIndex) => {
        const picker = document.createElement("select");
        picker.id = id;
        picker.className = "form-control";
        versions.forEach((version, index) => {
            const option = document.createElement("option");
            option.value = String(index);
            option.textContent = `Version ${version.version} · score ${version.overall_score}`;
            picker.append(option);
        });
        picker.value = String(selectedIndex);
        return picker;
    };

    const left = makePicker("compare-left", 0);
    const right = makePicker("compare-right", versions.length - 1);

    const pickers = document.createElement("div");
    pickers.className = "compare-pickers";
    pickers.append(left, right);

    const columns = document.createElement("div");
    columns.className = "compare-columns";

    const showColumns = () => {
        columns.replaceChildren();
        [left, right].forEach((picker) => {
            const version = versions[Number(picker.value)];
            const column = document.createElement("div");
            column.className = "compare-column";

            const heading = document.createElement("h3");
            heading.textContent = `Version ${version.version} · score ${version.overall_score}`;

            const text = document.createElement("div");
            text.className = "result-text";
            text.textContent = version.prompt;

            column.append(heading, text);
            columns.append(column);
        });
    };

    left.addEventListener("change", showColumns);
    right.addEventListener("change", showColumns);
    showColumns();

    box.replaceChildren(pickers, columns);
    box.hidden = false;
}

function toggleCompare() {
    const elements = getResultElements();
    const versions = elements.content.dataset.versions
        ? JSON.parse(elements.content.dataset.versions)
        : [];

    if (elements.compareBox.hidden) {
        renderCompare(versions);
    } else {
        elements.compareBox.hidden = true;
    }
}

function returnToOptimizer() {
    clearResults();
    window.location.hash = "optimize";
    document.getElementById("optimizer-form").scrollIntoView({ behavior: "smooth", block: "start" });
}

/** Copies the optimized prompt. Reports failure honestly instead of a false "Copied". */
async function copyOptimizedPrompt() {
    const elements = getResultElements();
    const text = elements.optimizedPrompt.textContent;

    if (!text) {
        return;
    }

    try {
        await navigator.clipboard.writeText(text);
        elements.copyFeedback.textContent = "Copied to clipboard.";
    } catch (error) {
        console.error("Clipboard write failed:", error);
        elements.copyFeedback.textContent =
            "Copy failed. Select the text above and copy it manually.";
    }
}

function initResults() {
    const elements = getResultElements();
    elements.copyButton.addEventListener("click", copyOptimizedPrompt);
    elements.compareButton.addEventListener("click", toggleCompare);
    elements.returnButton.addEventListener("click", returnToOptimizer);
}