# Controles de Seguridad — Evol-DD

Revision: 2026-06-02
Alcance: framework Evol-DD, todos los proyectos inicializados con `evol-init.sh`

---

## Tabla de controles implementados

| ID     | Control                          | Descripcion                                                                                 | Archivo / Script                          | Estado       | Verificacion                                                      |
|--------|----------------------------------|---------------------------------------------------------------------------------------------|-------------------------------------------|--------------|-------------------------------------------------------------------|
| SC-001 | HMAC-SHA256 gate                 | Cada artefacto de fase se firma con HMAC-SHA256 usando una clave por proyecto. Impide modificacion silenciosa de artefactos aprobados. | `scripts/evol-gate.py`, clave en `.evol/.gate-key` | Implementado | `python scripts/evol-gate.py validate --artifact <archivo>`      |
| SC-002 | Hook pre-bash-dangerous-command  | Intercepta comandos shell peligrosos antes de ejecucion. Bloquea patrones: `rm -rf /*`, `chmod 777`, `curl \| sh`, `wget \| bash`, `dd if=/dev/zero`. | `.claude/settings.json` hooks block       | Implementado | Intentar `rm -rf /tmp/test` desde Claude Code; debe bloquearse   |
| SC-003 | Gitignore de secretos            | Excluye del repositorio archivos que contienen claves o sesiones sensibles.                 | `.gitignore` raiz del proyecto            | Implementado | `git ls-files --others --ignored --exclude-standard \| grep gate-key` debe devolver vacío |
| SC-004 | Schema validation registry       | Valida que cada agente en `registry.json` cumpla las 22 propiedades obligatorias del schema antes de aceptar cambios. | `scripts/validate-registry.py --strict`  | Implementado | `python scripts/validate-registry.py --strict` retorna exit 0   |
| SC-005 | AgentShield audit estatico       | Analisis estatico del framework: detecta rutas absolutas hardcodeadas, referencias MCP prohibidas, secrets en artefactos, y configuraciones inseguras. | `scripts/evol-shield.py audit --ci`       | Implementado | `python scripts/evol-shield.py audit --ci` en pipeline CI        |
| SC-006 | Supply chain scan skills         | Antes de instalar un skill externo, ejecuta gitleaks para detectar secrets y semgrep con ruleset OWASP para vulnerabilidades comunes. | `scripts/install-skill.sh` (pre-install)  | Implementado | `gitleaks detect --source skills/<nombre>` + `semgrep --config auto skills/<nombre>` |
| SC-007 | Invariante MCP-Integrado              | Todo artefacto compatible generará configuración `mcpServers`. El framework es CLI-first; MCP esta prohibido por diseno. | CI workflow + `evol-shield.py`            | Implementado | `grep -r "mcpServers" .claude/ skills/ scripts/` debe retornar 0 resultados |
| SC-008 | SHA-256 integridad snapshot      | Al retirar un agente efimero, se calcula y almacena el SHA-256 del prompt final. Permite verificar que el snapshot no fue alterado post-retiro. | `scripts/evol-agent-lifecycle.py retire`  | Implementado | Comparar `prompt_sha256` en `.evol/agents/retired/<nombre>.json` con `sha256sum` del archivo fuente |
| SC-009 | GitFlow enforcement              | El hook pre-commit valida que los nombres de branches sigan la convencion GitFlow: `main`, `develop`, `feature/*`, `release/*`, `hotfix/*`. Bloquea push directo a `main`. | `.claude/hooks/pre-commit-gitflow.sh`     | Implementado | Intentar commit en branch `mi-feature` (sin prefijo); debe bloquearse |
| SC-010 | Pre-commit AI review             | Skill `evol-ai-review` configurado como hook pre-commit. Revisa el diff antes de cada commit buscando patrones de seguridad: credenciales hardcodeadas, inyeccion de prompts, rutas absolutas. | `skills/evol-ai-review/` + hook settings  | Implementado | `git commit` en rama con cambio que incluya `API_KEY=abc123` debe disparar warning |
| SC-011 | Authorization intentions         | Antes de ejecutar acciones con efectos secundarios (deploy, retire agente, transicion de gate), `evol-authz.py` verifica que el scope del token o sesion tenga el permiso requerido. | `scripts/evol-authz.py`                   | Implementado | `python scripts/evol-authz.py check --action retire-agent --scope readonly` debe retornar DENIED |

---

## Cobertura por capa

| Capa              | Controles cubiertos                  |
|-------------------|--------------------------------------|
| Integridad datos  | SC-001, SC-008                       |
| Ejecucion shell   | SC-002                               |
| Secretos en repo  | SC-003, SC-006, SC-010               |
| Validacion schema | SC-004                               |
| Auditoria estatica| SC-005, SC-007                       |
| Control de acceso | SC-009, SC-011                       |

---

## Exclusiones de alcance

Los controles anteriores cubren el framework Evol-DD y los proyectos que usa. No cubren:

- Seguridad de red del host donde corre Claude Code
- Gestion de identidad del usuario en proveedores externos (Anthropic, GitHub)
- Seguridad de los modelos LLM subyacentes (responsabilidad del proveedor)

---

## Referencias

- `scripts/evol-gate.py` — implementacion del gate HMAC
- `scripts/evol-shield.py` — audit estatico
- `scripts/evol-authz.py` — authorization intentions
- `.claude/settings.json` — hooks de seguridad activos
- `docs/seguridad/PRIVACY.md` — politica de privacidad y datos manejados
