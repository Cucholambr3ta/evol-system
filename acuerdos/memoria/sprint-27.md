# Memoria Sprint 27 — 2026-06-04

## Hitos

- INC E5: evol-memory.py sprint-close (11 tests)
  - Crea acuerdos/memoria/sprint-NN.md + acuerdos/lecciones/sprint-NN.md
  - INDEX.md idempotente + MEMORY.md inicializado en primer close
- INC E5: evol-init.sh genera MEMORY.md + INDEX.md en acuerdos/ al bootstrap
- INC E5: cierre-fase.md v1.4 — usa sprint-close, backward compat con lecciones.md root
- INC E6: evol-historias.md + evol-sprint.md (workflows portados de X-DD con evol- prefixes)
- INC E7: evol-gitflow.sh — setup dev/collab, sprint-start/close, pre-push (15 tests bats)
- INC E8: evol-discipline-check.py + integracion en evol-gate.py approve() (21 tests)
- Version 0.2.7 publicada en PyPI
- 54 pytest + 15 bats = 69 tests verdes

## Bloqueos

- 0.2.4 ya existia en PyPI (sesion anterior) — publicado como 0.2.7

## Proxima sesion

- Merge feature/evol-inc5-9 a develop
- Merge feature/sprint-memoria-lecciones a develop en X-DD
- Actualizar memoria/lecciones root con referencias a acuerdos/ como SSoT
