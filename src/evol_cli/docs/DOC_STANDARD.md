# DOC_STANDARD — Estándar de Documentación

SSoT para toda la documentación en proyectos Evol-DD.

## Reglas Obligatorias

### 1. Cero Emoticonos
Densidad de emoji: 0%. Sin excepciones.

### 2. Mermaid Obligatorio
- Arquitectura: C4 (Context, Container, Component)
- Secuencia: flujo entre componentes
- Estado: máquinas de estado
- Componentes: diagrama de componentes
- Despliegue: ambiente objetivo

### 3. Tablas para Datos Estructurados
- Requisitos
- Casos de prueba
- Matrices de trazabilidad
- Controles de seguridad
- Métricas

### 4. Gherkin Completo
Por feature:
- Happy path (REQUIRED)
- Error case (REQUIRED)
- Edge case with Examples (REQUIRED)

### 5. Profundidad Sustantiva
Cada sección con sub-secciones. No bullets sin desarrollo.

### 6. Trazabilidad Bidireccional
REQ-NNN <-> TC-NNN en ambas direcciones.

## Verificación

```bash
# Cero emojis
grep -rP "[\x{1F000}-\x{1FAFF}]" docs/  # debe ser 0

# Mermaid presente
grep -L "```mermaid" docs/arquitectura/*.md  # debe ser 0
```

## Aplicación

- evol-doc lleva estas reglas hard-coded
- Workflows referencia este documento
- Templates cumplen las secciones mínimas
- Gate de QA verifica cumplimiento