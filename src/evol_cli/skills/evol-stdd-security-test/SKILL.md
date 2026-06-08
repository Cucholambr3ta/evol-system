---
name: evol-stdd-security-test
description: Security-Test-Driven Development. Extiende TDD con tests de seguridad basados en amenazas STRIDE de THREATS.md.
category: discipline-base
trigger: /stdd
---

# evol-stdd-security-test

## Fase del Pipeline
Build (Fase 4)

## Artefacto Clave
`tests/security/**/*.security.test.ts`

## Flujo de Trabajo

### 1. Generar stubs desde THREATS.md
```bash
# Generar security tests para amenazas con security test requerido
evol-stdd stub --from=docs/specs/THREATS.md --output=tests/security/

# Por amenaza especifica
evol-stdd stub --threat=THR-001 --output=tests/security/authz/
```

### 2. Ejecutar ciclo STDD extendido
```bash
# ROJO — Test funcional falla
npx vitest run tests/unit/facturacion/exportar-reporte.test.ts

# ROJO-SEC — Security test falla
npx vitest run tests/security/authz/exportar-reporte.security.test.ts

# VERDE — Implementar codigo minimo para que ambos pasen
npx vitest watch tests/unit/facturacion/exportar-reporte.test.ts tests/security/authz/

# REFACTOR + HARDENING — Mejorar sin romper tests
npx vitest run tests/unit/ tests/security/
```

### 3. Ejecutar suite de security tests
```bash
# Ejecutar todos los security tests
npx vitest run tests/security/

# Ejecutar por categoria STRIDE
npx vitest run tests/security/authz/    # Elevation of Privilege
npx vitest run tests/security/auth/     # Spoofing
npx vitest run tests/security/disclosure/ # Information Disclosure
npx vitest run tests/security/availability/ # Denial of Service
npx vitest run tests/security/audit/    # Repudiation
npx vitest run tests/security/injection/ # Tampering

# Generar reporte para auditoria
npx vitest run tests/security/ --reporter=verbose
```

### 4. Validar cobertura contra THREATS.md
```bash
# Verificar que cada THR-NNN con security test requerido tiene su test
evol-stdd coverage --threats=docs/specs/THREATS.md --tests=tests/security/

# Generar reporte de cobertura
evol-stdd report --output=tests/results/stdd-coverage.json
```

## Formato Security Test

```typescript
// tests/security/authz/feat-001-rbac.security.test.ts
// THR: THR-001 (THREATS.md) — Escalada de privilegios en exportacion
// SEC-REQ: SEC-REQ-001 (SPEC.md) — RBAC en exportacion de reportes
// STRIDE: Elevation of Privilege
// Estado: FAILING BY DESIGN — implementacion RBAC pendiente
// Autor: Security-Engineer | Revisor: SecOps

import { test, expect } from 'vitest';
import { exportarReportePDF } from '../../../src/facturacion/exportar-reporte';
import { crearContextoUsuario } from '../../helpers/auth';

test.describe('THR-001 — RBAC en exportacion de reportes', () => {

  test('SEC-REQ-001 — Usuario sin rol "administrador" no puede exportar', async () => {
    const ctx = crearContextoUsuario({ rol: 'operador-lectura' });
    await expect(exportarReportePDF('2026-05', ctx)).rejects.toThrow('AuthorizationError');
  });

  test('SEC-REQ-001 — Token expirado es rechazado', async () => {
    const ctx = crearContextoUsuario({ rol: 'administrador', tokenExpirado: true });
    await expect(exportarReportePDF('2026-05', ctx)).rejects.toThrow('TokenExpiredError');
  });

  test('SEC-REQ-001 — IDOR: usuario A no accede a reportes del tenant B', async () => {
    const ctx = crearContextoUsuario({ rol: 'administrador', tenantId: 'tenant-a' });
    await expect(exportarReportePDF('2026-05', ctx, { tenantId: 'tenant-b' }))
      .rejects.toThrow('AuthorizationError');
  });

});
```

## Integración con Pipeline

| Fase | Uso |
|------|-----|
| Spec | THREATS.md define amenazas con security test requerido |
| Build | Ejecutar ciclo STDD para funciones con amenazas |
| QA | Tier 2 ejecuta security tests; 100% passing |
| Gate | Bloquea merge si algun security test falla |

## Referencia
- `docs/constitucion.md` Art. 8 (Mandato de testing)
- `docs/disciplinas/STDD.md`
- `docs/specs/THREATS.md` (amenazas con security test requerido)
- [OWASP Web Security Testing Guide (WSTG)](https://owasp.org/www-project-web-security-testing-guide/)
