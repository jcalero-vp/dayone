# Arquitectura objetivo

## MVP local

El MVP local usa archivos YAML y tools Python para enseñar el patrón:

```text
CLI / futuro backoffice
  -> agent.app
  -> load_profile
  -> load_project
  -> generate_onboarding_plan
  -> track_progress
```

Este flujo permite validar el dominio sin crear permisos reales.

## Arquitectura AWS objetivo

```text
Backoffice web
  -> API backend
  -> AgentCore Runtime con agente Strands
  -> Tools AWS
       -> IAM Identity Center
       -> CodeCommit / Git provider
       -> DynamoDB
       -> S3 docs
       -> EventBridge
       -> CloudWatch / X-Ray
```

## Componentes

### Backoffice

Interfaz para managers o admins. Campos mínimos:

- Nombre del empleado.
- Email.
- Perfil.
- Proyecto o conjunto de proyectos.
- Fecha de inicio.
- Buddy opcional.

### AgentCore Runtime

Hospeda el agente o tools. AgentCore Runtime se encarga de escalado, manejo de sesiones, aislamiento de seguridad e infraestructura administrada, lo que permite concentrarse en la experiencia del agente.

### Strands Agent

Contiene el razonamiento, system prompt y tools.

### DynamoDB

Persistencia de estado:

- Onboarding creado.
- Pasos completados.
- Errores.
- Aprobaciones pendientes.

### S3

Documentación interna versionada y preparada para indexación:

- Guías de proyecto.
- Runbooks.
- Diagramas.
- FAQs.

### IAM Identity Center

Asignación real de grupos y permission sets en fases posteriores.

## Decisiones del MVP

1. Usar YAML como contrato inicial.
2. Mantener permisos simulados hasta validar el flujo.
3. Diseñar cada acción como tool independiente.
4. Permitir que el agente explique qué haría antes de hacerlo.
5. Requerir aprobación humana para accesos sensibles.

## Preguntas abiertas

- ¿Qué proveedor Git se usará en producción?
- ¿Los proyectos serán uno-a-uno o un empleado puede entrar a varios proyectos?
- ¿Qué sistema será fuente de verdad de empleados?
- ¿Qué acciones requieren aprobación del manager, tech lead o security?
- ¿Cómo se medirá productividad día 1?
