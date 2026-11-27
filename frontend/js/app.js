/* ==========================================================================
   RolePrompt AI: Application startup
   Responsibilities:
   1. Start navigation (defined in navigation.js).
   2. Call the backend health endpoint and show the result in the sidebar.

   This file contains no page logic. Each feature gets its own file later.
   ========================================================================== */

// Relative URL: the request goes to the same server that served this page
const HEALTH_ENDPOINT = "/api/health";

/**
 * Calls GET /api/health and updates the status pill in the sidebar footer.
 * The pill shows "Online" only when the backend actually responds.
 */
async function checkBackendHealth() {
    const statusElement = document.getElementById("health-status");

    if (!statusElement) {
        console.warn("Element #health-status not found.");
        return;
    }

    try {
        const response = await fetch(HEALTH_ENDPOINT);

        // fetch() only rejects on network failure, so HTTP errors must be checked manually
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        statusElement.textContent = `Online (${data.status})`;
        statusElement.classList.remove("status-error");
        statusElement.classList.add("status-ok");
    } catch (error) {
        statusElement.textContent = "Offline";
        statusElement.classList.remove("status-ok");
        statusElement.classList.add("status-error");
        console.error("Health check failed:", error);
    }
}

// Start the application once the HTML has finished loading
document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    checkBackendHealth();
});