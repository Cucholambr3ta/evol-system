---
name: evol-governance
description: Policy-as-code y gobernanza automatizada. Define, implementa y ejecuta políticas como código para compliance y calidad.
category: transfer
trigger: /governance
---

# evol-governance

## Cuándo Usar

Activar esta skill cuando se necesita gobernanza automatizada:

- **Policy-as-code**: definir políticas en código, no en documentos
- **Compliance automation**: automatizar verificación de compliance
- **Policy enforcement**: ejecutar políticas automáticamente
- **Audit automation**: generar reportes de compliance automáticamente
- **Guardrails**: restricciones que previenen violaciones
- **Governance frameworks**: estructuras de gobierno para equipos/proyectos

**No usar para**: seguridad del código (usar evol-sec), gestión de proyectos (usar evol-pm).

## Conocimiento de Dominio

### Policy-as-Code
- **Declarative policies**: definir qué se permite, no cómo implementar
- **OPA (Open Policy Agent)**: lenguaje Rego para policy enforcement
- **Sentinel**: Hashicorp policy as code framework
- **Kyverno**: Kubernetes-native policy engine
- **Custom rules**: reglas específicas del proyecto/organización

### Compliance Frameworks
- **SOC 2**: security, availability, processing integrity, confidentiality, privacy
- **GDPR**: data protection, consent, right to be forgotten
- **HIPAA**: health information protection
- **PCI DSS**: payment card data security
- **ISO 27001**: information security management

### Policy Patterns
- **Preventive policies**: block violations before they happen
- **Detective policies**: identify violations after they happen
- **Corrective policies**: fix violations automatically
- **Compensating policies**: alternative controls when primary not feasible

### Automation Patterns
- **CI/CD integration**: policy checks in pipeline
- **Git hooks**: pre-commit, pre-push policy enforcement
- **Admission controllers**: Kubernetes admission control
- **Webhooks**: real-time policy enforcement
- **Scheduled scans**: periodic compliance checks

### Governance Structures
- **RACI matrix**: who's Responsible, Accountable, Consulted, Informed
- **Decision logs**: record of who decided what and why
- **Approval workflows**: gates for critical decisions
- **Escalation paths**: how to handle exceptions
- **Regular reviews**: periodic governance reviews

## Flujo de Trabajo

1. **Identify governance needs**: what policies are needed? compliance requirements?
2. **Define policies**: declarative rules, clear language, testable
3. **Implement as code**: OPA/Sentinel/custom, version controlled
4. **Integrate into pipeline**: CI/CD checks, git hooks, admission control
5. **Test policies**: verify they work, don't block legitimate work
6. **Deploy enforcement**: activate policies, monitor violations
7. **Handle exceptions**: exception process, approval workflow
8. **Review and iterate**: regular policy reviews, update as needed

## Integración con Pipeline

- **Briefing (Fase 1)**: understand compliance requirements, governance needs
- **Spec (Fase 2)**: document policies, compliance requirements, enforcement points
- **Plan (Fase 3)**: design policy architecture, select tools
- **Build (Fase 4)**: implement policies as code, integrate into pipeline
- **QA (Fase 5)**: test policy enforcement, verify no false positives
- **Retro (Fase 6)**: review policy effectiveness, update based on learnings

## Referencia

- Constitución Evol-DD: Art. 2 (gated pipeline - policy enforcement)
- Art. 8 (engineering standards - policy compliance)
- Agentes relacionados: evol-sec (security policies), evol-devops (CI/CD integration), evol-compliance-auditor (compliance verification)
- Open Policy Agent: https://www.openpolicyagent.org
- Hashicorp Sentinel: https://www.hashicorp.com/sentinel
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework
- Thoughtworks Technology Radar: policy as code
