---
description: Release de app móvil (iOS/Android). Signing, store submission, beta tracks, rollout escalonado.
---
# /mobile-release

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-MOB-REL | **Versión:** 1.0 | **Agente:** Mobile-App-Builder + Release-Manager
**Misión:** Publicar a App Store y Play Store sin sustos. Beta, rollout escalonado, kill switches listos.

## 0. Pre-flight
- Verifica `xdd.profile.yml > profile: mobile` (o `capabilities.mobile_release: true`).
- Requiere `/qa-review` aprobado y release candidate identificado.

## 1. Versionado
- `versionName` semver (1.2.3) + `versionCode` monotónico (incremental).
- Tag git `mobile-v<X.Y.Z>`.

## 2. Signing
<!-- CONFIGURAR: Gestión de credenciales de firma.                            -->
<!--  - iOS: App Store Connect API key + Match (fastlane) o cuenta manual       -->
<!--  - Android: keystore en secret manager + Google Play Service Account       -->
<!--  - Multiplataforma: EAS (Expo), Codemagic, Bitrise, fastlane               -->

Reglas:
- Keystores y API keys nunca en repo. Solo secret manager.
- Rotación de credenciales documentada en `runbooks/mobile-signing-rotation.md`.
- Acceso a release builds restringido (principio de mínimo privilegio).

## 3. Build
- Build reproducible en CI (no en máquina local del dev para release).
- Output: IPA (iOS) y AAB (Android).
- Tamaño binario contra `perf-budget` (alerta si > X MB).

## 4. Beta
- iOS: TestFlight (interno → externo).
- Android: Internal testing → Closed testing → Open testing.
- Período de soak mínimo (24-72h) antes de producción.

## 5. Producción
- Rollout escalonado (Android: 5% → 20% → 50% → 100%; iOS: phased release 7 días).
- Métricas a vigilar: crash-free users, ANR rate, retention, conversiones críticas.
- Kill switches (`/feature-flag` con prefijo `kill_*`) listos para degradación.

## 6. Store assets
- Screenshots actualizados por idioma (cruzar con `/i18n-setup`).
- Release notes user-facing (cruzar con `/release-cut`).
- Privacy nutrition labels (iOS) / Data safety (Android) coherentes con `PRIVACY.md`.

## 7. Post-release
- Monitorear crash dashboard 48h.
- Si crash-free < umbral o ANR alta → pause rollout + investigación.
- Lecciones a [[lecciones]].

## 8. Gated (Art. 2)
`"APROBADO"` antes de:
- Subir a App Store Connect / Play Console.
- Promover rollout a > 25%.
- Forzar update (mandatory upgrade).
