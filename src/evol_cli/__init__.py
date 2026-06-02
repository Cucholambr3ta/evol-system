"""Evol-DD CLI — Entry point dispatcher."""
import sys, os, subprocess, importlib.resources, shutil

SCRIPTS = {
    "gate": "evol-gate.py",
    "eval": "evol-eval.py",
    "flow": "evol-flow.py",
    "provider": "evol-provider.py",
    "shield": "evol-shield.py",
    "orchestrate": "evol-orchestrate.py",
    "agent": "evol-agent-lifecycle.py",
    "evolve": "evol-evolve.py",
    "research": "evol-researcher.py",
    "memory": "evol-memory.py",
    "lessons": "evol-lessons.py",
}

PROFILE_SCRIPT = "evol-profile.py"

def _version():
    return "0.1.0-dev"

def _scripts_dir():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "scripts")

def main():
    args = sys.argv[1:]

    if not args or args[0] == "--help" or args[0] == "-h":
        print("evol-dd", _version())
        print("Commands: gate, eval, flow, provider, shield, orchestrate, agent, evolve, research, memory, lessons, profile")
        print("Run: evol <command> --help")
        return

    if args[0] == "--version":
        print("evol-dd", _version())
        return

    cmd = args[0]

    if cmd == "profile":
        _run_script(PROFILE_SCRIPT, args[1:])
        return

    if cmd not in SCRIPTS:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

    _run_script(SCRIPTS[cmd], args[1:])

def _run_script(script_name, script_args):
    scripts_dir = _scripts_dir()
    script_path = os.path.join(scripts_dir, script_name)

    if not os.path.isfile(script_path):
        print(f"Script not found: {script_path}", file=sys.stderr)
        sys.exit(1)

    result = subprocess.run(
        [sys.executable, script_path] + script_args,
        cwd=os.getcwd(),
        env=dict(os.environ),
    )
    sys.exit(result.returncode)

def gate():
    _run_script(SCRIPTS["gate"], sys.argv[2:])

def eval_():
    _run_script(SCRIPTS["eval"], sys.argv[2:])

def flow():
    _run_script(SCRIPTS["flow"], sys.argv[2:])

def provider():
    _run_script(SCRIPTS["provider"], sys.argv[2:])

def shield():
    _run_script(SCRIPTS["shield"], sys.argv[2:])

def orchestrate():
    _run_script(SCRIPTS["orchestrate"], sys.argv[2:])

def agent():
    _run_script(SCRIPTS["agent"], sys.argv[2:])

def evolve():
    _run_script(SCRIPTS["evolve"], sys.argv[2:])

def research():
    _run_script(SCRIPTS["research"], sys.argv[2:])

def memory():
    _run_script(SCRIPTS["memory"], sys.argv[2:])

def lessons():
    _run_script(SCRIPTS["lessons"], sys.argv[2:])

if __name__ == "__main__":
    main()
