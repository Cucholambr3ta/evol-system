---
name: evol-uxdd-ux
description: UX-Driven Development. Disena user journeys, mensajes de UI sin jerga tecnica, y microinteracciones antes de escribir codigo frontend.
category: discipline-extended
trigger: /uxdd
---

# evol-uxdd-ux

## Fase del Pipeline
Briefing (Fase 1)

## Artefacto Clave
`ux/user_journeys/*.json`

## Flujo de Trabajo

### 1. Generar user journeys desde features
```bash
# Leer features y wireframes del briefing
evol-uxdd journey-generate --features=docs/features/FEATURES.md --wireframes=acuerdos/wireframes/ --output=ux/user_journeys/
```

### 2. Redactar mensajes de UI
```bash
# Generar mensajes sin jerga tecnica
evol-uxdd ui-messages --journeys=ux/user_journeys/ --output=ux/ui_messages/

# Verificar unicidad de strings
evol-uxdd check-duplicates --dir=ux/ui_messages/
```

### 3. Especificar microinteracciones
```bash
# Definir feedback y estados de componentes
evol-uxdd microinteractions --journeys=ux/user_journeys/ --output=ux/microinteractions/
```

### 4. Validar completitud
```bash
# Verificar que todo flujo principal tiene journey
evol-uxdd validate --journeys=ux/user_journeys/ --features=docs/features/FEATURES.md
```

## Formato User Journey

```json
{
  "journey": "JOURNEY-001",
  "name": "Registro de usuario",
  "flow": [
    {
      "step": 1,
      "action": "El usuario hace clic en 'Registrarse'",
      "screen": "landing",
      "emotion": "curioso"
    },
    {
      "step": 2,
      "action": "Completa el formulario de registro",
      "screen": "register-form",
      "emotion": "motivado"
    },
    {
      "step": 3,
      "action": "Recibe confirmacion por email",
      "screen": "confirmation",
      "emotion": "satisfecho"
    }
  ],
  "error_flows": [
    {
      "step": 2,
      "error": "Email ya registrado",
      "message": "Este email ya tiene una cuenta. Puedes iniciar sesion o recuperar tu contrasena.",
      "recovery_action": "Link a iniciar sesion"
    }
  ]
}
```

## Formato UI Messages

```markdown
# Mensajes de UI — [Pantalla]

| Clave | Mensaje | Contexto |
|-------|---------|----------|
| error.email.duplicate | Este email ya tiene una cuenta. Puedes iniciar sesion o recuperar tu contrasena. | Formulario de registro |
| success.registration | Tu cuenta ha sido creada. Revisa tu email para confirmar. | Post-registro |
```

## Integracion con Pipeline

| Fase | Uso |
|------|-----|
| Briefing | Generar journeys, mensajes y microinteracciones |
| Spec | Conectar journeys con REQ-NNN |
| Build | Implementar la UI conforme a los journeys |
| QA | Verificar que los flujos implementados coinciden |

## Referencia
- `docs/constitucion.md` Art. 2 (Pipeline gated)
- `docs/constitucion.md` Art. 5 (Domain consulting proactiva)
- `docs/disciplinas/UXDD.md`
- [User Journey Maps — Nielsen Norman Group](https://www.nngroup.com/articles/journey-mapping-101/)
- [Error Message Guidelines — Nielsen Norman Group](https://www.nngroup.com/articles/error-message-guidelines/)


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
