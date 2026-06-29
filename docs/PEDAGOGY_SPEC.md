# Pedagogy spec — onboarding-assistant workshop

> **This document owns:** how the workshop teaches (sequencing, checkpoints, timing, assessment).
> **It does not own:** what the assistant itself does as a product — see [`PRODUCT_SPEC.md`](PRODUCT_SPEC.md).
> Lab-by-lab commands and code pointers stay in [`WORKSHOP_LABS.md`](WORKSHOP_LABS.md); this document
> adds the instructional-design layer on top (why each lab exists, how we know it worked).

## Learning objective → lab → checkpoint map

Each of the 8 objectives in [`../WORKSHOP_OBJECTIVES.md`](../WORKSHOP_OBJECTIVES.md) maps to one concrete,
gradable checkpoint — not just "covered," but "verifiably passed."

| # | Objective | Lab / module | Checkpoint (pass/fail) |
|---|-----------|--------------|------------------------|
| LO1 | Explain what AgentCore solves | Lab 3 kickoff discussion | Participant names 3 AgentCore primitives used by the starter (Memory, Knowledge Base, Guardrails) and states what breaks if each is removed |
| LO2 | Build a basic Strands agent | Lab 2 | `python -m agent.strands_agent ...` runs end to end; participant points to where `Agent`, `tool`, and `model` are wired in `agent/strands_agent.py` |
| LO3 | Design tools linking reasoning to actions | Lab 2 exercise 1 (`mark_step_done`) + M2 RAG-tool exercise | Participant adds a new `@tool` and the agent calls it correctly, unprompted, in ≥1 of 2 sample conversations |
| LO4 | Model internal knowledge as versioned files | Lab 1 exercise 1 (new profile/project YAML) | A new profile + project combination produces a valid, complete plan |
| LO5 | Local simulation → real AWS | Lab 1 → Lab 2 → Lab 3 progression | Participant states, per layer (orchestration/tools/data/permissions/state), what's simulated today vs. real in Lab 3 — using the comparison table in `WORKSHOP_LABS.md` |
| LO6 | Design a backoffice (employee/profile/project) | Dedicated design exercise, before Lab 3 | Participant produces a 1-page sketch of the employee/profile/project relationship and marks which parts live in HR systems vs. this repo |
| LO7 | Automatic vs. human-approval actions | Lab 2 exercise 2 + HITL exercise (M4) | Participant classifies 6 sample actions (read profile, generate plan, mark step done, request prod access, request repo write, delete a resource) into automatic vs. needs-approval and defends the boundary |
| LO8 | Prepare an end-to-end demo | Capstone | Participant runs Lab 1 then Lab 2 live for a stakeholder and narrates the contrast between the two |

## "When NOT to use an agent" exercise (operationalizing the deterministic-core lesson)

The repo's centerpiece (`agent/tools/generate_plan.py`) is deterministic templating — it does not need
AI. That contrast is the lesson, not a caveat. Concrete exercise:

1. Time the Lab 1 generator and the Lab 2 agent against the **identical** input (same employee/profile/project).
2. Record: latency, cost (tokens vs. $0), and whether output is byte-identical across 2 runs.
3. Answer in writing: *"For which of these two layers would you accept a 2% wrong-answer rate? Why is
   that answer different for plan generation than for a Q&A tool over docs?"*

This produces a graded artifact, not a paragraph the participant skims.

## Timing per module

| Module | Duration |
|--------|----------|
| Lab 1 (local) | 30 min |
| Lab 2 (Strands agent) + M2 RAG-tool build | 60 min |
| Backoffice design exercise | 20 min |
| Lab 3 (AWS accelerator) + M4 HITL/approval-state exercise | 60–90 min (infra-heavy) |
| Capstone demo | 30 min |
| **Total** | **~3.5–4 hours** |

**Note on M2/M4:** these wire up tools that `PRODUCT_SPEC.md`'s MVP cut line marks "not yet built" —
they are net-new build exercises, not pre-existing labs in `WORKSHOP_LABS.md`. To fit the timing above,
the facilitator pre-provisions the Knowledge Base and approval-state data structure before the session;
participants extend the agent with a tool against that pre-provisioned infra, they do not stand up
Bedrock KB ingestion or CDK approval-state infra live in the window.

## Prerequisites per lab

| Lab | Prerequisites |
|-----|---------------|
| Lab 1 | Python 3.11+ (reference implementation); no AWS account required |
| Lab 2 | AWS account with Bedrock model access enabled; IAM permission to invoke Bedrock; `.env` configured |
| Lab 3 | AWS account with CDK bootstrap permissions; Node.js for CDK; Docker (CodeBuild/ECR steps); IAM permissions to deploy 4 CDK stacks |

**Python is not a hard prerequisite of the learning objectives.** The 8 LOs (tool-calling, deterministic
vs. agentic design, memory, HITL approval, etc.) are language-agnostic — Python is this repo's reference
implementation, not a constraint of the workshop. A participant fluent in another language with an AWS
SDK and an LLM client can reimplement the tools and meet every checkpoint above in that language; only
Lab 3's CDK infra is tied to Node.js/TypeScript by the tooling choice, not by a learning requirement.

## Participant self-check per lab

- **Lab 1:** `pytest` passes **and** I can explain what `generate_plan.py` does *not* use AI for.
- **Lab 2:** the agent picks the right tool without me naming it, in 2 of 2 sample prompts.
- **Lab 3:** I can point to which CDK stack provisions Memory, which provisions Guardrails, and which provisions the Knowledge Base.

## Anti-objectives — intentionally NOT taught, and why

| Not taught | Why |
|------------|-----|
| Production-grade evaluation design beyond the starter's built-in Faithfulness check | Too deep for a single workshop; the built-in check is sufficient to teach the *concept* of measurable grounding |
| Enterprise guardrail policy authoring | Out of scope per `WORKSHOP_OBJECTIVES.md` ("complete enterprise guardrails") |
| Real IAM/GitHub/Jira provisioning | Security risk in a shared workshop sandbox; simulated permissions are intentional, not a shortcut |
| Cost/latency optimization of the agent | Orthogonal to the agentic-*design* learning goal; would dilute the core lesson |

## Workshop success criterion

Unchanged from `WORKSHOP_OBJECTIVES.md`: the team can explain, modify, and extend the onboarding flow
without depending on a single expert, and can articulate the path to an AWS-native production solution.
