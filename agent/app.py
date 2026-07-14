from __future__ import annotations

import argparse
import json
import sys

from agent.prompts import SYSTEM_PROMPT
from agent.tools.generate_plan import generate_onboarding_plan
from agent.tools.load_profile import load_profile
from agent.tools.load_project import load_project
from agent.tools.track_progress import mark_step_done


def build_plan(employee: str, email: str, profile_id: str, project_id: str) -> str:
    """Build an onboarding plan using local declarative inputs.

    This function is deliberately framework-light so the workshop can run even
    before installing Strands Agents. When integrating with Strands, expose these
    functions as tools and use SYSTEM_PROMPT as the agent system prompt.
    """
    profile = load_profile(profile_id)
    project = load_project(project_id)
    return generate_onboarding_plan(employee, email, profile, project)


def _generate_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a developer onboarding plan.")
    parser.add_argument("--employee", required=True, help="Employee full name")
    parser.add_argument("--email", required=True, help="Employee email")
    parser.add_argument("--profile", required=True, help="Profile id, e.g. backend-dev")
    parser.add_argument("--project", required=True, help="Project id, e.g. payments-platform")
    parser.add_argument("--show-system-prompt", action="store_true")
    return parser


def _mark_step_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m agent.app mark-step",
        description="Mark an onboarding step as complete.",
    )
    parser.add_argument("--email", required=True, help="Employee email")
    parser.add_argument("--step-id", required=True, help="Step identifier")
    parser.add_argument("--note", default="", help="Optional note")
    return parser


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "mark-step":
        args = _mark_step_parser().parse_args(sys.argv[2:])
        event = mark_step_done(args.email, args.step_id, args.note)
        print(json.dumps(event, indent=2))
        return

    args = _generate_parser().parse_args()

    if args.show_system_prompt:
        print("# System prompt\n")
        print(SYSTEM_PROMPT)
        print("\n---\n")

    try:
        print(build_plan(args.employee, args.email, args.profile, args.project))
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
