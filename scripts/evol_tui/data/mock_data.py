"""Mock data para EVOL-DD TUI wireframe."""
from typing import Dict, List, Any

AGENTS: List[Dict[str, Any]] = [
    {"id": "evol-architect",    "specialty": "Arquitectura, ADRs",     "status": "active",   "runs": 42,  "last": "Hoy"},
    {"id": "evol-builder",      "specialty": "Implementación, TDD",    "status": "active",   "runs": 89,  "last": "Hoy"},
    {"id": "evol-qa",           "specialty": "Testing, Gherkin, BDD",  "status": "active",   "runs": 67,  "last": "Ayer"},
    {"id": "evol-sec",          "specialty": "Seguridad, STRIDE",      "status": "active",   "runs": 31,  "last": "Hoy"},
    {"id": "evol-devops",       "specialty": "CI/CD, pipelines",       "status": "active",   "runs": 18,  "last": "Hoy"},
    {"id": "evol-domain",       "specialty": "DDD, bounded contexts",  "status": "active",   "runs": 24,  "last": "Ayer"},
    {"id": "evol-doc",          "specialty": "Documentación",          "status": "active",   "runs": 56,  "last": "Hoy"},
    {"id": "evol-ux",           "specialty": "Discovery, validación",  "status": "inactive", "runs": 8,   "last": "3d"},
    {"id": "evol-data",         "specialty": "Data engineering",       "status": "inactive", "runs": 12,  "last": "5d"},
    {"id": "evol-reviewer",     "specialty": "Code review",            "status": "active",   "runs": 44,  "last": "Hoy"},
    {"id": "evol-orchestrator", "specialty": "Coordinación multi-ag.", "status": "active",   "runs": 15,  "last": "Hoy"},
    {"id": "evol-pm",           "specialty": "Proyecto, sprints",      "status": "active",   "runs": 29,  "last": "Ayer"},
    {"id": "evol-release",      "specialty": "Releases, CHANGELOG",    "status": "active",   "runs": 11,  "last": "2d"},
    {"id": "evol-analyst",      "specialty": "Impacto, blast radius",  "status": "active",   "runs": 37,  "last": "Hoy"},
    {"id": "evol-agent-factory","specialty": "Crear agentes efímeros", "status": "inactive", "runs": 6,   "last": "7d"},
    {"id": "evol-researcher",   "specialty": "Investigación autónoma", "status": "active",   "runs": 9,   "last": "2d"},
    {"id": "evol-sec-analyst",  "specialty": "Análisis CVE",           "status": "inactive", "runs": 4,   "last": "10d"},
    {"id": "evol-compliance",   "specialty": "Compliance, GDPR",       "status": "active",   "runs": 7,   "last": "3d"},
]

SKILLS: List[Dict[str, Any]] = [
    {"id": "evol-sdd-spec",        "category": "discipline", "desc": "Spec-Driven Development",     "phase": "Todas"},
    {"id": "evol-fdd-feature",     "category": "discipline", "desc": "Feature-Driven Development",  "phase": "1+3"},
    {"id": "evol-ddd-domain",      "category": "discipline", "desc": "Domain-Driven Design",        "phase": "2"},
    {"id": "evol-bdd-behavior",    "category": "discipline", "desc": "Behavior-Driven Development", "phase": "1+5"},
    {"id": "evol-atdd-acceptance", "category": "discipline", "desc": "Acceptance Test-Driven",      "phase": "1+5"},
    {"id": "evol-tdd-unit",        "category": "discipline", "desc": "Test-Driven Development",     "phase": "4"},
    {"id": "evol-stdd-security-test", "category": "discipline", "desc": "Security-Test-Driven",    "phase": "4"},
    {"id": "evol-secdd-security",  "category": "discipline", "desc": "Security-Driven Development", "phase": "5"},
    {"id": "evol-threat-model",    "category": "discipline", "desc": "Threat-Driven Development",   "phase": "2"},
    {"id": "agent-eval",           "category": "core",       "desc": "Eval & Testing",              "phase": "-"},
    {"id": "code-indexer",         "category": "core",       "desc": "Code Analysis",               "phase": "-"},
    {"id": "crear-agente",         "category": "core",       "desc": "Agent Lifecycle",             "phase": "-"},
    {"id": "evol-compact",         "category": "core",       "desc": "Context Engineering",         "phase": "-"},
    {"id": "evol-context7",        "category": "core",       "desc": "Documentation",               "phase": "-"},
    {"id": "evol-frontend-design", "category": "core",       "desc": "UI Design",                   "phase": "-"},
    {"id": "evol-sandbox",         "category": "core",       "desc": "Execution",                   "phase": "-"},
    {"id": "readme-master",        "category": "core",       "desc": "Documentation",               "phase": "-"},
]

PROJECTS: List[Dict[str, Any]] = [
    {"id": "saas-platform",      "name": "SaaS Platform",      "phase": "Build",    "health": 88, "tasks": 34},
    {"id": "api-gateway",        "name": "API Gateway v3",     "phase": "QA",       "health": 91, "tasks": 18},
    {"id": "auth-domain",        "name": "Auth Domain",        "phase": "Plan",     "health": 76, "tasks": 22},
    {"id": "payment-domain",     "name": "Payment Domain",     "phase": "Spec",     "health": 82, "tasks": 14},
    {"id": "analytics-pipeline", "name": "Analytics Pipeline", "phase": "Briefing", "health": 95, "tasks": 8},
]

DISCIPLINES: List[Dict[str, Any]] = [
    {"id": "SDD",        "type": "base",     "name": "SDD — Spec-Driven Development",       "phase": "Todas", "skill": "evol-sdd-spec"},
    {"id": "FDD",        "type": "base",     "name": "FDD — Feature-Driven Development",    "phase": "1+3",   "skill": "evol-fdd-feature"},
    {"id": "DDD",        "type": "base",     "name": "DDD — Domain-Driven Design",          "phase": "2",     "skill": "evol-ddd-domain"},
    {"id": "BDD",        "type": "base",     "name": "BDD — Behavior-Driven Development",   "phase": "1+5",   "skill": "evol-bdd-behavior"},
    {"id": "ATDD",       "type": "base",     "name": "ATDD — Acceptance Test-Driven",       "phase": "1+5",   "skill": "evol-atdd-acceptance"},
    {"id": "TDD",        "type": "base",     "name": "TDD — Test-Driven Development",       "phase": "4",     "skill": "evol-tdd-unit"},
    {"id": "STDD",       "type": "base",     "name": "STDD — Security-Test-Driven",         "phase": "4",     "skill": "evol-stdd-security-test"},
    {"id": "SecDD",      "type": "base",     "name": "SecDD — Security-Driven Development", "phase": "5",     "skill": "evol-secdd-security"},
    {"id": "THREAT",     "type": "base",     "name": "Threat-Driven Development",           "phase": "2",     "skill": "evol-threat-model"},
    {"id": "ODD_API",    "type": "extended", "name": "ODD_API — OpenAPI-Driven",            "phase": "2",     "skill": "evol-odd-api"},
    {"id": "UXDD",       "type": "extended", "name": "UXDD — UX-Driven Development",        "phase": "1",     "skill": "evol-uxdd-ux"},
    {"id": "A11yDD",     "type": "extended", "name": "A11yDD — Accessibility-Driven",       "phase": "1+5",   "skill": "evol-a11ydd"},
    {"id": "RDD",        "type": "extended", "name": "RDD — Refactoring-Driven",            "phase": "4",     "skill": "evol-rdd-refactor"},
    {"id": "PDD",        "type": "extended", "name": "PDD — Performance-Driven",            "phase": "5",     "skill": "evol-pdd-perf"},
    {"id": "CHAOS",      "type": "extended", "name": "Chaos — Resiliency-Driven",           "phase": "5",     "skill": "evol-chaos-resilience"},
    {"id": "MDD",        "type": "extended", "name": "MDD — Migration-Driven",              "phase": "3",     "skill": "evol-mdd-migrate"},
    {"id": "ESDD",       "type": "extended", "name": "ESDD — Event Sourcing-Driven",        "phase": "2",     "skill": "evol-esdd-events"},
    {"id": "CCDD",       "type": "extended", "name": "CCDD — Consumer-Driven Contract",     "phase": "5",     "skill": "evol-ccdd-contract"},
    {"id": "APIVDD",     "type": "extended", "name": "APIVDD — API Versioning-Driven",      "phase": "3",     "skill": "evol-apivdd"},
    {"id": "ODD_OBS",    "type": "extended", "name": "ODD_Obs — Observability-Driven",      "phase": "5",     "skill": "evol-odd-obs"},
    {"id": "IODD",       "type": "extended", "name": "IODD — Infrastructure-as-Code",       "phase": "2",     "skill": "evol-iodd-iac"},
    {"id": "PIPELINE",   "type": "extended", "name": "Pipeline-Driven",                     "phase": "4",     "skill": "evol-pipeline-ci"},
    {"id": "COMPLIANCE", "type": "extended", "name": "Compliance-Driven",                   "phase": "2",     "skill": "evol-compliance-drivers"},
    {"id": "PRIVACY",    "type": "extended", "name": "PrivacyDD — Privacy by Design",       "phase": "2",     "skill": "evol-privacy-drivers"},
    {"id": "DEBT",       "type": "extended", "name": "DebtBudgetDD — Tech Debt Budgeting",  "phase": "3",     "skill": "evol-debt-budget"},
    {"id": "DEPRECATION","type": "extended", "name": "DeprecationDD — Deprecation-Driven",  "phase": "3",     "skill": "evol-deprecation"},
    {"id": "ADD",        "type": "extended", "name": "ADD — Architecture Decision-Driven",  "phase": "2",     "skill": "evol-add-arch"},
    {"id": "EDA",        "type": "extended", "name": "EDA — Event-Driven Architecture",     "phase": "2",     "skill": "evol-eda"},
    {"id": "UDD",        "type": "extended", "name": "UDD — Use-Case-Driven",               "phase": "1",     "skill": "evol-udd-usecase"},
    {"id": "CDCDD",      "type": "extended", "name": "CDCDD — Change Data Capture",         "phase": "3",     "skill": "evol-cdcdd"},
    {"id": "SLODRIVEN",  "type": "extended", "name": "SLO/SLA-Driven",                      "phase": "5",     "skill": "evol-slo-sla"},
]

MEMORY_DRAWERS: List[Dict[str, Any]] = [
    {"id": "api-gateway",   "items": 14, "tier": "knowledge",  "vectors": 38},
    {"id": "auth-domain",   "items": 22, "tier": "memory",     "vectors": 67},
    {"id": "saas-platform", "items": 23, "tier": "memory",     "vectors": 91},
    {"id": "decisiones",    "items": 18, "tier": "knowledge",  "vectors": 44},
    {"id": "lecciones",     "items": 17, "tier": "memory",     "vectors": 52},
    {"id": "riesgos",       "items": 9,  "tier": "compressed", "vectors": 21},
    {"id": "convenciones",  "items": 11, "tier": "memory",     "vectors": 33},
    {"id": "payment-domain","items": 7,  "tier": "raw",        "vectors": 14},
]

ACTIVITY_LOG: List[Dict[str, Any]] = [
    {"text": "evol-builder movió TSK-208 a QA",          "time": "hace 5m"},
    {"text": "evol-qa cerró AUTH-95",                    "time": "hace 12m"},
    {"text": "Gate aprobado — SaaS Platform → Build",   "time": "hace 28m"},
    {"text": "Nueva entidad extraída: AuthService",      "time": "hace 41m"},
    {"text": "Conflicto detectado: definición duplicada","time": "hace 1h"},
    {"text": "evol-architect creó ADR-012",              "time": "hace 2h"},
    {"text": "Sprint 27 cerrado — 38 puntos entregados", "time": "hace 3h"},
]

GATES: List[Dict[str, Any]] = [
    {"project": "SaaS Platform", "from_phase": "Build", "to_phase": "QA",    "status": "pending"},
    {"project": "API Gateway v3","from_phase": "QA",    "to_phase": "Retro", "status": "pending"},
    {"project": "Auth Domain",   "from_phase": "Spec",  "to_phase": "Plan",  "status": "pending"},
]

ANALYTICS: Dict[str, Any] = {
    "velocity":         [28, 31, 29, 35, 38],
    "health":           [74, 78, 80, 79, 82],
    "sprints":          ["S24", "S25", "S26", "S27", "S28"],
    "risk":             [3, 4, 3, 5, 2],
    "blocked":          12,
    "velocity_current": 38,
    "health_current":   82,
}
