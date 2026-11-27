"""
RolePrompt AI: Refinement settings (Iteration 6).

All thresholds live here so they are not scattered through the code.
Change a value, then restart the server (the server reads Python files at startup).
"""

# A prompt scoring at or above this value stops refinement early.
QUALITY_THRESHOLD = 85

# Hard limit on refinement rounds. The loop in agent/__init__.py never exceeds it.
MAX_REFINEMENTS = 3

# If an accepted refinement gains fewer points than this, refinement stops,
# because further rounds are unlikely to change the result meaningfully.
MIN_USEFUL_GAIN = 2