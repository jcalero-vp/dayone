# Workshop objectives

## Purpose

Build an MVP of a technical onboarding assistant using AWS, Amazon Bedrock, Amazon Bedrock AgentCore and Strands Agents. The business case is reducing the time it takes for a new developer to become productive from day 1.

## Learning objectives

By the end of the workshop, the team should be able to:

1. Explain what problem Amazon Bedrock AgentCore solves in an agentic architecture.
2. Build a basic agent with Strands Agents.
3. Design tools that connect the agent's reasoning to concrete actions.
4. Model internal knowledge as versioned files, avoiding early dependence on external SaaS like Confluence.
5. Understand how to go from local simulation to real AWS integration.
6. Design a backoffice to parametrize onboarding by employee, profile and project.
7. Identify which actions should be automatic and which require human approval.
8. Prepare an end-to-end technical onboarding demo.

## Technical objectives

- Run a local Strands agent.
- Define onboarding profiles in YAML.
- Define projects in YAML.
- Generate personalized onboarding plans.
- Prepare future integration with AgentCore Runtime.
- Prepare an integration path with the AWS accelerator `sample-strands-agentcore-starter`.

## Expected outcome

A demo where the user enters:

- Employee name.
- Email.
- Profile, e.g. `backend-dev`.
- Project, e.g. `payments-platform`.

And the agent returns:

- Repositories to clone.
- Expected permissions.
- Day 1 checklist.
- Architecture explanation.
- Suggested first tasks.
- Risks or pending approvals.

## What's not implemented yet

To keep the MVP simple, real permissions and external SaaS integrations are not automated initially.

Out of scope for the first iteration:

- Real provisioning in IAM Identity Center.
- Real provisioning in GitHub, GitLab or CodeCommit.
- Real integration with Jira, Slack, Teams or Confluence.
- Production-grade backoffice.
- Advanced secrets management.
- Complete enterprise guardrails.

## Success criterion

The workshop is successful if the team can explain, modify and extend the onboarding flow without depending on a single expert, and if it's clear how to evolve the MVP toward an AWS-native production solution.
