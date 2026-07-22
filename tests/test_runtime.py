"""Tests for Phase 5 — AgentCore Runtime packaging."""
from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from agent.api import app
import agent.observability as observability
from agent.session import invoke_session
import agent.tools.track_progress as track_progress_module


client = TestClient(app)


def test_invoke_session_returns_plan_and_session_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(track_progress_module, "PROGRESS_DIR", tmp_path)

    result = invoke_session(
        employee_name="Ada Lovelace",
        employee_email="ada@example.com",
        profile_id="backend-dev",
        project_id="payments-platform",
    )

    assert result["employee_name"] == "Ada Lovelace"
    assert result["employee_email"] == "ada@example.com"
    assert result["profile_id"] == "backend-dev"
    assert result["project_id"] == "payments-platform"
    assert result["plan_markdown"].startswith("# Onboarding plan - Ada Lovelace")
    assert result["session_id"]
    assert result["started_at"].endswith("+00:00")
    assert result["completed_at"].endswith("+00:00")
    assert result["progress_event"] is None


def test_invoke_session_records_progress(tmp_path, monkeypatch):
    monkeypatch.setattr(track_progress_module, "PROGRESS_DIR", tmp_path)

    result = invoke_session(
        employee_name="Ada Lovelace",
        employee_email="ada@example.com",
        profile_id="backend-dev",
        project_id="payments-platform",
        record_step_id="clone-repos",
        record_step_note="Done",
    )

    assert result["progress_event"]["step_id"] == "clone-repos"
    assert result["progress_event"]["note"] == "Done"
    assert result["progress_event"]["completed_at"].endswith("+00:00")

    state_path = tmp_path / "ada_at_example.com.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["steps"][0]["step_id"] == "clone-repos"


def test_api_sessions_endpoint(tmp_path, monkeypatch):
    monkeypatch.setattr(track_progress_module, "PROGRESS_DIR", tmp_path)

    response = client.post(
        "/sessions",
        json={
            "employee_name": "Ada Lovelace",
            "employee_email": "ada@example.com",
            "profile_id": "backend-dev",
            "project_id": "payments-platform",
            "record_step_id": "run-tests",
            "record_step_note": "All green",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["session_id"]
    assert body["plan_markdown"].startswith("# Onboarding plan - Ada Lovelace")
    assert body["progress_event"]["step_id"] == "run-tests"


def test_json_formatter_emits_structured_log():
    observability.setup_logging()
    logger = logging.getLogger("test_runtime")

    record = logger.makeRecord(
        "test_runtime",
        logging.INFO,
        "test_runtime.py",
        1,
        "session completed",
        (),
        None,
    )
    record.session_id = "abc-123"
    formatted = observability.JsonFormatter().format(record)

    parsed = json.loads(formatted)
    assert parsed["message"] == "session completed"
    assert parsed["level"] == "INFO"
    assert parsed["session_id"] == "abc-123"
    assert "timestamp" in parsed
