# Payments Platform - Runbook inicial

## Primeras verificaciones

- Revisar métricas de errores 5xx.
- Revisar latencia p95 de `payments-api`.
- Revisar cola de eventos pendientes.
- Revisar logs del worker.

## Restricciones para nuevos desarrolladores

Durante onboarding, el desarrollador debe tener acceso de lectura a producción y escritura solo en staging.
