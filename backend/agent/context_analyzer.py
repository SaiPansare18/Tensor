"""
RolePrompt AI: Context analyzer (Iteration 5).

Component 2 of the agent. It checks the user's input and returns:
- questions:    essential information that is missing (blocks generation)
- assumptions:  reasonable defaults the agent will use (shown to the user)
- findings:     clarity, ambiguity and missing-item notes for the planner

It uses deterministic rules, not a model call. Keyword matching is a first filter:
it can miss information written with unusual wording, so the questions and
assumptions are visible to the user for review.
"""

import re
from dataclasses import dataclass, field
from typing import List

# Phrases that signal an underspecified request
VAGUE_PHRASES = ["make it better", "improve it", "fix it", "do something", "something like", "whatever", "stuff"]

# Words that suggest validation criteria were already given
VALIDATION_KEYWORDS = [
    "validate", "validation", "verify", "check", "test", "criteria", "accuracy",
    "must", "success", "acceptance", "should include",
]

# Words that suggest the user already described the expected output
OUTPUT_KEYWORDS = [
    "table", "list", "json", "report", "markdown", "steps", "bullet", "summary",
    "chart", "code", "format", "sections", "plain text",
]

MIN_WORDS_FOR_CLEAR_INSTRUCTION = 6


@dataclass
class ContextAnalysis:
    """Results of the analysis. Plain data, so the planner and API can read it easily."""

    clarity_notes: List[str] = field(default_factory=list)
    ambiguities: List[str] = field(default_factory=list)
    missing_context: List[str] = field(default_factory=list)
    questions: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)

    @property
    def needs_clarification(self):
        """True when at least one essential item is missing."""
        return len(self.questions) > 0


def keyword_present(text, keywords):
    """
    Returns True if any keyword appears in the text as a whole word.
    Lookbehind and lookahead stop "go" from matching "good", while still
    matching symbols such as "```" and trailing-space keywords such as "def ".
    """
    lowered = text.lower()
    for keyword in keywords:
        prefix = r"(?<!\w)" if keyword[0].isalnum() else ""
        suffix = r"(?!\w)" if keyword[-1].isalnum() else ""
        pattern = prefix + re.escape(keyword) + suffix
        if re.search(pattern, lowered):
            return True
    return False


def analyze_context(request_data, classification):
    """
    Analyzes the request for the selected task.
    request_data: dict with snake_case keys from OptimizeRequest.
    classification: result of classifier.classify().
    """
    prompt = request_data["original_prompt"]
    context = request_data.get("context", "") or ""
    constraints = request_data.get("constraints", "") or ""
    output_format = request_data["output_format"]

    # Essential and optional requirements are checked against the prompt and context together
    combined_text = f"{prompt}\n{context}"
    task = classification["task"]

    analysis = ContextAnalysis()

    # --- Clarity ---------------------------------------------------------
    if len(prompt.split()) < MIN_WORDS_FOR_CLEAR_INSTRUCTION:
        analysis.clarity_notes.append("The instruction is short, so the objective may be underspecified.")
        analysis.assumptions.append(
            "Because the instruction is brief, the objective follows the standard objective of the selected task."
        )

    # --- Ambiguous requirements ----------------------------------------
    vague_found = [phrase for phrase in VAGUE_PHRASES if keyword_present(prompt, [phrase])]
    if vague_found:
        analysis.ambiguities.append(f"Vague wording found: {', '.join(vague_found)}.")
        analysis.assumptions.append(
            "Vague wording is replaced with the standard objective of the selected task."
        )

    # --- Missing context (essential -> question, optional -> assumption) --
    for requirement in task["requirements"]:
        if keyword_present(combined_text, requirement["keywords"]):
            continue

        analysis.missing_context.append(requirement["label"])

        if requirement["essential"]:
            analysis.questions.append(requirement["question"])
        else:
            analysis.assumptions.append(requirement["assumption"])

    # --- Missing constraints -------------------------------------------
    if not constraints.strip():
        analysis.assumptions.append(
            "No constraints were provided, so the prompt adds no length, tool or style restrictions "
            "beyond the output format."
        )

    # --- Unclear output expectations ------------------------------------
    if not keyword_present(prompt, OUTPUT_KEYWORDS):
        analysis.assumptions.append(
            f"The output format follows the form selection ('{output_format}')."
        )

    # --- Missing validation criteria -----------------------------------
    if not keyword_present(f"{prompt}\n{context}", VALIDATION_KEYWORDS):
        analysis.assumptions.append(
            "No validation criteria were given, so the standards of the role and task are applied."
        )

    return analysis