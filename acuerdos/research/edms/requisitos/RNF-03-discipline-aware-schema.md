# RNF-03 — Discipline-Aware Schema

**Estado:** Aprobado | **Prioridad:** Alta

## Descripción

Campo `disciplinas[]` multi-value en metadata. 31 disciplinas como filtro.

## Validación

```python
store.index("Decidimos usar gate HMAC", {
    "disciplinas": ["sec-driven", "ddd"]
})
results = store.search("gate", filters={"disciplinas": "sec-driven"})
assert len(results) > 0
```

## 31 Disciplinas

FDD, DDD, TDD, BDD, SecDD, STDD, QDD, DevDD, InfDD, DataDD, OpsDD, GitDD, DocDD, UXDD, PMDD, AIDDD, EDMS, CompDD, PerfDD, TestDD, RelDD, MigDD, APIDD, EventDD, CacheDD, LogDD, MonDD, AlertDD, IncDD, ComplDD, AuditDD
