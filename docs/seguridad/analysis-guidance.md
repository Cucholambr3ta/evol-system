# Analysis Guidance — Adversarial Prioritization

Use this guidance to prioritize security findings by real adversarial impact,
not by theoretical severity.

## Decision Framework

For each finding, answer in order:

1. REACHABILITY: Can an attacker actually trigger this?
   - Is the vulnerable code path reachable from an untrusted input?
   - Are there authentication/authorization barriers in the path?
   - If not reachable: downgrade severity by one level.

2. EXPLOITABILITY: Can it be reliably exploited?
   - Is a working PoC constructible with known techniques?
   - Are mitigations (ASLR, canary, NX) in place and effective?
   - If not exploitable: downgrade severity by one level.

3. IMPACT: What can the attacker achieve?
   - CIA triad: Confidentiality, Integrity, Availability
   - Blast radius: single user vs all users vs system
   - If limited blast radius: downgrade severity by one level.

4. REMEDIATION COST: How hard is it to fix?
   - Quick fix (1-2 lines): fix immediately
   - Design change (architectural): plan for next sprint, mitigate now
   - Third-party dep: pin version + file issue

## Priority Queue

After evaluating all findings:

| Priority | Criteria | Action |
|----------|---------|--------|
| P0 | CRITICAL + reachable + exploitable | Block gate immediately |
| P1 | HIGH + reachable | Fix before next phase |
| P2 | HIGH + not reachable OR MEDIUM + reachable | Fix in current sprint |
| P3 | MEDIUM + not reachable OR LOW | Backlog |
| P4 | INFO | Document, no action required |

## Analyst Loop

After presenting findings, offer this menu:
1. Deep — Analyze top P0/P1 findings in full 4-mode pipeline
2. Fix — Generate patches for confirmed findings
3. Report — Generate THREATS.md / findings.json summary
4. Scope — Retry with different scope (single file, single module)
5. Done — Close analysis session, update memoria.md
