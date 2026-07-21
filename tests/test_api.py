import json

from fastapi.testclient import TestClient

from agent.api import app
import agent.api as api_module
import agent.tools.track_progress as track_progress_module


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_profile_and_project_endpoints():
    profiles_response = client.get("/profiles")
    projects_response = client.get("/projects")

    assert profiles_response.status_code == 200
    assert projects_response.status_code == 200
    assert any(profile["id"] == "backend-dev" for profile in profiles_response.json()["profiles"])
    assert any(project["id"] == "payments-platform" for project in projects_response.json()["projects"])

    profile_response = client.get("/profiles/backend-dev")
    project_response = client.get("/projects/payments-platform")

    assert profile_response.status_code == 200
    assert project_response.status_code == 200
    assert profile_response.json()["id"] == "backend-dev"
    assert project_response.json()["id"] == "payments-platform"


def test_onboarding_plan_endpoint_returns_markdown_and_ui_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(track_progress_module, "PROGRESS_DIR", tmp_path)

    response = client.post(
        "/onboarding-plans",
        json={
            "employee_name": "Ada Lovelace",
            "employee_email": "ada@example.com",
            "profile_id": "backend-dev",
            "project_id": "payments-platform",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert "# Onboarding plan - Ada Lovelace" in body["plan_markdown"]
    assert body["profile"]["id"] == "backend-dev"
    assert body["project"]["id"] == "payments-platform"
    assert body["repositories"][0]["name"] == "payments-api"
    assert "aws" in body["permissions"]
    assert body["progress"] == {"employee_email": "ada@example.com", "steps": []}


def test_progress_endpoint_records_step(tmp_path, monkeypatch):
    monkeypatch.setattr(track_progress_module, "PROGRESS_DIR", tmp_path)

    response = client.post(
        "/progress/steps",
        json={
            "employee_email": "ada@example.com",
            "step_id": "clone-repos",
            "note": "Completed local clone",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["event"]["step_id"] == "clone-repos"
    assert body["progress"]["steps"][0]["note"] == "Completed local clone"

    state_path = tmp_path / "ada_at_example.com.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["steps"][0]["step_id"] == "clone-repos"


def test_agent_onboarding_plan_endpoint_invokes_strands_agent(monkeypatch):
    prompts = []

    class FakeAgent:
        def __call__(self, prompt: str) -> str:
            prompts.append(prompt)
            return "The onboarding plan has been generated successfully."

    monkeypatch.setattr(api_module, "build_strands_agent", lambda: FakeAgent())

    response = client.post(
        "/agent/onboarding-plans",
        json={
            "employee_name": "Ada Lovelace",
            "employee_email": "ada@example.com",
            "profile_id": "backend-dev",
            "project_id": "payments-platform",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "strands"
    assert body["agent_response"] == "The onboarding plan has been generated successfully."
    assert body["plan_markdown"].startswith("# Onboarding plan - Ada Lovelace")
    assert body["plan_markdown_source"] == "local_tool_result"
    assert body["profile"]["id"] == "backend-dev"
    assert body["project"]["id"] == "payments-platform"
    assert "load_profile" in prompts[0]
    assert "load_project" in prompts[0]
    assert "generate_onboarding_plan" in prompts[0]
    assert "not a summary" in prompts[0]


def test_missing_profile_returns_404():
    response = client.get("/profiles/missing-profile")

    assert response.status_code == 404
    assert "Profile 'missing-profile' not found" in response.json()["detail"]
