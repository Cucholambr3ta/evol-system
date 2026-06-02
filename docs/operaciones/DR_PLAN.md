# Plan de Recuperacion ante Desastres — Evol-DD

Revision: 2026-06-02 | Propietario: equipo de desarrollo del proyecto | Alcance: framework Evol-DD y proyectos que lo usan

---

## Objetivos de recuperacion

| Parametro | Objetivo         | Justificacion                                                                          |
|-----------|------------------|----------------------------------------------------------------------------------------|
| RTO       | < 30 minutos     | El framework es local y stateless por diseno; la restauracion no requiere infraestructura externa |
| RPO       | Ultima sesion commiteada | Todo estado critico vive en git. El estado global (`~/.evol/state.db`) es reconstruible desde lecciones y memoria |

---

## Activos criticos

| Activo                        | Ubicacion                                     | Respaldo primario                       | Respaldo secundario               | Tiempo de restore estimado |
|-------------------------------|-----------------------------------------------|-----------------------------------------|-----------------------------------|---------------------------|
| Codigo fuente del framework   | Repo git local + remoto                       | `git push origin main` diario           | Fork personal o backup tar.gz     | < 5 minutos (git clone)   |
| Codigo fuente del proyecto    | Repo git local + remoto                       | `git push origin` en cada sesion        | Fork personal                     | < 5 minutos (git clone)   |
| AGENT_MEMORY.md               | Raiz del proyecto (git)                       | Commiteado si el usuario lo versiona    | Copia manual en backup semanal    | < 1 minuto (git checkout) |
| lecciones.md                  | Raiz del proyecto (git)                       | Commiteado                              | Copia manual en backup semanal    | < 1 minuto (git checkout) |
| memoria.md                    | Raiz del proyecto (git)                       | Commiteado                              | Copia manual en backup semanal    | < 1 minuto (git checkout) |
| registry.json                 | Raiz del proyecto (git)                       | Commiteado                              | Regenerable desde agents/*.md     | < 2 minutos (regenerar)   |
| skills/ y commands/           | Raiz del proyecto (git)                       | Commiteado                              | Re-sync desde framework           | < 5 minutos (evol-adapt)  |
| ~/.evol/state.db (instincts)  | Home del usuario (NO en git)                  | Backup semanal manual a directorio seguro | Reconstruible desde lecciones.md | 15-30 minutos (reconstruir) |
| .evol/.gate-key               | Raiz del proyecto (gitignored)                | NO tiene respaldo (por diseno)          | Regenerable con `evol gate init`  | < 1 minuto (regenerar)    |

---

## Escenario 1: Maquina del usuario perdida o inutilizable

**Descripcion:** fallo de hardware, robo, o reinstalacion completa del sistema operativo.

**Impacto:** perdida de estado local no commiteado, `~/.evol/state.db`, y cualquier archivo gitignoreado.

**Procedimiento de restauracion:**

```bash
# 1. En la maquina nueva, instalar dependencias base
# Python 3.9+, git, pip
python3 --version
git --version

# 2. Clonar el framework Evol-DD
git clone <url-repo-evol-dd> evol-dd
cd evol-dd
pip install -r requirements.txt  # si existe

# 3. Clonar el proyecto
git clone <url-repo-proyecto> mi-proyecto
cd mi-proyecto

# 4. Inicializar el entorno del proyecto (recrea .evol/, hooks, etc.)
bash /ruta/a/evol-dd/scripts/evol-init.sh --restore

# 5. Regenerar la gate key (la original se perdio con la maquina)
python /ruta/a/evol-dd/scripts/evol-gate.py init

# 6. Re-firmar artefactos existentes con la nueva clave
python /ruta/a/evol-dd/scripts/evol-gate.py re-sign --all

# 7. Si existe backup de ~/.evol/state.db, restaurarlo
cp /path/al/backup/state.db.backup ~/.evol/state.db

# 8. Si no hay backup de state.db, reconstruir instincts desde lecciones
python /ruta/a/evol-dd/scripts/evol-lessons.py rebuild-instincts

# 9. Verificar estado
bash /ruta/a/evol-dd/scripts/evol-doctor.sh
```

**Estado post-restore:** el proyecto queda operativo con la ultima sesion commiteada. Se pierde el estado de sesion no commiteado (`dialog/`, `tool_result/`) y los instincts si no habia backup.

---

## Escenario 2: Repositorio remoto corrupto o eliminado

**Descripcion:** el remote de git queda inaccesible, es eliminado accidentalmente, o presenta corrupcion de objetos.

**Impacto:** perdida del acceso al backup primario del codigo. El repositorio local sigue siendo valido.

**Procedimiento de restauracion:**

```bash
# 1. Verificar que el repo local esta intacto
git fsck --full
git log --oneline -10

# 2. Crear un nuevo repositorio remoto (GitHub, GitLab, o autohosteado)
# En GitHub: gh repo create <nombre> --private

# 3. Reapuntar el remote al nuevo repositorio
git remote set-url origin <nueva-url-remoto>

# 4. Push completo del historial al nuevo remoto
git push --mirror origin

# 5. Verificar que todos los branches y tags llegaron
git fetch origin
git branch -a

# 6. Si se dispone de un fork o backup tar.gz como fuente alternativa:
# Opcion A: restaurar desde fork
git remote add backup <url-fork>
git fetch backup
git merge backup/main

# Opcion B: restaurar desde tar.gz
tar -xzf backup-proyecto-YYYYMMDD.tar.gz
cd proyecto-backup
git remote set-url origin <nueva-url-remoto>
git push --mirror origin
```

**Estado post-restore:** el repositorio remoto queda restaurado desde la ultima copia local disponible. Si el repo local es mas reciente que cualquier backup, no hay perdida de datos.

---

## Escenario 3: Gate key perdida o comprometida

**Descripcion:** el archivo `.evol/.gate-key` fue eliminado, corrompido, o expuesto (ver tambien PROC-004 en RUNBOOK.md).

**Impacto:** imposibilidad de validar firmas HMAC de artefactos existentes. No bloquea el desarrollo, pero invalida la cadena de aprobacion registrada.

**Procedimiento de restauracion:**

```bash
# 1. Confirmar que la key esta ausente o es invalida
ls -la .evol/.gate-key  # si no existe
python scripts/evol-gate.py status  # si existe pero es invalida

# 2. Eliminar la key invalida si existe
rm -f .evol/.gate-key

# 3. Generar nueva clave
python scripts/evol-gate.py init

# 4. Re-firmar todos los artefactos de fase con la nueva clave
# NOTA: esto invalida las firmas anteriores; documentar el incidente
python scripts/evol-gate.py re-sign --all

# 5. Crear un commit documentando la regeneracion de la clave
git add memoria.md  # actualizar memoria con el incidente
git commit -m "sec: regeneracion de gate key por [motivo]

La clave HMAC fue regenerada. Todos los artefactos fueron re-firmados.
Firmas anteriores son invalidas por diseno (rotacion de clave)."

# 6. Verificar que el nuevo estado es consistente
python scripts/evol-gate.py status
bash scripts/evol-doctor.sh
```

**Estado post-restore:** el gate queda operativo con nueva clave. La cadena de firmas anterior queda invalida, lo cual es el comportamiento esperado tras una rotacion de clave.

---

## Escenario 4: state.db corrupto o datos inconsistentes

**Descripcion:** `~/.evol/state.db` no se puede abrir, reporta errores SQLite, o contiene instincts claramente erroneos que afectan el comportamiento del framework.

**Impacto:** perdida de instincts acumulados y/o proposals de investigacion. El proyecto sigue siendo operativo porque `state.db` no es critico para el pipeline principal.

**Procedimiento de restauracion:**

```bash
# 1. Diagnosticar el problema
sqlite3 ~/.evol/state.db "PRAGMA integrity_check;"
sqlite3 ~/.evol/state.db "PRAGMA quick_check;"

# 2. Si hay backup disponible, restaurar directamente
cp ~/.evol/state.db.backup.YYYYMMDD ~/.evol/state.db
sqlite3 ~/.evol/state.db "PRAGMA integrity_check;"  # verificar backup

# 3. Si no hay backup, intentar recuperacion con pruning
python scripts/evol-state.py prune --repair

# 4. Si la DB esta irrecuperable, crear una nueva vacia
mv ~/.evol/state.db ~/.evol/state.db.corrupted.$(date +%Y%m%d)
python scripts/evol-state.py init  # crea nueva DB con schema correcto

# 5. Reconstruir instincts desde el historial de lecciones del proyecto
# Este proceso es aproximado; no restaura todos los instincts, pero reconstruye los mas relevantes
python scripts/evol-lessons.py rebuild-instincts

# 6. Reconstruir proposals desde los research reports si existen
# (si evol-researcher.py guardo reportes en el repo)
find . -name "RESEARCH_*.md" -exec python scripts/evol-researcher.py import {} \;

# 7. Verificar que el sistema funciona sin state.db corrupto
python scripts/evol-state.py list
bash scripts/evol-doctor.sh
```

**Estado post-restore:** la DB queda operativa pero con estado parcial. Los instincts se reconstruyen gradualmente durante el uso normal del framework. No hay impacto en el pipeline de desarrollo principal.

---

## Plan de backup recomendado

### Backup diario (automatizable)

```bash
# Agregar al crontab o ejecutar manualmente al final de la sesion:
# crontab -e
# 0 23 * * * cd /ruta/al/proyecto && git push origin HEAD

# Push del proyecto al remoto
git push origin HEAD
```

### Backup semanal

```bash
# 1. Backup del estado global de Evol-DD
cp ~/.evol/state.db ~/.evol/state.db.backup.$(date +%Y%m%d)
# Mantener los ultimos 4 backups
ls -t ~/.evol/state.db.backup.* | tail -n +5 | xargs rm -f

# 2. Backup completo del directorio del proyecto (incluyendo gitignoreados)
tar -czf ~/backups/proyecto-$(date +%Y%m%d).tar.gz \
  --exclude=".git/objects" \
  /ruta/al/proyecto/
# Mantener los ultimos 4 backups
ls -t ~/backups/proyecto-*.tar.gz | tail -n +5 | xargs rm -f

# 3. Verificar que el remoto esta actualizado
git remote -v
git status
git log origin/main..HEAD --oneline  # commits locales no pusheados
```

### Verificacion periodica del plan DR

Se recomienda ejecutar un drill del plan DR cada 3 meses:

1. Verificar que el remote tiene el historial completo: `git fetch origin && git log origin/main --oneline -5`
2. Verificar que `evol-doctor.sh` funciona en entorno limpio (container o VM temporal)
3. Verificar que el procedimiento de `evol gate init` + `re-sign` produce un estado valido
4. Documentar el resultado del drill en `memoria.md`
