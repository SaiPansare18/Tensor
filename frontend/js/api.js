/* ==========================================================================
   RolePrompt AI: Backend API client (Iteration 8)
   The only file that calls fetch(). Provides JSON helpers for the optimizer
   and the history page, a timeout, and readable error messages.
   No API keys are used or stored here.
   ========================================================================== */

const API_BASE_URL = "/api";
const REQUEST_TIMEOUT_MS = 150000;
const READ_TIMEOUT_MS = 15000;

class ApiError extends Error {
    constructor(message, { status = 0, code = "unknown", details = "" } = {}) {
        super(message);
        this.name = "ApiError";
        this.status = status;
        this.code = code;
        this.details = details;
    }
}

function readErrorDetail(data, status) {
    const detail = data ? data.detail : undefined;

    if (detail && typeof detail === "object" && !Array.isArray(detail)) {
        return {
            message: detail.message || `The server returned HTTP ${status}.`,
            code: detail.code || "http_error",
        };
    }
    if (Array.isArray(detail)) {
        const first = detail[0] || {};
        const field = Array.isArray(first.loc) ? first.loc.slice(1).join(".") : "";
        return {
            message: `The server rejected a field${field ? ` (${field})` : ""}: ${first.msg || "invalid value"}.`,
            code: "validation_error",
        };
    }
    if (typeof detail === "string") {
        return { message: `The server returned HTTP ${status}: ${detail}`, code: "http_error" };
    }
    return { message: `The server returned HTTP ${status}.`, code: "http_error" };
}

function snippet(text) {
    return text ? text.slice(0, 200) : "(empty response body)";
}

/**
 * Sends a request and returns the parsed body (or null for 204 No Content).
 * The timer covers the full exchange and is always cleared.
 */
async function sendRequest(method, path, body, timeoutMs) {
    const url = `${API_BASE_URL}${path}`;
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);

    const options = {
        method,
        headers: { Accept: "application/json" },
        signal: controller.signal,
    };
    if (body !== undefined) {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(body);
    }

    let response;
    let text;
    try {
        response = await fetch(url, options);
        text = await response.text();
    } catch (error) {
        if (error && error.name === "AbortError") {
            throw new ApiError(
                "The request took too long. Try again, or lower MAX_REFINEMENTS in backend/agent/config.py.",
                { code: "timeout" }
            );
        }
        throw new ApiError(
            `Could not reach the backend at ${url}. Check that the server is running.`,
            { code: "network_error", details: String(error) }
        );
    } finally {
        clearTimeout(timer);
    }

    if (response.status === 204) {
        return null;
    }

    let data = null;
    try {
        data = text ? JSON.parse(text) : null;
    } catch (parseError) {
        data = null;
    }

    if (!response.ok) {
        const { message, code } = readErrorDetail(data, response.status);
        throw new ApiError(message, {
            status: response.status,
            code,
            details: `${method} ${url} returned ${response.status}. Body: ${snippet(text)}`,
        });
    }

    if (data === null) {
        throw new ApiError(`The server sent HTTP ${response.status} without readable JSON.`, {
            status: response.status,
            code: "invalid_response",
        });
    }

    return data;
}

/** GET helper for the history page. */
function getJson(path) {
    return sendRequest("GET", path, undefined, READ_TIMEOUT_MS);
}

/** DELETE helper for the history page. Resolves with null on success. */
function deleteJson(path) {
    return sendRequest("DELETE", path, undefined, READ_TIMEOUT_MS);
}

/** POST helper for the models page. Returns the parsed body. */
function postJson(path, body) {
    return sendRequest("POST", path, body, READ_TIMEOUT_MS);
}

function assertOptimizationShape(data) {
    const isValid =
        data !== null &&
        typeof data === "object" &&
        typeof data.original_prompt === "string" &&
        typeof data.optimized_prompt === "string" &&
        typeof data.explanation === "string" &&
        typeof data.status === "string";

    if (!isValid) {
        throw new ApiError("The backend response did not have the expected format.", {
            code: "invalid_response",
        });
    }
    return data;
}

/** Sends the optimizer payload to POST /api/optimize. */
async function requestOptimization(payload) {
    const data = await sendRequest("POST", "/optimize", payload, REQUEST_TIMEOUT_MS);
    return assertOptimizationShape(data);
}