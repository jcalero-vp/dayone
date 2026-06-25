# Plan de integración con acelerador AWS

## Acelerador recomendado

Usar como referencia `aws-samples/sample-strands-agentcore-starter`, un starter full-stack para prototipado de agentes con Amazon Bedrock AgentCore, Strands Agents SDK, FastAPI y htmx.

## Estrategias posibles

### Opción A: usar este repo como dominio

Mantener este repo para el workshop y copiar sus conceptos al starter:

- `profiles/`
- `projects/`
- `agent/prompts.py`
- `agent/tools/`

Ventaja: aprendizaje claro, bajo acoplamiento.

### Opción B: migrar este repo dentro del starter

Clonar el starter y reemplazar/adaptar su agente con el dominio de onboarding.

Ventaja: más rápido para tener UI, telemetry y estructura full-stack.

### Opción C: mantener ambos repos (RECOMENDADA para el workshop)

- Starter AWS: infraestructura, UI y deployment.
- Este repo: ejercicios, perfiles, dominio y documentación del workshop.

Ventaja: ideal para entrenamiento del equipo. Bajo riesgo de romper el path local (Lab 1), el dominio
queda versionado y explicable, y la infra evoluciona por separado. Elegí A si querés un único repo de
dominio liviano; elegí B solo si la prioridad es tener UI full-stack cuanto antes.

## Prerequisitos

Antes de tocar el acelerador conviene tener:

- Cuenta AWS con permisos para Amazon Bedrock (y AgentCore en fases posteriores).
- **Acceso al modelo habilitado** en la consola de Bedrock → *Model access*, para el `BEDROCK_MODEL_ID`
  que uses (ver `.env.example`).
- AWS CLI configurado (`aws configure` o SSO) y región definida (`AWS_REGION`).
- Python 3.11+, `git` y el SDK de Strands instalado (Lab 2 completo: `agent/strands_agent.py` corre).
- Docker disponible (el starter empaqueta el agente en contenedor para AgentCore Runtime).

## Runbook (Opción C — comandos concretos)

1. Clonar el starter (idempotente; queda en `.aws-samples/`, ya ignorado por git):
   ```bash
   bash accelerator/clone_aws_starter.sh
   ```
2. Explorar su estructura y leer su README (la fuente de verdad de sus comandos):
   ```bash
   ls .aws-samples/sample-strands-agentcore-starter
   ${PAGER:-less} .aws-samples/sample-strands-agentcore-starter/README.md
   ```
3. **Localizar** dónde se define el agente del starter (no asumir la ruta — buscarla):
   ```bash
   grep -rn "Agent(" .aws-samples/sample-strands-agentcore-starter --include="*.py"
   grep -rn "from strands" .aws-samples/sample-strands-agentcore-starter --include="*.py"
   ```
4. Llevar el dominio de onboarding al starter sin acoplar repos: instalá este repo como dependencia
   o copiá `agent/tools/`, `agent/prompts.py`, `profiles/` y `projects/`.
5. Registrar las tools de onboarding en el `Agent` del starter — son las mismas `@tool` de
   `agent/strands_agent.py` (`load_profile`, `load_project`, `generate_onboarding_plan`, `mark_step_done`).
6. Probar local con el mecanismo del starter (su README indica el comando exacto; típicamente
   FastAPI/uvicorn o un script/`make` de run).
7. Empaquetar y desplegar a AgentCore Runtime con el starter toolkit (seguir el README del starter).
8. Verificar trazas, logs y errores en CloudWatch / observabilidad de AgentCore.

## Criterio para avanzar

No migrar al starter hasta que el agente local de este repo pueda:

- Cargar perfil.
- Cargar proyecto.
- Generar plan.
- Registrar al menos un paso completado.
