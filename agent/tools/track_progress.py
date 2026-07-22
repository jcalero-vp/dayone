from __future__ import annotations

from pathlib import Path
import json

from agent.config import PROGRESS_DIR
import agent.memory_backend as memory_backend


def mark_step_done(employee_email: str, step_id: str, note: str = "") -> dict:
    """Track onboarding progress.

    When AgentCore Memory is configured (`MEMORY_ID` / `BEDROCK_AGENTCORE_MEMORY_ID`
    is set), progress events are persisted there so they survive across
    AgentCore Runtime containers and scaling. Otherwise this falls back to a
    local JSON file, which is appropriate for the CLI workshop path but does
    NOT survive redeploys or multiple runtime instances.
    """
    event = memory_backend.build_event(step_id, note)

    if memory_backend.is_enabled():
        memory_backend.save_progress_event(employee_email, event)
        return event

    PROGRESS_DIR.mkdir(exist_ok=True)
    path = Path(PROGRESS_DIR) / f"{employee_email.replace('@', '_at_')}.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {"employee_email": employee_email, "steps": []}

    data["steps"].append(event)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return event


def load_progress(employee_email: str) -> dict:
    """Read the full onboarding progress document for an employee.

    Uses the same backend selection as `mark_step_done` (AgentCore Memory when
    configured, local JSON file otherwise).
    """
    if memory_backend.is_enabled():
        return memory_backend.load_progress(employee_email)

    path = Path(PROGRESS_DIR) / f"{employee_email.replace('@', '_at_')}.json"
    if not path.exists():
        return {"employee_email": employee_email, "steps": []}
    return json.loads(path.read_text(encoding="utf-8"))
