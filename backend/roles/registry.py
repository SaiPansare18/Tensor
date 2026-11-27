"""
RolePrompt AI: Role registry (Iteration 5).

The registry is the single entry point the agent uses to find roles and tasks.
To add a new role, create a new module in roles/, then import it here and add
it to ROLE_MODULES. The agent code does not change.
"""

from roles import data_analyst, software_developer

# Order here controls the order that list_roles() returns.
ROLE_MODULES = [data_analyst.ROLE, software_developer.ROLE]

# Index for fast lookup by id, such as "data-analyst".
_ROLES_BY_ID = {role["id"]: role for role in ROLE_MODULES}


def get_role(role_id):
    """Returns the role configuration for an id, or None if the role does not exist."""
    return _ROLES_BY_ID.get(role_id)


def get_task(role_id, task_id):
    """Returns one task of a role, or None if the role or the task is unknown."""
    role = get_role(role_id)
    if role is None:
        return None
    return role["tasks"].get(task_id)


def list_roles():
    """Returns every registered role configuration."""
    return list(ROLE_MODULES)