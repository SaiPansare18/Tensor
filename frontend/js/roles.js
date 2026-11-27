/* ==========================================================================
   RolePrompt AI: Role and task catalog (Iteration 3)
   Responsibilities:
   1. Hold the list of professional roles and their task categories.
   2. Provide small helpers that fill <select> elements with those options.

   This is a temporary frontend copy. In Iteration 5 the role definitions move
   to backend/roles/ and the agent uses them. Keep the ids identical so the
   switch does not change the form logic.

   This file has no side effects. It only defines data and functions.
   ========================================================================== */

const ROLE_CATALOG = [
    {
        id: "data-analyst",
        label: "Data Analyst",
        description: "Turns raw data into clean, analyzable, and reportable insight.",
        tasks: [
            { id: "data-cleaning", label: "Data Cleaning" },
            { id: "exploratory-data-analysis", label: "Exploratory Data Analysis" },
            { id: "sql-query-generation", label: "SQL Query Generation" },
            { id: "data-visualization", label: "Data Visualization" },
            { id: "statistical-analysis", label: "Statistical Analysis" },
            { id: "business-intelligence", label: "Business Intelligence" },
            { id: "predictive-analytics", label: "Predictive Analytics" },
            { id: "data-reporting", label: "Data Reporting" },
        ],
    },
    {
        id: "software-developer",
        label: "Software Developer",
        description: "Builds, debugs, and documents software across the stack.",
        tasks: [
            { id: "frontend-development", label: "Frontend Development" },
            { id: "backend-development", label: "Backend Development" },
            { id: "full-stack-development", label: "Full-Stack Development" },
            { id: "debugging", label: "Debugging" },
            { id: "code-optimization", label: "Code Optimization" },
            { id: "software-architecture", label: "Software Architecture" },
            { id: "api-development", label: "API Development" },
            { id: "testing-and-documentation", label: "Testing and Documentation" },
        ],
    },
];

/** Returns the role object for an id such as "data-analyst", or null if unknown. */
function getRoleById(roleId) {
    return ROLE_CATALOG.find((role) => role.id === roleId) || null;
}

/** Returns the task list for a role. Returns an empty list when no role is chosen. */
function getTasksForRole(roleId) {
    const role = getRoleById(roleId);
    return role ? role.tasks : [];
}

/** Creates one <option> element. Text is set with textContent, never innerHTML. */
function createOption(value, label) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = label;
    return option;
}

/** Fills the role <select> with a placeholder followed by every role. */
function populateRoleSelect(selectElement) {
    selectElement.replaceChildren(createOption("", "Select a role"));
    ROLE_CATALOG.forEach((role) => {
        selectElement.append(createOption(role.id, role.label));
    });
}

/**
 * Fills the task <select> for the given role.
 * With no role, it shows a single instruction instead of tasks.
 */
function populateTaskSelect(selectElement, roleId) {
    selectElement.replaceChildren();

    if (!roleId) {
        selectElement.append(createOption("", "Select a role first"));
        return;
    }

    selectElement.append(createOption("", "Select a task category"));
    getTasksForRole(roleId).forEach((task) => {
        selectElement.append(createOption(task.id, task.label));
    });
}