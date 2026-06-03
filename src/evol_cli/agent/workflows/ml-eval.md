---
description: Evaluación sistemática de modelos ML/LLM. Datasets dorados, métricas, drift detection, A/B.
name: ml-eval
trigger: /evol ml-eval
---
# /ml-eval

> **Estandar de documentacion:** Todo artefacto que produzca este workflow cumple
> [`docs/DOC_STANDARD.md`](../../docs/DOC_STANDARD.md): sin emojis, diagramas Mermaid
> obligatorios, tablas para datos estructurados, Gherkin donde aplique, secciones
> minimas y trazabilidad bidireccional.
**ID:** FLUJO-MLEVAL | **Versión:** 1.0 | **Agente:** AI-Engineer + Data-Engineer
**Misión:** "Funciona en mi laptop" no es válido para modelos. Evaluación reproducible y continua.

## 0. Pre-flight
- Aplica si el producto integra ML/LLM (clasificador, recomendador, generación, agente).
- Requiere `DOMAIN.md` para entender qué métrica de negocio es la real.

## 1. Datasets dorados
- **Eval set** versionado, separado del training.
- Casos cubren: happy path, edge cases, adversariales, regresiones históricas.
- Tamaño suficiente para significancia estadística.
- Etiquetado por humanos cualificados (con guía de etiquetado).

## 2. Métricas
- **Técnicas**: accuracy, precision, recall, F1, ROC-AUC, BLEU/ROUGE, exactitud factual, calibración.
- **De negocio**: la métrica real que el modelo debe mover (conversión, satisfacción, tickets evitados).
- **Operativas**: latencia p50/p95, costo por inferencia (cruzar `/finops-baseline`), tasa de error.
- **Seguridad/alineamiento**: jailbreaks, toxicidad, sesgo por subgrupos.

## 3. Pipeline de evaluación
<!-- CONFIGURAR: Stack eval.                                                   -->
<!--  - LLM: Promptfoo, OpenAI Evals, DeepEval, LangSmith, Braintrust           -->
<!--  - Clásico ML: MLflow, Weights & Biases, Comet                             -->
<!--  - Internal: scripts + dataset versionado en DVC/LakeFS                    -->

- Eval corre en CI para cada cambio de prompt/modelo/preprocesado.
- Resultados comparados vs baseline; degradación bloquea merge.

## 4. Drift en producción
- Monitoreo de distribución de inputs (data drift).
- Monitoreo de distribución de outputs (concept drift).
- Re-evaluación periódica sobre golden set + muestras de producción etiquetadas.

## 5. A/B testing de modelos
- Shadow mode (predicción sin actuar) antes de exponer.
- Cruzar con `/feature-flag` para rollout escalonado.
- Stop rule: criterios pre-definidos para promoción o rollback.

## 6. Trazabilidad
- Versión de modelo + dataset + prompt + parámetros registrados con cada predicción crítica.
- Reproducibilidad del experimento.

## 7. Gated (Art. 2)
`"APROBADO"` antes de:
- Reemplazar modelo en producción.
- Cambiar prompt en flujo crítico.
- Re-entrenar con nuevo dataset.

## 8. Cierre
- Reporte de eval a `qa-review` Tier 3 (LLM-Judge).
- ADR si decisión de modelo es estructural.
- Lecciones a [[lecciones]].
