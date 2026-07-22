"""Session-based invocation wrapper for the onboarding agent.

This module is intentionally framework-light so it can be called from a local
script, the FastAPI layer, or an AgentCore Runtime handler. In production it
would be backed by managed runtime infrastructure (Fargate / Lambda / ECS).
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from agent.app import build_plan
from agent.tools.track_progress import load_progress, mark_step_done

logger = logging.getLogger(__name__)


def invoke_session(
    employee_name: str,
    employee_email: str,
    profile_id: str,
    project_id: str,
    *,
    record_step_id: str | None = None,
    record_step_note: str = "",
) -> dict[str, Any]:
    """Run a single onboarding session and return a stable payload.

    The returned dict is the contract between the local workshop code and a
    future AgentCore Runtime / backoffice UI. It can be persisted to DynamoDB
    or returned from an HTTP endpoint without changing the agent tools.
    """
    session_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc).isoformat()
    logger.info(
        "session started",
        extra={
            "session_id": session_id,
            "employee_email": employee_email,
            "profile_id": profile_id,
            "project_id": project_id,
        },
    )

    try:
        plan_markdown = build_plan(employee_name, employee_email, profile_id, project_id)
    except Exception as exc:
        logger.exception("session failed", extra={"session_id": session_id})
        raise

    completed_at = datetime.now(timezone.utc).isoformat()
    progress_event = None
    if record_step_id:
        progress_event = mark_step_done(employee_email, record_step_id, record_step_note)

    # Full accumulated progress (not just this call's event). This is what
    # makes onboarding progress durable across separate /sessions calls: the
    # underlying backend is AgentCore Memory when configured, or the local
    # JSON file otherwise (see agent/tools/track_progress.py).
    progress = load_progress(employee_email)

    logger.info(
        "session completed",
        extra={
            "session_id": session_id,
            "employee_email": employee_email,
            "duration_ms": _duration_ms(started_at, completed_at),
        },
    )

    return {
        "session_id": session_id,
        "employee_name": employee_name,
        "employee_email": employee_email,
        "profile_id": profile_id,
        "project_id": project_id,
        "plan_markdown": plan_markdown,
        "started_at": started_at,
        "completed_at": completed_at,
        "progress_event": progress_event,
        "progress": progress,
    }


def _duration_ms(started_at: str, completed_at: str) -> int:
    """Compute elapsed milliseconds between two ISO UTC timestamps."""
    start = datetime.fromisoformat(started_at)
    end = datetime.fromisoformat(completed_at)
    return int((end - start).total_seconds() * 1000)
