#!/usr/bin/env bash
set -e

CONFIG_FILE="evol.config.yml"

show_usage() {
    echo "Evol-DD MCP Manager"
    echo "Usage: evol-mcp.sh <command> [args...]"
    echo "Commands:"
    echo "  list                     List configured MCP servers"
    echo "  add <name> <cmd> [args]  Add a new MCP server"
    echo "  remove <name>            Remove an MCP server"
    echo "  status                   Check if MCP is enabled and servers are defined"
}

check_python() {
    if ! command -v python3 >/dev/null 2>&1; then
        echo "[error] python3 is required"
        exit 1
    fi
}

list_servers() {
    check_python
    python3 -c "
import yaml, os, sys
if not os.path.exists('$CONFIG_FILE'):
    print('No evol.config.yml found.')
    sys.exit(0)
with open('$CONFIG_FILE') as f:
    data = yaml.safe_load(f) or {}
mcp = data.get('mcp', {})
servers = mcp.get('servers', {})
if not servers:
    print('No servers configured.')
    sys.exit(0)
print('Configured MCP Servers:')
for name, conf in servers.items():
    cmd = conf.get('command', '')
    args = ' '.join(conf.get('args', []))
    print(f'  - {name}: {cmd} {args}')
"
}

add_server() {
    local name="$1"
    local cmd="$2"
    shift 2
    local args=("$@")
    
    check_python
    python3 -c "
import yaml, os, json, sys
config_path = '$CONFIG_FILE'
data = {}
if os.path.exists(config_path):
    with open(config_path) as f:
        data = yaml.safe_load(f) or {}

if 'mcp' not in data:
    data['mcp'] = {}
data['mcp']['enabled'] = True

if 'servers' not in data['mcp']:
    data['mcp']['servers'] = {}

data['mcp']['servers']['$name'] = {
    'command': '$cmd',
    'args': json.loads('$(python3 -c "import json, sys; print(json.dumps(sys.argv[1:]))" "${args[@]}")')
}

with open(config_path, 'w') as f:
    yaml.dump(data, f, default_flow_style=False)

print(f'[evol-mcp] Added server \'$name\'')
"
}

remove_server() {
    local name="$1"
    check_python
    python3 -c "
import yaml, os, sys
config_path = '$CONFIG_FILE'
if not os.path.exists(config_path):
    print('No evol.config.yml found.')
    sys.exit(0)
with open(config_path) as f:
    data = yaml.safe_load(f) or {}

if 'mcp' in data and 'servers' in data['mcp']:
    if '$name' in data['mcp']['servers']:
        del data['mcp']['servers']['$name']
        with open(config_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
        print(f'[evol-mcp] Removed server \'$name\'')
    else:
        print(f'[evol-mcp] Server \'$name\' not found.')
"
}

status_servers() {
    check_python
    python3 -c "
import yaml, os, sys
if not os.path.exists('$CONFIG_FILE'):
    print('[status] MCP is NOT configured (no config file)')
    sys.exit(0)
with open('$CONFIG_FILE') as f:
    data = yaml.safe_load(f) or {}
mcp = data.get('mcp', {})
servers = mcp.get('servers', {})
print(f'[status] MCP is ENABLED with {len(servers)} servers.')
"
}

case "$1" in
    list) list_servers ;;
    add) 
        if [ "$#" -lt 3 ]; then show_usage; exit 1; fi
        add_server "$2" "$3" "${@:4}" 
        ;;
    remove) 
        if [ -z "$2" ]; then show_usage; exit 1; fi
        remove_server "$2" 
        ;;
    status) status_servers ;;
    *) show_usage; exit 1 ;;
esac
