"""
RolePrompt AI: Agent workflow (Iterations 5, 6 and 9).

run_optimization() receives the provider and model chosen by the route and
passes them to the generator and refiner.

    Input -> Classification -> Context Analysis -> Planning -> Generation
          -> Evaluation -> [Refinement -> Evaluation] up to MAX_REFINEMENTS times
          -> Response
"""

from agent.classifier import classify
from agent.config import MAX_REFINEMENTS, MIN_USEFUL_GAIN, QUALITY_THRESHOLD
from agent.context_analyzer import analyze_context
from agent.evaluator import evaluate_prompt
from agent.generator import generate_prompt
from agent.planner import build_plan
from agent.refiner import refine_prompt


def _make_version(number, refinement_iteration, prompt, evaluation, note):
    return {
        "version": number,
        "refinement_iteration": refinement_iteration,
        "prompt": prompt,
        "overall_score": evaluation["overall"],
        "evaluation": evaluation["scores"],
        "note": note,
    }


def _describe_accepted_round(number, before, after, changes):
    improved = []
    for key, item in after["criteria"].items():
        old_score = before["criteria"][key]["score"]
        if item["score"] > old_score:
            improved.append(f"{item['label']} {old_score} -> {item['score']}")

    text = f"Refinement {number}: overall score {before['overall']} -> {after['overall']}."
    if improved:
        text += " Improved criteria: " + "; ".join(improved) + "."
    if changes:
        text += " Changes made: " + "; ".join(changes) + "."
    return text


def _criteria_details(evaluation):
    return [
        {
            "key": key,
            "label": item["label"],
            "weight": item["weight"],
            "score": item["score"],
            "weaknesses": item["weaknesses"],
            "suggestions": item["suggestions"],
        }
        for key, item in evaluation["criteria"].items()
    ]


def run_optimization(request_data, provider, model):
    """
    Runs the full workflow with the given provider and model.
    Raises ClassificationError or LLMProviderError; the route maps them to HTTP errors.
    """
    classification = classify(request_data["role"], request_data["task"])
    analysis = analyze_context(request_data, classification)

    if analysis.needs_clarification:
        return {
            "original_prompt": request_data["original_prompt"],
            "optimized_prompt": "",
            "status": "clarification_needed",
            "explanation": (
                "Essential information is missing, so no prompt was generated. "
                "Answer the questions below in the instruction or context fields, then submit again."
            ),
            "assumptions": analysis.assumptions,
            "clarification_questions": analysis.questions,
        }

    plan = build_plan(request_data, classification, analysis)

    generated = generate_prompt(plan, classification, provider, model)
    current_prompt = generated["optimized_prompt"]

    current_eval = evaluate_prompt(current_prompt, classification, request_data)
    versions = [_make_version(1, 0, current_prompt, current_eval, "Initial generation")]
    improvements = []
    refinements_performed = 0

    while current_eval["overall"] < QUALITY_THRESHOLD and refinements_performed < MAX_REFINEMENTS:
        refinements_performed += 1
        round_number = refinements_performed

        revision = refine_prompt(current_prompt, current_eval, classification, request_data, provider, model)
        revised_eval = evaluate_prompt(revision["optimized_prompt"], classification, request_data)
        gain = revised_eval["overall"] - current_eval["overall"]

        if gain <= 0:
            improvements.append(
                f"Refinement {round_number}: discarded because the score did not improve "
                f"({current_eval['overall']} -> {revised_eval['overall']}). "
                "The previous version was kept."
            )
            break

        improvements.append(
            _describe_accepted_round(round_number, current_eval, revised_eval, revision["changes"])
        )
        current_prompt = revision["optimized_prompt"]
        current_eval = revised_eval
        versions.append(
            _make_version(len(versions) + 1, round_number, current_prompt, current_eval, f"Refinement {round_number}")
        )

        if gain < MIN_USEFUL_GAIN:
            improvements.append(
                f"Stopped after refinement {round_number}: the last gain was below {MIN_USEFUL_GAIN} points."
            )
            break

    return {
        "original_prompt": request_data["original_prompt"],
        "optimized_prompt": current_prompt,
        "status": "success",
        "explanation": generated["explanation"],
        "assumptions": analysis.assumptions,
        "clarification_questions": [],
        "overall_score": current_eval["overall"],
        "evaluation": current_eval["scores"],
        "criteria_details": _criteria_details(current_eval),
        "quality_threshold": QUALITY_THRESHOLD,
        "max_refinements": MAX_REFINEMENTS,
        "refinement_iterations": refinements_performed,
        "improvements": improvements,
        "remaining_weaknesses": current_eval["weaknesses"],
        "versions": versions,
    }