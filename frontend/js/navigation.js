/* ==========================================================================
   RolePrompt AI: Navigation (Iteration 2)
   Responsibilities:
   1. Show only the page section that matches the URL hash (e.g. #roles).
   2. Highlight the matching sidebar item and update the top bar title.
   3. Open and close the mobile sidebar drawer.

   Routing uses URL hashes, so the browser never sends them to the server.
   FastAPI keeps serving only "/", and back/forward buttons work normally.
   ========================================================================== */

// Maps each hash name to the title shown in the top bar.
// Keys must match data-page values in index.html.
const PAGE_TITLES = {
    dashboard: "Dashboard",
    optimize: "Optimize Prompt",
    history: "Prompt History",
    roles: "Roles",
    models: "Models",
    settings: "Settings",
};

const DEFAULT_PAGE = "dashboard";

/**
 * Reads the current hash (e.g. "#roles") and returns a valid page name.
 * Unknown or empty hashes fall back to the dashboard.
 */
function getPageFromHash() {
    const pageName = window.location.hash.replace("#", "");
    return Object.prototype.hasOwnProperty.call(PAGE_TITLES, pageName)
        ? pageName
        : DEFAULT_PAGE;
}

/**
 * Makes one page visible and updates the sidebar, title and document title.
 * Everything else is hidden through CSS (.page without .is-active is display: none).
 */
function showPage(pageName) {
    // Show the matching section, hide the rest
    document.querySelectorAll(".page").forEach((section) => {
        section.classList.toggle("is-active", section.dataset.page === pageName);
    });

    // Highlight the matching sidebar link and mark it for screen readers
    document.querySelectorAll(".nav-item").forEach((link) => {
        const isActive = link.dataset.page === pageName;
        link.classList.toggle("active", isActive);

        if (isActive) {
            link.setAttribute("aria-current", "page");
        } else {
            link.removeAttribute("aria-current");
        }
    });

    // Update visible and browser-tab titles
    document.getElementById("page-title").textContent = PAGE_TITLES[pageName];
    document.title = `${PAGE_TITLES[pageName]} · RolePrompt AI`;

    // Close the mobile drawer after choosing a page, then scroll to the top
    closeSidebar();
    window.scrollTo({ top: 0, behavior: "auto" });
}

/** Opens the mobile sidebar drawer and shows the dark backdrop. */
function openSidebar() {
    document.getElementById("sidebar").classList.add("is-open");
    document.getElementById("sidebar-overlay").classList.add("is-visible");
    document.getElementById("menu-toggle").setAttribute("aria-expanded", "true");
}

/** Closes the mobile sidebar drawer. Safe to call when it is already closed. */
function closeSidebar() {
    document.getElementById("sidebar").classList.remove("is-open");
    document.getElementById("sidebar-overlay").classList.remove("is-visible");
    document.getElementById("menu-toggle").setAttribute("aria-expanded", "false");
}

/** Connects all navigation event listeners. Called once from app.js. */
function initNavigation() {
    // Respond to hash changes (clicking links, typing a URL, back/forward buttons)
    window.addEventListener("hashchange", () => {
        showPage(getPageFromHash());
    });

    // Hamburger button toggles the drawer
    const menuToggle = document.getElementById("menu-toggle");
    menuToggle.addEventListener("click", () => {
        const isOpen = document.getElementById("sidebar").classList.contains("is-open");
        if (isOpen) {
            closeSidebar();
        } else {
            openSidebar();
        }
    });

    // Clicking the dark backdrop closes the drawer
    document.getElementById("sidebar-overlay").addEventListener("click", closeSidebar);

    // The Escape key also closes the drawer, which keyboard users expect
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeSidebar();
        }
    });

    // Show the page that matches the URL when the page first loads
    showPage(getPageFromHash());
}