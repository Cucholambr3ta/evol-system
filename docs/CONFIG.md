# Configuracion — evol.config.yml

## Schema Real

El archivo `evol.config.yml` es la fuente unica de configuracion del framework.
No debe contener secretos ni rutas runtime absolutas.

## Secciones

### evol_version

```yaml
evol_version: 0.1.0-dev
```

Version del framework. Sincronizada con `VERSION` y `pyproject.toml`.

### mempalace

```yaml
mempalace:
  enabled: true
  mode: cli           # cli | base (sin CLI)
  default_wing: evol-dd
  index_paths:
    - .agent
    - .evol
    - docs
    - prompts
    - scripts
    - templates
    - schemas
    - CLAUDE.md
    - README.md
    - memoria.md
    - lecciones.md
  triggers:
    - session_start
    - file_write
    - git_commit
  debounce_seconds: 5
```

**Rutas exclusionadas de indexado** (sempre negadas):
- `.evol/.gate-key`
- `.evol/.gate-log.jsonl`
- `.git/`
- `dialog/`
- `tool_result/`
- `memory/raw/`
- `*.key`, `*.pem`, `.env*`

**Seguridad:** El archivo `evol.config.yml` del framework actual incluye `.evol` en `index_paths`. Esto es un hallazgo conocido (Fix 007). En proyectos generados, `.evol` debe excluirse del indexado. El campo `index_paths` es un allowlist — si una ruta no aparece, no se indexa.

### pipeline

```yaml
pipeline:
  gates:
    - enforce_artifacts
    - require_approval
    - require_signature
    - block_on_missing_spec
  phases:
    - briefing
    - spec
    - plan
    - build
    - qa
    - retro
```

### agents

```yaml
agents:
  registry: prompts/agents/registry.json
  max_concurrent: 5
  fallback_strategy: escalate_to_orchestrator
  orchestration_pattern: lead_plus_specialists
  ephemeral:
    default_expires_after_days: 30
    retire_on_task_complete: false
    archive_path: .evol/agents/retired
```

### ide_adapters

```yaml
ide_adapters:
  generate_for:
    - claude-code
    - opencode
  mcp: false
```

## Perfil — evol.profile.yml

```yaml
profile: custom
version: 1
trigger: evol
brand:
  name: "Evol-DD"
  color: "#7C3AED"
  tagline: "El framework que evoluciona."
capabilities: []
stacks: []
```

El perfil `custom` indica proyecto generado con configuracion manual.
Perfiles auto-generados reflejan su nombre en el campo `profile`.

## Relacion con Manifests

`evol.config.yml` es configuracion runtime. `manifests/install-*.json` define que archivos se instalan por modulo/perfil.
两者 son complementarios: config controla comportamiento; manifests controla distribucion.

## Rutas Absolutas Prohibidas

No debe contener rutas como `/home/user/...`. Todas las rutas deben ser relativas al proyecto o resolver via variables de entorno (`EVOL_HOME`, `EVOL_DATA_DIR`).
