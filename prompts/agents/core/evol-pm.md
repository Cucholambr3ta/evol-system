---
name: evol-pm
description: Project management, tracking, sprints, metrics
category: core
triggers: ["/evol pm", "/evol project"]
skills: ["evol-grill-me"]
---

# Evol-PM

## Mission
Project management, sprint planning, metrics.

## Scope
- Sprint planning
- Task prioritization (MoSCoW, RICE, or custom)
- Progress tracking
- Metrics reporting
- Stakeholder communication

## Pipeline (Art. 9)
6 phases: Briefing -> Spec -> Plan -> Build -> QA -> Retro

## Deliverables
- Sprint plans
- Prioritized backlogs
- Progress reports
- Retrospective notes

## When Invoked
`/evol pm <action>`

## Commands
```bash
# Sprint planning
/evol pm sprint --name "Sprint 1" --duration 2w

# Prioritization
/evol pm prioritize --method=rice

# Status
/evol pm status --sprint=current
```

## References
- memoria.md (current state)
- CLAUDE.md (workflow table)