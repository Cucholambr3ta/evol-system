---
name: evol-fact-check
description: Verificación de claims y detección de desinformación con pipeline de 11 pasos (SIFT + CRAAP + MFS scoring). Produce Fact-Check Card con veredicto, score de manipulación y componente educativo. Inspirado en petar-nauka/fact-check-skill.
origin: evol-dd
inspired_by: petar-nauka/fact-check-skill (atribución en NOTICE)
when_to_use: Cuando hay claims externos (documentación de terceros, benchmarks, artículos, propuestas técnicas) que necesitan verificación antes de incorporarlos al proyecto. Trigger: "verifica esto", "fact-check", "es verdad que", "comprueba este claim".
triggers:
  - "fact-check"
  - "verifica esto"
  - "es verdad que"
  - "comprueba este claim"
  - "fuente confiable?"
  - "valida esta afirmación"
evals: evals/evol-fact-check/
---

# evol-fact-check

Pipeline de verificación técnica y detección de desinformación integrado
al flujo Evol-DD. Combina metodología SIFT, criterios CRAAP, prebunking y
scoring MFS (Manipulation & Falsehood Score) para producir veredictos
auditables.

## Modos de operación

| Modo | Cuándo usar | Input |
|------|-------------|-------|
| `full` | Verificación completa (11 pasos) | Texto / URL / imagen |
| `compare` | Comparación de dos fuentes | Fuente A vs Fuente B |
| `quick` | Verificación rápida (4 pasos) | Pregunta sí/no simple |
| `prebunk` | Mapa de narrativas falsas activas sobre tema | Topic query |

## Pipeline completo (11 pasos)

### Paso 1 — Descomposición de claims
Rompe el contenido en unidades verificables independientes.

Tipos de claim:
- `F` — Factual (verificable con datos)
- `O` — Opinión (no verificable per se)
- `P` — Predicción (verificable en el futuro)
- `U` — Unverifiable (sin método de verificación disponible)
- `I` — Implicación (verdad literal, contexto engañoso)
- `S` — Estadística (requiere metodología + fuente primaria)

### Paso 2 — Investigación de fuentes (SIFT)
**S**top — pausa antes de reaccionar al contenido.
**I**nvestigate la fuente: quién es, cuál es su historial, tiene bias declarado.
**F**ind better coverage: busca cobertura de alta calidad del mismo evento.
**T**race claims: sigue el claim hasta su origen.

Niveles de fuente (CRAAP scoring):

| Tier | Tipo | Peso |
|------|------|------|
| 1 | Peer-reviewed, primaria | 1.0 |
| 2 | Organismos gubernamentales, instituciones académicas | 0.9 |
| 3 | Medios de referencia con estándares editoriales | 0.8 |
| 4 | Expertos con historial verificable | 0.7 |
| 5 | Medios secundarios confiables | 0.6 |
| 6 | Medios con bias conocido | 0.4 |
| 7 | Fuentes anónimas / sin editorial | 0.2 |
| 8 | Fuentes con historial de desinformación | 0.0 |

### Paso 3 — Evaluación profunda (Lateral Reading)
1. Audit del sitio/autor fuera del sitio.
2. Verificar credenciales del autor.
3. Evaluar evidencia presentada.
4. Cross-reference con fuentes Tier 1-3.

### Paso 4 — Trazado de origen
- Primera aparición del claim (fecha, plataforma, idioma).
- Mutaciones del claim en su propagación.
- Asociación con campañas coordinadas conocidas.

### Paso 5 — Detección de red flags

| Categoría | Código | Ejemplos |
|-----------|--------|---------|
| Emocional | A | Urgencia extrema, miedo, indignación artificial |
| Atribución | B | "Fuentes dicen", citas sin verificar, autor anónimo |
| Falacias lógicas | C | Ad hominem, hombre de paja, pendiente resbaladiza |
| Temporal/contextual | D | Imagen/dato descontextualizado, fecha incorrecta |
| Coordinado/estructural | E | Lenguaje idéntico en múltiples fuentes, timing sospechoso |
| Salud-específico | F | Curas milagrosas, negación de consenso científico |

### Paso 6 — Veredicto + MFS Score

**Escala de veredicto:**

| Veredicto | Significado |
|-----------|-------------|
| `CONFIRMADO` | Múltiples fuentes Tier 1-2 corroboran |
| `MAYORMENTE VERDADERO` | Verdadero con matices menores |
| `MIXTO` | Parte verdad, parte falso o sin contexto |
| `NO VERIFICADO` | Insuficiente evidencia en cualquier dirección |
| `ENGAÑOSO` | Verdad técnica con contexto que distorsiona significado |
| `FALSO` | Refutado por fuentes Tier 1-2 |

**MFS Score (Manipulation & Falsehood Score):**
```
MFS = (CFS × 0.50) + (MTS × 0.30) + (SCD × 0.20)
```
- `CFS` — Claim Falsehood Score (0-10)
- `MTS` — Manipulation Technique Score (0-10)
- `SCD` — Source Credibility Deficit (0-10)

MFS 0-3: Bajo riesgo | 4-6: Moderado | 7-8: Alto | 9-10: Crítico

### Paso 7 — Calibración de confianza
Factores que aumentan/disminuyen confianza en el veredicto. Siempre transparente.

### Paso 8 — Cadena de razonamiento
Para veredictos no obvios: lógica paso a paso desde claim hasta conclusión.

### Paso 9 — Análisis contrafactual
"¿Qué necesitaría ser verdad para que este claim fuera correcto?"

### Paso 10 — Componente educativo
- Técnica de manipulación identificada y cómo reconocerla.
- Cómo verificar este tipo de claim en el futuro.
- Narrativas conocidas relacionadas.

### Paso 11 — Output

Produce **Fact-Check Report** en Markdown:

```markdown
# Fact-Check Report — <claim resumido>
**Fecha:** <ISO date> | **Veredicto:** <VEREDICTO> | **MFS:** <score>/10

## Claim analizado
<claim literal>

## Fuentes consultadas
| Fuente | Tier | CRAAP Score | Dice |

## Red flags detectados
<código> — <descripción>

## Razonamiento
<cadena lógica>

## Contrafactual
<qué haría este claim verdadero>

## Educativo
<cómo reconocer esta técnica>

## Confianza en el veredicto: <Alta/Media/Baja>
<factores>
```

## Modo quick (4 pasos)

Para claims simples:
1. Descomponer en 1 claim verificable.
2. Buscar fuente Tier 1-3 que confirme o refute.
3. Asignar veredicto.
4. Output: 3 líneas (claim / veredicto / fuente).

## Integración Evol-DD

- Invocada por `/research` para validar fuentes externas propuestas.
- Invocada por `/cross-validate` para confrontar claims entre artefactos.
- Invocada por `/security-audit` para verificar claims de CVEs y advisories.
- Invocada por `/analisis-impacto` cuando hay decisiones basadas en benchmarks externos.

## Agentes que la usan

- `evol-researcher` — verifica fuentes durante investigación
- `evol-qa` — valida claims sobre comportamiento de modelos
- `evol-doc` — verifica afirmaciones en documentación

## Atribución
Concepto inspirado en [petar-nauka/fact-check-skill](https://github.com/petar-nauka/fact-check-skill).
Implementación nativa Evol-DD: pipeline 11 pasos adaptado al contexto técnico,
MFS score integrado, output Markdown compatible con DOC_STANDARD.md.


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
