---
description: Configura internacionalización del proyecto. Extracción, locales, RTL, formato de fechas/números.
---
# /i18n-setup

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-I18N | **Versión:** 1.0 | **Agente:** I18n-Engineer + Frontend-Developer
**Misión:** Habilitar el producto para múltiples idiomas y regiones sin retrabajos.

## 0. Pre-flight
- Verifica si el perfil declara `capabilities.i18n: true` en `xdd.profile.yml`.
- Si no, pregunta si activar.

## 1. Alcance
Define en `memoria.md`:
- Idiomas iniciales (con `default`).
- Si soporta RTL (árabe, hebreo).
- Regiones (en-US vs en-GB) y plurales (CLDR).
- Contenido dinámico (BD vs estático).

## 2. Stack
<!-- CONFIGURAR: Stack de i18n por plataforma.                                -->
<!--  - React/Next: i18next, react-intl (FormatJS), Lingui, next-intl          -->
<!--  - Vue: vue-i18n                                                          -->
<!--  - Mobile: react-i18next, Flutter intl, native (Localizable.strings)      -->
<!--  - Backend: ICU MessageFormat (errors, emails)                            -->

## 3. Estructura de archivos
```
locales/
  en/
    common.json
    errors.json
    emails.json
  es/
    common.json
    ...
```

## 4. Convenciones
- Claves jerárquicas (`checkout.title`, `errors.network.timeout`).
- Nunca concatenar strings — usar interpolación + ICU para plurales y género.
- Fechas/números con `Intl.DateTimeFormat` / `Intl.NumberFormat` (nunca formateo manual).
- Imágenes con texto evitadas; usar SVG con texto traducible.

## 5. Extracción y traducción
- Comando `i18n:extract` corre en pre-commit (no commitear código con strings sueltos).
- Pipeline a TMS (Crowdin, Lokalise, Phrase) o gestión manual en repo.
- Idioma fallback siempre completo.

## 6. Testing
- Pseudo-localización en CI (acentos + expansión) para detectar overflow UI.
- Snapshot por locale crítico.

## 7. Cierre
- Documenta en `README.md` proceso de añadir nuevo locale.
- Actualiza `FEATURES.md` con coverage por locale.
