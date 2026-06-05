---
name: iac-driven
trigger: /evol iac-driven
description: Infrastructure-as-Code-Driven Development (IODD). Especifica los recursos de infraestructura como codigo declarativo desde la fase de spec. Produce infra/main.tf (modulos) + dependencies_graph.json, recreable desde cero y sin recursos manuales en consola. Usar en proyectos cloud o con infraestructura automatizada. Disciplina docs/disciplinas/IODD.md.
phase: spec
category: devops
---

# /evol iac-driven — Infrastructure-as-Code-Driven Development (IODD)

> **Estandar de documentacion:** cumple [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md).
> Disciplina: [`docs/disciplinas/IODD.md`](../../docs/disciplinas/IODD.md).

**ID:** FLUJO-IODD | **Version:** 1.0 | **Agente:** Infra-Coder (efimero) + DevOps
**Mision:** Declarar la infraestructura como codigo modular, versionado y recreable desde cero.
**Activacion:** solo si `evol.profile.yml` declara `iodd` en `methodologies:`.

## 0. Pre-flight

- Requiere `docs/specs/SPEC.md` (NFR) y los ADRs de infraestructura ([ADD](../../docs/disciplinas/ADD.md)).
- Lee `acuerdos/memoria/MEMORY.md` + lecciones (Art. 3).
- Si no hay NFR ni decisiones de infra: ABORT -> completar Spec/ADD primero.

## 1. Especificar recursos como modulos

`infra/main.tf` (+ modulos por dominio: red, computo, datos, IAM). Declarativo, parametrizado
por entorno (dev/staging/prod). Herramienta: Terraform u [OpenTofu](https://github.com/opentofu/opentofu).

## 2. Grafo de dependencias

`infra/dependencies_graph.json`: relaciones entre recursos (que depende de que). Permite
razonar el orden de aprovisionamiento y el blast radius de un cambio.

## 3. Validacion (dry-run)

- `terraform validate` (o `tofu validate`).
- `terraform plan` por entorno: el plan debe ser limpio y reproducible.
- Estimacion de costo si la tooling lo permite.

## 4. Tests de infraestructura

Tests que verifican propiedades clave (puertos cerrados por defecto, cifrado en reposo,
tags obligatorios). Sin recursos manuales en consola.

## 5. Output + gate (worker -> auditor)

- Sidecar `.json` via `evol-doc-sync`. Fuentes con URL (DOC_STANDARD).
- **Auditor** rechaza si: `plan` no limpio, hay drift, o recursos creados a mano.

## 6. Integracion

- Las decisiones vienen de [ADD](../../docs/disciplinas/ADD.md).
- El deploy de [Pipeline-Driven](../../docs/disciplinas/PIPELINE-DRIVEN.md) consume esta infra.
- La observabilidad ([ODD_Obs](../../docs/disciplinas/ODD_OBS.md)) se aprovisiona aqui.

---
*Evol-DD — disciplina IODD. Ver [docs/disciplinas/IODD.md](../../docs/disciplinas/IODD.md).*
