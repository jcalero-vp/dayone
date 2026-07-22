"""Tests for AgentCore Memory-backed onboarding progress persistence.

These tests mock `agent.memory_backend._get_client` so they do not require
real AWS credentials, the `bedrock_agentcore` package's network calls, or a
provisioned Memory resource. They verify that when `MEMORY_ID` is configured,
`agent/tools/track_progress.py` durably persists and reconstructs onboarding
progress via AgentCore Memory instead of the local JSON file, which is the
gap that matters for a real AgentCore Runtime deployment (ephemeral,
horizontally-scaled containers).
"""
from __future__ import annotations

import json

import agent.memory_backend as memory_backend
import agent.tools.track_progress as track_progress


class FakeMemoryClient:
    """In-memory stand-in for bedrock_agentcore.memory.MemoryClient."""

    def __init__(self) -> None:
        self.events: dict[tuple[str, str, str], list[dict]] = {}

    def create_event(self, *, memory_id, actor_id, session_id, messages):
        key = (memory_id, actor_id, session_id)
        text, role = messages[0]
        event = {"payload": [{"conversational": {"role": role, "content": {"text": text}}}]}
        self.events.setdefault(key, []).append(event)
        return event

    def list_events(self, *, memory_id, actor_id, session_id, max_results=100, include_payload=True):
        key = (memory_id, actor_id, session_id)
        return list(self.events.get(key, []))[:max_results]


def test_mark_step_done_uses_memory_backend_when_enabled(monkeypatch):
    fake_client = FakeMemoryClient()
    monkeypatch.setenv("MEMORY_ID", "mem-123")
    monkeypatch.setattr(memory_backend, "_get_client", lambda: fake_client)

    event = track_progress.mark_step_done("ada@example.com", "clone-repos", "Done")

    assert event["step_id"] == "clone-repos"
    assert event["note"] == "Done"

    actor_id = memory_backend._actor_id("ada@example.com")
    key = ("mem-123", actor_id, memory_backend.ONBOARDING_MEMORY_SESSION)
    assert len(fake_client.events[key]) == 1
    stored_text = fake_client.events[key][0]["payload"][0]["conversational"]["content"]["text"]
    assert json.loads(stored_text)["step_id"] == "clone-repos"


def test_load_progress_reconstructs_steps_from_memory(monkeypatch):
    fake_client = FakeMemoryClient()
    monkeypatch.setenv("MEMORY_ID", "mem-123")
    monkeypatch.setattr(memory_backend, "_get_client", lambda: fake_client)

    track_progress.mark_step_done("ada@example.com", "clone-repos", "Done")
    track_progress.mark_step_done("ada@example.com", "run-tests", "All green")

    progress = track_progress.load_progress("ada@example.com")

    assert progress["employee_email"] == "ada@example.com"
    step_ids = [step["step_id"] for step in progress["steps"]]
    assert step_ids == ["clone-repos", "run-tests"]


def test_progress_persists_across_separate_calls_simulating_new_containers(monkeypatch):
    """Simulate two separate, unrelated invocations sharing only Memory state.

    This is the scenario that a local-file-only implementation cannot satisfy
    once deployed to AgentCore Runtime: each call may land on a different
    container instance with no shared disk.
    """
    fake_client = FakeMemoryClient()
    monkeypatch.setenv("MEMORY_ID", "mem-123")
    monkeypatch.setattr(memory_backend, "_get_client", lambda: fake_client)

    # "Container A" handles the first step.
    track_progress.mark_step_done("ada@example.com", "clone-repos", "Done")

    # "Container B" (fresh process, same fake backend) reads progress and adds a step.
    progress_before = track_progress.load_progress("ada@example.com")
    assert len(progress_before["steps"]) == 1

    track_progress.mark_step_done("ada@example.com", "run-tests", "All green")
    progress_after = track_progress.load_progress("ada@example.com")
    assert len(progress_after["steps"]) == 2


def test_memory_disabled_by_default(monkeypatch):
    monkeypatch.delenv("MEMORY_ID", raising=False)
    monkeypatch.delenv("BEDROCK_AGENTCORE_MEMORY_ID", raising=False)
    assert memory_backend.is_enabled() is False


def test_invoke_session_progress_survives_separate_calls(monkeypatch):
    """End-to-end: agent/session.py::invoke_session should surface durable
    progress across independent calls when AgentCore Memory is configured,
    simulating two /sessions HTTP calls hitting different Runtime containers.
    """
    from agent.session import invoke_session

    fake_client = FakeMemoryClient()
    monkeypatch.setenv("MEMORY_ID", "mem-123")
    monkeypatch.setattr(memory_backend, "_get_client", lambda: fake_client)

    first = invoke_session(
        employee_name="Ada Lovelace",
        employee_email="ada@example.com",
        profile_id="backend-dev",
        project_id="payments-platform",
        record_step_id="clone-repos",
        record_step_note="Done",
    )
    assert [s["step_id"] for s in first["progress"]["steps"]] == ["clone-repos"]

    second = invoke_session(
        employee_name="Ada Lovelace",
        employee_email="ada@example.com",
        profile_id="backend-dev",
        project_id="payments-platform",
        record_step_id="run-tests",
        record_step_note="All green",
    )
    assert [s["step_id"] for s in second["progress"]["steps"]] == ["clone-repos", "run-tests"]
