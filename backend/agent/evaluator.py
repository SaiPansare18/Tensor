"""
RolePrompt AI: Prompt evaluator (Iteration 6).

Scores an optimized prompt on seven weighted criteria. Each criterion is a
rule-based check, not a model call, so the scores are free and repeatable.

Important limits:
- These are internal heuristic indicators, not validated measures of prompt quality.
- The checks look for structure and coverage. They cannot tell whether a
  constraint was invented by the model. That needs a human reading the prompt.
"""

import re

from agent.context_analyzer import VAGUE_PHRASES, keyword_present
from agent.planner import OUTPUT_FORMAT_LABELS

# The seven components every optimized prompt must address
SEVEN_COMPONENTS = [
    "Role",
    "Objective",
    "Context",
    "Task Instructions",
    "Constraints",
    "Output Format",
    "Validation",
]

# Criterion key, display label, weight in percent. Weights total 100.
CRITERIA = [
    ("clarity", "Clarity", 15),
    ("role_relevance", "Role relevance", 15),
    ("context_completeness", "Context completeness", 15),
    ("task_specificity", "Task specificity", 15),
    ("constraints", "Constraints", 10),
    ("output_structure", "Output structure", 15),
    ("validation_requirements", "Validation requirements", 15),
]

SENTENCE_WORD_LIMIT = 35
VERIFY_WORDS = ["validate", "verify", "check", "confirm", "report", "state", "test", "measure", "count", "compare"]

ROLE_IDENTITY = {
    "data-analyst": ["data analyst", "analyst"],
    "software-developer": ["software developer", "developer", "software engineer", "engineer"],
}

ROLE_DOMAIN = {
    "data-analyst": ["data", "dataset", "analysis", "sql", "column", "metric", "statistic"],
    "software-developer": ["code", "function", "api", "module", "test", "software", "debug"],
}

STOPWORDS = {
    "about", "above", "after", "again", "their", "there", "these", "those", "which", "while",
    "would", "could", "should", "using", "without", "within", "across", "between", "every",
    "other", "where", "being", "whose", "into", "onto", "under", "over", "also", "only",
}


# ---------------------------------------------------------------------------
# Section helpers: find "### 2. Objective" style headings in the prompt text
# ---------------------------------------------------------------------------
def _is_heading(line, name):
    """True when a line is a heading for the given component, e.g. '### 4. Task Instructions'."""
    pattern = r"^(#+\s*)?(\*\*)?(\d+[.)]\s*)?" + re.escape(name) + r"\s*:?\s*(\*\*)?$"
    return re.match(pattern, line.strip(), re.IGNORECASE) is not None


def _section_body(text, name):
    """
    Returns the lines under a heading, or None if the heading is missing.
    The body ends at the next component heading or the Assumptions heading.
    """
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if _is_heading(line, name):
            start = index + 1
            break
    if start is None:
        return None

    stop_headings = [other for other in SEVEN_COMPONENTS + ["Assumptions"] if other != name]
    body = []
    for line in lines[start:]:
        if any(_is_heading(line, other) for other in stop_headings):
            break
        body.append(line)
    return body


def _bullets(lines):
    """Returns the lines that start with a bullet marker or a number."""
    return [line.strip() for line in lines if re.match(r"^\s*([-*•]|\d+[.)])\s+", line)]


def _significant_words(text):
    """Returns unique lowercase words of five or more letters, without common stopwords."""
    seen = []
    for word in re.findall(r"[a-z]{5,}", text.lower()):
        if word not in STOPWORDS and word not in seen:
            seen.append(word)
    return seen


def _result(score, weaknesses, suggestions):
    return {"score": int(max(0, min(100, round(score)))), "weaknesses": weaknesses, "suggestions": suggestions}


# ---------------------------------------------------------------------------
# One function per criterion. Each returns score, weaknesses and suggestions.
# ---------------------------------------------------------------------------
def score_clarity(text, classification):
    weaknesses, suggestions = [], []
    score = 100

    vague = [phrase for phrase in VAGUE_PHRASES if keyword_present(text, [phrase])]
    if vague:
        score -= 15 * len(vague)
        weaknesses.append(f"Vague wording: {', '.join(vague)}.")
        suggestions.append("Replace vague phrases with specific requirements.")

    sentences = [s for s in re.split(r"[.!?\n]+", text) if s.strip()]
    long_count = sum(1 for s in sentences if len(s.split()) > SENTENCE_WORD_LIMIT)
    if long_count:
        score -= min(10 * long_count, 30)
        weaknesses.append(f"{long_count} sentence(s) are longer than {SENTENCE_WORD_LIMIT} words.")
        suggestions.append("Split long sentences into shorter, single instructions.")

    return _result(score, weaknesses, suggestions)


def score_role_relevance(text, classification):
    role_id = classification["role_id"]
    role_label = classification["role_label"]
    task_label = classification["task_label"]
    weaknesses, suggestions = [], []
    score = 0

    if keyword_present(text, ROLE_IDENTITY[role_id]):
        score += 50
    else:
        weaknesses.append(f"The prompt does not name the professional role ({role_label}).")
        suggestions.append(f"State the role ({role_label}) in the Role component.")

    if keyword_present(text, [task_label.lower()]):
        score += 30
    else:
        weaknesses.append(f"The selected task ({task_label}) is not named.")
        suggestions.append(f"Name the task category ({task_label}) in the Objective.")

    domain_hits = sum(1 for word in ROLE_DOMAIN[role_id] if keyword_present(text, [word]))
    if domain_hits >= 2:
        score += 20
    else:
        weaknesses.append("Few domain-specific terms for this role.")
        suggestions.append("Use terms specific to the role's work, such as the data or system involved.")

    return _result(score, weaknesses, suggestions)


def score_context(text, classification):
    requirements = classification["task"]["requirements"]
    weaknesses, suggestions = [], []
    missing = []

    if requirements:
        covered = 0
        for requirement in requirements:
            label_present = requirement["label"].lower() in text.lower()
            if keyword_present(text, requirement["keywords"]) or label_present:
                covered += 1
            else:
                missing.append(requirement["label"])
        ratio = covered / len(requirements)
    else:
        ratio = 1.0

    score = 100 * ratio

    body = _section_body(text, "Context")
    if body is None or not any(line.strip() for line in body):
        score = min(score, 60)
        weaknesses.append("The Context section is empty or missing.")
        suggestions.append("Add a Context section that restates the known inputs.")

    for label in missing:
        weaknesses.append(f"Missing context: {label}.")
        suggestions.append(f"Add {label} to Context, or record it as an assumption.")

    return _result(score, weaknesses, suggestions)


def score_task_specificity(text, classification):
    task = classification["task"]
    weaknesses, suggestions = [], []

    words = _significant_words(f"{task['label']} {task['objective']}")
    text_lower = text.lower()
    hits = sum(1 for word in words if word[:5] in text_lower)
    ratio = hits / len(words) if words else 1.0

    # Reaching half of the objective's key words earns full marks
    score = 100 * min(1.0, ratio / 0.5)

    if score < 60:
        weaknesses.append("The task instructions do not reflect the selected task's objective closely.")
        suggestions.append(f"Restate the specific deliverable that the {task['label']} task requires.")

    return _result(score, weaknesses, suggestions)


def score_constraints(text, request_data):
    weaknesses, suggestions = [], []
    score = 0

    body = _section_body(text, "Constraints")
    if body is None:
        weaknesses.append("There is no Constraints section.")
        suggestions.append("Add a Constraints section.")
    else:
        score += 50
        if _bullets(body):
            score += 30
        else:
            weaknesses.append("The Constraints section has no listed items.")
            suggestions.append("List at least one measurable constraint.")

    user_constraints = (request_data.get("constraints") or "").strip()
    if user_constraints:
        user_words = _significant_words(user_constraints)
        if not user_words:
            score += 20
        else:
            text_lower = text.lower()
            hits = sum(1 for word in user_words if word[:5] in text_lower)
            if hits / len(user_words) >= 0.5:
                score += 20
            else:
                weaknesses.append("The user's constraints are not fully reflected in the prompt.")
                suggestions.append("Copy each user constraint into the Constraints section.")
    else:
        # No user constraints were given, so nothing can be missing
        score += 20

    return _result(score, weaknesses, suggestions)


def score_output_structure(text, request_data):
    weaknesses, suggestions = [], []

    found = [name for name in SEVEN_COMPONENTS if _section_body(text, name) is not None]
    missing = [name for name in SEVEN_COMPONENTS if name not in found]
    score = 80 * len(found) / len(SEVEN_COMPONENTS)

    format_label = OUTPUT_FORMAT_LABELS[request_data["output_format"]]
    format_keyword = format_label.split()[0].lower()
    if format_keyword in text.lower():
        score += 20
    else:
        weaknesses.append("The required output format is not stated.")
        suggestions.append(f"State the output format: {format_label}.")

    if missing:
        weaknesses.append(f"Missing sections: {', '.join(missing)}.")
        suggestions.append("Add headings for the missing components.")

    return _result(score, weaknesses, suggestions)


def score_validation(text, classification):
    weaknesses, suggestions = [], []

    body = _section_body(text, "Validation")
    if body is None:
        weaknesses.append("There is no Validation section.")
        suggestions.append("Add a Validation section with measurable checks.")
        return _result(0, weaknesses, suggestions)

    verifiable = [
        bullet for bullet in _bullets(body)
        if any(word in bullet.lower() for word in VERIFY_WORDS)
    ]
    score = 30 + min(len(verifiable), 5) * 14

    if len(verifiable) < 3:
        weaknesses.append(f"Only {len(verifiable)} verifiable validation criteria (target: 3 or more).")
        suggestions.append("Add measurable checks, such as row counts, expected outputs or test cases.")

    return _result(score, weaknesses, suggestions)


# ---------------------------------------------------------------------------
# Public function
# ---------------------------------------------------------------------------
def evaluate_prompt(prompt_text, classification, request_data):
    """
    Scores the prompt and returns:
        overall:   weighted score out of 100 (rounded)
        scores:    {criterion_key: score}
        criteria:  {criterion_key: {label, weight, score, weaknesses, suggestions}}
        weaknesses: flat list of "Label: text" strings
    """
    results = {
        "clarity": score_clarity(prompt_text, classification),
        "role_relevance": score_role_relevance(prompt_text, classification),
        "context_completeness": score_context(prompt_text, classification),
        "task_specificity": score_task_specificity(prompt_text, classification),
        "constraints": score_constraints(prompt_text, request_data),
        "output_structure": score_output_structure(prompt_text, request_data),
        "validation_requirements": score_validation(prompt_text, classification),
    }

    criteria = {}
    weaknesses = []
    weighted_total = 0.0

    for key, label, weight in CRITERIA:
        result = results[key]
        criteria[key] = {
            "label": label,
            "weight": weight,
            "score": result["score"],
            "weaknesses": result["weaknesses"],
            "suggestions": result["suggestions"],
        }
        weighted_total += result["score"] * weight / 100
        weaknesses.extend(f"{label}: {text}" for text in result["weaknesses"])

    return {
        "overall": round(weighted_total),
        "scores": {key: value["score"] for key, value in criteria.items()},
        "criteria": criteria,
        "weaknesses": weaknesses,
    }