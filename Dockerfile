FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python", "-m", "agent.app", "--employee", "Demo User", "--email", "demo@example.com", "--profile", "backend-dev", "--project", "payments-platform"]
