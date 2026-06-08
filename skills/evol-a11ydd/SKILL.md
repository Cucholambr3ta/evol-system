---
name: evol-a11ydd
description: Accessibility-Driven Development. Asigna criterios WCAG 2.1 AA por componente, ejecuta Lighthouse/axe-core, y genera tests de lector de pantalla.
category: discipline-extended
trigger: /a11y
---

# evol-a11ydd

## Fase del Pipeline
Briefing (Fase 1) + QA (Fase 5)

## Artefacto Clave
`a11y/wcag_criteria.json`

## Flujo de Trabajo

### 1. Asignar criterios WCAG por componente
```bash
# Leer componentes de UI y asignar criterios
evol-a11ydd assign --ui-messages=ux/ui_messages/ --output=a11y/wcag_criteria.json
```

### 2. Generar tests de lector de pantalla
```bash
# Generar escenarios Gherkin para navegacion con lector
evol-a11ydd screen-reader-tests --criteria=a11y/wcag_criteria.json --output=a11y/screen_reader_tests/
```

### 3. Ejecutar testing automatico
```bash
# Lighthouse Accessibility audit
npx lighthouse http://localhost:3000 --only-categories=accessibility --output=json --output-path=a11y/lighthouse-report.json

# axe-core en tests automatizados
npx playwright test --project=a11y
```

### 4. Verificar scores
```bash
# Validar que Lighthouse A11y > 90
evol-a11ydd check-score --report=a11y/lighthouse-report.json --threshold=90

# Validar 0 issues criticos axe-core
evol-a11ydd check-criticals --report=a11y/axe-report.json --block-on=critical
```

## Formato WCAG Criteria

```json
{
  "componente": "LoginForm",
  "criterios": [
    {
      "id": "WCAG-1.1.1",
      "nivel": "A",
      "descripcion": "Texto alternativo para iconos decorativos",
      "implementado": false
    },
    {
      "id": "WCAG-1.3.1",
      "nivel": "A",
      "descripcion": "Estructura semantica del formulario",
      "implementado": false
    },
    {
      "id": "WCAG-2.4.7",
      "nivel": "AA",
      "descripcion": "Indicador de foco visible en campos",
      "implementado": false
    }
  ]
}
```

## Formato Screen Reader Test

```gherkin
@a11y
Feature: Navegacion con lector de pantalla en LoginForm

  Scenario: El usuario navega al campo de email
    Given el usuario esta en la pagina de login
    And el lector de pantalla esta activo
    When el usuario presiona Tab
    Then el lector annuncia "Email, campo de texto, requerido"

  Scenario: El usuario envia el formulario con error
    Given el usuario dejo el campo email vacio
    When el usuario presiona "Iniciar sesion"
    Then el lector annuncia "Error: El email es requerido"
```

## Integracion con Pipeline

| Fase | Uso |
|------|-----|
| Briefing | Asignar criterios WCAG por componente |
| Build | Implementar accesibilidad; inyectar axe-core en tests |
| QA | Lighthouse + axe-core + revision manual de flujos clave |
| Gate | Bloquea si Lighthouse A11y < 90 o hay issues criticos |

## Referencia
- `docs/constitucion.md` Art. 2 (Pipeline gated)
- `docs/constitucion.md` Art. 9 (Evol-DD Pipeline)
- `docs/disciplinas/A11yDD.md`
- [WCAG 2.2 — W3C Recommendation](https://www.w3.org/TR/WCAG22/)
- [axe-core — Deque](https://github.com/dequelabs/axe-core)
- [The A11Y Project](https://github.com/a11yproject/a11yproject.com)


## Memory Integration

This skill integrates with the EDMS (Evol-DD Memory System) for persistent knowledge management.

### Memory Commands

After completing the main task, execute these commands to persist knowledge:

```bash
# Store decisions made during this task
python3 scripts/evol-memory.py edms-store "$(cat acuerdos/memoria/decisiones.md)" --tipo decision

# Extract entities from the work done
python3 scripts/evol-memory.py edms-extract "$(cat WORKING-CONTEXT.md)"

# Create relationships between entities
python3 scripts/evol-memory.py edms-link "$(cat WORKING-CONTEXT.md)"

# Detect any contradictions with existing knowledge
python3 scripts/evol-memory.py edms-conflicts
```

### What to Store

- **Decisions**: Architecture choices, design patterns, technology selections
- **Entities**: Components, services, modules, dependencies
- **Relationships**: How components interact, data flows, dependencies
- **Lessons**: What worked, what didn't, improvements for next time

### Memory File Updates

Update these files with task-specific knowledge:

1. `acuerdos/memoria/decisiones.md` - Record key decisions
2. `acuerdos/memoria/convenciones.md` - Update conventions if needed
3. `acuerdos/memoria/riesgos.md` - Note any new risks identified
4. `WORKING-CONTEXT.md` - Update with current state
5. `memoria.md` - Log the activity in the flight recorder
