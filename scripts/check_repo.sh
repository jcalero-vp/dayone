#!/usr/bin/env bash
set -euo pipefail

python -m agent.app --employee "Smoke Test" --email smoke@example.com --profile backend-dev --project payments-platform >/tmp/onboarding-plan.md
pytest

echo "Repo check OK"
