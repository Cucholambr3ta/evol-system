# Comandos de Model Context Protocol (MCP)

> **Módulo:** `mcp-manager`  
> **Comando Base:** `evol-mcp.sh`

Evol-DD soporta de manera nativa servidores Model Context Protocol (MCP). La configuración de servidores MCP se guarda en el archivo `evol.config.yml` del proyecto y el comando `evol-mcp.sh` permite gestionarlos fácilmente.

## `evol-mcp.sh list`
Lista todos los servidores MCP configurados actualmente en el proyecto.

- **Fase recomendada:** Cualquier momento.
- **Acción:** Lee `evol.config.yml` e imprime los comandos de los servidores activos.

## `evol-mcp.sh add <name> <cmd> [args...]`
Añade un nuevo servidor MCP a la configuración del proyecto.

- **Ejemplo:** `evol-mcp.sh add github npx -y @modelcontextprotocol/server-github`
- **Fase recomendada:** Setup o ampliación de integraciones.
- **Acción:** Actualiza el archivo `evol.config.yml` habilitando el servidor especificado de forma persistente.

## `evol-mcp.sh remove <name>`
Elimina un servidor MCP de la configuración actual.

- **Ejemplo:** `evol-mcp.sh remove github`
- **Fase recomendada:** Mantenimiento de integraciones.
- **Acción:** Remueve el bloque de servidor correspondiente de `evol.config.yml`.

## `evol-mcp.sh status`
Muestra el estado de la habilitación de MCP y la cantidad de servidores configurados.

- **Fase recomendada:** Diagnóstico / Troubleshooting.
- **Acción:** Revisa rápidamente la validez de la configuración y cuántos servidores están definidos.
