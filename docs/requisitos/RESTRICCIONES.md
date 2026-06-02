# Restricciones — Evol-DD

## Resumen

Este documento especifica las restricciones tecnicas, dependencias externas y suposiciones del proyecto.

---

## Dependencias Externas

### Requeridas

| Dependencia | Version minima | Proposito | Fallback |
|-------------|---------------|-----------|----------|
| git | 2.x | Version control, hooks | - |
| python3 | 3.10 | Scripts principales | - |

### Opcionales

| Dependencia | Version | Proposito | Fallback si no disponible |
|-------------|---------|-----------|---------------------------|
| MemPalace CLI | any | Busqueda semantica | Modo BASE |
| Node.js | any | GitNexus indexing | Sin GitNexus |
| gitleaks | any | Secrets detection | Warning, scan skipped |
| semgrep | any | SAST | Warning, scan skipped |
| bats | any | Shell tests | Skip tests |
| pytest | any | Python tests | Skip tests |
| anthropic | any | LLM provider | MockProvider |

---

## Limitaciones Conocidas

### L01: Transferencia cross-proyecto no implementada

**Restriccion:** En v0.1, el aprendizaje es por proyecto. Un patron aprendido en proyecto A no beneficia a proyecto B.

**Razon:** No hay mecanismo de transferencia entre proyectos del mismo usuario.

**Impacto:** Usuario debe re-ensenar patrones en cada proyecto.

**Roadmap:** v0.2 implementara transferencia cross-proyecto.

### L02: Umbral confidence no calibrado

**Restriccion:** El umbral `min-confidence: 0.7` para evol-evolve.py no tiene justificacion empirica.

**Razon:** Valor inicial para primeros sprints de uso real.

**Impacto:** Puede requerir ajuste en produccion.

**Roadmap:** Calibrar en v0.2 basado en datos reales.

### L03: Decay por tiempo perjudica uso esporadico

**Restriccion:** Un patron correcto aprendido hace 60 dias puede expirar antes de alcanzar confidence suficiente.

**Razon:** Sistema de decay temporal no considera patrones de uso esporadico.

**Impacto:** Usuarios ocasionales pueden perder patterns validos.

**Roadmap:** Documentado, recalibrar en v0.2.

### L04: Skills sin version pinning en sync-community

**Restriccion:** evol-evolve.py sync-community no implementa version pinning completo en v0.1.

**Razon:** Initial implementation usa topic search sin commit SHA.

**Impacto:** Actualizacion de skill puede traer cambios no deseados.

**Roadmap:** Implementar commit SHA pinning en v0.2.

### L05: Recall semantico requiere MemPalace activo

**Restriccion:** El recall de agente efimero solo recupera contexto semantico si MemPalace estuvo activo al momento del retire.

**Razon:** Sin MemPalace, solo se tiene snapshot JSON.

**Impacto:** Si MemPalace no estuvo activo, recall basico (JSON only).

**Mitigacion:** Documentar en modos.md, siempre ofrecer modo BASE.

---

## Suposiciones

### S01: Python 3.10+ disponible

Se asume que el entorno de desarrollo tiene Python 3.10 o superior instalado.

**Verificacion:** evol-doctor.sh check.

### S02: Git instalado

Se asume que git esta disponible para version control y hooks.

**Verificacion:** evol-doctor.sh check.

### S03: Directorio HOME accesible

Se asume que HOME esta configurado para escritura en `~/.evol/`.

**Verificacion:** evol-gate.py init crea .evol/.

### S04: Sistema de archivos case-sensitive

Se asume filesystem case-sensitive (Linux, macOS). Windows puede tener comportamiento inesperado.

**Mitigacion:** Nombres kebab-case consistentemente.

### S05: Permisos de escritura en HOME

Se asume que el usuario tiene permisos de escritura en su directorio HOME para:
- `~/.evol/` (state, gate key, snapshots)
- `~/.local/bin/` (wrapper global)
- `~/.claude/` (settings IDE)

### S06: Timeout de red 30s

Se asume que 30 segundos es timeout razonable para llamadas de red (MemPalace, GitHub).

**Verificacion:** _evol_common.py subprocess timeout.

### S07: Sesion defined as interaction

Una sesion comienza cuando el agente recibe la primera instruccion del usuario y termina cuando el usuario cierra la interaccion o el agente ejecuta hook Stop.

**Verificacion:** evol-memory.py load/summarize.

---

## Constraints Arquitectonicos

### C01: Sin MCP

**Constraint:** Evol-DD no usa MCP de ningun tipo — sin servidor MCP, sin protocolo de red MCP, sin configuracion de servidor en ningun IDE.

**Razon:** Diferenciacion de X-DD, simplicidad, seguridad.

**Impacto:** MemPalace se usa solo en modo CLI.

### C02: Gate key por proyecto

**Constraint:** Cada proyecto tiene su propia gate key en `.evol/.gate-key`. No hay key global.

**Razon:** Aislamiento criptografico entre proyectos.

**Mitigacion:** `evol gate init --from-global` copia key global como punto de partida.

### C03: Agentes core nunca se retiran

**Constraint:** Los 16 agentes core son permanentes y nunca pueden ser retireados.

**Razon:** Responsabilidad sobre estado del sistema.

**Verificacion:** evol-agent-lifecycle.py rechaza retire de agentes core.

### C04: Sin modifica de gobernanza por efimeros

**Constraint:** Agentes efimeros no pueden modificar archivos de gobernanza (constitucion, gate, hooks).

**Razon:** Seguridad, integridad del sistema.

**Verificacion:** Plantilla agent.template.md incluye restriction.

### C05: Conventional Commits obligatorios

**Constraint:** Todos los commits deben seguir Conventional Commits.

**Razon:** Trazabilidad, changelog automatico.

**Verificacion:** pre-commit-gitflow.sh valida formato.

---

## Ambientes Soportados

| Ambiente | Soportado | Notas |
|----------|-----------|-------|
| Linux (Ubuntu 20.04+) | Si | Desarrollo principal |
| Linux (Ubuntu 18.04) | Si | Con Python 3.10+ manual |
| macOS | Si |Compatibilidad completa |
| Windows (WSL2) | Si | Con WSL2 |
| Windows (native) | Parcial | Bash no disponible, usar PowerShell |
| CI (GitHub Actions) | Si | Matrix 3.10/3.11/3.12 |

---

## Compatibilidad con IDEs

### Confirmado funcionando

- Claude Code (slash commands)
- OpenCode (slash commands)

### Probado

- Cursor (@-mention)
- Windsurf (slash natives)
- VSCode Copilot (slash /chat)

### No probado

- Antigravity
- Codex

---

## Off-Limits (No implementar)

### OL01: MCP server

No construir servidor MCP propio ni usar protocolo MCP.

### OL02: Key global

No implementar gate key global. Por proyecto siempre.

### OL03: Agentes core retireables

No permitir retire de agentes core.

### OL04: Rutas absolutas en configs

No generar rutas absolutas del host en configs IDE.

### OL05: Emojis en docs

No emojis en ninguna documentacion. Zero tolerance.

### OL06: Dependencias externas para memory/lessons

No usar paquetes pip para evol-memory.py y evol-lessons.py. stdlib only.