# AWS accelerator integration plan

## Recommended accelerator

Use as reference `aws-samples/sample-strands-agentcore-starter`, a full-stack starter for agent prototyping with Amazon Bedrock AgentCore, the Strands Agents SDK, FastAPI and htmx.

## Possible strategies

### Option A: use this repo as the domain layer

Keep this repo for the workshop and copy its concepts into the starter:

- `profiles/`
- `projects/`
- `agent/prompts.py`
- `agent/tools/`

Advantage: clear learning, low coupling.

### Option B: migrate this repo into the starter

Clone the starter and replace/adapt its agent with the onboarding domain.

Advantage: faster to get a UI, telemetry and full-stack structure.

### Option C: keep both repos (RECOMMENDED for the workshop)

- AWS starter: infrastructure, UI and deployment.
- This repo: exercises, profiles, domain and workshop documentation.

Advantage: ideal for training the team. Low risk of breaking the local path (Lab 1), the domain
stays versioned and explainable, and the infra evolves separately. Choose A if you want a single
lightweight domain repo; choose B only if having a full-stack UI as soon as possible is the priority.

## Prerequisites

Before touching the accelerator it helps to have:

- An AWS account with permissions for Amazon Bedrock (and AgentCore in later phases).
- **Model access enabled** in the Bedrock console → *Model access*, for the `BEDROCK_MODEL_ID`
  you use (see `.env.example`).
- AWS CLI configured (`aws configure` or SSO) and a defined region (`AWS_REGION`).
- Python 3.11+, `git` and the Strands SDK installed (Lab 2 complete: `agent/strands_agent.py` runs).
- Docker available (the starter packages the agent in a container for AgentCore Runtime).

## Starter's real structure (verified)

Paths confirmed against `aws-samples/sample-strands-agentcore-starter` (cloned into `.aws-samples/`).
If the starter changes, reconfirm with:
`grep -rn "Agent(" .aws-samples/sample-strands-agentcore-starter/agent --include="*.py"`.

- `agent/my_agent.py` — defines the agent: `app = BedrockAgentCoreApp()` and
  `agent = Agent(model=..., system_prompt=..., tools=tools, ...)`. **Tools are registered here.**
- `agent/tools/` — the starter's example tools (`knowledge_base.py`, `web_search.py`,
  `url_fetcher.py`, `weather.py`).
- `cdk/` — infrastructure as code (CDK): `deploy-all.sh`, `bin/`, `lib/`. Creates Cognito,
  DynamoDB, Bedrock Guardrail, Knowledge Base, AgentCore Memory and AgentCore Runtime.
- `chatapp/` — web UI (FastAPI, run with `uvicorn app.main:app`).

## Runbook (Option C — concrete commands)

All commands assume you're standing in the starter's root:
`cd .aws-samples/sample-strands-agentcore-starter`.

1. Clone the starter (idempotent; lands in `.aws-samples/`, already gitignored):
   ```bash
   bash accelerator/clone_aws_starter.sh
   ```
2. Install infra dependencies and deploy the stacks (creates Runtime, Memory, KB, Cognito, DynamoDB):
   ```bash
   cd cdk && npm install
   ./deploy-all.sh --region us-east-1 --profile <your-profile> --ingress furl
   cd ..
   ```
3. Bring the onboarding domain into the starter's `agent/` (without coupling repos): copy from THIS
   repo `agent/tools/*.py`, `agent/prompts.py`, `profiles/` and `projects/` into the starter's `agent/`.
4. Register our tools in `agent/my_agent.py`: import the onboarding `@tool`s (the same ones from
   `agent/strands_agent.py`: `load_profile`, `load_project`, `generate_onboarding_plan`,
   `mark_step_done`), add them to the `tools` list passed to `Agent(...)`, and use our `SYSTEM_PROMPT`
   (from `agent/prompts.py`) as `system_prompt`.
5. Create a test user for the UI:
   ```bash
   cd chatapp/scripts
   ./create-user.sh your-email@example.com 'YourPassword123@' --admin
   cd ../..
   ```
6. Test the UI locally (requires the stacks already deployed; `sync-env` pulls config from Secrets Manager):
   ```bash
   cd chatapp
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ./sync-env.sh --region us-east-1 --dev-mode     # --dev-mode bypasses Cognito
   uvicorn app.main:app --reload --port 8080       # http://localhost:8080
   ```
7. Observability: the agent already emits traces/logs (see the starter's `agent/OBSERVABILITY.md`) →
   check CloudWatch / X-Ray and the analytics stacks in DynamoDB.

## Criterion to move forward

Do not migrate to the starter until the local agent in this repo can:

- Load a profile.
- Load a project.
- Generate a plan.
- Record at least one completed step.
