# Guía de labs del workshop

Esta guía hila los tres labs del workshop, del path local simulado al agente real y al acelerador AWS.
El objetivo no es tener todo resuelto, sino que quede **claro qué se quiere lograr en cada paso**.

## Mapa: ¿qué está simulado y qué vas a construir?

| Capa | Lab 1 (local) | Lab 2 (Strands) | Lab 3 (acelerador) |
|------|---------------|-----------------|--------------------|
| Orquestación | `build_plan()` en Python | **Agente Strands** decide qué tool usar | Agente sobre AgentCore Runtime |
| Tools | Funciones Python | Mismas funciones como `@tool` | Mismas tools + AWS reales (futuro) |
| Datos | YAML en `profiles/` y `projects/` | YAML (igual) | YAML + S3 / DynamoDB (futuro) |
| Permisos | **Simulados** (texto en el plan) | Simulados | IAM Identity Center (futuro) |
| Estado | JSON en `.local-progress/` | JSON local | DynamoDB (futuro) |

> Regla de oro: **el repo siempre debe correr en Lab 1 sin instalar el SDK de Strands.**
> Lab 2 y Lab 3 son opcionales y aditivos; no rompen el path local.

---

## Lab 1 — Agente local (entender el dominio)

**Meta:** ejecutar el generador de planes y entender el modelo declarativo.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m agent.app --employee "Ada Lovelace" --email ada@example.com \
  --profile backend-dev --project payments-platform
pytest
```

**Ejercicios:**
1. Agregar un perfil nuevo en `profiles/` (ej. `data-engineer.yaml`).
2. Agregar un proyecto nuevo en `projects/`.
3. Generar un plan con esa combinación y revisar el Markdown resultante.

**Criterio para avanzar a Lab 2:** el plan se genera con repos, permisos y checklist correctos.

---

## Lab 2 — Tools Strands (el agente razona)

**Meta:** que un **agente** decida cuándo invocar cada tool, en lugar de llamarlas nosotros.

```bash
# 1) Habilitar el SDK
#    Descomenta en requirements.txt: strands-agents, bedrock-agentcore
pip install strands-agents bedrock-agentcore

# 2) Configurar AWS + Bedrock
cp .env.example .env          # setea AWS_REGION y BEDROCK_MODEL_ID
#    Requiere credenciales AWS y acceso habilitado al modelo en Bedrock.

# 3) Ejecutar el agente real
python -m agent.strands_agent --employee "Ada Lovelace" --email ada@example.com \
  --profile backend-dev --project payments-platform
```

Ver `agent/strands_agent.py`: envuelve las **mismas** funciones de `agent/tools/` como `@tool`
(lectura: `load_profile`, `load_project`; generación: `generate_onboarding_plan`;
escritura: `mark_step_done`) y las pasa a un `Agent` Strands con `SYSTEM_PROMPT`.

**Ejercicios:**
1. Agregar la tool de escritura `mark_step_done` a una conversación y registrar un paso.
2. Pedirle al agente que explique **qué haría** antes de hacerlo (human-in-the-loop).
3. Revisar el contrato de tools peligrosas en `docs/AGENTCORE_STRANDS_NOTES.md`.

**Criterio para avanzar a Lab 3:** el agente carga perfil + proyecto, genera el plan y registra un paso.

---

## Lab 3 — Acelerador AWS (camino a producción)

**Meta:** usar `aws-samples/sample-strands-agentcore-starter` para infra/UI/deploy, manteniendo
este repo como capa de dominio (**Opción C** recomendada — ver `accelerator/INTEGRATION_PLAN.md`).

```bash
bash accelerator/clone_aws_starter.sh   # clona el starter en .aws-samples/ (ya en .gitignore)
```

Luego seguí el runbook concreto en `accelerator/INTEGRATION_PLAN.md` (prerequisitos, comandos y
dónde vive el agente del starter).

**Criterio de éxito del workshop:** el equipo puede explicar, modificar y extender el flujo de
onboarding, y sabe cómo evolucionarlo hacia una solución AWS-native de producción.
