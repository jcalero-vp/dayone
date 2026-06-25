# Payments Platform - Arquitectura

La plataforma de pagos está compuesta por tres repositorios principales:

- `payments-api`: API síncrona para operaciones de pago.
- `payments-worker`: procesamiento asíncrono, reintentos y conciliación.
- `payments-infra`: infraestructura como código.

## Objetivo del sistema

Procesar pagos de forma segura, trazable y auditable, separando operaciones síncronas de procesamiento asíncrono.

## Flujo simplificado

1. Un cliente invoca `payments-api`.
2. La API valida la operación.
3. La API publica un evento.
4. `payments-worker` procesa el evento.
5. Los resultados quedan disponibles para consulta y conciliación.
