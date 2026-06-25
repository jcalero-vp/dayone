#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR=".aws-samples"
REPO_URL="https://github.com/aws-samples/sample-strands-agentcore-starter.git"

mkdir -p "$TARGET_DIR"

if [ -d "$TARGET_DIR/sample-strands-agentcore-starter/.git" ]; then
  echo "Starter already cloned. Pulling latest changes..."
  git -C "$TARGET_DIR/sample-strands-agentcore-starter" pull --ff-only
else
  echo "Cloning AWS starter into $TARGET_DIR..."
  git clone "$REPO_URL" "$TARGET_DIR/sample-strands-agentcore-starter"
fi

echo "Done. Read accelerator/INTEGRATION_PLAN.md for next steps."
