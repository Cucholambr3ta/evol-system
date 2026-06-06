# Comandos de OPERACIONES

Listado granular de todos los triggers pertenecientes al dominio **OPERACIONES**.

---

### `/evol ci-cd-setup`
**Archivo:** `.agent/workflows/ci-cd-setup.md`

**Descripción:**
Automate the configuration of the CI/CD pipeline, establishing a continuous delivery environment that ensures code quality, security, and visual compliance. In version 2.2.0, it enforces "Deployment Interoperability" (Art. 6) to ensure cross-environment synchronization.

---

### `/evol db-migrate`
**Archivo:** `.agent/workflows/db-migrate.md`

**Descripción:**
Gestión de migraciones de BD en Fase 4. Genera migración up/down, seed y verifica rollback.

---

### `/evol dependency-update`
**Archivo:** `.agent/workflows/dependency-update.md`

**Descripción:**
Mantenimiento proactivo de dependencias y mitigación de vulnerabilidades en la cadena de suministro.

---

### `/evol deploy-prod`
**Archivo:** `.agent/workflows/deploy-prod.md`

**Descripción:**
Pipeline completo de deploy a producción con gates, rollback y notificaciones.

---

### `/evol dr-drill`
**Archivo:** `.agent/workflows/dr-drill.md`

**Descripción:**
Define y prueba el plan de recuperación ante desastres. Produce DR_PLAN.md y log de drills.

---

### `/evol incidente-ID`
**Archivo:** `.agent/workflows/incidente-ID.md`

**Descripción:**
Gestión de respuesta crítica a incidentes y hotfixes en producción.

---

### `/evol mem`
**Archivo:** `.agent/workflows/Memoria Persistente-sync.md`

**Descripción:**
Sincroniza el proyecto activo con Memoria Persistente. Ejecutar al inicio de sesion para cargar contexto semantico, o al cierre para persistir cambios. Activa Memoria Persistente — el agente recuerda el proyecto, lecciones y patrones previos sin que el usuario repita contexto. Usar cuando el usuario diga "sincroniza memoria", "indexa Memoria Persistente", "/evol mem", o quiera activar continuidad semantica entre sesiones.

---

### `/evol mobile-release`
**Archivo:** `.agent/workflows/mobile-release.md`

**Descripción:**
Release de app móvil (iOS/Android). Signing, store submission, beta tracks, rollout escalonado.

---

### `/evol release-cut`
**Archivo:** `.agent/workflows/release-cut.md`

**Descripción:**
Corte de release con semver, CHANGELOG automático y release notes user-facing.

---

### `/evol rollback`
**Archivo:** `.agent/workflows/rollback.md`

**Descripción:**
Reversión segura y rápida a estados estables ante fallos críticos.

---

### `/evol secure-isolation-ops`
**Archivo:** `.agent/workflows/secure-isolation-ops.md`

**Descripción:**
Garantizar el aislamiento físico y lógico de tareas de alto riesgo (Pentesting, Stress Testing, Malware Analysis) mediante el uso de contenedores Docker efímeros. Protege el host de Evol-DD y automatiza la destrucción de contextos post-ejecución (Art. 7.3 Const.).

---

### `/evol-update`
**Archivo:** `.agent/workflows/evol-update.md`

**Descripción:**
Actualiza el core global de Evol-DD a la última versión y genera un reporte de novedades.

---

### `/evol-update-project`
**Archivo:** `.agent/workflows/evol-update-project.md`

**Descripción:**
Orquesta la actualización de un proyecto existente a la nueva versión de Evol-DD, garantizando la preservación de mejoras locales, previniendo regresiones y resolviendo conflictos de manera inteligente.

---

