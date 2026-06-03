---
name: evol-sandbox
description: Provider-agnostic sandbox skill. Backends E2B, Daytona, Microsandbox, local docker, none.
category: security
trigger: /sandbox
---

# evol-sandbox

## Philosophy
Sandbox execution for untrusted code. Multiple backend support with graceful fallback.

## Backends
- **E2B**: cloud sandbox (requires API key)
- **Daytona**: cloud sandbox (requires credentials)
- **Microsandbox**: lightweight local isolation
- **local-docker**: docker-based isolation
- **none**: no sandbox (insecure, requires explicit flag)

## When to Use
- Running untrusted code
- Security testing (fuzzing, penetration testing)
- Contract test execution
- Stress testing

## Commands
```
/sandbox exec --backend=<backend> <command>
/sandbox list
/sandbox status
/sandbox health
```

## Security Rules
- Never execute untrusted code outside sandbox
- Scan with evol-shield before sandbox execution
- Log all sandbox executions

## Reference
skills/evol-sandbox/SKILL.md