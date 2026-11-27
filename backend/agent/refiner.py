"""
RolePrompt AI: Refiner (Iteration 9).

Revises a prompt using the evaluator's findings. Like the generator, it uses the
provider and model it is given.
"""

from typing import List

from llm.base_provider import ProviderResponseError

# Only the weakest criteria are sent for revision, to keep the edit targeted
MAX_CRITERIA_TO_FIX = 3


def _weakest_criteria(evaluation):
    """Returns up to MAX_CRITERIA_TO_FIX criteria scoring below 100, lowest first."""
    weak = [item for item in evaluation["criteria"].values() if item["score"] < 100]
    weak.sort(key=lambda item: item["score"])
    return weak[:MAX_CRITERIA_TO_FIX]


def build_refinement_messages(current_prompt, evaluation, classification, request_data):
    """Returns (system_prompt, user_message) for one refinement round."""
    role_label = classification["role_label"]
    task_label = classification["task_label"]

    system_prompt = (
        f"You are an expert prompt editor. You revise a prompt written for a {role_label} "
        f"working on the task '{task_label}'.\n\n"
        "Rules:\n"
        "- Change only the parts named in the focus list. Keep every other section word for word.\n"
        "- Keep the seven headings in this order: Role, Objective, Context, Task Instructions, "
        "Constraints, Output Format, Validation.\n"
        "- Do not add facts, figures, file names, or constraints that the user did not provide.\n"
        "- Do not ask questions inside the prompt.\n\n"
        "Respond only with a JSON object with exactly two keys: "
        "\"optimized_prompt\" (the full revised prompt as a string) and "
        "\"changes\" (a list of short strings, each describing one change and why it was made)."
    )

    focus_lines = []
    for item in _weakest_criteria(evaluation):
        suggestions = "; ".join(item["suggestions"]) or "Strengthen this area."
        focus_lines.append(f"- {item['label']} (score {item['score']}): {suggestions}")
    focus_text = "\n".join(focus_lines) or "- No specific weakness; improve clarity only."

    constraints_text = (request_data.get("constraints") or "").strip() or "None provided"
    context_text = (request_data.get("context") or "").strip() or "None provided"

    user_message = (
        f"Original instruction:\n\"\"\"\n{request_data['original_prompt']}\n\"\"\"\n\n"
        f"User-provided context: {context_text}\n"
        f"User-provided constraints: {constraints_text}\n\n"
        f"Focus list (weakest criteria and what to change):\n{focus_text}\n\n"
        f"Current prompt:\n\"\"\"\n{current_prompt}\n\"\"\""
    )

    return system_prompt, user_message


def refine_prompt(current_prompt, evaluation, classification, request_data, provider, model):
    """Calls the provider once and returns {"optimized_prompt": str, "changes": [str, ...]}."""
    system_prompt, user_message = build_refinement_messages(
        current_prompt, evaluation, classification, request_data
    )
    answer = provider.generate_json(system_prompt=system_prompt, user_message=user_message, model=model)

    revised = answer.get("optimized_prompt")
    if not isinstance(revised, str) or not revised.strip():
        raise ProviderResponseError("The refinement did not include a revised prompt. Try again.")

    raw_changes = answer.get("changes", [])
    changes: List[str] = []
    if isinstance(raw_changes, list):
        changes = [item.strip() for item in raw_changes if isinstance(item, str) and item.strip()]

    return {"optimized_prompt": revised.strip(), "changes": changes}