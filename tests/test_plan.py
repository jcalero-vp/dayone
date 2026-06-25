from agent.app import build_plan


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
    assert "Checklist día 1" in plan
