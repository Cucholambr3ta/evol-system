---
description: Corte de release con semver, CHANGELOG automático y release notes user-facing.
---
# /release-cut

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-REL | **Versión:** 1.0 | **Agente:** Release-Manager + Git-Workflow-Master
**Misión:** Releases predecibles, trazables y comunicadas. Sin "qué cambió en esta versión?".

## 0. Pre-flight
- Verifica que estás en rama `release/*` o `main` con todo verde.
- Verifica que todos los commits siguen Conventional Commits (`feat:`, `fix:`, `chore:`, `BREAKING CHANGE:`).
- Verifica que `/qa-review` pasó en la rama.

## 1. Determinar versión (semver)
Calcula bump desde commits desde último tag:
- `BREAKING CHANGE` o `!` → major
- `feat:` → minor
- `fix:`, `perf:`, `refactor:` → patch
- Solo `chore:`, `docs:`, `test:` → no release

Pregunta al usuario para confirmar el bump propuesto.

<!-- CONFIGURAR: Herramienta de versionado/changelog. Opciones:                 -->
<!--  - semantic-release (Node) / release-please (poliglota, GitHub-native)     -->
<!--  - changesets (monorepos JS/TS)                                            -->
<!--  - cz-cli + standard-version                                               -->
<!--  - cargo-release (Rust), goreleaser (Go), poetry-dynamic-versioning (Py)   -->

## 2. Generar CHANGELOG
Auto-generar/actualizar `CHANGELOG.md` (Keep a Changelog format) agrupando:
- Added, Changed, Deprecated, Removed, Fixed, Security.

## 3. Release notes user-facing
Crear `RELEASES/v<X.Y.Z>.md` desde `templates/release-notes.template.md`. Traducir tech-speak a beneficios. Pedir al usuario edición final.

## 4. Tag y push
- Tag firmado: `git tag -s v<X.Y.Z> -m "Release v<X.Y.Z>"`
- Push tag y rama.
- CI dispara build de artefactos y release en plataforma (GitHub Releases, npm, Docker Hub, etc.).

## 5. Comunicación
- Publicar release notes en canal habitual (in-app, blog, email, Discord).
- Actualizar status page si aplica.
- Cerrar issues vinculados.

## 6. Post-release
- Monitorear métricas críticas durante ventana de observación (1-24h).
- Si regresión → `/rollback`.
- Si éxito → `/cierre-fase` para retro.

## 7. Gated (Art. 2)
`"APROBADO"` antes de publicar tag major o cambios breaking.
