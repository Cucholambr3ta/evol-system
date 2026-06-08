---
name: evol-workflow-design
description: Diseño de procesos automatizados, patrones de workflow, CI/CD design e integración de sistemas.
category: transfer
trigger: /workflow
---

# evol-workflow-design

## Cuándo Usar

Activar esta skill cuando se necesita diseñar o mejorar procesos automatizados:

- **Workflow patterns**: secuencia, paralelismo, branching, merging
- **CI/CD design**: pipelines de integración continua y delivery
- **System integration**: conectar sistemas heterogéneos
- **Process automation**: automatizar tareas repetitivas
- **Error handling**: retry, fallback, compensation, dead letter queues
- **Orchestration**: coordinar múltiples servicios/tareas

**No usar para**: orquestación de agentes Evol-DD (usar evol-orchestrator), infraestructura (usar evol-devops).

## Conocimiento de Dominio

### Workflow Patterns
- **Sequential**: A → B → C (simple, predictable)
- **Parallel**: A → (B | C) → D (faster, concurrent)
- **Conditional**: A → if X then B else C (decision points)
- **Loop**: A → B → if not done, back to A (iteration)
- **Fork-join**: split into parallel, wait for all to complete
- **Compensation**: undo previous steps if something fails

### CI/CD Design
- **Build stage**: compile, lint, type check
- **Test stage**: unit, integration, E2E tests
- **Security stage**: SAST, dependency scanning, secrets detection
- **Deploy stage**: staging, canary, production
- **Rollback**: automatic rollback on failure
- **Feature flags**: decouple deployment from release

### System Integration
- **Synchronous**: REST, gRPC (real-time, blocking)
- **Asynchronous**: queues, events (non-blocking, resilient)
- **Event-driven**: pub/sub, event sourcing
- **API gateway**: single entry point, routing, rate limiting
- **Service mesh**: inter-service communication, observability

### Error Handling
- **Retry with backoff**: exponential backoff, jitter
- **Circuit breaker**: stop calling failing service
- **Fallback**: provide degraded functionality
- **Dead letter queue**: capture failed messages for investigation
- **Compensation**: undo completed steps (saga pattern)
- **Idempotency**: safe to retry, same result

### Process Automation
- **Rule engines**: business rules without code changes
- **Scheduled tasks**: cron, time-based triggers
- **Event-driven**: trigger on events, not time
- **Human-in-the-loop**: approval steps, manual intervention
- **Audit trail**: log all actions for compliance

## Flujo de Trabajo

1. **Map current process**: how does it work today? (as-is)
2. **Identify automation opportunities**: repetitive, error-prone, slow
3. **Design target process**: how should it work? (to-be)
4. **Select patterns**: sequential, parallel, event-driven, etc.
5. **Design error handling**: retry, fallback, compensation
6. **Implement pipeline**: CI/CD, workflow engine, integration
7. **Test end-to-end**: happy path, error paths, edge cases
8. **Monitor and improve**: metrics, alerts, continuous optimization

## Integración con Pipeline

- **Briefing (Fase 1)**: understand current processes, pain points
- **Spec (Fase 2)**: document workflow requirements, integration points
- **Plan (Fase 3)**: design workflow architecture, select tools
- **Build (Fase 4)**: implement workflows with error handling
- **QA (Fase 5)**: test all paths, error scenarios, edge cases
- **Retro (Fase 6)**: analyze workflow metrics, identify improvements

## Referencia

- Constitución Evol-DD: Art. 9 (pipeline de 6 fases)
- Art. 2 (gated workflow patterns)
- Agentes relacionados: evol-devops (CI/CD), evol-systems-design (system interactions), evol-orchestrator (agent orchestration)
- Martin Fowler - "Patterns of Enterprise Application Architecture"
- Chris Richardson - "Microservices Patterns": saga, circuit breaker
- Camunda: workflow automation platform
