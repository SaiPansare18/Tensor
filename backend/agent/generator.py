"""
RolePrompt AI: Generator (Iteration 9).

Builds the messages, calls the provider it is given once, and checks the answer.
It does not know which provider that is.
"""

from llm.base_provider import ProviderResponseError


def build_generation_messages(plan, classification):
    """Returns (system_prompt, user_message) built from the plan and the role configuration."""
    role = classification["role"]
    component_list = "\n".join(f"{index}. {name}" for index, name in enumerate(plan["components"], start=1))

    system_prompt = (
        f"{role['persona']}\n\n"
        "Rewrite the user's instruction as a professional prompt that a language model can follow. "
        "The optimized prompt must address these seven components, in this order, with clear headings:\n"
        f"{component_list}\n\n"
        f"Optimization level: {plan['level_guidance']}\n"
        f"Target model: {plan['target_guidance']}\n\n"
        "Rules:\n"
        "- Do not add an 'Assumptions' heading or list. Assumptions are reported separately.\n"
        "- Include the validation criteria from the user message in the Validation component.\n"
        "- Do not invent facts, figures, file names, data or constraints that the user did not provide.\n"
        "- Do not ask questions inside the optimized prompt.\n\n"
        "Respond only with a JSON object with exactly two string keys: "
        "\"optimized_prompt\" (the full rewritten prompt) and "
        "\"explanation\" (3 to 6 sentences describing what changed and why)."
    )

    constraints_text = "\n".join(f"- {item}" for item in plan["constraints"]) or "None provided"
    validation_text = "\n".join(f"- {item}" for item in plan["validation_criteria"])
    assumptions_text = "\n".join(f"- {item}" for item in plan["assumptions"]) or "None"
    ambiguities_text = "\n".join(f"- {item}" for item in plan["ambiguities"]) or "None found"

    user_message = (
        f"Role: {plan['role_label']}\n"
        f"Task: {plan['task_label']}\n"
        f"Task objective: {plan['objective']}\n"
        f"Expected output format: {plan['output_format']}\n\n"
        f"Original instruction:\n\"\"\"\n{plan['original_prompt']}\n\"\"\"\n\n"
        f"Additional context: {plan['context']}\n\n"
        f"Constraints:\n{constraints_text}\n\n"
        f"Validation criteria to include:\n{validation_text}\n\n"
        f"Ambiguities found:\n{ambiguities_text}\n\n"
        f"Assumptions (for your reasoning only; do not copy them into the prompt):\n{assumptions_text}"
    )

    return system_prompt, user_message


def generate_prompt(plan, classification, provider, model):
    """Calls the provider once and returns {"optimized_prompt": str, "explanation": str}."""
    system_prompt, user_message = build_generation_messages(plan, classification)
    answer = provider.generate_json(system_prompt=system_prompt, user_message=user_message, model=model)

    optimized_prompt = answer.get("optimized_prompt")
    explanation = answer.get("explanation")

    if not isinstance(optimized_prompt, str) or not optimized_prompt.strip():
        raise ProviderResponseError("The model's answer did not include an optimized prompt. Try again.")
    if not isinstance(explanation, str) or not explanation.strip():
        raise ProviderResponseError("The model's answer did not include an explanation. Try again.")

    return {
        "optimized_prompt": optimized_prompt.strip(),
        "explanation": explanation.strip(),
    }