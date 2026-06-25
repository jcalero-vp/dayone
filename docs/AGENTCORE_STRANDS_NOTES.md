# AgentCore + Strands notes

## Qué investigar durante el workshop

- Cómo empaquetar el agente para AgentCore Runtime.
- Cómo exponer endpoints compatibles con el runtime.
- Cómo activar observabilidad en CloudWatch.
- Cómo manejar sesiones de conversación.
- Cómo separar tools de lectura, tools de escritura y tools de aprobación.

## Ruta recomendada

1. Ejecutar local sin Strands para entender el dominio.
2. Instalar Strands Agents SDK.
3. Convertir `load_profile`, `load_project`, `generate_onboarding_plan` y `mark_step_done` en tools Strands.
4. Ejecutar el agente local con Strands.
5. Empaquetar con AgentCore Starter Toolkit.
6. Desplegar en AgentCore Runtime.
7. Medir trazas, logs y errores.

## Contrato conceptual de tools

### Tools de lectura

- `load_profile(profile_id)`
- `load_project(project_id)`
- `search_internal_docs(query)` futuro

### Tools de generación

- `generate_onboarding_plan(employee, email, profile, project)`

### Tools de escritura

- `mark_step_done(employee_email, step_id, note)`
- `request_permission_approval(employee_email, permission_set)` futuro

### Tools peligrosas

Estas no deben ejecutarse automáticamente en el MVP:

- Crear usuario real.
- Otorgar permisos productivos.
- Leer secretos productivos.
- Desplegar a producción.

## Ejemplo concreto: envolver una función como tool

Cada función de `agent/tools/` se convierte en tool de Strands con el decorador `@tool`. El docstring
es lo que el modelo lee para decidir cuándo usarla, así que escribilo claro:

```python
from strands import Agent, tool
from strands.models import BedrockModel

from agent.prompts import SYSTEM_PROMPT
from agent.tools.load_profile import load_profile as _load_profile

@tool
def load_profile(profile_id: str) -> dict:
    """Carga un perfil declarativo de onboarding desde profiles/<id>.yaml."""
    return _load_profile(profile_id)

# ... idem load_project, generate_onboarding_plan, mark_step_done ...

agent = Agent(
    model=BedrockModel(model_id="anthropic.claude-3-5-sonnet-20241022-v2:0", region_name="us-east-1"),
    system_prompt=SYSTEM_PROMPT,
    tools=[load_profile, load_project, generate_onboarding_plan, mark_step_done],
)
print(agent("Genera el plan de onboarding para Ada con perfil backend-dev en payments-platform"))
```

La implementación completa y ejecutable está en `agent/strands_agent.py`. Para correrla:

```bash
pip install strands-agents bedrock-agentcore     # o descomenta en requirements.txt
cp .env.example .env                             # AWS_REGION + BEDROCK_MODEL_ID
python -m agent.strands_agent --employee "Ada Lovelace" --email ada@example.com \
  --profile backend-dev --project payments-platform
```

## Nota

El código actual corre sin instalar Strands para que el workshop empiece rápido. La integración real con Strands debe hacerse como ejercicio guiado.
