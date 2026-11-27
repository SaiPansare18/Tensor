"""
RolePrompt AI: Software Developer role configuration (Iteration 5).

This file holds all Software Developer instructions. No other file contains them.
See data_analyst.py for the meaning of objective, validation and requirements.
"""

# ---------------------------------------------------------------------------
# Keyword lists used by requirements
# ---------------------------------------------------------------------------
STACK_KEYWORDS = [
    "python", "fastapi", "django", "flask", "javascript", "typescript", "react", "vue",
    "angular", "svelte", "html", "css", "vanilla", "node", "express", "java", "spring",
    "golang", "rust", "c#", ".net", "php", "laravel", "ruby", "rails", "kotlin", "swift",
    "tailwind", "bootstrap",
]

CODE_KEYWORDS = [
    "```", "def ", "function ", "const ", "=>", "};", "#include", "console.log", "print(",
    "public static", "module", "endpoint", "component", "feature",
]

ERROR_KEYWORDS = [
    "error", "exception", "traceback", "stack trace", "bug", "crash", "fails", "failing",
    "not working", "unexpected", "broken", "500", "404",
]

# ---------------------------------------------------------------------------
# Shared requirements
# ---------------------------------------------------------------------------
STACK = {
    "key": "technology",
    "label": "Technology stack",
    "essential": True,
    "keywords": STACK_KEYWORDS,
    "question": "Which language, framework or stack should this use (for example Python with FastAPI, or vanilla JavaScript)?",
}

CODE = {
    "key": "code",
    "label": "Code or feature description",
    "essential": True,
    "keywords": CODE_KEYWORDS,
    "question": "Paste the relevant code, or describe the function, module or feature this applies to.",
}

# ---------------------------------------------------------------------------
# Role definition
# ---------------------------------------------------------------------------
ROLE = {
    "id": "software-developer",
    "label": "Software Developer",
    "persona": (
        "You are a senior software engineer. You write precise, testable engineering instructions, "
        "name the assumptions you make, and prefer simple, maintainable designs."
    ),
    "validation_standards": [
        "Define how success is verified, such as tests, expected outputs or observable behavior.",
        "State the language, framework and versions the solution must use.",
        "Mention edge cases and failure behavior explicitly.",
    ],
    "tasks": {
        "frontend-development": {
            "label": "Frontend Development",
            "objective": "Specify a user interface that is correct, accessible, responsive and consistent with the stated stack.",
            "validation": [
                "Require checks for keyboard navigation, screen sizes and empty or error states.",
                "State which browsers or devices must be supported.",
            ],
            "requirements": [STACK],
        },
        "backend-development": {
            "label": "Backend Development",
            "objective": "Specify server-side logic with clear inputs, outputs, error handling and data validation.",
            "validation": [
                "Require input validation and explicit error responses.",
                "Require at least one automated test for the main success path and one failure path.",
            ],
            "requirements": [STACK],
        },
        "full-stack-development": {
            "label": "Full-Stack Development",
            "objective": "Specify a feature that spans the interface, the API and the data layer, with a clear contract between them.",
            "validation": [
                "Define the request and response contract between frontend and backend.",
                "Require an end-to-end check of the main user flow.",
            ],
            "requirements": [STACK],
        },
        "debugging": {
            "label": "Debugging",
            "objective": "Specify a systematic diagnosis of a defect: reproduce, isolate, explain the cause and verify the fix.",
            "validation": [
                "Require a reproduction step and the expected versus actual behavior.",
                "Require a regression check that proves the fix works and nothing else broke.",
            ],
            "requirements": [
                {
                    "key": "error_details",
                    "label": "Error or unexpected behavior",
                    "essential": True,
                    "keywords": ERROR_KEYWORDS,
                    "question": "What goes wrong? Paste the error message or traceback, or describe the behavior you see and the behavior you expect.",
                },
                CODE,
            ],
        },
        "code-optimization": {
            "label": "Code Optimization",
            "objective": "Specify improvements to speed, memory or readability while keeping behavior identical.",
            "validation": [
                "Require the behavior to remain identical, verified by existing or new tests.",
                "Require a before and after measurement for any performance claim.",
            ],
            "requirements": [
                CODE,
                {
                    "key": "performance_goal",
                    "label": "Performance goal",
                    "essential": False,
                    "keywords": ["slow", "performance", "latency", "memory", "faster", "seconds", "ms", "complexity", "throughput"],
                    "assumption": "No performance target was named, so the prompt asks for the main trade-offs and a measurable goal.",
                },
            ],
        },
        "software-architecture": {
            "label": "Software Architecture",
            "objective": "Specify a system design with clear components, responsibilities, data flow and trade-offs.",
            "validation": [
                "Require a list of components with one responsibility each.",
                "Require the main trade-offs and the options that were rejected, with reasons.",
            ],
            "requirements": [
                {
                    "key": "system",
                    "label": "System or feature being designed",
                    "essential": True,
                    "keywords": ["system", "service", "application", "platform", "architecture", "microservice", "monolith", "feature", "product", "app", "backend", "database", "component"],
                    "question": "Which system or feature is being designed, and what are its main components?",
                },
                {
                    "key": "scale",
                    "label": "Scale requirements",
                    "essential": False,
                    "keywords": ["users", "requests", "traffic", "scale", "per second", "load", "concurrent", "uptime", "latency"],
                    "assumption": "No scale requirements were given, so the design states its assumptions about load and growth.",
                },
            ],
        },
        "api-development": {
            "label": "API Development",
            "objective": "Specify API endpoints with clear resources, request and response formats, status codes and validation.",
            "validation": [
                "Require documented request and response examples for each endpoint.",
                "Require HTTP status codes for success and each failure case.",
            ],
            "requirements": [
                {
                    "key": "endpoints",
                    "label": "Endpoints or resources",
                    "essential": True,
                    "keywords": ["endpoint", "route", "rest", "graphql", "api", "http", "json", "request", "response", "resource"],
                    "question": "Which resources or endpoints should the API expose, and what does a request and response look like?",
                },
                {
                    "key": "authentication",
                    "label": "Authentication",
                    "essential": False,
                    "keywords": ["auth", "token", "jwt", "oauth", "api key", "permission", "login"],
                    "assumption": "No authentication method was named, so the prompt requires the design to state its authentication approach.",
                },
            ],
        },
        "testing-and-documentation": {
            "label": "Testing and Documentation",
            "objective": "Specify tests and documentation that verify behavior and explain how to use the code.",
            "validation": [
                "Require tests for the main behavior, edge cases and failure paths.",
                "Require documentation that a new developer can follow without asking questions.",
            ],
            "requirements": [
                CODE,
                {
                    "key": "test_or_doc_format",
                    "label": "Test framework or documentation format",
                    "essential": False,
                    "keywords": ["pytest", "jest", "unittest", "vitest", "mocha", "junit", "cypress", "playwright", "docstring", "readme", "jsdoc", "sphinx"],
                    "assumption": "No test framework or documentation format was named, so the prompt uses the most common option for the detected language.",
                },
            ],
        },
    },
}