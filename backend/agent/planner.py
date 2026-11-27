"""
RolePrompt AI: Planner (Iteration 5, fixed for Iteration 9 providers).

Component 3 of the agent. It turns the inputs and the analysis into a structured
plan. The plan is plain data. It contains no model call.

Target guidance falls back to the provider-neutral text for any provider that has
no specific wording, so every provider choice (gemini, openai, claude, generic)
produces a plan.
"""

# Human-readable labels for the output format values sent by the form
OUTPUT_FORMAT_LABELS = {
    "markdown": "Structured Markdown",
    "bullets": "Bulleted list",
    "steps": "Numbered steps",
    "table": "Table",
    "json": "JSON",
    "code": "Code with explanation",
    "report": "Report with sections",
    "text": "Plain text",
}

LEVEL_GUIDANCE = {
    "light": "Keep the user's wording and structure. Fix clarity, grammar and missing details only.",
    "standard": "Rewrite for clarity and structure. Cover the seven components where they add value.",
    "deep": "Restructure fully. Cover all seven components, add explicit validation criteria, and make constraints measurable.",
}

NEUTRAL_TARGET_GUIDANCE = "The prompt must work with any capable language model."

# Provider-specific wording. Providers not listed here use NEUTRAL_TARGET_GUIDANCE.
TARGET_GUIDANCE = {
    "generic": NEUTRAL_TARGET_GUIDANCE,
    "openai": "The prompt will be sent to an OpenAI model. Use clear section headers and explicit instructions.",
}

# The seven parts every optimized prompt covers (from the project specification)
SEVEN_COMPONENTS = [
    "Role",
    "Objective",
    "Context",
    "Task Instructions",
    "Constraints",
    "Output Format",
    "Validation",
]


def _split_constraints(text):
    """Turns a block of constraint text into a clean list, one item per line."""
    items = []
    for line in text.splitlines():
        cleaned = line.strip(" \t-•")
        if cleaned:
            items.append(cleaned)
    return items


def get_target_guidance(target_model):
    """Returns the guidance text for a provider choice, or the neutral text if none is defined."""
    return TARGET_GUIDANCE.get(target_model, NEUTRAL_TARGET_GUIDANCE)


def build_plan(request_data, classification, analysis):
    """
    Returns the plan dict used by the generator.
    Every key is something the generator can place into one of the seven components.
    """
    task = classification["task"]
    role = classification["role"]

    return {
        "role_label": classification["role_label"],
        "task_label": classification["task_label"],
        "objective": task["objective"],
        "original_prompt": request_data["original_prompt"],
        "context": request_data.get("context", "") or "None provided",
        "constraints": _split_constraints(request_data.get("constraints", "") or ""),
        "output_format": OUTPUT_FORMAT_LABELS[request_data["output_format"]],
        "target_guidance": get_target_guidance(request_data.get("target_model", "generic")),
        "level_guidance": LEVEL_GUIDANCE[request_data["optimization_level"]],
        "validation_criteria": list(task["validation"]) + list(role["validation_standards"]),
        "assumptions": list(analysis.assumptions),
        "ambiguities": list(analysis.ambiguities),
        "components": list(SEVEN_COMPONENTS),
    }