#!/usr/bin/env python3
"""
Evol-DD Common Utilities
Stdlib only — no external dependencies
"""
import os, sys, logging, json, subprocess, hashlib

EVOL_VERSION = "0.1.0-dev"
EVOL_STATE_DB = os.path.expanduser("~/.evol/state.db")
EVOL_DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/.."

# === Logging ===
def get_logger(name="evol"):
    l = logging.getLogger(name)
    if not l.handlers:
        l.setLevel(logging.INFO)
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter("[%(name)s] %(levelname)s: %(message)s"))
        l.addHandler(h)
    return l

logger = get_logger()

# === MemPalace safe wrapper ===
def mempalace_safe(*args, fallback=None):
    """Call mempalace CLI if available, else return fallback."""
    try:
        result = subprocess.run(["mempalace"] + list(args), capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return result.stdout.strip()
        return fallback
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return fallback

# === Tool discovery ===
def find_tool(tool_name, extra_paths=None):
    """Find tool in PATH + extra_paths. Returns path or None."""
    import shutil
    paths = [os.environ.get("PATH", "").split(os.pathsep)]
    if extra_paths:
        paths.append(extra_paths)
    for p in paths:
        found = shutil.which(tool_name, path=os.pathsep.join(p))
        if found:
            return found
    return None

def find_mempalace():
    """Find mempalace in standard locations."""
    locations = [
        os.environ.get("PATH", ""),
        os.path.expanduser("~/.local/bin"),
        os.path.expanduser("~/.venv/bin"),
        "venv/bin",
        ".venv/bin",
    ]
    for loc in locations:
        found = find_tool("mempalace", [loc])
        if found:
            return found
    return None

# === SHA-256 ===
def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

# === JSON helpers ===
def load_json(path):
    with open(path) as f:
        return json.load(f)

def save_json(path, data, indent=2):
    with open(path, "w") as f:
        json.dump(data, f, indent=indent)

# === Data dirs ===
def get_data_dir():
    """Return absolute path to evol-dd data directory. Supports EVOL_DATA_DIR override."""
    if os.environ.get("EVOL_DATA_DIR"):
        return os.environ["EVOL_DATA_DIR"]
    return os.path.dirname(os.path.abspath(__file__)) + "/.."

# === Constants ===
HOOK_PROFILES = ["minimal", "standard", "strict"]
ORCHESTRATION_PATTERNS = ["sequential", "parallel", "parallel_then_sync", "party"]
PROVIDER_MODES = ["mock", "anthropic"]

# === Exit codes ===
EXIT_OK = 0
EXIT_ERROR = 1
EXIT_BLOCKED = 2  # Hook blocked
EXIT_GATE_REQUIRED = 3

# === LLM Provider (lazy import) ===
_provider = None

def get_provider():
    global _provider
    if _provider is None:
        try:
            from evol_provider import get_provider as gp
            _provider = gp()
        except Exception:
            class MockProvider:
                def complete(self, prompt, max_tokens=500, **kwargs):
                    return {"content": "[mock response]"}
            _provider = MockProvider()
    return _provider
