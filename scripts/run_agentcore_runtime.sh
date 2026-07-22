#!/usr/bin/env bash
set -euo pipefail

# Build and run the onboarding API as a long-running AgentCore Runtime container.
# In production this image would be pushed to Amazon ECR and consumed by
# AgentCore Runtime / ECS / Lambda Web Adapter instead of running locally.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE_NAME="onboarding-agentcore:latest"
PORT="${AGENTCORE_PORT:-8080}"

cd "$REPO_ROOT"

echo "Building AgentCore Runtime image..."
docker build -t "$IMAGE_NAME" .

echo "Running container on http://localhost:${PORT} ..."
exec docker run --rm \
  -p "${PORT}:8080" \
  -e AWS_REGION \
  -e BEDROCK_MODEL_ID \
  "$IMAGE_NAME"
