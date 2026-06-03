---
name: agent-eval
description: Eval-harness para skills/agents/workflows Evol-DD. 4 grader types. Suite por skill.
category: quality-gate
trigger: /eval
---

# agent-eval

## Philosophy
Eval harness for skills/agents/workflows. Suite per skill with cases.jsonl + grader.yaml.

## Grader Types

### structural
Verify file structure, presence of required elements.

### behavioral
Verify script behavior: exit codes, output format.

### output_match
Exact output matching for deterministic outputs.

### pass_at_k
Pass@k sampling: run k times, succeed if any pass.

### llm_judge
LLM as judge for nuanced evaluation.

## Suite Structure
```
evals/<skill-name>/
  cases.jsonl    # Test cases (one JSON per line)
  grader.yaml    # Grader configuration
```

## Commands
```
/eval run --suite=<skill-name>
/eval list
/eval report <run-id>
```

## Integration
- Runs in CI to gate merges
- Can run locally: evol eval run --suite=NAME
- Results persisted in evol-state.db

## Reference
skills/agent-eval/SKILL.md
