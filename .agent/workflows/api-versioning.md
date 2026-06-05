---
name: api-versioning
trigger: /evol api-versioning
description: API Versioning-Driven Development (APIVDD). Define la estrategia de versionado y las politicas de deprecacion ANTES de implementar cambios en la API. Detecta breaking changes, genera deprecation_schedule y guias de migracion. Usar en APIs publicas con multiples versiones conviviendo o consumidores externos. Disciplina docs/disciplinas/APIVDD.md.
phase: plan
category: api
---

# /evol api-versioning — API Versioning-Driven Development (APIVDD)

> **Estandar de documentacion:** cumple [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md).
> Disciplina: [`docs/disciplinas/APIVDD.md`](../../docs/disciplinas/APIVDD.md).

**ID:** FLUJO-APIVDD | **Version:** 1.0 | **Agente:** Versioning-Policy (efimero) + Architect
**Mision:** Planificar el versionado y la deprecacion de la API antes de romper a un consumidor.
**Activacion:** solo si `evol.profile.yml` declara `apivdd` en `methodologies:`.

## 0. Pre-flight

- Requiere `api/openapi.yaml` (ODD_API) o `api/openapi_v{n}.yaml`.
- Lee `acuerdos/memoria/MEMORY.md` + lecciones (Art. 3).
- Si no hay contrato OpenAPI: ABORT -> ejecutar `/evol api-contract` primero.

## 1. Detectar breaking changes

Comparar el contrato nuevo contra la version anterior. Clasificar cada cambio:
- **Compatible** (additive): nuevo endpoint/campo opcional.
- **Breaking**: cambio de tipo, campo removido, semantica alterada.

## 2. Estrategia de versionado

Decidir y documentar: versionado en path (`/v2`), header, o media-type. Aplicar
[SemVer](https://semver.org/) al contrato. Registrar la decision (enlazar ADR si aplica).

## 3. Calendario de deprecacion

`api_versions/deprecation_schedule.json`: por version deprecada, fecha de sunset, version de
reemplazo, y canal de comunicacion al consumidor.

## 4. Guias de migracion

`api_versions/breaking_changes/<cambio>.md`: por cada breaking change, el plan de migracion
paso a paso para el consumidor.

## 5. Output + gate (worker -> auditor)

- Sidecar `.json` via `evol-doc-sync`. Fuentes con URL (DOC_STANDARD).
- Configurar check de breaking changes en CI.
- **Auditor** rechaza cualquier breaking change sin plan de migracion documentado.

## 6. Integracion

- Opera sobre el contrato de [ODD_API](../../docs/disciplinas/ODD_API.md).
- Alimenta [DeprecationDD](../../docs/disciplinas/DeprecationDD.md) (sunset del codigo viejo).
- [CCDD](../../docs/disciplinas/CCDD.md) detecta que consumidores rompe cada cambio.

---
*X-DD — disciplina APIVDD. Ver [docs/disciplinas/APIVDD.md](../../docs/disciplinas/APIVDD.md).*
