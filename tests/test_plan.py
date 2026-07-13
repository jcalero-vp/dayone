from pathlib import Path

import pytest

from agent.app import build_plan
from agent.config import PROFILES_DIR, PROJECTS_DIR
from agent.tools.generate_plan import generate_onboarding_plan
from agent.tools.load_profile import load_profile
from agent.tools.load_project import load_project


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
