---
name: evol-talk-compact
description: Compresion de output del orquestador X-DD. 3 niveles. Ahorro tokens ~50-75%.
category: compression
trigger: /compact-talk
---

# evol-talk-compact

## Philosophy
Orquestador output compression inspired by caveman (juliusbrussee/caveman, MIT).

## Levels
- **light**: Remove redundant headers, keep technical precision
- **medium**: Fragment sentences, drop articles/fillers
- **aggressive**: Keep only technical terms + action verbs

## Example Transformations
| Original | Compacted |
|----------|-----------|
| "The answer is 4." | "4" |
| "Based on the information provided, the answer is..." | "[info provided] → ..." |
| "I will now execute the following command..." | "Exec: ..." |

## When to Use
- Orchestrator verbose output
- Multi-agent coordination logs
- CI/CD pipeline output

## Reference
skills/evol-talk-compact/SKILL.md