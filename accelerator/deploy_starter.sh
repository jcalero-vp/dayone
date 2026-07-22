#!/usr/bin/env bash
set -euo pipefail

# Deploy the onboarding assistant to AWS using the AgentCore starter.
# This implements Phase 5 step 2 (infrastructure/deployment) from Workshop_plan.md.
#
# Prerequisites (manual, not automated by this script):
#   - AWS CLI configured (`aws configure` or SSO).
#   - Model access enabled in the Bedrock console for BEDROCK_MODEL_ID.
#   - Docker and Node.js/npm installed.
#   - A .env file with AWS_REGION and BEDROCK_MODEL_ID for the local workshop path.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STARTER_DIR="$REPO_ROOT/.aws-samples/sample-strands-agentcore-starter"
PYTHON="${PYTHON:-python3}"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "ERROR: '$PYTHON' not found. Install python3 or set the PYTHON environment variable." >&2
    exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
    echo "ERROR: npm is not installed. Install Node.js and npm to deploy the CDK stacks." >&2
    exit 1
fi

AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_PROFILE="${AWS_PROFILE:-default}"
BEDROCK_MODEL_ID="${BEDROCK_MODEL_ID:-}"

# The starter's deploy-all.sh uses the AWS SDK credential chain, not the aws binary.
# We do a lightweight sanity check for credentials before invoking CDK.
AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-}"
AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-}"
AWS_CREDS_FOUND=0
if [[ -n "$AWS_ACCESS_KEY_ID" && -n "$AWS_SECRET_ACCESS_KEY" ]]; then
    AWS_CREDS_FOUND=1
elif [[ -n "$AWS_PROFILE" && -f "$HOME/.aws/credentials" ]]; then
    AWS_CREDS_FOUND=1
elif [[ -f "$HOME/.aws/credentials" ]]; then
    AWS_CREDS_FOUND=1
fi

if [[ "$AWS_CREDS_FOUND" -eq 0 ]]; then
    echo "WARNING: No AWS credentials detected. Set AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY or configure ~/.aws/credentials." >&2
fi

if [[ -z "$BEDROCK_MODEL_ID" && ! -f "$REPO_ROOT/.env" ]]; then
    echo "WARNING: BEDROCK_MODEL_ID is not set and $REPO_ROOT/.env does not exist." >&2
    echo "  Copy .env.example to .env and set AWS_REGION and BEDROCK_MODEL_ID." >&2
fi

# 1. Prepare the starter with onboarding domain and tool registration.
"$PYTHON" "$REPO_ROOT/accelerator/prepare_starter.py"

if [[ "${SKIP_DEPLOY:-}" == "true" ]]; then
    echo "SKIP_DEPLOY=true: preparation complete, skipping CDK deployment."
    exit 0
fi

# 2. Deploy the AWS infrastructure.
echo "Deploying with AWS_REGION=$AWS_REGION and AWS_PROFILE=$AWS_PROFILE"
cd "$STARTER_DIR/cdk"
npm install
./deploy-all.sh --region "$AWS_REGION" --profile "$AWS_PROFILE" --ingress furl

# 3. Create a test user for the UI.
cd "$STARTER_DIR/chatapp/scripts"
./create-user.sh "${TEST_EMAIL:-admin@example.com}" "${TEST_PASSWORD:-Workshop123!}" --admin

echo ""
echo "Deployment complete. Run the UI with:"
echo "  cd $STARTER_DIR/chatapp"
echo "  ./sync-env.sh --region ${AWS_REGION:-us-east-1} --dev-mode"
echo "  uvicorn app.main:app --reload --port 8080"
