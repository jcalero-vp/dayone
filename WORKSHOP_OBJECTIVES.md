# Objetivos del workshop

## Propósito

Construir un MVP de asistente de onboarding técnico usando AWS, Amazon Bedrock, Amazon Bedrock AgentCore y Strands Agents. El caso de negocio es reducir el tiempo necesario para que un nuevo desarrollador sea productivo desde el día 1.

## Objetivos de aprendizaje

Al finalizar el workshop, el equipo debería poder:

1. Explicar qué problema resuelve Amazon Bedrock AgentCore en una arquitectura agéntica.
2. Crear un agente básico con Strands Agents.
3. Diseñar tools que conecten el razonamiento del agente con acciones concretas.
4. Modelar conocimiento interno como archivos versionados, evitando depender al inicio de SaaS externos como Confluence.
5. Entender cómo se puede pasar de simulación local a integración real con AWS.
6. Diseñar un backoffice para parametrizar onboarding por empleado, perfil y proyecto.
7. Identificar qué acciones deben ser automáticas y cuáles requieren aprobación humana.
8. Preparar una demo end-to-end de onboarding técnico.

## Objetivos técnicos

- Ejecutar un agente Strands local.
- Definir perfiles de onboarding en YAML.
- Definir proyectos en YAML.
- Generar planes de onboarding personalizados.
- Preparar la integración futura con AgentCore Runtime.
- Preparar una ruta de integración con el acelerador de AWS `sample-strands-agentcore-starter`.

## Resultado esperado

Una demo donde el usuario ingresa:

- Nombre del empleado.
- Email.
- Perfil, por ejemplo `backend-dev`.
- Proyecto, por ejemplo `payments-platform`.

Y el agente devuelve:

- Repositorios que debe clonar.
- Permisos esperados.
- Checklist del día 1.
- Explicación de arquitectura.
- Primeras tareas sugeridas.
- Riesgos o aprobaciones pendientes.

## Qué no se implementa todavía

Para mantener el MVP simple, inicialmente no se automatizan permisos reales ni integraciones con SaaS externos.

Quedan fuera de la primera iteración:

- Alta real en IAM Identity Center.
- Alta real en GitHub, GitLab o CodeCommit.
- Integración real con Jira, Slack, Teams o Confluence.
- Backoffice productivo.
- Gestión avanzada de secretos.
- Guardrails empresariales completos.

## Criterio de éxito

El workshop es exitoso si el equipo puede explicar, modificar y extender el flujo de onboarding sin depender de una sola persona experta, y si queda claro cómo evolucionar el MVP hacia una solución AWS-native de producción.
