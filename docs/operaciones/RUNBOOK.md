# Runbook de Operaciones — Evol-DD

Revision: 2026-06-02
Audiencia: desarrolladores que operan proyectos inicializados con Evol-DD

Convencion de comandos: los paths relativos asumen que el working directory es la raiz del proyecto Evol-DD. Los paths con `~` son relativos al home del usuario.

---

### PROC-001: Bootstrap de nuevo proyecto desde cero

**Sintoma:** directorio vacio o proyecto nuevo sin inicializar.

**Causa probable:** nuevo proyecto o migracion de otro framework.

**Comandos:**

```bash
# 1. Clonar o entrar al directorio del proyecto
cd /ruta/al/proyecto

# 2. Inicializar Evol-DD (crea estructura, .evol/, gitignore, hooks)
bash /ruta/a/evol-dd/scripts/evol-init.sh

# 3. Verificar que la inicializacion fue exitosa
bash /ruta/a/evol-dd/scripts/evol-doctor.sh

# 4. Inicializar el gate del proyecto
python /ruta/a/evol-dd/scripts/evol-gate.py init

# 5. Primer commit
git add .
git commit -m "chore: bootstrap evol-dd"
```

**Verificacion:** `evol-doctor.sh` debe reportar todos los checks en verde. `.evol/.gate-key` debe existir y estar en `.gitignore`.

---

### PROC-002: Diagnostico cuando evol-doctor reporta errores

**Sintoma:** `evol-doctor.sh` reporta uno o mas checks fallidos.

**Causa probable:** dependencias faltantes, configuracion incorrecta, artefactos corruptos o estado inconsistente.

**Comandos:**

```bash
# 1. Obtener salida detallada en JSON para analizar cada check
bash scripts/evol-doctor.sh --json > /tmp/doctor-report.json
cat /tmp/doctor-report.json

# 2. Para cada check fallido, ver el detalle:
# - "missing_dependency": instalar la herramienta faltante (python3, git, gitleaks, semgrep)
# - "gate_key_missing": ejecutar PROC-004
# - "registry_invalid": ejecutar python scripts/validate-registry.py --strict para ver errores
# - "hooks_not_installed": reinstalar hooks
bash scripts/evol-init.sh --hooks-only

# 3. Para problemas de schema en registry:
python scripts/validate-registry.py --strict 2>&1 | head -50

# 4. Para artefactos con HMAC invalido:
python scripts/evol-gate.py status

# 5. Re-ejecutar doctor para confirmar resolucion
bash scripts/evol-doctor.sh
```

**Verificacion:** `evol-doctor.sh` retorna exit 0 y todos los checks aparecen como OK.

---

### PROC-003: Recuperar agente efimero retirado (recall)

**Sintoma:** se necesita restaurar un agente que fue retirado con `evol-agent-lifecycle.py retire`.

**Causa probable:** retiro accidental, o necesidad de reutilizar la logica de un agente archivado.

**Comandos:**

```bash
# 1. Listar agentes retirados disponibles
ls -la .evol/agents/retired/

# 2. Ver el snapshot del agente (contiene prompt, metadatos y sha256)
cat .evol/agents/retired/<nombre-agente>.json

# 3. Verificar integridad del snapshot
python scripts/evol-agent-lifecycle.py verify --name <nombre-agente>

# 4. Ejecutar recall para restaurar el agente al estado activo
python scripts/evol-agent-lifecycle.py recall --name <nombre-agente>

# 5. Verificar que el agente fue restaurado en el registry
python scripts/validate-registry.py --strict

# 6. Si el registry necesita regenerarse:
python scripts/migrate-agents-to-registry.py
```

**Verificacion:** el agente aparece en `registry.json` con estado activo. `evol-doctor.sh` no reporta inconsistencias.

---

### PROC-004: Reset de gate key comprometida

**Sintoma:** la clave `.evol/.gate-key` fue expuesta accidentalmente (commit, log, pantalla compartida) o se sospecha compromiso.

**Causa probable:** commit accidental del archivo de clave, o copia de la clave a un medio inseguro.

**Comandos:**

```bash
# 1. Si la clave fue commiteada, removerla del historial de git
# ADVERTENCIA: esto reescribe historial, coordinar con el equipo antes de ejecutar
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .evol/.gate-key' \
  --prune-empty --tag-name-filter cat -- --all

# O con git-filter-repo (recomendado sobre filter-branch):
# pip install git-filter-repo
git filter-repo --path .evol/.gate-key --invert-paths

# 2. Verificar que .evol/.gate-key esta en .gitignore
grep "gate-key" .gitignore

# 3. Eliminar la clave comprometida
rm .evol/.gate-key

# 4. Generar nueva clave
python scripts/evol-gate.py init

# 5. Re-firmar todos los artefactos existentes con la nueva clave
python scripts/evol-gate.py re-sign --all

# 6. Forzar push del historial limpio al remoto (coordinar con equipo)
git push origin --force --all
```

**Verificacion:** `python scripts/evol-gate.py status` valida todos los artefactos con la nueva clave. `git log --all --full-history -- .evol/.gate-key` no debe mostrar el archivo en ningun commit.

---

### PROC-005: Limpiar instincts stale o erroneos

**Sintoma:** `evol-evolve.py` propone mejoras basadas en patrones obsoletos, o `evol-doctor.sh` reporta instincts con alta tasa de error.

**Causa probable:** instincts acumulados durante una fase de experimentacion que no deben persistir, o instincts generados a partir de lecciones incorrectas.

**Comandos:**

```bash
# 1. Ver instincts actuales con su estado y fecha
python scripts/evol-state.py list

# 2. Ver instincts con tasa de error alta o antiguedad excesiva
python scripts/evol-state.py list --filter "error_rate > 0.3"
python scripts/evol-state.py list --older-than 90

# 3. Marcar un instinct especifico como deprecado (sin borrar)
python scripts/evol-state.py deprecate --id <instinct-id>

# 4. Limpiar instincts deprecados y mas antiguos que N dias
python scripts/evol-state.py prune --older-than 90 --deprecated-only

# 5. Para limpiar todos los instincts (reset completo de aprendizaje)
# ADVERTENCIA: operacion destructiva, considerar backup antes
cp ~/.evol/state.db ~/.evol/state.db.backup.$(date +%Y%m%d)
python scripts/evol-state.py prune --all-instincts

# 6. Verificar estado post-limpieza
python scripts/evol-state.py list
```

**Verificacion:** `python scripts/evol-state.py list` muestra solo instincts vigentes. `evol-evolve.py` no referencia los IDs eliminados.

---

### PROC-006: Actualizar Evol-DD y propagar cambios al proyecto

**Sintoma:** hay una nueva version de Evol-DD disponible, o tras instalar una actualizacion
los workflows/skills/commands del proyecto estan desactualizados.

**Causa probable:** nueva version del framework publicada en PyPI, o actualizacion manual
del repo fuente (legacy-mode).

**Comandos — Modo pip (recomendado):**

```bash
# 1. Verificar si hay actualizacion disponible
evol update check
# → "Actualizacion disponible: 0.1.0-dev → 0.2.0" o "Sistema actualizado"

# 2. Aplicar actualizacion completa desde el directorio del proyecto
cd /tu-proyecto
evol update apply
# Hace automaticamente:
#   - pipx upgrade evol-dd (o pip install --upgrade)
#   - Propaga .agent/workflows/*.md actualizados al proyecto
#   - Propaga templates/ actualizados
#   - Regenera configs IDE (evol-adapt.sh all)

# 3. Verificar estado post-actualizacion
evol --version          # debe mostrar nueva version
evol doctor             # debe reportar 0 errores criticos
bash scripts/lint-workflows.sh    # 0 errores, 0 warnings
python3 scripts/validate-registry.py --strict
```

**Comandos — Modo legacy (scripts copiados localmente):**

```bash
# 1. Apuntar al repo fuente con los cambios
export EVOL_SOURCE_DIR=/ruta/al/repo/evol-dd
# (hacer git pull en ese repo primero si aplica)

# 2. Verificar diferencia de version
evol update check

# 3. Aplicar: copia scripts evol-*, propaga workflows, regenera IDE
cd /tu-proyecto
evol update apply --project .

# 4. Verificar
evol doctor
bash scripts/lint-workflows.sh
python3 scripts/validate-registry.py --strict
```

**Verificacion post-update:**

```bash
evol update status      # version actual + modo instalacion
evol --version          # debe coincidir con VERSION del paquete
evol doctor --json | python3 -c "import json,sys; d=json.load(sys.stdin); print('OK' if d.get('ok') else 'WARN')"
```

**Verificacion:** `lint-workflows.sh` retorna exit 0. `validate-registry.py --strict` retorna exit 0. `evol-doctor.sh` sin errores.

---

### PROC-007: Rotacion de API key LLM (ANTHROPIC_API_KEY)

**Sintoma:** la API key de Anthropic fue comprometida, expirada o se requiere rotacion por politica de seguridad.

**Causa probable:** key expuesta en logs, pantalla compartida, o rotacion periodica preventiva.

**Comandos:**

```bash
# 1. Revocar la key comprometida en console.anthropic.com antes de continuar

# 2. Verificar que la key no esta hardcodeada en ningun archivo del proyecto
grep -r "sk-ant-" . --include="*.md" --include="*.yml" --include="*.json" --include="*.py" --include="*.sh"
# Si grep devuelve resultados, remover las ocurrencias antes de continuar

# 3. Verificar que ANTHROPIC_API_KEY no esta en .env commiteado
git log --all --oneline --diff-filter=A -- .env
# Si .env fue commiteado alguna vez, ejecutar git filter-repo para limpiarlo

# 4. Generar nueva key en console.anthropic.com

# 5. Actualizar la variable de entorno en el entorno local
# Opcion A: export temporal (solo sesion actual)
export ANTHROPIC_API_KEY="sk-ant-<nueva-clave>"

# Opcion B: agregar a ~/.bashrc o ~/.zshrc (persistente)
# Editar manualmente el archivo de profile del shell

# Opcion C: usar el archivo .env local (gitignored)
echo "ANTHROPIC_API_KEY=sk-ant-<nueva-clave>" > .env
grep ".env" .gitignore  # verificar que esta gitignoreado

# 6. Verificar que el proveedor LLM responde con la nueva key
python scripts/evol-doctor.sh --check llm-provider

# 7. Si se usan CI/CD runners, actualizar el secret en el proveedor de CI
# (GitHub Actions: Settings > Secrets > ANTHROPIC_API_KEY)
```

**Verificacion:** `evol-doctor.sh --check llm-provider` reporta conexion exitosa. Ningun archivo del repo contiene la key anterior ni la nueva.
