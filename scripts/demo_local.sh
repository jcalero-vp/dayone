#!/usr/bin/env bash
set -euo pipefail

python -m agent.app \
  --employee "Ada Lovelace" \
  --email "ada.lovelace@example.com" \
  --profile "backend-dev" \
  --project "payments-platform"
