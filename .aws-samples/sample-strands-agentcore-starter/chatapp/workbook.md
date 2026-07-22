# HTMX ChatApp Workbook

This workbook documents how to run the `chatapp` locally against the `htmx_onboardingapp` AWS stack.

## 1. Prerequisites

- Python 3.11+ installed on Windows
- AWS CLI configured with a valid profile (e.g. `default`) in `us-east-1`
- The CDK stacks (Foundation + Agent) have been deployed
- Active virtual environment at `.venv/`

## 2. Generate the `.env` file

The app needs AWS resource IDs (Cognito, AgentCore Runtime ARN, Memory ID, DynamoDB tables, etc.). These are stored in AWS Secrets Manager.

```powershell
cd .aws-samples\sample-strands-agentcore-starter\chatapp

$env:APP_NAME = 'htmx-onboardingapp'
.venv\Scripts\python.exe sync-env.py --region us-east-1 --profile default --dev-mode
```

This writes `.env` with values from the secret `htmx-onboardingapp/appconfig` and enables `DEV_MODE` so Cognito authentication is bypassed.

## 3. Start the server

Activate the virtual environment and start Uvicorn:

```powershell
.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8080
```

Then open `http://localhost:8080` in your browser.

## 4. Verify it is using the right AgentCore runtime

Check the generated `.env`:

```powershell
Select-String -Path .env -Pattern '^AGENTCORE_RUNTIME_ARN='
```

It should contain the ARN for `htmx_onboardingapp`, e.g.:

```text
arn:aws:bedrock-agentcore:us-east-1:<account>:runtime/htmx_onboardingapp-<suffix>
```

You can also confirm the runtime exists and is `READY`:

```powershell
aws bedrock-agentcore-control list-agent-runtimes --region us-east-1 --profile default --output json
```

## 5. Test the chat endpoint

```powershell
.venv\Scripts\python.exe -c "
import uuid
from fastapi.testclient import TestClient
from app.main import app
with TestClient(app) as c:
    r = c.post('/api/chat', json={'prompt':'hi','session_id': str(uuid.uuid4())})
    print(r.status_code)
    print(next(r.iter_text()))
"
```

A successful call returns `200` and an SSE stream.

## 6. Troubleshooting

### Port 8080 already in use

Find the process:

```powershell
netstat -ano | findstr :8080
```

Kill it:

```powershell
taskkill /PID <PID> /F
```

### AWS token expired

Refresh credentials, then re-run `sync-env.py`.

### `ModuleNotFoundError: No module named 'jose'`

This only affects Cognito auth. In `DEV_MODE` the import is optional. If you want to test real auth, install:

```powershell
.venv\Scripts\python.exe -m pip install 'python-jose[cryptography]'
```

## 7. Stop the server

Press `Ctrl+C` in the terminal running `uvicorn`.
