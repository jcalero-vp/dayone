#!/usr/bin/env bash
set -euo pipefail

# Generate a stable onboarding plan for snapshot testing and workshop demos.
# Writes the output to generated/onboarding-plan.md.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUTPUT_DIR="$REPO_ROOT/generated"
OUTPUT_FILE="$OUTPUT_DIR/onboarding-plan.md"

mkdir -p "$OUTPUT_DIR"

cd "$REPO_ROOT"
python -m agent.app \
  --employee "Ada Lovelace" \
  --email "ada@example.com" \
  --profile "backend-dev" \
  --project "payments-platform" \
  > "$OUTPUT_FILE"

echo "Onboarding plan generated at $OUTPUT_FILE"
