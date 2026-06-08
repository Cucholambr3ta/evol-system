---
name: evol-iodd-iac
description: Infrastructure-as-Code Discipline — Terraform, Pulumi, IaC patterns, drift detection
category: discipline-extended
trigger: /iodd-iac
---

# evol-iodd-iac

## Fase del Pipeline

**Spec (Fase 2) — Especificación y Diseño**

Activar cuando se necesita diseñar o auditar infraestructura como código:
- Definición de infraestructura (Terraform/Pulumi)
- Patrones IaC (módulos, estado remoto, workspaces)
- Detección de drift
- Validación de seguridad IaC

## Artefacto Clave

**`infra/` (Terraform/Pulumi files)**

```hcl
# infra/main.tf
module "vpc" {
  source = "./modules/vpc"
  cidr_block = var.vpc_cidr
  environment = var.environment
}

module "eks" {
  source = "./modules/eks"
  cluster_name = "${var.project}-${var.environment}"
  vpc_id = module.vpc.vpc_id
}

# infra/variables.tf
variable "environment" {
  type = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod"
  }
}
```

## Flujo de Trabajo

```bash
# 1. Analizar infraestructura existente
find infra/ -name "*.tf" -o -name "*.ts" | head -20

# 2. Generar estructura de módulos
python3 scripts/iodd-iac/scaffold.py \
  --project myproject \
  --provider aws \
  --output infra/

# 3. Validar configuración
cd infra && terraform validate && cd ..

# 4. Detectar drift
python3 scripts/iodd-iac/drift-detect.py \
  --infra-dir infra/ \
  --output docs/infra/DRIFT_REPORT.md

# 5. Ejecutar Checkov (security scan)
checkov -d infra/ --framework terraform

# 6. Generar documentación
python3 scripts/iodd-iac/docs-gen.py \
  --infra-dir infra/ \
  --output docs/infra/INFRASTRUCTURE.md

# 7. Plan de cambios
cd infra && terraform plan -out=plan.out && cd ..
```

### Estado Remoto

```hcl
# infra/backend.tf
terraform {
  backend "s3" {
    bucket         = "myproject-tfstate"
    key            = "env/prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

## Integración con Pipeline

| Fase | Gate | Check | Automático |
|------|------|-------|------------|
| Briefing | Requisitos infra | Recursos necesarios identificados | No |
| Spec | Diseño IaC | Archivos .tf/.ts creados | Sí |
| Plan | Validación infra | `terraform validate` pass | Sí |
| Build | Apply infra | Recursos provisionados | Sí |
| QA | Drift detectado | Sin drift o justificado | Sí |
| Retro | Lecciones infra | Mejoras documentadas | No |

## Referencia

- **Constitución Art. 8** — Estándares de ingeniería
- **Constitución Art. 9** — Fase Spec del Pipeline
- **Discipline Doc** — `docs/disciplines/IODD_IaC.md`
- **Terraform Best Practices** — https://www.terraform-best-practices.com/
- **Pulumi Patterns** — https://www.pulumi.com/docs/guides/
