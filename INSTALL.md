# Instalación

## Requisitos

- Python 3.10+
- Git
- (Opcional) MemPalace CLI para Modo COMPLETO

## Instalación global

```bash
bash scripts/evol-global-install.sh
```

## Bootstrap de proyecto

```bash
bash scripts/evol-init.sh /path/to/project --profile=core
```

## Perfiles

| Perfil | Descripción |
|--------|-------------|
| minimal | Nucleo mínimo con lecciones y memoria |
| core | Estándar para proyectos |
| developer | Desarrollo activo con agentes efímeros |
| security | Enfoque SecDD |
| research | Investigación y evolución |
| full | Instalación completa |
| lean | Ligthweight, requiere global install |

## Modos de operación

- **COMPLETO**: MemPalace activo, búsqueda semántica
- **BASE**: Sin MemPalace, funciona completamente

## Actualización

```bash
pip install -e .
```