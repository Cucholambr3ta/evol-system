---
name: evol-balance
description: Balance de carga y optimización de recursos en el sistema Evol-DD. Aplica patrones de workload balancing, resource allocation y performance optimization.
category: game-inspired
trigger: /balance
---

# evol-balance

## Cuándo Usar

Activar esta skill cuando se necesita optimizar la distribución de carga y recursos:

- **Workload balancing**: distribuir tareas entre agentes equitativamente
- **Resource allocation**: asignar CPU, memoria, tokens de LLM, tiempo de humanos
- **Performance optimization**: identificar cuellos de botella, optimizar throughput
- **Capacity planning**: prever necesidades futuras de recursos
- **Bottleneck analysis**: encontrar y resolver cuellos de botella
- **Cost optimization**: maximizar valor por unidad de recurso

**No usar para**: diseño de sistemas de interacción (usar evol-systems-design), timing del pipeline (usar evol-pacing).

## Conocimiento de Dominio

### Workload Balancing
- **Round-robin**: distribución circular simple, no considera capacidad
- **Weighted distribution**: asignar carga proporcional a capacidad
- **Least connections**: enviar trabajo al agente con menos carga actual
- **Resource-aware routing**: routing basado en disponibilidad de recursos

### Resource Allocation
- **Token budgets**: asignar presupuestos de tokens por agente/tarea
- **Time boxing**: limitar tiempo máximo por tarea
- **Priority queues**: tareas de mayor prioridad primero
- **Preemption**: interrumpir tareas de baja prioridad para high priority

### Performance Optimization
- **Amdahl's Law**: speedup limitado por la parte serial del sistema
- **Little's Law**: L = λW (items in system = arrival rate × wait time)
- **Queuing theory**:理解 tiempos de espera y throughput
- **Caching strategies**: cache hit/miss, invalidation, warming

### Capacity Planning
- **Horizontal scaling**: más instancias, no más potentes
- **Vertical scaling**: instancias más potentes, no más
- **Auto-scaling**: escalar basado en métricas (CPU, queue depth, etc.)
- **Graceful degradation**: funcionar con menos recursos, no fallar

### Cost Optimization
- **Cost per task**: cuánto cuesta cada tarea en recursos
- **ROI por agente**: retorno de inversión por agente
- **Spot instances**: usar recursos baratos para workloads flexibles
- **Reserved capacity**: comprometerse a cambio de descuento

## Flujo de Trabajo

1. **Mapear recursos actuales**: ¿Qué hay? (agentes, LLM tokens, tiempo humano, infra)
2. **Medir utilización**: trackear uso real vs. capacidad disponible
3. **Identificar cuellos de botella**: dónde se acumula trabajo, dónde hay idle
4. **Redistribuir carga**: reasignar tareas para equilibrar utilización
5. **Optimizar resource allocation**: ajustar budgets, prioridades, limits
6. **Implementar métricas**: throughput, latency, utilization, cost
7. **Planificar capacidad**: prever necesidades futuras, escalar proactivamente
8. **Monitorear y ajustar**: continuous optimization basado en datos reales

## Integración con Pipeline

- **Briefing (Fase 1)**: entender recursos disponibles y constraints
- **Spec (Fase 2)**: documentar requisitos de recursos por fase
- **Plan (Fase 3)**: asignar recursos a fases, identificar dependencias de recursos
- **Build (Fase 4)**: monitorear uso de recursos, optimizar en tiempo real
- **QA (Fase 5)**: testear con carga real, identificar bottlenecks
- **Retro (Fase 6)**: analizar eficiencia de uso de recursos, planificar mejoras

## Referencia

- Constitución Evol-DD: Art. 6 (orquestación multi-agente)
- Art. 2 (pipeline con gates - resource allocation)
- Agentes relacionados: evol-systems-design (diseño de sistemas), evol-devops (infra), evol-pm (capacity planning)
- Tom DeMarco - "Peopleware": human factors in productivity
- Gene Kim - "The Phoenix Project": theory of constraints in dev
- opsdev.io: DevOps metrics and optimization
