# API reference

Base URL: `http://127.0.0.1:8000`. Errors use `{"detail": {"code": "...", "message": "..."}}`, except validation errors (422), which FastAPI reports in its own format.

## GET /api/health

Returns `{"status": "ok", "service": "RolePrompt AI", "version": "0.9.0"}`.

## POST /api/optimize

Request body:

| Field | Type | Rules |
|---|---|---|
| `role` | string | `data-analyst` or `software-developer` |
| `task` | string | A task id belonging to the role, for example `data-cleaning` |
| `original_prompt` | string | 10 to 4000 characters |
| `context` | string | Optional, up to 1500 characters |
| `constraints` | string | Optional, up to 1000 characters |
| `output_format` | string | `markdown`, `bullets`, `steps`, `table`, `json`, `code`, `report` or `text` |
| `target_model` | string | `generic` (default provider), `gemini`, `openai` or `claude` |
| `optimization_level` | string | `light`, `standard` (default) or `deep` |
| `model` | string | Optional. Must be in the provider's supported list |

Response (200):

```json
{
  "session_id": "f3d3d32e-c6bd-45e3-97ce-63fb52c1243e",
  "original_prompt": "Clean my sales CSV and find regions with missing data",
  "optimized_prompt": "...",
  "status": "success",
  "explanation": "...",
  "assumptions": ["No constraints were provided, ..."],
  "clarification_questions": [],
  "provider": "gemini",
  "model": "gemini-3.5-flash-lite",
  "overall_score": 93,
  "evaluation": {"clarity": 100, "role_relevance": 70},
  "criteria_details": [],
  "quality_threshold": 85,
  "max_refinements": 3,
  "refinement_iterations": 0,
  "improvements": [],
  "remaining_weaknesses": [],
  "versions": [{"version": 1, "refinement_iteration": 0, "prompt": "...", "overall_score": 93, "evaluation": {}, "note": "Initial generation"}]
}
```

When essential information is missing, `status` is `clarification_needed`, `optimized_prompt` is empty, and `clarification_questions` lists the questions. No model is called.

Errors:

| HTTP | Code | Meaning |
|---|---|---|
| 400 | `unknown_role`, `task_not_in_role`, `invalid_request` | The role, task or model choice is not valid |
| 422 | (validation) | A field is missing or outside its allowed values |
| 429 | `rate_limited` | The provider's rate limit was reached |
| 502 | `invalid_api_key`, `invalid_response` | The provider rejected the key, or returned an unusable answer |
| 503 | `not_configured`, `unavailable` | The provider has no key, or could not be reached |

Failed requests are not saved.

## GET /api/history?page=1&page_size=20

Lists saved sessions, newest first. `page` is at least 1; `page_size` is 1 to 100.

```json
{"items": [{"id": "...", "original_prompt": "...", "role": "data-analyst", "task": "data-cleaning", "status": "success", "overall_score": 93, "refinement_iterations": 0, "created_at": "2026-11-27T10:14:43+00:00"}], "total": 1, "page": 1, "page_size": 20}
```

## GET /api/sessions/{session_id}

Returns one saved session with its versions and evaluation. No model is called.

- 400 `invalid_session_id` if the ID is not a UUID.
- 404 `session_not_found` if no session has that ID.

## DELETE /api/sessions/{session_id}

Deletes the session and its versions. Returns 204 with no body. Same error codes as the GET above.

## GET /api/models

```json
{"default_provider": "gemini", "providers": [{"id": "gemini", "display_name": "Google Gemini", "status": "configured", "configured_model": "gemini-3.5-flash-lite", "supported_models": ["gemini-3.5-flash-lite", "gemini-2.5-flash"], "last_check_message": null}]}
```

Status values: `not_configured`, `configured`, `connected`, `connection_failed`. Keys are never included.

## POST /api/models/connect

Request: `{"provider": "gemini"}`. Sends one small test request to the provider. Returns `{"provider": "...", "status": "...", "message": "..."}`. Unknown provider names return 400.