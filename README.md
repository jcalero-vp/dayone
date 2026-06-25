# Onboarding AgentCore Workshop

MVP de workshop para construir un asistente agéntico de onboarding de desarrolladores usando **Amazon Bedrock AgentCore**, **Strands Agents** y servicios AWS nativos.

El objetivo del repo es servir como punto de partida para que el equipo aprenda a crear, ejecutar y desplegar un agente que, a partir de un empleado + perfil + proyecto, genere un plan de onboarding, explique repositorios, liste permisos esperados y registre progreso.

> **Estado: simulado vs. lo que vas a construir.** Este repo arranca como **Lab 1** — un generador
> de planes en Python plano que corre **sin** el SDK de Strands. El agente real (Strands + Bedrock)
> es **Lab 2** y el acelerador AWS es **Lab 3**. Los permisos, repos y estado son **simulados** hasta
> fases posteriores. Guía completa de labs: [`docs/WORKSHOP_LABS.md`](docs/WORKSHOP_LABS.md).

## Objetivos del MVP

- Aprender AgentCore Runtime y Strands Agents con un caso realista.
- Reducir dependencias externas tipo Confluence/Jira/Slack durante el MVP.
- Usar documentación local versionada en el repo y/o S3.
- Modelar permisos y onboarding como plantillas declarativas.
- Preparar el camino para una UI de backoffice donde un manager seleccione empleado, perfil y proyecto.

## Arquitectura MVP

```text
Backoffice futuro / CLI
        |
        v
Strands Agent
        |
        +--> tools/load_profile.py
        +--> tools/load_project.py
        +--> tools/generate_plan.py
        +--> tools/track_progress.py
        |
        v
AgentCore Runtime futuro
        |
        +--> DynamoDB futuro: estado del onboarding
        +--> S3 futuro: docs internas versionadas
        +--> IAM Identity Center futuro: permisos reales
        +--> CodeCommit/GitHub futuro: repos reales
```

## Estructura

```text
.
├── agent/                         # Código del agente Strands
│   ├── app.py                      # Agente mínimo
│   ├── config.py                   # Configuración
│   ├── prompts.py                  # System prompts
│   └── tools/                      # Tools locales simuladas
├── profiles/                       # Perfiles declarativos de onboarding
├── projects/                       # Proyectos declarativos
├── docs/                           # Objetivos, contexto y decisiones
├── accelerator/                    # Integración con sample AWS
├── scripts/                        # Scripts de setup/demo
├── infra/backoffice/               # Placeholder para backoffice futuro
└── tests/                          # Tests mínimos
```

## Quickstart local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m agent.app --employee "Ada Lovelace" --email ada@example.com --profile backend-dev --project payments-platform
```

Salida esperada: un plan de onboarding en Markdown con repos, permisos, checklist y primeros pasos.

## Path Strands (agente real, opcional)

El path local de arriba (`agent/app.py`) corre **sin** el SDK. Para que un **agente Strands** orqueste
las mismas tools (Lab 2), usá [`agent/strands_agent.py`](agent/strands_agent.py):

```bash
# 1) Habilitar el SDK (descomenta strands-agents y bedrock-agentcore en requirements.txt)
pip install strands-agents bedrock-agentcore

# 2) Configurar AWS + Bedrock
cp .env.example .env          # setea AWS_REGION y BEDROCK_MODEL_ID (requiere acceso al modelo)

# 3) Ejecutar el agente real
python -m agent.strands_agent --employee "Ada Lovelace" --email ada@example.com \
  --profile backend-dev --project payments-platform
```

Las tools son las **mismas** funciones de `agent/tools/`, ahora envueltas como `@tool` de Strands.
Detalle del contrato de tools (lectura / generación / escritura / peligrosas) en
[`docs/AGENTCORE_STRANDS_NOTES.md`](docs/AGENTCORE_STRANDS_NOTES.md).

## Usar el acelerador AWS

Este workshop está diseñado para poder convivir con el acelerador oficial `aws-samples/sample-strands-agentcore-starter`.

```bash
bash accelerator/clone_aws_starter.sh
```

Luego revisen `accelerator/INTEGRATION_PLAN.md` para decidir si:

1. Usan este repo como capa de dominio y copian sus tools/prompts al starter.
2. Usan el starter como base full-stack y migran este MVP dentro de su carpeta `agent/`.
3. Mantienen ambos: starter para infraestructura y este repo para ejercicios del workshop.

## Roadmap sugerido

### Fase 1: Workshop local
- Ejecutar agente local.
- Entender Strands tools y prompts.
- Agregar un nuevo perfil y proyecto.
- Generar un plan de onboarding.

### Fase 2: AgentCore
- Empaquetar agente para AgentCore Runtime.
- Configurar observabilidad.
- Invocar por sesión.
- Comparar local vs runtime administrado.

### Fase 3: Backoffice
- Crear UI mínima: empleado, email, perfil, proyecto.
- Persistir estado en DynamoDB.
- Generar checklist por empleado.

### Fase 4: Permisos reales
- Conectar IAM Identity Center.
- Mapear perfiles a permission sets.
- Aprobar acciones sensibles human-in-the-loop.

## Principio de diseño

El onboarding debe ser declarativo:

```yaml
employee: ada@example.com
profile: backend-dev
project: payments-platform
```

El sistema deriva automáticamente repos, permisos, tareas, documentación y próximos pasos.
