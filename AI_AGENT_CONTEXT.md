# Contexto para agentes de IA

Este archivo está pensado para ser leído por agentes de IA, asistentes de coding o herramientas de generación de código antes de modificar este repositorio.

## Contexto del proyecto

Estamos construyendo un MVP de asistente agéntico de onboarding para desarrolladores. El objetivo final es que un nuevo desarrollador sea productivo desde el día 1.

El equipo quiere aprender y usar:

- AWS.
- Amazon Bedrock.
- Amazon Bedrock AgentCore.
- Strands Agents.
- Patrones de agentes con tools.
- Arquitecturas AWS-native con baja dependencia inicial de SaaS externos.

## Restricciones importantes

1. Priorizar soluciones AWS-native.
2. No asumir integraciones reales con Confluence, Jira, Slack o GitHub en el MVP inicial.
3. Modelar permisos, proyectos y perfiles como YAML versionado.
4. Diseñar para que luego pueda existir un backoffice donde se ingrese empleado + perfil + proyecto.
5. Mantener el código simple para fines de workshop.
6. Evitar automatizar permisos reales sin aprobación explícita.
7. Todo cambio debe preservar la capacidad de ejecutar el agente localmente.

## Dominio funcional

El flujo esperado es:

1. Un manager o admin selecciona un empleado.
2. Selecciona un perfil, por ejemplo `backend-dev`.
3. Selecciona un proyecto, por ejemplo `payments-platform`.
4. El agente carga el perfil y proyecto.
5. El agente genera un plan de onboarding personalizado.
6. El agente puede registrar progreso.

## Archivos relevantes

- `profiles/*.yaml`: define perfiles, permisos esperados y tareas base.
- `projects/*.yaml`: define proyectos, repositorios, arquitectura y tareas específicas.
- `agent/app.py`: entrada principal del agente.
- `agent/tools/*.py`: herramientas invocables por el agente.
- `docs/ARCHITECTURE.md`: arquitectura objetivo.
- `accelerator/INTEGRATION_PLAN.md`: cómo usar el sample AWS.

## Estilo de implementación

- Python simple.
- Funciones pequeñas.
- Tools explícitas.
- YAML legible.
- Markdown para documentación.
- Tests mínimos pero útiles.

## Próximas evoluciones esperadas

- Conectar con AgentCore Runtime.
- Agregar DynamoDB para tracking real.
- Agregar S3 como knowledge source.
- Agregar IAM Identity Center para permisos reales.
- Agregar backoffice con Amplify, App Runner o FastAPI.
- Agregar guardrails y observabilidad.

## Instrucción para agentes de IA

Cuando modifiques este repo, no lo conviertas en una solución compleja de producción prematuramente. Primero debe funcionar como material de aprendizaje y workshop. Prefiere cambios pequeños, explicables y orientados a enseñar AgentCore y Strands Agents.
