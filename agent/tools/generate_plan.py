from typing import Any


def _bullet(items: list[str], indent: int = 0) -> str:
    prefix = " " * indent + "- "
    return "\n".join(prefix + str(item) for item in items)


def generate_onboarding_plan(
    employee_name: str,
    employee_email: str,
    profile: dict[str, Any],
    project: dict[str, Any],
) -> str:
    """Generate a personalized onboarding plan as Markdown."""
    repos = project.get("repositories", [])
    profile_permissions = profile.get("permissions", {})
    base_checklist = profile.get("base_checklist", {})

    repo_section = []
    for repo in repos:
        repo_section.append(
            f"### {repo['name']}\n"
            f"{repo.get('description', '')}\n\n"
            f"```bash\n"
            f"git clone {repo.get('clone_url', '<clone-url-pending>')}\n"
            f"cd {repo['name']}\n"
            f"{repo.get('bootstrap', '# bootstrap pending')}\n"
            f"{repo.get('test', '# test command pending')}\n"
            f"```"
        )

    day_1 = base_checklist.get("day_1", [])
    week_1 = base_checklist.get("week_1", [])

    plan = f"""# Onboarding plan - {employee_name}

**Empleado:** {employee_name}  
**Email:** {employee_email}  
**Perfil:** {profile.get('name', profile.get('id'))}  
**Proyecto:** {project.get('name', project.get('id'))}

## Objetivo de negocio del proyecto

{project.get('business_goal', 'Pendiente de documentar.')}

## Resumen de arquitectura

{project.get('architecture_summary', 'Pendiente de documentar.')}

## Permisos esperados

### AWS
{_bullet(profile_permissions.get('aws', []))}

### Repositorios
- Acceso esperado: {profile_permissions.get('repositories', {}).get('access', 'pending')}

### CI/CD
{_bullet(profile_permissions.get('ci_cd', []))}

## Repositorios a clonar

{chr(10).join(repo_section)}

## Checklist día 1

{_bullet(day_1)}

## Checklist semana 1

{_bullet(week_1)}

## Primeras tareas sugeridas

{_bullet(project.get('first_tasks', []))}

## Documentación sugerida

{_bullet(project.get('key_docs', []))}

## Aprobaciones y riesgos

### Aprobaciones requeridas por perfil
{_bullet(profile.get('approvals_required', []))}

### Notas de riesgo del proyecto
{_bullet(project.get('risk_notes', []))}

## Estado MVP

Este plan fue generado con datos declarativos locales. En la versión productiva, estos pasos pueden conectarse a IAM Identity Center, repos reales, pipelines y DynamoDB.
"""
    return plan.strip() + "\n"
