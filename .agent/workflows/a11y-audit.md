---
description: Auditoría de accesibilidad WCAG 2.1 AA. Automatizada en CI + revisión humana de flujos críticos.
---
# /a11y-audit

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-A11Y | **Versión:** 1.0 | **Agente:** Frontend-Developer + Accessibility-Auditor
**Misión:** Producto usable para personas con discapacidad. WCAG 2.1 AA mínimo, AAA donde sea razonable.

## 0. Pre-flight
- Solo aplica si el producto tiene UI (web, mobile, desktop).

## 1. Cobertura automática (CI)
<!-- CONFIGURAR: Herramientas.                                                 -->
<!--  - Web: axe-core (Playwright/Cypress), Pa11y, Lighthouse a11y              -->
<!--  - Mobile: Accessibility Scanner (Android), Accessibility Inspector (iOS)  -->
<!--  - Design system: Storybook + axe addon                                    -->

Tests automatizados verifican:
- Contraste de color (4.5:1 texto normal, 3:1 large)
- Roles ARIA correctos, no abusivos
- Labels en todos los form controls
- Foco visible y orden lógico
- Alternativas de texto en imágenes

## 2. Cobertura manual (no automatizable)
Revisión humana de flujos críticos (signup, checkout, settings):
- **Teclado**: navegación 100% con teclado, sin trampas de foco
- **Lector de pantalla**: VoiceOver (macOS/iOS) + NVDA (Windows) + TalkBack (Android)
- **Zoom 200%** sin pérdida de contenido ni scroll horizontal
- **Reduce motion**: respetar `prefers-reduced-motion`
- **Color**: información no solo por color (probar con simulador daltonismo)

## 3. Componentes
- Design system con componentes accesibles por construcción.
- Cada componente nuevo trae tests a11y antes de merge.
- Documentación de patrones (modales, menús, formularios) sigue ARIA Authoring Practices Guide.

## 4. Contenido
- Estructura semántica (h1-h6 correctos, landmarks).
- Idioma declarado (`<html lang>`) — cruzar con `/i18n-setup`.
- Vídeos con subtítulos, transcripciones de audio.

## 5. CI gate
- PR bloquea si violación nivel `serious` o `critical`.
- Violaciones `moderate` permitidas con justificación temporal y issue trackeado.

## 6. Cierre
- Reporte a `qa-review` Tier 2.
- Hallazgos críticos a `lecciones.md`.
- Roadmap de mejoras a11y mantenido (no "lo arreglamos cuando podamos").
