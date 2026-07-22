"""AgentCore Memory-backed persistence for onboarding progress.

`agent/tools/track_progress.py` writes to a local JSON file by default, which
is fine for the CLI workshop path but does NOT survive AgentCore Runtime
deployments: each session may run in a fresh container with an ephemeral
filesystem, and there is no shared disk across concurrent/ scaled instances.

When the runtime is configured with an AgentCore Memory resource (the same
one the AWS starter creates and wires via `MEMORY_ID` /
`BEDROCK_AGENTCORE_MEMORY_ID`), this module persists onboarding progress
events as structured JSON payloads in Memory instead of on local disk. Memory
partitions events by `actor_id` (the employee email) and `session_id`; we use
a stable session id per employee so all onboarding progress accumulates in
one place regardless of how many separate `/sessions` calls are made.

This is intentionally isolated behind a small functional interface so
`track_progress.py` (and its tests) do not need the `bedrock_agentcore`
package installed or AWS credentials configured unless Memory is enabled.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

# All onboarding progress for a given employee is stored under one stable
# Memory session id, distinct from the per-request session ids returned by
# `agent/session.py::invoke_session` (those are for tracing/observability).
ONBOARDING_MEMORY_SESSION = "onboarding-progress"


def _memory_id() -> str | None:
    return os.getenv("BEDROCK_AGENTCORE_MEMORY_ID") or os.getenv("MEMORY_ID")


def is_enabled() -> bool:
    """Whether AgentCore Memory should be used instead of the local JSON file."""
    return bool(_memory_id())


@lru_cache(maxsize=1)
def _get_client() -> Any:
    from bedrock_agentcore.memory import MemoryClient

    region = os.getenv("AWS_REGION", "us-east-1")
    return MemoryClient(region_name=region)


def _actor_id(employee_email: str) -> str:
    """Return an AgentCore Memory-compatible actor_id.

    Memory actor IDs must match the pattern `[a-zA-Z0-9][a-zA-Z0-9-_/]*`;
    email addresses contain '.' and '@', so we map those to safe characters.
    """
    sanitized = employee_email.replace("@", "_at_").replace(".", "_")
    return sanitized


def save_progress_event(employee_email: str, event: dict[str, Any]) -> None:
    """Persist one onboarding progress event to AgentCore Memory."""
    memory_id = _memory_id()
    if not memory_id:
        raise RuntimeError("AgentCore Memory is not configured (MEMORY_ID unset)")

    client = _get_client()
    client.create_event(
        memory_id=memory_id,
        actor_id=_actor_id(employee_email),
        session_id=ONBOARDING_MEMORY_SESSION,
        messages=[(json.dumps(event, ensure_ascii=False), "assistant")],
    )


def load_progress(employee_email: str, max_results: int = 200) -> dict[str, Any]:
    """Reconstruct the onboarding progress document from AgentCore Memory events."""
    memory_id = _memory_id()
    if not memory_id:
        raise RuntimeError("AgentCore Memory is not configured (MEMORY_ID unset)")

    client = _get_client()
    raw_events = client.list_events(
        memory_id=memory_id,
        actor_id=_actor_id(employee_email),
        session_id=ONBOARDING_MEMORY_SESSION,
        max_results=max_results,
        include_payload=True,
    )

    steps: list[dict[str, Any]] = []
    for raw_event in raw_events or []:
        for payload in _extract_text_payloads(raw_event):
            try:
                steps.append(json.loads(payload))
            except (TypeError, ValueError):
                continue

    steps.sort(key=lambda step: step.get("completed_at", ""))
    return {"employee_email": employee_email, "steps": steps}


def _extract_text_payloads(raw_event: dict[str, Any]) -> list[str]:
    """Pull the text content blocks out of a MemoryClient event record.

    Mirrors the extraction logic used by the AWS starter's `MemoryHook`
    (`agent/my_agent.py`), which reads `payload[].conversational.content.text`.
    """
    payloads: list[str] = []
    for payload_item in raw_event.get("payload", []):
        conversational = payload_item.get("conversational") if isinstance(payload_item, dict) else None
        if not conversational:
            continue
        text = conversational.get("content", {}).get("text", "")
        if text:
            payloads.append(text)
    return payloads


def build_event(step_id: str, note: str = "") -> dict[str, Any]:
    """Build the same event shape used by the local JSON backend."""
    return {
        "step_id": step_id,
        "note": note,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
