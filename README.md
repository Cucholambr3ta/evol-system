<div align="center">
  <h1>Evol-DD</h1>
  <p><b>El framework de desarrollo agéntico que aprende con cada proyecto que construye.</b></p>
  
  <p>
    <img src="https://img.shields.io/pypi/v/evol-dd?color=blue&logo=pypi&logoColor=white" alt="PyPI Version">
    <img src="https://img.shields.io/badge/python-3.10+-3776AB?logo=python&logoColor=white" alt="Python Version">
    <img src="https://img.shields.io/badge/license-MIT-4CAF50?logo=opensourceinitiative&logoColor=white" alt="License">
    <img src="https://img.shields.io/badge/branching-GitFlow-F05032?logo=git&logoColor=white" alt="GitFlow">
  </p>
</div>

<br/>

Evol-DD elimina los servidores permanentes mediante **Model Context Protocol (MCP)** y memoria local. Está diseñado para equipos que necesitan agentes que recuerden el contexto entre sesiones, conviertan errores en lecciones arquitectónicas y corran nativamente dentro del IDE sin depender de plataformas cerradas.

---

## ❖ Por qué Evol-DD

La mayoría de frameworks de IA tienen más de 180 agentes permanentes en disco, dependen de infraestructura compleja y repiten los mismos errores proyecto tras proyecto.

<table>
  <thead>
    <tr>
      <th>Problema Común</th>
      <th>Solución Evol-DD</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>► Agentes infinitos y pesados</td>
      <td><b>16 Core</b> + Agentes Efímeros bajo demanda.</td>
    </tr>
    <tr>
      <td>► Amnesia de sesión a sesión</td>
      <td><b>Memoria Nativa</b> serializada en <code>AGENT_MEMORY.md</code>.</td>
    </tr>
    <tr>
      <td>► Mismos errores recurrentes</td>
      <td><b>Motor de Lecciones</b> integrado al flujo CI/CD.</td>
    </tr>
    <tr>
      <td>► Cerrado a una plataforma</td>
      <td><b>100% Portable</b> (Cursor, Windsurf, Claude Code, Copilot).</td>
    </tr>
  </tbody>
</table>

---

## ❖ El Ecosistema "Aha! Moments"

### 1. Memoria Local Persistente
Busca decisiones pasadas y contexto sin tokens adicionales en el LLM.

```bash
python3 scripts/evol-memory.py search "decisión arquitectónica sobre la BD"
```

### 2. Motor de Lecciones
Automatiza que el agente nunca repita el mismo error técnico.

```bash
python3 scripts/evol-lessons.py add --categoria SEGURIDAD --leccion "Gate key aislada por proyecto"
```

### 3. Agentes Efímeros Criptográficos
Levanta un especialista para un ticket y retíralo (hash SHA-256) cuando acabe.

```bash
python3 scripts/evol-agent-lifecycle.py create --name "auditor-sec" --expires-after 1
```

---

## ❖ Instalación y Desinstalación

Requiere **Python 3.10+** y `pipx`.

### Instalación Rápida
```bash
# 1. Instalación Global (disponible en todos los IDEs vía pipx)
pipx install evol-dd && evol

# 2. Inicializar tu repositorio
evol init . --profile core
```

### Desinstalación
Si deseas retirar Evol-DD de tu sistema y de tus IDEs:
```bash
# Elimina el paquete global
pipx uninstall evol-dd

# Eliminar skills e integraciones locales de tus IDEs
rm -rf ~/.claude/commands/evol*
rm -rf ~/.gemini/skills/evol*
```
*(Nota: Tus datos de memoria y lecciones en los repositorios locales no se borran, ya que pertenecen a tu código fuente).*

---

## ❖ Arquitectura del Sistema (Mermaid)

```mermaid
graph TD
    A[IDE / Terminal] --> B[Evol CLI]
    B --> C[Orquestador]
    C --> D[Memoria & Lecciones Local]
    C --> E[Ejecutor GitFlow]
    C --> F[Agentes Efímeros]
    C -.-> G[Model Context Protocol]
```

---

## ❖ Documentación y Ecosistema (FAQ)

<details>
<summary><b>► Compatibilidad de IDEs</b></summary>
<br>
Soporte "Zero-Config" vía comando <code>/evol</code> para:
<ul>
  <li>Claude Code</li>
  <li>OpenCode</li>
  <li>Cursor</li>
  <li>Windsurf</li>
  <li>Antigravity</li>
  <li>VSCode Copilot (vía Tasks)</li>
</ul>
</details>

<details>
<summary><b>► Documentación Completa y Gobernanza</b></summary>
<br>
<ul>
  <li><a href="docs/constitucion.md">Constitución Evol-DD</a></li>
  <li><a href="AGENTS.md">Manifest de Agentes</a></li>
  <li><a href="docs/arquitectura/ARQUITECTURA.md">C4 Model</a></li>
</ul>
</details>

---

## ❖ Contribución y Licencia
Distribuido bajo la Licencia MIT. Las contribuciones son clave; asegúrate de respetar el GitFlow nativo al contribuir. Nuestro `pre-push` se encargará de verificar el estándar de documentación.
