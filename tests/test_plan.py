import json
from pathlib import Path
import sys

import pytest
from pydantic import ValidationError

from agent.app import build_plan, main
from agent.config import PROFILES_DIR, PROJECTS_DIR
from agent.models import Profile, Project
from agent.tools.generate_plan import generate_onboarding_plan
from agent.tools.load_profile import load_profile
from agent.tools.load_project import load_project
from agent.tools.track_progress import mark_step_done
import agent.tools.load_profile as load_profile_module
import agent.tools.load_project as load_project_module
import agent.tools.track_progress as track_progress_module


def test_build_plan_contains_employee_and_project():
    plan = build_plan(
        employee="Ada Lovelace",
        email="ada@example.com",
        profile_id="backend-dev",
        project_id="payments-platform",
    )
    assert "Ada Lovelace" in plan
    assert "Payments Platform" in plan
    assert "payments-api" in plan
    assert "Day 1 checklist" in plan


def test_build_plan_for_new_profile_and_project():
    plan = build_plan(
        employee="Test QA",
        email="qa@example.com",
        profile_id="qa-engineer",
        project_id="customer-portal",
    )
    assert "Test QA" in plan
    assert "Customer Portal" in plan
    assert "customer-portal-web" in plan
    assert "Day 1 checklist" in plan
    assert "Week 1 checklist" in plan
    assert "Approvals required by profile" in plan

    plan = build_plan(
        employee="Test Data",
        email="data@example.com",
        profile_id="data-engineer",
        project_id="data-lake",
    )
    assert "Test Data" in plan
    assert "Data Lake" in plan
    assert "data-lake-pipelines" in plan
    assert "Approvals required by profile" in plan


def test_missing_profile_and_project():
    with pytest.raises(FileNotFoundError, match="Profile 'missing-profile' not found.*Available:"):
        load_profile("missing-profile")

    with pytest.raises(FileNotFoundError, match="Project 'missing-project' not found.*Available:"):
        load_project("missing-project")


def test_profile_schema():
    for path in sorted(PROFILES_DIR.glob("*.yaml")):
        profile = load_profile(path.stem)
        assert profile["id"] == path.stem
        assert profile["name"]
        assert profile["summary"]
        permissions = profile["permissions"]
        assert "aws" in permissions
        assert "repositories" in permissions and "access" in permissions["repositories"]
        assert "ci_cd" in permissions
        assert "day_1" in profile["base_checklist"]
        assert "week_1" in profile["base_checklist"]
        assert isinstance(profile["approvals_required"], list)


def test_project_schema():
    for path in sorted(PROJECTS_DIR.glob("*.yaml")):
        project = load_project(path.stem)
        assert project["id"] == path.stem
        assert project["name"]
        assert project["business_goal"]
        assert project["architecture_summary"]
        for repo in project["repositories"]:
            assert repo["name"]
            assert repo["description"]
            assert repo["clone_url"]
            assert repo["bootstrap"]
            assert repo["test"]
        assert project["key_docs"]
        assert project["first_tasks"]
        assert project["risk_notes"]


def test_sensitive_permissions_are_approvals():
    for path in sorted(PROFILES_DIR.glob("*.yaml")):
        profile = load_profile(path.stem)
        permissions = profile["permissions"]
        flat_permissions = set(permissions.get("aws", [])) | set(permissions.get("ci_cd", []))
        flat_permissions.add(permissions.get("repositories", {}).get("access", ""))

        for approval in profile["approvals_required"]:
            assert approval not in flat_permissions, (
                f"Sensitive approval '{approval}' should not appear in permissions for {profile['id']}"
            )

        plan = generate_onboarding_plan(
            employee_name="Test",
            employee_email="test@example.com",
            profile=profile,
            project=load_project("payments-platform"),
        )
        assert "Approvals required by profile" in plan
        for approval in profile["approvals_required"]:
            assert approval in plan


def test_pydantic_profile_and_project_models():
    for path in sorted(PROFILES_DIR.glob("*.yaml")):
        profile = load_profile(path.stem)
        model = Profile.model_validate(profile)
        assert model.id == path.stem
        assert model.name == profile["name"]

    for path in sorted(PROJECTS_DIR.glob("*.yaml")):
        project = load_project(path.stem)
        model = Project.model_validate(project)
        assert model.id == path.stem
        assert model.name == project["name"]


def test_invalid_profile_yaml_raises_value_error(tmp_path, monkeypatch):
    monkeypatch.setattr(load_profile_module, "PROFILES_DIR", tmp_path)
    bad_path = tmp_path / "bad.yaml"
    bad_path.write_text("id: bad\nname: Missing fields\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Profile 'bad' has invalid YAML"):
        load_profile("bad")


def test_invalid_project_yaml_raises_value_error(tmp_path, monkeypatch):
    monkeypatch.setattr(load_project_module, "PROJECTS_DIR", tmp_path)
    bad_path = tmp_path / "bad.yaml"
    bad_path.write_text("id: bad\nname: Missing fields\nunknown_field: value\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Project 'bad' has invalid YAML"):
        load_project("bad")


def test_pydantic_model_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        Profile.model_validate({
            "id": "test",
            "name": "Test",
            "summary": "Test",
            "unknown_field": "should fail",
        })


def test_mark_step_done_appends_and_timestamp(tmp_path, monkeypatch):
    monkeypatch.setattr(track_progress_module, "PROGRESS_DIR", tmp_path)

    event1 = mark_step_done("ada@example.com", "clone-repos", "Done")
    event2 = mark_step_done("ada@example.com", "run-tests", "All green")

    assert event1["step_id"] == "clone-repos"
    assert event2["step_id"] == "run-tests"
    assert event1["completed_at"].endswith("+00:00")
    assert event2["completed_at"].endswith("+00:00")

    state_path = tmp_path / "ada_at_example.com.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert len(state["steps"]) == 2
    assert state["employee_email"] == "ada@example.com"


def test_mark_step_cli(capsys, tmp_path, monkeypatch):
    monkeypatch.setattr(track_progress_module, "PROGRESS_DIR", tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        ["agent", "mark-step", "--email", "ada@example.com", "--step-id", "clone-repos", "--note", "Done"],
    )

    main()

    captured = capsys.readouterr()
    assert "clone-repos" in captured.out
    assert "completed_at" in captured.out

    state_path = tmp_path / "ada_at_example.com.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert len(state["steps"]) == 1
    assert state["steps"][0]["step_id"] == "clone-repos"
    assert state["steps"][0]["completed_at"].endswith("+00:00")
