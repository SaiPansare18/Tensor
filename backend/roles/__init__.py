"""
Role configuration package for RolePrompt AI.

Each role is a separate module (data_analyst.py, software_developer.py).
The registry (registry.py) is the only file that imports them, so the rest of
the agent asks the registry for roles and tasks instead of importing role files.
"""