---
name: /evol cierre
description: Flight recorder close — summary milestones in memoria.md
trigger: /evol cierre
category: core
---

# Evol-Cierre (Flight Recorder)

## Mission
Close session by writing milestones to memoria.md.

## Protocol
1. Read current memoria.md
2. Update "Bitacora de Sesiones" with:
   - Date/time
   - Goal
   - Milestones achieved
   - Decisions made
   - Blockers
   - Next session plan
3. Run agent lifecycle GC if applicable
4. Execute stop hooks

## When Invoked
- `/evol cierre`
- Session end

## Art. 3 Compliance
memoria.md is the source of truth. Updated at every significant session close.