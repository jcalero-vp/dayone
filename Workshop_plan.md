Based on the README, I would implement this as a **progressive workshop-to-production path**, not as a big-bang AWS deployment. The repo is intentionally starting as a local, simulated Lab 1 app, then evolving into Strands + Bedrock AgentCore, then backoffice, then real permissions/state. The key constraint is to keep the local Python path working while adding the agent/runtime layers later. 

## Recommended implementation plan

### Phase 0 — Baseline setup and repo validation

Goal: confirm the current MVP runs exactly as the README expects.

Run:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m agent.app \
  --employee "Ada Lovelace" \
  --email ada@example.com \
  --profile backend-dev \
  --project payments-platform

pytest
```

The expected output is a Markdown onboarding plan with repositories, permissions, checklist, and first steps. 

Deliverables:

| Deliverable                      | Purpose                                                   |
| -------------------------------- | --------------------------------------------------------- |
| Working local CLI                | Confirms Lab 1 still works                                |
| Sample generated onboarding plan | Demonstrates current domain model                         |
| Test baseline                    | Ensures future Strands/AWS work does not break local mode |

---

### Phase 1 — Strengthen the declarative domain model

The README’s core design principle is that onboarding should be declarative: employee, profile, and project are enough for the system to derive repos, permissions, tasks, docs, and next steps.

Implement or tighten:

```text
profiles/
  backend-dev.yaml
  data-engineer.yaml
  frontend-dev.yaml
  qa-engineer.yaml

projects/
  payments-platform.yaml
  customer-portal.yaml
  data-lake.yaml
```

For each **profile**, standardize:

```yaml
id:
name:
summary:
permissions:
  aws:
  repositories:
    access:
  ci_cd:
base_checklist:
  day_1:
  week_1:
approvals_required:
```

For each **project**, standardize:

```yaml
id:
name:
business_goal:
architecture_summary:
repositories:
  - name:
    description:
    clone_url:
    bootstrap:
    test:
key_docs:
first_tasks:
risk_notes:
```

Acceptance criteria:

| Check                   | Expected result                                |
| ----------------------- | ---------------------------------------------- |
| Missing profile/project | Clear error with available options             |
| New profile + project   | Generates a valid onboarding plan              |
| YAML schema             | Consistent enough to validate in tests         |
| Sensitive permissions   | Listed as approvals, not automatically granted |

The existing code already loads YAML profile/project files and generates the Markdown plan from them, so this phase is mostly about making the data model reliable and extensible.

---

### Phase 2 — Improve the local MVP before adding Strands

Do this before AWS/AgentCore work.

Recommended enhancements:

1. Add Pydantic models for `Profile`, `Project`, `Repository`, and `PermissionSet`.
2. Add validation errors for malformed YAML.
3. Add tests for:

   * valid profile loading;
   * valid project loading;
   * invalid profile/project IDs;
   * generated Markdown sections;
   * dangerous permissions appearing under approvals only;
   * progress tracking.
4. Improve `generate_onboarding_plan()` so output is stable and easy to snapshot-test.
5. Add `scripts/demo.sh` to run a repeatable workshop demo.

The local app currently calls `load_profile`, `load_project`, and `generate_onboarding_plan` directly through `agent.app.build_plan()`, which is exactly the lightweight path the README wants to preserve.

---

### Phase 3 — Add progress tracking as a first-class MVP feature

The README says the assistant should not only generate plans, but also track progress.

Current progress tracking writes local JSON under `.local-progress/`, which is appropriate for the workshop MVP and can later map to DynamoDB.

Implementation steps:

```text
agent/tools/track_progress.py
  mark_step_done(employee_email, step_id, note)

.local-progress/
  ada_at_example.com.json
```

Add CLI support such as:

```bash
python -m agent.app mark-step \
  --email ada@example.com \
  --step-id clone-repos \
  --note "Completed local clone and bootstrap"
```

Acceptance criteria:

| Check                    | Expected result                                             |
| ------------------------ | ----------------------------------------------------------- |
| Mark step complete       | JSON state file updated                                     |
| Multiple completed steps | Appends events, does not overwrite                          |
| Timestamp                | Uses UTC ISO timestamp                                      |
| Later migration path     | Can be replaced by DynamoDB without changing agent contract |

---

### Phase 4 — Convert local functions into Strands tools

The README’s optional “real agent” path uses the same underlying tool functions, wrapped for Strands.

The repo already sketches this in `agent/strands_agent.py`:

```text
load_profile
load_project
generate_onboarding_plan
mark_step_done
```

Those are wrapped as Strands tools and passed into a Strands `Agent` with the repo’s `SYSTEM_PROMPT`.

Also expose the same onboarding capabilities through a small local API so the
future backoffice UI can call stable HTTP endpoints instead of shelling out to
the CLI. Keep the API thin: it should call the same tool/domain functions used
by the CLI and Strands agent, not duplicate onboarding logic.

Recommended API surface:

```text
GET  /health
GET  /profiles
GET  /profiles/{profile_id}
GET  /projects
GET  /projects/{project_id}
POST /onboarding-plans
POST /agent/onboarding-plans
POST /progress/steps
```

Example request for `POST /onboarding-plans`:

```json
{
  "employee_name": "Ada Lovelace",
  "employee_email": "ada@example.com",
  "profile_id": "backend-dev",
  "project_id": "payments-platform"
}
```

The response should return the generated Markdown plan plus enough structured
metadata for a UI to render repositories, permissions, approvals, and progress
status later.

Implementation steps:

```bash
pip install strands-agents bedrock-agentcore

cp .env.example .env
# set AWS_REGION
# set BEDROCK_MODEL_ID
# confirm Bedrock model access

python -m agent.strands_agent \
  --employee "Ada Lovelace" \
  --email ada@example.com \
  --profile backend-dev \
  --project payments-platform
```

#### API implementation

Expose the same tool functions through a small FastAPI app in `agent/api.py`:

```text
GET  /health
GET  /profiles
GET  /profiles/{profile_id}
GET  /projects
GET  /projects/{project_id}
POST /onboarding-plans
POST /agent/onboarding-plans
POST /progress/steps
```

Run the API locally:

```bash
python -m uvicorn agent.api:app --reload --port 8000
```

Example `POST /onboarding-plans` request:

```json
{
  "employee_name": "Ada Lovelace",
  "employee_email": "ada@example.com",
  "profile_id": "backend-dev",
  "project_id": "payments-platform"
}
```

The response returns the generated Markdown plan plus structured metadata (`profile`, `project`, `repositories`, `permissions`, `approvals_required`, `progress`) for a UI to render. The `/agent/onboarding-plans` endpoint invokes the Strands `Agent` with the same prompt and returns the agent response alongside the local tool output.

Keep the API thin: it should import and call `load_profile`, `load_project`, `build_plan`, and `mark_step_done` instead of duplicating onboarding logic.

Run the API tests:

```bash
pytest tests/test_api.py
```

Acceptance criteria:

| Check                  | Expected result                                                    |
| ---------------------- | ------------------------------------------------------------------ |
| Agent loads profile    | Uses `load_profile` tool                                           |
| Agent loads project    | Uses `load_project` tool                                           |
| Agent generates plan   | Uses `generate_onboarding_plan`                                    |
| Agent records progress | Uses `mark_step_done` only when requested                          |
| API exposes local tools | HTTP endpoints call the same functions used by CLI/Strands         |
| UI-ready plan endpoint | `POST /onboarding-plans` returns generated plan data for a UI       |
| Agent plan endpoint    | `POST /agent/onboarding-plans` invokes Strands + Bedrock           |
| Sensitive actions      | Agent explains or requests approval before write/high-risk actions |

The notes explicitly separate read tools, generation tools, write tools, and dangerous tools; real user creation, production permission grants, reading production secrets, and production deploys should not run automatically in the MVP.

---

### Phase 5 — Package for AgentCore Runtime

After the Strands version works locally, package it for AgentCore Runtime. The README’s roadmap lists this as the AgentCore phase: package runtime, configure observability, invoke per session, and compare local vs. managed behavior. ([GitHub][1])

Amazon describes AgentCore Runtime as a secure, serverless, purpose-built hosting environment for agents and tools.

Implementation steps:

1. Keep this repo as the domain layer.
2. Use the AWS starter/accelerator for infrastructure and deployment.
3. Register the onboarding tools in the starter agent.
4. Configure runtime environment variables.
5. Add CloudWatch/X-Ray observability checks.
6. Test session-based invocation.

I would follow the repo’s **Option C recommendation**: keep the AWS starter for infrastructure, UI, and deployment, and keep this repo for domain exercises, profiles, tools, and workshop documentation.

---

### Phase 6 — Build the minimal backoffice UI

The README says the future backoffice should let a manager select employee, email, profile, and project.

Recommended MVP screen:

```text
Create onboarding plan
----------------------
Employee name:   [              ]
Employee email:  [              ]
Profile:         [backend-dev v]
Project:         [payments-platform v]

[Generate plan]
```

Output:

```text
- Markdown onboarding plan
- Repositories to clone
- Required permissions
- Day 1 checklist
- Week 1 checklist
- Approval-required permissions
- Progress status
```

Start with a simple UI backed by the local/AgentCore invocation. Do not connect Jira, Slack, Confluence, IAM Identity Center, or real production repositories yet unless the MVP has already passed the local + Strands + AgentCore acceptance criteria.

---

### Phase 7 — Replace simulated state and permissions with AWS-native services

The README says DynamoDB, S3, IAM Identity Center, and real repos are future integrations.

Suggested migration:

| Current simulation       | Production replacement                |
| ------------------------ | ------------------------------------- |
| YAML docs in repo        | S3 versioned documentation            |
| `.local-progress/*.json` | DynamoDB onboarding state             |
| Text-based permissions   | IAM Identity Center permission sets   |
| Example clone URLs       | GitHub/CodeCommit repository metadata |
| Manual approval notes    | Human-in-the-loop approval workflow   |

Important rule: real permission grants should be approval-gated. The system may recommend access, but it should not grant sensitive permissions automatically.

---

## Suggested backlog

### Must-have for MVP

| Item                                            | Priority |
| ----------------------------------------------- | -------- |
| Local CLI works                                 | P0       |
| Profile/project YAML validation                 | P0       |
| Markdown onboarding plan generation             | P0       |
| Progress tracking                               | P0       |
| Tests for all local tools                       | P0       |
| New sample profile and project                  | P1       |
| Strands tool wrappers                           | P1       |
| Human-in-the-loop wording for sensitive actions | P1       |

### Should-have before AWS deployment

| Item                               | Priority |
| ---------------------------------- | -------- |
| Stable Pydantic schemas            | P1       |
| Snapshot tests for generated plans | P1       |
| Better error handling              | P1       |
| `.env` validation                  | P1       |
| Observability plan                 | P1       |
| AgentCore packaging runbook        | P1       |

### Later production work

| Item                            | Priority |
| ------------------------------- | -------- |
| Backoffice UI                   | P2       |
| DynamoDB state                  | P2       |
| S3 documentation source         | P2       |
| IAM Identity Center integration | P2/P3    |
| Real repo discovery             | P3       |
| Approval workflow               | P3       |

---

## Practical sequencing

I would implement it in this order:

```text
1. Run existing local app.
2. Add/validate profile and project schemas.
3. Expand sample data.
4. Harden Markdown plan generation.
5. Add local progress tracking to the CLI.
6. Add tests and CI.
7. Run Strands version locally.
8. Add human-in-the-loop behavior for write/sensitive tools.
9. Package with AgentCore Runtime.
10. Integrate with AWS starter using Option C.
11. Add minimal backoffice UI.
12. Replace local JSON with DynamoDB.
13. Replace simulated permissions with IAM Identity Center approval flow.
```

My main recommendation: **treat this repo as the domain and workshop layer, not the production infrastructure repo**. Keep Lab 1 always runnable without Strands, then layer Strands, AgentCore, UI, state, and real permissions incrementally.
