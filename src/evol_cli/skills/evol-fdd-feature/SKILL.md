---
name: evol-fdd-feature
description: Feature-Driven Development. Descompone features en FEATURES.md con priorización RICE/MoSCoW, story mapping, y criterios de aceptación.
category: discipline-base
trigger: /fdd
---

# evol-fdd-feature

## Fase del Pipeline
Fase 1 (Briefing) + Fase 3 (Plan)

## Artefacto Clave
`docs/features/FEATURES.md`

## Flujo de Trabajo

### 1. Generar FEATURES.md
```bash
evol-fdd features-generate --from=acuerdos/idea/
```

### 2. Priorizar con RICE/MoSCoW
```bash
evol-fdd features-prioritize --method=RICE
# Returns: Reach, Impact, Confidence, Effort score
```

### 3. Story Mapping
```bash
evol-fdd story-map --features=docs/features/FEATURES.md
```

### 4. Validar
```bash
evol-fdd features-validate --check=dependencies
```

## Formato FEATURE

```markdown
## FEAT-001: [Nombre]

**Prioridad:** Must/Should/Could/Won't
**RICE Score:** [R×I×C]/E
**Fases:** 1, 3

### User Story
Como [rol], quiero [acción] para [beneficio].

### Criterios de Aceptación
- [ ] Dado/ Cuando/ Entonces

### Dependencias
- REQUIERE: FEAT-002
- BLOQUEA: FEAT-003
```

## Integración con Pipeline

| Fase | Uso |
|------|-----|
| Briefing | Generar features iniciales, priorizar |
| Spec | Conectar features con REQ-NNN |
| Plan | Organizar por features verticales |
| Build | Implementar por feature |
