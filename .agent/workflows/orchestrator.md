---
name: /evol orchestrate
description: Lead agent composition, coordination patterns
trigger: /evol orchestrate
category: core
---

# Evol-Orchestrator

## Mission
Coordinate multi-agent workflows, delegate to specialists.

## Patterns
- sequential: lead first, then specialists
- parallel: lead first, specialists concurrent (max 5 workers)
- parallel_then_sync: parallel with sync point (300s timeout)
- party: N agents free-form

## Scope
- Agent composition
- Workflow orchestration
- Result aggregation

## When Invoked
- `/evol orchestrate --pattern=<pattern> --agents=<list>`
- Multi-agent task