"""OPCIONAL — Implementación con Strands Agents del asistente de onboarding.

Este archivo es el objetivo del **Lab 2** del workshop. El path por defecto
(`agent/app.py`) corre SIN el SDK de Strands llamando a `build_plan()` directamente.
Aquí, en cambio, un **agente Strands razona** y decide cuándo invocar cada tool.

Requisitos para ejecutarlo (no necesarios para el path local de `agent/app.py`):

    # 1) Instalar el SDK (o descomentar las líneas en requirements.txt)
    pip install strands-agents bedrock-agentcore

    # 2) Configurar credenciales AWS + acceso al modelo Bedrock
    cp .env.example .env        # setea AWS_REGION y BEDROCK_MODEL_ID

    # 3) Ejecutar el agente real
    python -m agent.strands_agent \\
        --employee "Ada Lovelace" --email ada@example.com \\
        --profile backend-dev --project payments-platform

Las tools envueltas aquí son EXACTAMENTE las mismas funciones locales que usa
`agent/app.py`. La diferencia es quién las orquesta: antes nosotros, ahora el agente.
"""
from __future__ import annotations

import argparse
import os

from agent.prompts import SYSTEM_PROMPT
from agent.tools.load_profile import load_profile as _load_profile
from agent.tools.load_project import load_project as _load_project
from agent.tools.generate_plan import generate_onboarding_plan as _generate_onboarding_plan
from agent.tools.track_progress import mark_step_done as _mark_step_done

try:
    from strands import Agent, tool
    from strands.models import BedrockModel
except ImportError as exc:  # pragma: no cover - solo se dispara sin el SDK instalado
    raise SystemExit(
        "\n[onboard-assistant] El SDK de Strands no está instalado.\n"
        "Este es el path 'agente real' del workshop (Lab 2).\n"
        "  1) Descomenta 'strands-agents' y 'bedrock-agentcore' en requirements.txt\n"
        "     (o instala: pip install strands-agents bedrock-agentcore).\n"
        "  2) Configura credenciales AWS y acceso al modelo Bedrock (.env).\n"
        "  3) Para el path LOCAL sin SDK usa: python -m agent.app ...\n"
        f"  (detalle del import: {exc})\n"
    )


# --- Tools de lectura -------------------------------------------------------
@tool
def load_profile(profile_id: str) -> dict:
    """Carga un perfil declarativo de onboarding desde profiles/<id>.yaml.

    Devuelve permisos esperados, checklist base y aprobaciones requeridas.
    """
    return _load_profile(profile_id)


@tool
def load_project(project_id: str) -> dict:
    """Carga un proyecto declarativo desde projects/<id>.yaml.

    Devuelve repositorios, arquitectura, primeras tareas y notas de riesgo.
    """
    return _load_project(project_id)


# --- Tool de generación -----------------------------------------------------
@tool
def generate_onboarding_plan(
    employee_name: str,
    employee_email: str,
    profile: dict,
    project: dict,
) -> str:
    """Genera el plan de onboarding en Markdown a partir de un perfil y un proyecto.

    `profile` y `project` son los dicts devueltos por load_profile y load_project.
    """
    return _generate_onboarding_plan(employee_name, employee_email, profile, project)


# --- Tool de escritura ------------------------------------------------------
@tool
def mark_step_done(employee_email: str, step_id: str, note: str = "") -> dict:
    """Registra un paso de onboarding completado (estado local del MVP).

    En producción esto se reemplaza por una escritura en DynamoDB.
    """
    return _mark_step_done(employee_email, step_id, note)


def build_agent() -> Agent:
    """Construye el agente Strands con modelo Bedrock + tools de onboarding."""
    model = BedrockModel(
        model_id=os.environ.get(
            "BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"
        ),
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
    )
    return Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[
            load_profile,
            load_project,
            generate_onboarding_plan,
            mark_step_done,
        ],
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generar un plan de onboarding usando un agente Strands real."
    )
    parser.add_argument("--employee", required=True, help="Nombre completo del empleado")
    parser.add_argument("--email", required=True, help="Email del empleado")
    parser.add_argument("--profile", required=True, help="Id de perfil, ej. backend-dev")
    parser.add_argument("--project", required=True, help="Id de proyecto, ej. payments-platform")
    args = parser.parse_args()

    agent = build_agent()
    prompt = (
        f"Genera el plan de onboarding para el empleado '{args.employee}' "
        f"(email {args.email}) con el perfil '{args.profile}' en el proyecto "
        f"'{args.project}'. Usa las tools load_profile y load_project para obtener "
        f"los datos y luego generate_onboarding_plan para producir el plan en Markdown."
    )
    result = agent(prompt)
    print(result)


if __name__ == "__main__":
    main()
