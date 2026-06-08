---
name: evol-threat-model
description: Threat-Driven Development. Aplica modelado de amenazas STRIDE antes del desarrollo para definir controles de seguridad obligatorios.
category: discipline-base
trigger: /threat-model
---

# evol-threat-model

## Fase del Pipeline
Spec (Fase 2)

## Artefacto Clave
`docs/specs/THREATS.md`

## Flujo de Trabajo

### 1. Identificar activos y actores adversariales
```bash
# Analizar DOMAIN.md para identificar activos criticos
evol-threat assets --from=docs/specs/DOMAIN.md --output=.evol/threats/assets.json

# Definir actores adversariales
evol-threat actors --output=.evol/threats/actors.json
```

### 2. Construir DFD con fronteras de confianza
```bash
# Generar Data Flow Diagram desde DOMAIN.md
evol-threat dfd --from=docs/specs/DOMAIN.md --output=docs/specs/dfd.mermaid

# Identificar fronteras de confianza
evol-threat trust-boundaries --dfd=docs/specs/dfd.mermaid --output=.evol/threats/trust-zones.json
```

### 3. Aplicar STRIDE por aggregate y endpoint
```bash
# Analizar cada componente del dominio
evol-threat stride --domain=docs/specs/DOMAIN.md --output=.evol/threats/stride-analysis.json

# Generar THR-NNN desde el analisis
evol-threat generate --analysis=.evol/threats/stride-analysis.json --output=docs/specs/THREATS.md
```

### 4. Clasificar amenazas por riesgo
```bash
# Evaluar probabilidad e impacto
evol-threat classify --threats=docs/specs/THREATS.md --output=.evol/threats/classification.json

# Identificar amenazas criticas que bloquean gate
evol-threat critical --classification=.evol/threats/classification.json --output=.evol/threats/critical.json
```

### 5. Generar SEC-REQ y stubs STDD
```bash
# Generar SEC-REQ-NNN para amenazas criticas
evol-threat sec-req --critical=.evol/threats/critical.json --output=docs/specs/SEC-REQ.md

# Copiar SEC-REQ-NNN a SPEC.md
evol-threat copy-sec-req --from=docs/specs/SEC-REQ.md --to=docs/specs/SPEC.md

# Generar stubs STDD desde THREATS.md
evol-threat stubs --threats=docs/specs/THREATS.md --output=tests/security/
```

### 6. Validar THREATS.md
```bash
# Verificar que todos los aggregates tienen al menos una amenaza
evol-threat coverage --threats=docs/specs/THREATS.md --domain=docs/specs/DOMAIN.md

# Validar estructura del archivo
evol-threat validate --file=docs/specs/THREATS.md
```

## Formato THR-NNN

```markdown
## THR-001: IDOR en exportacion de facturas

**Categoria STRIDE:** Elevation of Privilege
**Componente afectado:** Aggregate: Factura
**Vector de ataque:** IDOR en GET /facturas/:id — acceso a facturas de otro tenant
**Probabilidad:** HIGH
**Impacto:** HIGH
**Riesgo:** CRITICO

### Control propuesto
En cada consulta a la tabla `facturas`, agregar una clausula WHERE que verifique
que `tenant_id` coincide con el `tenant_id` extraido del JWT del solicitante.

### Implementacion obligatoria
- El repositorio `FacturaRepository.findById(id, tenantId)` siempre recibe el tenantId
- El servicio extrae el tenantId del contexto de autenticacion, nunca de la URL
- El test STDD verifica que el acceso cross-tenant retorna 403

**SEC-REQ vinculado:** SEC-REQ-001
**Security test requerido:** SI
**Estado:** ABIERTO
```

## Integración con Pipeline

| Fase | Uso |
|------|-----|
| Spec | Amenazas se identifican antes del codigo |
| Spec | SEC-REQ-NNN van a SPEC.md como requisitos |
| Build | Stubs STDD guian el ciclo de seguridad |
| QA | SecDD verifica controles en runtime |
| Retro | Amenazas no mitigadas van a lecciones.md |

## Referencia
- `docs/constitucion.md` Art. 2 (Pipeline gated)
- `docs/disciplinas/THREAT-DRIVEN.md`
- [STRIDE — Microsoft Threat Modeling](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)
- [OWASP Threat Modeling](https://owasp.org/www-community/Threat_Modeling)
