# Payments Platform - Architecture

The payments platform is composed of three main repositories:

- `payments-api`: synchronous API for payment operations.
- `payments-worker`: asynchronous processing, retries and reconciliation.
- `payments-infra`: infrastructure as code.

## System goal

Process payments securely, traceably and auditably, separating synchronous operations from asynchronous processing.

## Simplified flow

1. A client invokes `payments-api`.
2. The API validates the operation.
3. The API publishes an event.
4. `payments-worker` processes the event.
5. Results become available for lookup and reconciliation.
