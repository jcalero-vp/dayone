from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field

from agent.app import build_plan
from agent.config import PROFILES_DIR, PROJECTS_DIR
from agent.tools.load_profile import load_profile
from agent.tools.load_project import load_project
import agent.tools.track_progress as progress_tools


app = FastAPI(
    title="Onboarding Assistant API",
    description="Thin HTTP API over the workshop onboarding domain functions.",
    version="0.1.0",
)


class OnboardingPlanRequest(BaseModel):
    employee_name: str = Field(min_length=1)
    employee_email: EmailStr
    profile_id: str = Field(min_length=1)
    project_id: str = Field(min_length=1)


class ProgressStepRequest(BaseModel):
    employee_email: EmailStr
    step_id: str = Field(min_length=1)
    note: str = ""


def build_strands_agent() -> Any:
    from agent.strands_agent import build_agent

    return build_agent()


def _raise_domain_error(exc: Exception) -> None:
    if isinstance(exc, FileNotFoundError):
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if isinstance(exc, ValueError):
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    raise exc


def _load_progress(employee_email: str) -> dict[str, Any]:
    path = Path(progress_tools.PROGRESS_DIR) / f"{employee_email.replace('@', '_at_')}.json"
    if not path.exists():
        return {"employee_email": employee_email, "steps": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _build_agent_prompt(request: OnboardingPlanRequest) -> str:
    return (
        f"Generate the complete onboarding plan for employee '{request.employee_name}' "
        f"(email {request.employee_email}) with profile '{request.profile_id}' on project "
        f"'{request.project_id}'. Use the load_profile and load_project tools to get "
        f"the data, then call generate_onboarding_plan. Return the full Markdown plan "
        f"from the tool, not a summary."
    )


def _build_plan_payload(request: OnboardingPlanRequest) -> dict[str, Any]:
    profile = load_profile(request.profile_id)
    project = load_project(request.project_id)
    plan_markdown = build_plan(
        employee=request.employee_name,
        email=str(request.employee_email),
        profile_id=request.profile_id,
        project_id=request.project_id,
    )

    return {
        "employee_name": request.employee_name,
        "employee_email": str(request.employee_email),
        "profile_id": request.profile_id,
        "project_id": request.project_id,
        "plan_markdown": plan_markdown,
        "profile": profile,
        "project": project,
        "repositories": project["repositories"],
        "permissions": profile["permissions"],
        "approvals_required": profile["approvals_required"],
        "progress": _load_progress(str(request.employee_email)),
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/profiles")
def list_profiles() -> dict[str, list[dict[str, Any]]]:
    profiles = []
    for path in sorted(Path(PROFILES_DIR).glob("*.yaml")):
        profile = load_profile(path.stem)
        profiles.append(
            {
                "id": profile["id"],
                "name": profile["name"],
                "summary": profile["summary"],
                "approvals_required": profile["approvals_required"],
            }
        )
    return {"profiles": profiles}


@app.get("/profiles/{profile_id}")
def get_profile(profile_id: str) -> dict[str, Any]:
    try:
        return load_profile(profile_id)
    except (FileNotFoundError, ValueError) as exc:
        _raise_domain_error(exc)
        raise


@app.get("/projects")
def list_projects() -> dict[str, list[dict[str, Any]]]:
    projects = []
    for path in sorted(Path(PROJECTS_DIR).glob("*.yaml")):
        project = load_project(path.stem)
        projects.append(
            {
                "id": project["id"],
                "name": project["name"],
                "business_goal": project["business_goal"],
                "repositories": [repo["name"] for repo in project["repositories"]],
            }
        )
    return {"projects": projects}


@app.get("/projects/{project_id}")
def get_project(project_id: str) -> dict[str, Any]:
    try:
        return load_project(project_id)
    except (FileNotFoundError, ValueError) as exc:
        _raise_domain_error(exc)
        raise


@app.post("/onboarding-plans")
def create_onboarding_plan(request: OnboardingPlanRequest) -> dict[str, Any]:
    try:
        return _build_plan_payload(request)
    except (FileNotFoundError, ValueError) as exc:
        _raise_domain_error(exc)
        raise


@app.post("/agent/onboarding-plans")
def create_agent_onboarding_plan(request: OnboardingPlanRequest) -> dict[str, Any]:
    prompt = _build_agent_prompt(request)
    try:
        plan_payload = _build_plan_payload(request)
        agent = build_strands_agent()
    except SystemExit as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (FileNotFoundError, ValueError) as exc:
        _raise_domain_error(exc)
        raise

    try:
        result = agent(prompt)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Strands agent invocation failed: {exc}") from exc

    return {
        **plan_payload,
        "mode": "strands",
        "agent_response": str(result),
        "plan_markdown_source": "local_tool_result",
    }


@app.post("/progress/steps")
def mark_progress_step(request: ProgressStepRequest) -> dict[str, Any]:
    event = progress_tools.mark_step_done(
        employee_email=str(request.employee_email),
        step_id=request.step_id,
        note=request.note,
    )
    return {
        "employee_email": str(request.employee_email),
        "event": event,
        "progress": _load_progress(str(request.employee_email)),
    }
