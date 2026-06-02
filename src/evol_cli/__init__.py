"""Evol-DD CLI — Entry point dispatcher."""
import sys, runpy, os

def _data_dir():
    """Return data directory for package."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DISPATCH = {
    "gate": "scripts.evol_gate",
    "eval": "scripts.evol_eval",
    "flow": "scripts.evol_flow",
    "provider": "scripts.evol_provider",
    "shield": "scripts.evol_shield",
    "orchestrate": "scripts.evol_orchestrate",
    "agent": "scripts.evol_agent_lifecycle",
    "evolve": "scripts.evol_evolve",
    "research": "scripts.evol_researcher",
    "memory": "scripts.evol_memory",
    "lessons": "scripts.evol_lessons",
}

def main():
    """Main entry point."""
    args = sys.argv[1:]

    if not args or args[0] == "--help" or args[0] == "-h":
        print("Evol-DD v0.1.0-dev")
        print("Commands: gate, eval, flow, provider, shield, orchestrate, agent, evolve, research, memory, lessons")
        print("Run: evol <command> --help")
        return

    cmd = args[0]

    if cmd not in DISPATCH:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

    module_name = DISPATCH[cmd]
    sys.argv = ["evol-" + cmd] + args[1:]

    runpy.run_module(module_name, run_name="__main__")

def gate():
    from scripts import evol_gate
    evol_gate.main()

def eval_():
    from scripts import evol_eval
    evol_eval.main()

def flow():
    from scripts import evol_flow
    evol_flow.main()

def provider():
    from scripts import evol_provider
    evol_provider.main()

def shield():
    from scripts import evol_shield
    evol_shield.main()

def orchestrate():
    from scripts import evol_orchestrate
    evol_orchestrate.main()

def agent():
    from scripts import evol_agent_lifecycle
    evol_agent_lifecycle.main()

def evolve():
    from scripts import evol_evolve
    evol_evolve.main()

def research():
    from scripts import evol_researcher
    evol_researcher.main()

def memory():
    from scripts import evol_memory
    evol_memory.main()

def lessons():
    from scripts import evol_lessons
    evol_lessons.main()

if __name__ == "__main__":
    main()