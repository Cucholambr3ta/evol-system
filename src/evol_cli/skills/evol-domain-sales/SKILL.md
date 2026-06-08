---
name: evol-domain-sales
description: Asesor de dominio para construir software de ventas, e-commerce y plataformas de transacción. Aporta conocimiento en checkout flows, integración de pagos, gestión de inventario y modelos de precios.
category: domain-advisor
trigger: /domain-sales
---

# evol-domain-sales

## Cuándo Usar

Activar esta skill cuando el sistema Evol-DD necesita construir o auditar software en el dominio de ventas y e-commerce:

- **Checkout y carrito de compras**: diseño de flujos de pago, persistencia de carrito, recuperación de carrito abandonado
- **Integración de pagos**: pasarelas de pago (Stripe, PayPal, MercadoPago), suscripciones, reembolsos, disputas
- **Gestión de inventario**: stock en tiempo real, reservas, alertas de stock bajo, multi-almacén
- **Modelos de precios**: pricing dinámico, descuentos, cupones, precios por volumen, suscripciones escalonadas
- **Órdenes y fulfillment**: estados de orden, logística, devoluciones, tracking
- **Catálogo de productos**: búsqueda, filtros, variantes (talla/color), recomendar productos

**No usar para**: software financiero contable (usar evol-domain-finance), analytics de marketing (usar evol-domain-marketing).

## Conocimiento de Dominio

### Checkout Flows
- **Carrito → Checkout → Pago → Confirmación**: flujo estándar con puntos de abandono monitoreables
- **Guest checkout vs. cuenta registrada**: trade-offs entre conversión y retención
- **One-click checkout**: Amazon-style, requiere tokenización previa
- **Checkout multinacional**: impuestos por jurisdicción, moneda local, métodos de pago regionales

### Integración de Pagos
- **Stripe**: Payments Intents API, webhook handling, 3D Secure, Link
- **PayPal**: REST API, vault para suscripciones, buyer protection
- **MercadoPago**: Tokenización, pagos en cuotas, split de pagos
- **Cripto**: integración Lightning Network, stablecoins para cross-border
- **PCI DSS**: nivel de compliance según volumen, tokenización, no almacenar PAN

### Gestión de Inventario
- **Stock tracking**: optimistic locking para evitar overselling
- **Reservas**: TTL-based para carritos, liberación automática
- **Multi-almacén**: fulfillment desde almacén más cercano
- **Inventario digital**: licencias, keys, downloads

### Modelos de Precios
- **Flat rate, tiered, usage-based, freemium**: cuándo usar cada uno
- **Descuentos**: porcentaje, monto fijo, BOGO, volumen
- **Suscripciones**: monthly/annual, trials, pausas, cancelaciones
- **Dynamic pricing**: demanda, estacionalidad, competencia (cuidado con backlash)

### Seguridad y Fraude
- **3D Secure**: frictionless vs. challenge flow
- **Velocity checks**: transacciones por tiempo
- **Device fingerprinting**: detección de fraude
- **Chargebacks**: representment, evidence gathering

## Flujo de Trabajo

1. **Identificar el contexto de ventas**: ¿Qué se está vendiendo? (productos físicos, digitales, servicios, suscripciones)
2. **Mapear el flujo de compra**: customer journey desde descubrimiento hasta post-compra
3. **Diseñar la integración de pagos**: seleccionar proveedores, definir manejo de errores y edge cases
4. **Planificar inventario**: modelo de stock, estrategia de reservas, alertas
5. **Definir modelo de precios**: pricing strategy, descuentos, promociones
6. **Implementar seguridad**: fraude, PCI compliance, datos sensibles
7. **Testear con datos reales**: sandbox con tarjetas de prueba, edge cases de pago
8. **Monitorear métricas**: conversión de checkout, tasa de abandono, error rate de pagos

## Integración con Pipeline

- **Briefing (Fase 1)**: identificar modelo de negocio y revenue streams
- **Spec (Fase 2)**: documentar flujos de pago, reglas de negocio de precios, estados de orden
- **Plan (Fase 3)**: estimar complejidad de integraciones de pago, dependencias de proveedores
- **Build (Fase 4)**: implementar con TDD, usar sandbox para pagos
- **QA (Fase 5)**: testear flujos de pago exitosos y fallidos, edge cases de inventario
- **Retro (Fase 6)**: analizar métricas de conversión, identificar puntos de fricción

## Referencia

- Constitución Evol-DD: Art. 5 (consultoría de dominio proactiva)
- Art. 9: pipeline de 6 fases
- Agentes relacionados: evol-domain (modelado de dominio), evol-sec (seguridad de pagos), evol-qa (testeo de flujos)
- Stripe Documentation: https://stripe.com/docs
- PCI DSS Standard: https://www.pcisecuritystandards.org
