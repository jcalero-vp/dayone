---
description: Main workflow for each phase implementation
---

# Phase Implementation Workflow

Use this workflow for every phase of the project.

## Core Rules

1. Always create a new git branch for each phase implementation.
2. Always perform a code review before any commit.
3. Always ask the user for permission before committing changes.

## Steps

1. Confirm the phase name and scope with the user.
2. Create a new branch from the agreed base branch (e.g. `git checkout -b phase/<name>`).
3. Implement the changes for that phase.
4. Review the diff against the existing codebase and the phase requirements.
5. Present the changes to the user and ask for approval to commit.
6. Only commit after the user explicitly says to commit.
7. Push or open a pull request only if the user requests it.
