"""
RolePrompt AI: Classifier (Iteration 5).

Component 1 of the agent. It does not guess a role from the text. The role and
task come from the form, and this stage checks that they exist in the registry
and that the task belongs to the role.
"""

from roles.registry import get_role, get_task


class ClassificationError(Exception):
    """Raised when the role is unknown or the task does not belong to the role."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def classify(role_id, task_id):
    """
    Returns a dict with the role and task details the later stages need.
    Raises ClassificationError when the pair is not valid.
    """
    role = get_role(role_id)
    if role is None:
        raise ClassificationError(
            "unknown_role",
            f"'{role_id}' is not a supported professional role.",
        )

    task = get_task(role_id, task_id)
    if task is None:
        raise ClassificationError(
            "task_not_in_role",
            f"The task '{task_id}' does not belong to the {role['label']} role. "
            "Choose a task from that role's list.",
        )

    return {
        "role_id": role_id,
        "role_label": role["label"],
        "task_id": task_id,
        "task_label": task["label"],
        "role": role,   # full role configuration, used by the generator
        "task": task,   # full task configuration, used by the analyzer and planner
    }