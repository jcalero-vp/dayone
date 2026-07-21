"""OPTIONAL — Strands Agents implementation of the onboarding assistant.

This file is the goal of **Lab 2** of the workshop. The default path
(`agent/app.py`) runs WITHOUT the Strands SDK by calling `build_plan()` directly.
Here, instead, a **Strands agent reasons** and decides when to invoke each tool.

Requirements to run it (not needed for the local path in `agent/app.py`):

    # 1) Install the SDK (or uncomment the lines in requirements.txt)
    pip install strands-agents bedrock-agentcore

    # 2) Configure AWS credentials + Bedrock model access
    cp .env.example .env        # set AWS_REGION and BEDROCK_MODEL_ID

    # 3) Run the real agent
    python -m agent.strands_agent \\
        --employee "Ada Lovelace" --email ada@example.com \\
        --profile backend-dev --project payments-platform

The tools wrapped here are EXACTLY the same local functions used by
`agent/app.py`. The difference is who orchestrates them: before it was us, now it's the agent.
"""
from __future__ import annotations

import argparse
import json
import os
from typing import Any, Optional

from bedrock_agentcore import BedrockAgentCoreApp

try:
    from .config import load_runtime_config
    from .prompts import SYSTEM_PROMPT
    from .tools.load_profile import load_profile as _load_profile
    from .tools.load_project import load_project as _load_project
    from .tools.generate_plan import generate_onboarding_plan as _generate_onboarding_plan
    from .tools.track_progress import mark_step_done as _mark_step_done
except ImportError:  # pragma: no cover - allows running the file directly
    from config import load_runtime_config
    from prompts import SYSTEM_PROMPT
    from tools.load_profile import load_profile as _load_profile
    from tools.load_project import load_project as _load_project
    from tools.generate_plan import generate_onboarding_plan as _generate_onboarding_plan
    from tools.track_progress import mark_step_done as _mark_step_done

try:
    from strands import Agent, tool
    from strands.models import BedrockModel
except ImportError as exc:  # pragma: no cover - only triggers without the SDK installed
    raise SystemExit(
        "\n[onboard-assistant] The Strands SDK is not installed.\n"
        "This is the 'real agent' path of the workshop (Lab 2).\n"
        "  1) Install the dependencies from requirements.txt.\n"
        "  2) Configure AWS credentials and Bedrock model access in .env.\n"
        "  3) For the LOCAL path without the SDK use: python -m agent.app ...\n"
        f"  (import detail: {exc})\n"
    )


# --- Read tools --------------------------------------------------------------
@tool
def load_profile(profile_id: str) -> dict:
    """Load a declarative onboarding profile from profiles/<id>.yaml.

    Returns expected permissions, base checklist and required approvals.
    """
    return _load_profile(profile_id)


@tool
def load_project(project_id: str) -> dict:
    """Load a declarative project from projects/<id>.yaml.

    Returns repositories, architecture, first tasks and risk notes.
    """
    return _load_project(project_id)


# --- Generation tool ----------------------------------------------------------
@tool
def generate_onboarding_plan(
    employee_name: str,
    employee_email: str,
    profile: dict,
    project: dict,
) -> str:
    """Generate the onboarding plan in Markdown from a profile and a project.

    `profile` and `project` are the dicts returned by load_profile and load_project.
    """
    return _generate_onboarding_plan(employee_name, employee_email, profile, project)


# --- Write tool ----------------------------------------------------------------
@tool
def mark_step_done(employee_email: str, step_id: str, note: str = "") -> dict:
    """Record a completed onboarding step (local MVP state).

    In production this is replaced by a write to DynamoDB.
    """
    return _mark_step_done(employee_email, step_id, note)


app = BedrockAgentCoreApp()


def build_agent() -> Agent:
    """Build the Strands agent with a Bedrock model + onboarding tools."""
    config = load_runtime_config()
    model = BedrockModel(
        model_id=config["BEDROCK_MODEL_ID"],
        region_name=config["AWS_REGION"],
    )
    return Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[
            load_profile,
            load_project,
            generate_onboarding_plan,
            mark_step_done,
        ],
    )


def build_request_payload(
    employee_name: str,
    employee_email: str,
    profile_id: str,
    project_id: str,
) -> dict[str, Any]:
    """Create a structured payload for runtime use."""
    return {
        "employee_name": employee_name,
        "employee_email": employee_email,
        "profile_id": profile_id,
        "project_id": project_id,
    }


def build_initial_prompt(payload: dict[str, Any]) -> str:
    """Create the standard onboarding prompt from a structured payload."""
    return (
        f"Generate the onboarding plan for employee '{payload['employee_name']}' "
        f"(email {payload['employee_email']}) with profile '{payload['profile_id']}' on project "
        f"'{payload['project_id']}'. Use the load_profile and load_project tools to get "
        f"the data and then generate_onboarding_plan to produce the plan in Markdown."
    )


def process_payload(payload: dict[str, Any], agent: Optional[Agent] = None) -> str:
    """Handle a structured runtime payload and return the agent response."""
    if agent is None:
        agent = build_agent()
    return str(agent(build_initial_prompt(payload)))


def handle_runtime_request(payload: dict[str, Any], agent: Optional[Agent] = None) -> dict[str, Any]:
    """Return a structured response object for a runtime host."""
    response_text = process_payload(payload, agent=agent)
    return {
        "status": "ok",
        "payload": payload,
        "response": response_text,
    }


@app.entrypoint
def handler(payload: dict[str, Any], context: Any) -> dict[str, Any]:
    """Main AgentCore entrypoint for onboarding requests."""
    agent = build_agent()
    return handle_runtime_request(payload, agent=agent)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate an onboarding plan using a real Strands agent."
    )
    parser.add_argument("--employee", required=True, help="Employee full name")
    parser.add_argument("--email", required=True, help="Employee email")
    parser.add_argument("--profile", required=True, help="Profile id, e.g. backend-dev")
    parser.add_argument("--project", required=True, help="Project id, e.g. payments-platform")
    args = parser.parse_args()

    agent = build_agent()
    request_payload = build_request_payload(
        employee_name=args.employee,
        employee_email=args.email,
        profile_id=args.profile,
        project_id=args.project,
    )
    result = handle_runtime_request(request_payload, agent=agent)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
