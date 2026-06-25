# Backoffice - especificación inicial

## Objetivo

Crear una interfaz interna para iniciar un onboarding técnico sin ejecutar pasos manuales dispersos.

## Usuario principal

- Manager.
- Tech lead.
- Engineering enablement.
- People/IT admin.

## Formulario mínimo

Campos requeridos:

- `employee_name`
- `employee_email`
- `profile_id`
- `project_ids`

Campos opcionales:

- `start_date`
- `buddy_email`
- `seniority`
- `location`
- `notes`

## Acciones del botón "Crear onboarding"

1. Validar perfil.
2. Validar proyecto.
3. Generar plan.
4. Crear registro de estado.
5. Calcular permisos esperados.
6. Crear tareas día 1.
7. Marcar aprobaciones requeridas.
8. Enviar link al nuevo empleado.

## Vista de detalle

Debe mostrar:

- Plan generado.
- Repositorios.
- Permisos solicitados.
- Permisos aprobados.
- Checklist.
- Progreso.
- Riesgos.
- Logs de acciones.

## Estados del onboarding

- `draft`
- `pending_approval`
- `ready_for_day_1`
- `in_progress`
- `blocked`
- `completed`

## Reglas de seguridad

- El backoffice no debe otorgar acceso productivo sensible sin aprobación.
- Toda acción debe quedar auditada.
- El empleado solo debe ver información autorizada.
- Las plantillas de permisos deben versionarse y revisarse por security/platform.
