# AgentCore + Strands notes

## What to research during the workshop

- How to package the agent for AgentCore Runtime.
- How to expose runtime-compatible endpoints.
- How to enable observability in CloudWatch.
- How to handle conversation sessions.
- How to separate read tools, write tools and approval tools.

## Recommended path

1. Run locally without Strands to understand the domain.
2. Install the Strands Agents SDK.
3. Convert `load_profile`, `load_project`, `generate_onboarding_plan` and `mark_step_done` into Strands tools.
4. Run the agent locally with Strands.
5. Package with the AgentCore Starter Toolkit.
6. Deploy to AgentCore Runtime.
7. Measure traces, logs and errors.

## Conceptual tool contract

### Read tools

- `load_profile(profile_id)`
- `load_project(project_id)`
- `search_internal_docs(query)` (future)

### Generation tools

- `generate_onboarding_plan(employee, email, profile, project)`

### Write tools

- `mark_step_done(employee_email, step_id, note)`
- `request_permission_approval(employee_email, permission_set)` (future)

### Dangerous tools

These must not run automatically in the MVP:

- Create a real user.
- Grant production permissions.
- Read production secrets.
- Deploy to production.

## Concrete example: wrapping a function as a tool

Each function in `agent/tools/` becomes a Strands tool with the `@tool` decorator. The docstring is
what the model reads to decide when to use it, so write it clearly:

```python
from strands import Agent, tool
from strands.models import BedrockModel

from agent.prompts import SYSTEM_PROMPT
from agent.tools.load_profile import load_profile as _load_profile

@tool
def load_profile(profile_id: str) -> dict:
    """Load a declarative onboarding profile from profiles/<id>.yaml."""
    return _load_profile(profile_id)

# ... same for load_project, generate_onboarding_plan, mark_step_done ...

agent = Agent(
    model=BedrockModel(model_id="anthropic.claude-3-5-sonnet-20241022-v2:0", region_name="us-east-1"),
    system_prompt=SYSTEM_PROMPT,
    tools=[load_profile, load_project, generate_onboarding_plan, mark_step_done],
)
print(agent("Generate the onboarding plan for Ada with backend-dev profile on payments-platform"))
```

The full, runnable implementation lives in `agent/strands_agent.py`. To run it:

```bash
pip install strands-agents bedrock-agentcore     # or uncomment in requirements.txt
cp .env.example .env                             # AWS_REGION + BEDROCK_MODEL_ID
python -m agent.strands_agent --employee "Ada Lovelace" --email ada@example.com \
  --profile backend-dev --project payments-platform
```

## Note

The current code runs without installing Strands so the workshop can start quickly. The real integration with Strands should be done as a guided exercise.
