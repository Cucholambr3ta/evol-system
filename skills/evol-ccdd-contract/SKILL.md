---
name: evol-ccdd-contract
description: Consumer-Driven Contract Development. Verifica que el proveedor cumple los contratos de consumidor (Pact), bloqueando si algun contrato se rompe.
category: discipline-extended
trigger: /ccdd
---

# evol-ccdd-contract

## Fase del Pipeline
QA (Fase 5)

## Artefacto Clave
`tests/contract/*.contract.test.ts`

## Flujo de Trabajo

### 1. Publicar contratos de consumidor
```bash
# Consumidores publican sus expectativas al broker
evol-ccdd publish --consumer=consumers/frontend/ --broker=$PACT_BROKER_URL

# Listar contratos registrados
evol-ccdd list-contracts --broker=$PACT_BROKER_URL
```

### 2. Descargar contratos del broker
```bash
# Descargar contratos pendientes de verificacion
evol-ccdd fetch --provider=api-service --broker=$PACT_BROKER_URL --output=tests/contract/pacts/

# Generar tests de verificacion desde contratos
evol-ccdd generate-tests --pacts=tests/contract/pacts/ --output=tests/contract/
```

### 3. Ejecutar verificacion del proveedor
```bash
# Ejecutar tests de contrato
npx vitest run tests/contract/ --reporter=json --output=tests/contract/results.json

# Publicar resultado al broker
evol-ccdd publish-result --results=tests/contract/results.json --broker=$PACT_BROKER_URL
```

### 4. Verificar que todos los contratos pasaron
```bash
# Validar 100% contratos verificados
evol-ccdd verify-all --results=tests/contract/results.json --block-on=failure

# Generar reporte
evol-ccdd report --results=tests/contract/results.json --output=tests/contract/verification_results.json
```

## Formato Contract Test

```typescript
// tests/contract/frontend.contract.test.ts
import { describe, it, expect } from 'vitest';
import { Pact } from '@pact-foundation/pact';

const provider = new Pact({
  consumer: 'frontend',
  provider: 'api-service',
  port: 1234,
});

describe('Contrato: Frontend -> API Service', () => {

  it('GET /api/usuarios retorna lista de usuarios', async () => {
    await provider.addInteraction({
      state: 'usuarios existen',
      uponReceiving: 'una peticion GET /api/usuarios',
      withRequest: {
        method: 'GET',
        path: '/api/usuarios',
      },
      willRespondWith: {
        status: 200,
        body: {
          usuarios: [{ id: 'usr_001', nombre: 'Ana' }],
        },
      },
    });

    const response = await fetch('http://localhost:1234/api/usuarios');
    expect(response.status).toBe(200);
  });

});
```

## Formato verification_results.json

```json
{
  "provider": "api-service",
  "timestamp": "2026-06-07T10:00:00Z",
  "contracts_verified": 3,
  "contracts_passed": 3,
  "contracts_failed": 0,
  "results": [
    {
      "consumer": "frontend",
      "status": "passed",
      "interactions": 5
    }
  ]
}
```

## Integracion con Pipeline

| Fase | Uso |
|------|-----|
| Spec | Los consumidores declaran sus expectativas |
| QA | El proveedor verifica todos los contratos |
| Retro | Revisar contratos rotos historicos |
| Gate | Bloquea si el proveedor rompe algun contrato de consumidor |

## Referencia
- `docs/constitucion.md` Art. 2 (Pipeline gated)
- `docs/constitucion.md` Art. 9 (Evol-DD Pipeline)
- `docs/disciplinas/CCDD.md`
- [Consumer-Driven Contracts — Martin Fowler](https://martinfowler.com/articles/consumerDrivenContracts.html)
- [Pact Foundation](https://github.com/pact-foundation)
- [Pact — CI/CD Setup Guide](https://docs.pact.io/ci_cd)


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
