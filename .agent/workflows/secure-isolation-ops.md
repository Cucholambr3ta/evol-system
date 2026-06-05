---
description: Garantizar el aislamiento físico y lógico de tareas de alto riesgo (Pentesting, Stress Testing, Malware Analysis) mediante el uso de contenedores Docker efímeros. Protege el host de Evol-DD y automatiza la destrucción de contextos post-ejecución (Art. 7.3 Const.).
name: secure-isolation-ops
trigger: /evol secure-isolation-ops
---

# /secure-isolation-ops

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-000 | **Versión:** 2.3.0
**Mission:** Garantizar el aislamiento físico y lógico de tareas de alto riesgo (Pentesting, Stress Testing, Malware Analysis) mediante el uso de contenedores Docker efímeros. Protege el host de Evol-DD y automatiza la destrucción de contextos post-ejecución (Art. 7.3 Const.).


## 0. PRE-FLIGHT: MEMORY SEAL (START)
- Registro obligatorio en `memoria.md` (Art. 4 Constitución).
Workflow Command: `/isolate`
**Version:** 2.2.0 (2026-03-20)
**Status:** ACTIVE

---

## 1. STRATEGIC DIRECTIVES (INQUEBRANTABLES)

- **Ephemeral Context:** Todo contenedor debe ser destruido (`--rm`) inmediatamente después de finalizar la tarea.
- **Read-Only Mounting:** Los montajes del host al contenedor deben ser estrictamente de solo lectura (`:ro`) a menos que Orchestrator autorice explícitamente la escritura.
- **Network Isolation:** Las tareas de ciberseguridad deben ejecutarse en redes virtuales aisladas para evitar escaneos accidentales en la red local.
- **Zero Context Rot:** Ninguna credencial o dato sensible debe persistir dentro de la imagen del contenedor.

## 2. Evol-DD CORE CONTROL DOMAINS

### 2.1 Firewall de Comandos (Governance)

- Actúa como Gatekeeper antes de lanzar cualquier contenedor con privilegios elevados.
- Audita los puntos de montaje solicitados por el subagente.
- Monitorea el consumo de CPU/RAM para evitar ataques de denegación de servicio (Malware tests).

### 2.2 Orchestration (Operations)

- **Motor Principal:** `skill-docker-orchestrator`.
- **Integrado en:** `FLUJO_062` (Advanced Pentesting), `FLUJO_014` (Stress Test).
- **Control Técnico:** `scripts/docker-firewall.sh`.

## 3. ASSET PROTOCOL

- **Input:** Imagen Docker, Script de Ataque/Prueba, Configuración de Red.
- **Output:** Reporte de Seguridad, Logs Aislados, Evidencia Forense.

## 4. OPERATIONAL FLOW

| Phase | Action | Actor | Standard |
| :--- | :--- | :--- | :--- |
| **I. Provisioning** | Pull de la imagen segura y creación de red aislada. | `skill-docker-orchestrator` | Security Mode |
| **II. Mounting** | Montaje de solo lectura de los archivos de prueba. | Subagente 06 | Min. Privilege |
| **III. Attack/Test** | Ejecución del comando de hacking o prueba de carga. | Subagente Especializado | Isolated |
| **IV. Extraction** | Exportación de los resultados al host de Evol-DD. | Orchestrator | Integrity |
| **V. Destruction** | Eliminación de contenedor y red temporal. | `skill-docker-orchestrator` | Art. 7.3 (Const.) |

## 5. RECOVERY & ERRORS

- **[ERR-071-1]:** Docker Daemon Unreachable -> Reintentar conexión o solicitar reinicio de servicio.
- **[ERR-071-2]:** Resource Limit Exceeded -> Limitar los recursos del contenedor (`--cpus`, `--memory`).
- **[ERR-071-3]:** Escape Attempt Detected -> Congelar contenedor y alertar a Orchestrator de inmediato.

---
**Next Step:** Usar `/isolate --image [target] --cmd [operation]` para iniciar una sesión segura.


## POST-FLIGHT: MEMORY SEAL (END)
- Cierre de sesión y persistencia final en `memoria.md`.