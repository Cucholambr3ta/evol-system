---
description: Cluster instincts acumulados → propone skills/agents/commands nuevos. Humano aprueba (T6.1) antes de promover.
name: evolve
trigger: /evol evolve
---
# /evolve

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-EVOLVE | **Versión:** 1.0 | **Agente:** Architect & Code-Reviewer
**Misión:** Convertir patrones aprendidos automáticamente (instincts) en artefactos versionados (skills/agents/commands) tras aprobación humana.

## 0. Pre-condición (gate)

```bash
test -f scripts/xdd-state.py || { echo "Sprint 9 requerido"; exit 1; }
python3 scripts/xdd-state.py stats
```

## 1. Detectar clusters candidatos

```bash
python3 scripts/xdd-state.py evolve \
  --min-confidence 0.5 \
  --min-cluster-size 3 \
  --json | tee /tmp/xdd-evolve-proposals.json
```

Output: lista de clusters con `proposed_type` (skill/agent/command), `proposed_name`, `rationale`.

## 2. Revisión humana de propuestas

Para cada propuesta:
1. Mostrar al usuario el rationale + instincts subyacentes.
2. **Pedir aprobación explícita** (T6.1 mitigación — NO auto-promover).
3. Si aprueba: proceder a sección 3.
4. Si rechaza: marcar evolution como `rejected` en SQLite.

## 3. Generación del artefacto aprobado

Según `proposed_type`:

### → command (slash command nuevo)
1. Copiar `templates/workflow.template.md` (si existe) a `.agent/workflows/<proposed_name>.md`
2. Frontmatter `description:` derivado del rationale.
3. Pasos sugeridos extraídos de patterns de los instincts cluster.

### → skill (skill nueva)
1. Crear `skills/<proposed_name>/SKILL.md` con frontmatter `name`, `description`, `origin: evolved`, `when_to_use`.
2. Body con triggers extraídos de instincts.

### → agent (subagente nuevo)
1. Crear `prompts/agents/<categoria>/<categoria>-<proposed_name>.md` con frontmatter completo.
2. Ejecutar `python3 scripts/migrate-agents-to-registry.py` + `validate-registry.py --strict`.
3. `bash scripts/generate-equipo.sh` regenera `docs/equipo.md`.

## 4. Marcar instincts como promovidos

```bash
# (vía xdd-state.py — Sprint 10 puede agregar comando `promote`)
# Por ahora: UPDATE manual o script propio
```

## 5. Cierre

- Si se generó artefacto: invocar `/cierre-fase` para registrar la evolución en `lecciones.md`.
- Commit con `feat(evolve): promote instinct cluster <cluster_id> to <type>:<name>`.
- Update `docs/CHANGELOG.md` sección `Evolved`.

## Reglas duras

1. **NUNCA auto-promover sin aprobación humana** (T6.1 del threat model).
2. **NO modificar registry sin re-correr validate** — drift = bug.
3. **Toda evolution queda registrada** en tabla `evolutions` de SQLite (auditable).
4. **Rationale obligatorio** — el humano debe poder entender por qué se propone.

## Post-condición

```bash
python3 scripts/xdd-state.py stats
# evolutions count debe haber crecido o el rejected count
```

---
*Driven by X-DD Continuous Learning (Sprint 9)*
