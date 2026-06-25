# Backoffice - initial specification

## Goal

Create an internal interface to start a technical onboarding without running scattered manual steps.

## Primary user

- Manager.
- Tech lead.
- Engineering enablement.
- People/IT admin.

## Minimal form

Required fields:

- `employee_name`
- `employee_email`
- `profile_id`
- `project_ids`

Optional fields:

- `start_date`
- `buddy_email`
- `seniority`
- `location`
- `notes`

## "Create onboarding" button actions

1. Validate profile.
2. Validate project.
3. Generate plan.
4. Create state record.
5. Calculate expected permissions.
6. Create day 1 tasks.
7. Flag required approvals.
8. Send link to the new employee.

## Detail view

Must show:

- Generated plan.
- Repositories.
- Requested permissions.
- Approved permissions.
- Checklist.
- Progress.
- Risks.
- Action logs.

## Onboarding states

- `draft`
- `pending_approval`
- `ready_for_day_1`
- `in_progress`
- `blocked`
- `completed`

## Security rules

- The backoffice must not grant sensitive production access without approval.
- Every action must be audited.
- The employee should only see authorized information.
- Permission templates must be versioned and reviewed by security/platform.
