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

## Estructura real del starter (verificada)

Rutas confirmadas contra `aws-samples/sample-strands-agentcore-starter` (clonado en `.aws-samples/`).
Si el starter cambia, reconfirmá con:
`grep -rn "Agent(" .aws-samples/sample-strands-agentcore-starter/agent --include="*.py"`.

- `agent/my_agent.py` — define el agente: `app = BedrockAgentCoreApp()` y
  `agent = Agent(model=..., system_prompt=..., tools=tools, ...)`. **Aquí se registran las tools.**
- `agent/tools/` — tools de ejemplo del starter (`knowledge_base.py`, `web_search.py`,
  `url_fetcher.py`, `weather.py`).
- `cdk/` — infraestructura como código (CDK): `deploy-all.sh`, `bin/`, `lib/`. Crea Cognito,
  DynamoDB, Bedrock Guardrail, Knowledge Base, AgentCore Memory y AgentCore Runtime.
- `chatapp/` — UI web (FastAPI, se corre con `uvicorn app.main:app`).

## Runbook (Opción C — comandos concretos)

Todos los comandos asumen que estás parado en la raíz del starter:
`cd .aws-samples/sample-strands-agentcore-starter`.

1. Clonar el starter (idempotente; queda en `.aws-samples/`, ya ignorado por git):
   ```bash
   bash accelerator/clone_aws_starter.sh
   ```
2. Instalar dependencias de infra y desplegar los stacks (crea Runtime, Memory, KB, Cognito, DynamoDB):
   ```bash
   cd cdk && npm install
   ./deploy-all.sh --region us-east-1 --profile <tu-perfil> --ingress furl
   cd ..
   ```
3. Llevar el dominio de onboarding al `agent/` del starter (sin acoplar repos): copiá desde ESTE repo
   `agent/tools/*.py`, `agent/prompts.py`, `profiles/` y `projects/` dentro de `agent/` del starter.
4. Registrar nuestras tools en `agent/my_agent.py`: importá las `@tool` de onboarding (las mismas de
   `agent/strands_agent.py`: `load_profile`, `load_project`, `generate_onboarding_plan`,
   `mark_step_done`), agregalas a la lista `tools` que recibe `Agent(...)`, y usá nuestro `SYSTEM_PROMPT`
   (de `agent/prompts.py`) como `system_prompt`.
5. Crear un usuario de prueba para la UI:
   ```bash
   cd chatapp/scripts
   ./create-user.sh tu-email@example.com 'TuPassword123@' --admin
   cd ../..
   ```
6. Probar local la UI (requiere los stacks ya desplegados; `sync-env` baja la config de Secrets Manager):
   ```bash
   cd chatapp
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ./sync-env.sh --region us-east-1 --dev-mode     # --dev-mode bypassa Cognito
   uvicorn app.main:app --reload --port 8080       # http://localhost:8080
   ```
7. Observabilidad: el agente ya emite trazas/logs (ver `agent/OBSERVABILITY.md` del starter) →
   revisá CloudWatch / X-Ray y los stacks de analytics en DynamoDB.

## Criterio para avanzar

No migrar al starter hasta que el agente local de este repo pueda:

- Cargar perfil.
- Cargar proyecto.
- Generar plan.
- Registrar al menos un paso completado.
