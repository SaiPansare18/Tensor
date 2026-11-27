"""Evaluator tests (Iteration 10). The scores are heuristics; these tests check structure, not quality."""

from agent.classifier import classify
from agent.evaluator import CRITERIA, evaluate_prompt
from tests.conftest import VALID_PROMPT

REQUEST = {
    "role": "data-analyst",
    "task": "data-cleaning",
    "original_prompt": "Clean my sales CSV and find regions with missing data",
    "context": "",
    "constraints": "",
    "output_format": "markdown",
}


def test_weights_total_one_hundred():
    assert sum(weight for _, _, weight in CRITERIA) == 100


def test_overall_score_stays_within_bounds():
    classification = classify("data-analyst", "data-cleaning")
    result = evaluate_prompt("Just a short line.", classification, REQUEST)
    assert 0 <= result["overall"] <= 100


def test_structured_prompt_scores_higher_than_bare_prompt():
    classification = classify("data-analyst", "data-cleaning")
    bare = evaluate_prompt("Just a short line.", classification, REQUEST)
    structured = evaluate_prompt(VALID_PROMPT, classification, REQUEST)
    assert structured["overall"] > bare["overall"]