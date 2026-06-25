# Backoffice placeholder

This folder is reserved for the future backoffice implementation.

Recommended options for the MVP:

1. FastAPI + htmx, aligned with the AWS starter.
2. Amplify Hosting + API Gateway + Lambda.
3. App Runner for a simple containerized app.

Minimal form:

- Name.
- Email.
- Profile.
- Project.

The backend must invoke the agent and save state in DynamoDB in later phases.
