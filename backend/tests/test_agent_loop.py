"""
Refinement loop tests (Iteration 10).
The evaluator is replaced with scripted scores, so the loop logic is tested
on its own: the three-round cap, early stop, and discarding a revision that does not help.
"""

import agent
from agent import run_optimization
from llm.registry import PROVIDERS

REQUEST = {
    "role": "data-analyst",
    "task": "data-cleaning",
    "original_prompt": "Clean my sales CSV and find regions with missing data",
    "context": "",
    "constraints": "",
    "output_format": "markdown",
    "target_model": "generic",
    "optimization_level": "standard",
}


def scripted_evaluator(scores):
    """Returns an evaluator stub that yields the given overall scores in order."""
    remaining = iter(scores)

    def evaluate(prompt_text, classification, request_data):
        return {"overall": next(remaining), "scores": {}, "criteria": {}, "weaknesses": []}

    return evaluate


def run_with(monkeypatch, scores, threshold):
    monkeypatch.setattr(agent, "evaluate_prompt", scripted_evaluator(scores))
    monkeypatch.setattr(agent, "QUALITY_THRESHOLD", threshold)
    return run_optimization(dict(REQUEST), PROVIDERS["gemini"], "gemini-3.5-flash-lite")


def test_refinement_stops_at_three_rounds(monkeypatch, fake_gemini):
    result = run_with(monkeypatch, [50, 60, 70, 80, 90], threshold=101)
    assert result["refinement_iterations"] == 3
    assert len(result["versions"]) == 4
    assert result["overall_score"] == 80


def test_discarded_revision_keeps_previous_version(monkeypatch, fake_gemini):
    result = run_with(monkeypatch, [50, 50], threshold=101)
    assert result["refinement_iterations"] == 1
    assert len(result["versions"]) == 1
    assert result["overall_score"] == 50


def test_loop_stops_early_when_threshold_is_reached(monkeypatch, fake_gemini):
    result = run_with(monkeypatch, [50, 90], threshold=85)
    assert result["refinement_iterations"] == 1
    assert result["overall_score"] == 90