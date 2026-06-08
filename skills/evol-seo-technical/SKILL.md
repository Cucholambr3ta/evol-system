---
name: evol-seo-technical
description: Technical SEO: Core Web Vitals, structured data, technical architecture para que el software sea encontrable.
category: transfer
trigger: /seo
---

# evol-seo-technical

## Cuándo Usar

Activar esta skill cuando se necesita optimizar el SEO técnico del software:

- **Core Web Vitals**: LCP, FID/INP, CLS - métricas de experiencia que Google mide
- **Structured data**: schema.org, JSON-LD, rich results
- **Technical architecture**: crawlability, indexability, site structure
- **Page speed**: optimización de rendimiento para SEO
- **Mobile-first**: responsive design, mobile indexing
- **International SEO**: hreflang, multi-language, multi-region

**No usar para**: content SEO y keyword research (usar evol-domain-marketing), analytics de tráfico (usar evol-data).

## Conocimiento de Dominio

### Core Web Vitals
- **LCP (Largest Contentful Paint)**: <2.5s, qué tan rápido carga el contenido principal
- **INP (Interaction to Next Paint)**: <200ms, qué tan rápido responde a interacciones
- **CLS (Cumulative Layout Shift)**: <0.1, qué tan estable es el layout visual
- **TTFB (Time to First Byte)**: <800ms, qué tan rápido responde el servidor

### Structured Data
- **JSON-LD**: formato recomendado para structured data
- **Schema.org**: vocabulario estándar para tipos de datos
- **Rich results**: featured snippets, knowledge panels, carousels
- **Validation**: Google Rich Results Test, Schema.org validator

### Technical Architecture
- **Crawlability**: can search engines discover all pages?
- **Indexability**: can search engines index all important pages?
- **Sitemap**: XML sitemap, updated regularly, submitted to Search Console
- **Robots.txt**: allow/disallow crawling, important directives
- **Canonical tags**: prevent duplicate content issues
- **Internal linking**: logical structure, anchor text optimization

### Page Speed
- **Image optimization**: WebP, lazy loading, responsive images
- **Code splitting**: load only what's needed
- **Caching**: browser caching, CDN, service workers
- **Compression**: gzip, brotli
- **Critical rendering path**: prioritize above-the-fold content

### Mobile SEO
- **Mobile-first indexing**: Google indexes mobile version first
- **Responsive design**: one URL, adapts to screen size
- **Touch targets**: minimum 48px, adequate spacing
- **Viewport meta**: proper viewport configuration
- **AMP**: accelerated mobile pages (less relevant now)

### International SEO
- **hreflang**: language/region targeting
- **URL structure**: ccTLD, subdirectory, subdomain
- **Content localization**: not just translation, cultural adaptation
- **Multi-region**: targeting multiple countries with same language

## Flujo de Trabajo

1. **Audit técnico**: crawl site, identify issues (broken links, redirects, etc.)
2. **Measure Core Web Vitals**: Lighthouse, PageSpeed Insights, CrUX data
3. **Review structured data**: validate existing, identify opportunities
4. **Analyze site architecture**: crawlability, indexability, internal linking
5. **Optimize page speed**: images, code, caching, compression
6. **Ensure mobile compliance**: responsive, touch targets, viewport
7. **Implement international SEO**: hreflang, URL structure if multi-language
8. **Monitor and iterate**: Search Console, rankings, traffic changes

## Integración con Pipeline

- **Briefing (Fase 1)**: understand SEO goals, target keywords, competition
- **Spec (Fase 2)**: document technical SEO requirements, structured data needs
- **Plan (Fase 3)**: prioritize SEO improvements by impact × effort
- **Build (Fase 4)**: implement SEO best practices during development
- **QA (Fase 5)**: test Core Web Vitals, validate structured data, check mobile
- **Retro (Fase 6)**: analyze ranking changes, traffic impact, iterate

## Referencia

- Constitución Evol-DD: Art. 4 (readabilidad, performance)
- Agentes relacionados: evol-domain-marketing (content SEO), evol-builder (implementation), evol-devops (performance)
- Google Search Central: https://developers.google.com/search
- Web.dev: https://web.dev
- Schema.org: https://schema.org
- Lighthouse CI: https://github.com/GoogleChrome/lighthouse-ci


## Memory Integration

This skill integrates with the EDMS (Evol-DD Memory System) for persistent knowledge management.

### Memory Commands

After completing the main task, execute these commands to persist knowledge:

```bash
# Store decisions made during this task
python3 scripts/evol-memory.py edms-store "$(cat acuerdos/memoria/decisiones.md)" --tipo decision

# Extract entities from the work done
python3 scripts/evol-memory.py edms-extract "$(cat WORKING-CONTEXT.md)"

# Create relationships between entities
python3 scripts/evol-memory.py edms-link "$(cat WORKING-CONTEXT.md)"

# Detect any contradictions with existing knowledge
python3 scripts/evol-memory.py edms-conflicts
```

### What to Store

- **Decisions**: Architecture choices, design patterns, technology selections
- **Entities**: Components, services, modules, dependencies
- **Relationships**: How components interact, data flows, dependencies
- **Lessons**: What worked, what didn't, improvements for next time

### Memory File Updates

Update these files with task-specific knowledge:

1. `acuerdos/memoria/decisiones.md` - Record key decisions
2. `acuerdos/memoria/convenciones.md` - Update conventions if needed
3. `acuerdos/memoria/riesgos.md` - Note any new risks identified
4. `WORKING-CONTEXT.md` - Update with current state
5. `memoria.md` - Log the activity in the flight recorder
