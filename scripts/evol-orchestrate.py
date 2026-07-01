#!/usr/bin/env python3
"""Evol-DD Orchestration Engine — Multi-agent runtime coordination.

Patterns: sequential, parallel, parallel_then_sync, party, autonomous_loop.
Records orchestration runs in SQLite (orchestrations table).

autonomous_loop (ralph-style): ejecuta un PLAN ya aprobado por gate como bucle
multi-contexto. Por cada item pendiente: implementa -> testea -> commit -> actualiza
estado -> repite, hasta agotar el backlog. Reusa artefactos existentes de Evol-DD:
  - backlog  = PLAN.md + CASOS_GHERKIN.md (Fase 3, aprobados por gate HMAC)
  - progreso = memoria.md + WORKING-CONTEXT.md
  - estado   = evol-state (SQLite)
  - commits  = evol-gitflow por iteracion
Inspirado en snarktank/ralph (atribucion en NOTICE). Opera DENTRO de Fase 4 (Build),
nunca salta el gate de aprobacion previo.
"""
import os, sys, json, argparse, time, subprocess
from datetime import datetime
from pathlib import Path
from _evol_common import get_state_db, get_logger, save_json, load_json, ORCHESTRATION_PATTERNS, EXIT_OK, EXIT_ERROR

logger = get_logger("orchestrate")

REGISTRY_PATH = "prompts/agents/registry.json"

BUILTIN_PATTERNS = {
    "security_review": {
        "type": "sequential",
        "description": "Code review + security audit + threat detection",
        "steps": [
            {"agent": "evol-reviewer", "task": "Code review"},
            {"agent": "evol-sec", "task": "Security audit"},
            {"agent": "evol-sec", "task": "Threat detection (STRIDE)"},
        ],
    },
    "feature_squad": {
        "type": "parallel_then_sync",
        "description": "PM + Backend + UI + QA in parallel, sync at spec approval",
        "steps": [
            {"agent": "evol-pm", "task": "Feature spec"},
            {"agent": "evol-builder", "task": "Backend implementation"},
            {"agent": "evol-ux", "task": "UI design"},
            {"agent": "evol-qa", "task": "Test plan"},
        ],
        "sync_point": "spec_approval",
        "timeout": 300,
    },
    "release_train": {
        "type": "sequential",
        "description": "Release coordination: contract tests + deploy + docs",
        "steps": [
            {"agent": "evol-qa", "task": "Contract testing"},
            {"agent": "evol-devops", "task": "Deployment"},
            {"agent": "evol-doc", "task": "Release documentation"},
            {"agent": "evol-release", "task": "Version bump + CHANGELOG"},
        ],
    },
    "briefing squad": {
        "type": "parallel_then_sync",
        "description": "Discovery + UX + Domain in parallel for briefing phase",
        "steps": [
            {"agent": "evol-researcher", "task": "Market research"},
            {"agent": "evol-ux", "task": "User discovery"},
            {"agent": "evol-domain", "task": "Domain modeling"},
        ],
        "sync_point": "briefing_approval",
        "timeout": 180,
    },
    "brainstorm_party": {
        "type": "party",
        "description": "Free-form brainstorming with multiple agents",
        "steps": [
            {"agent": "evol-architect", "task": "Architecture ideas"},
            {"agent": "evol-builder", "task": "Implementation ideas"},
            {"agent": "evol-ux", "task": "User experience ideas"},
            {"agent": "evol-pm", "task": "Product priorities"},
        ],
    },
    "autonomous_loop": {
        "type": "autonomous_loop",
        "description": "Ralph-style: implement an approved PLAN item-by-item across "
                       "contexts (implement -> test -> commit -> update -> repeat)",
        "steps": [
            {"agent": "evol-builder", "task": "Implement next pending PLAN item"},
            {"agent": "evol-qa", "task": "Test the implemented item"},
            {"agent": "evol-devops", "task": "Commit via evol-gitflow + update state"},
        ],
        "backlog_source": "PLAN.md",
        "progress_sink": "memoria.md",
        "max_iterations": 50,
        "requires_gate": "plan",
        "timeout": 600,
    },
}


def _get_db():
    db_path = get_state_db()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _load_registry():
    """Load agent registry."""
    if os.path.exists(REGISTRY_PATH):
        return load_json(REGISTRY_PATH)
    return {"agents": []}


def _get_agent_prompt(agent_name):
    """Get agent prompt file path."""
    registry = _load_registry()
    for agent in registry.get("agents", []):
        if agent["name"] == agent_name:
            agent_file = agent.get("file", "")
            full_path = os.path.join("prompts/agents", agent_file)
            if os.path.exists(full_path):
                return full_path
    return None


def list_patterns(as_json=False):
    """List available orchestration patterns."""
    all_patterns = {}
    all_patterns.update(BUILTIN_PATTERNS)

    if as_json:
        result = {}
        for name, pat in all_patterns.items():
            result[name] = {
                "type": pat["type"],
                "description": pat["description"],
                "agents": [s["agent"] for s in pat["steps"]],
                "step_count": len(pat["steps"]),
            }
        print(json.dumps(result, indent=2))
    else:
        print("Available orchestration patterns:")
        print()
        for name, pat in all_patterns.items():
            agents = " → ".join(s["agent"] for s in pat["steps"])
            print(f"  {name} ({pat['type']})")
            print(f"    {pat['description']}")
            print(f"    Agents: {agents}")
            print()


def run_pattern(pattern_name, exec_mode=False, as_json=False, timeout=None):
    """Run an orchestration pattern (dry-run or execute)."""
    if pattern_name not in BUILTIN_PATTERNS:
        print(f"[ERROR] Unknown pattern: {pattern_name}")
        print(f"Available: {', '.join(BUILTIN_PATTERNS.keys())}")
        return EXIT_ERROR

    pattern = BUILTIN_PATTERNS[pattern_name]
    pattern_type = pattern["type"]
    steps = pattern["steps"]
    run_timeout = timeout or pattern.get("timeout", 300)

    run_id = f"orch-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    start_time = time.time()

    result = {
        "run_id": run_id,
        "pattern": pattern_name,
        "type": pattern_type,
        "timestamp": datetime.now().isoformat(),
        "exec_mode": exec_mode,
        "steps": [],
        "status": "pending",
    }

    logger.info("Running pattern: %s (type=%s, exec=%s)", pattern_name, pattern_type, exec_mode)

    if pattern_type == "sequential":
        _run_sequential(steps, result, exec_mode, run_timeout)
    elif pattern_type == "parallel":
        _run_parallel(steps, result, exec_mode, run_timeout)
    elif pattern_type == "parallel_then_sync":
        _run_parallel_then_sync(steps, result, exec_mode, run_timeout, pattern.get("sync_point"))
    elif pattern_type == "party":
        _run_party(steps, result, exec_mode, run_timeout)
    elif pattern_type == "autonomous_loop":
        _run_autonomous_loop(steps, result, exec_mode, run_timeout, pattern)

    elapsed = time.time() - start_time
    result["elapsed_seconds"] = round(elapsed, 2)

    failed = [s for s in result["steps"] if s.get("status") == "failed"]
    result["status"] = "failed" if failed else "completed"

    _record_run(result)

    if as_json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\nOrchestration: {pattern_name} ({pattern_type})")
        print(f"  Run ID: {run_id}")
        print(f"  Status: {result['status']}")
        print(f"  Elapsed: {elapsed:.1f}s")
        print(f"  Steps:")
        for i, step in enumerate(result["steps"]):
            status = step.get("status", "pending")
            icon = "OK" if status == "completed" else "FAIL" if status == "failed" else "SKIP"
            print(f"    [{icon}] {i+1}. {step['agent']}: {step['task']}")
            if step.get("error"):
                print(f"         Error: {step['error']}")

    return EXIT_OK


def _run_sequential(steps, result, exec_mode, timeout):
    """Execute steps one by one. Stop on failure."""
    for i, step in enumerate(steps):
        step_result = _execute_step(step, i, exec_mode, timeout)
        result["steps"].append(step_result)
        if step_result["status"] == "failed":
            logger.warning("Step %d failed, stopping sequence", i)
            for remaining in steps[i+1:]:
                result["steps"].append({
                    "agent": remaining["agent"],
                    "task": remaining["task"],
                    "status": "skipped",
                    "reason": "previous step failed",
                })
            break


def _run_parallel(steps, result, exec_mode, timeout):
    """Execute all steps concurrently (simulated — real parallelism via MCP)."""
    for i, step in enumerate(steps):
        step_result = _execute_step(step, i, exec_mode, timeout)
        result["steps"].append(step_result)


def _run_parallel_then_sync(steps, result, exec_mode, timeout, sync_point):
    """Execute in parallel, then wait for sync point."""
    for i, step in enumerate(steps):
        step_result = _execute_step(step, i, exec_mode, timeout)
        result["steps"].append(step_result)

    result["sync_point"] = sync_point or "auto"
    result["sync_status"] = "reached"


def _run_party(steps, result, exec_mode, timeout):
    """Free-form: all agents run without strict ordering."""
    for i, step in enumerate(steps):
        step_result = _execute_step(step, i, exec_mode, timeout)
        result["steps"].append(step_result)


def _run_autonomous_loop(steps, result, exec_mode, timeout, pattern):
    """Ralph-style autonomous loop over an approved PLAN.

    Each iteration runs the step sequence (implement -> test -> commit) on the
    next pending backlog item, then re-evaluates the backlog. Stops when the
    backlog is empty, a step fails, or max_iterations is reached.

    Backlog tracking reuses Evol-DD artifacts: PLAN.md (items) + memoria.md
    (progress) + evol-state (status). In dry-run (exec_mode=False) it reports
    the planned iterations without executing agents or commits.
    """
    backlog_src = pattern.get("backlog_source", "PLAN.md")
    progress_sink = pattern.get("progress_sink", "memoria.md")
    max_iter = pattern.get("max_iterations", 50)
    required_gate = pattern.get("requires_gate")

    result["loop"] = {
        "backlog_source": backlog_src,
        "progress_sink": progress_sink,
        "max_iterations": max_iter,
        "requires_gate": required_gate,
        "iterations": [],
    }

    # Gate guard: an autonomous loop must run on an already-approved PLAN.
    if required_gate:
        marker = Path(f".evol/.gate-{required_gate}-approved")
        gate_ok = marker.exists() or os.environ.get("EVOL_SKIP_GATE_CHECK") == "1"
        result["loop"]["gate_ok"] = gate_ok
        if not gate_ok:
            logger.warning("autonomous_loop: gate '%s' not approved; refusing to run",
                           required_gate)
            result["steps"].append({
                "agent": "evol-orchestrator",
                "task": f"gate check ({required_gate})",
                "status": "failed",
                "error": f"PLAN gate '{required_gate}' not approved. "
                         f"Run /evol gate approve --phase {required_gate} first "
                         f"(or set EVOL_SKIP_GATE_CHECK=1 to override).",
            })
            return

    backlog = _load_plan_backlog(backlog_src)
    result["loop"]["backlog_count"] = len(backlog)

    if not backlog:
        logger.info("autonomous_loop: empty backlog in %s", backlog_src)
        result["steps"].append({
            "agent": "evol-orchestrator",
            "task": "load backlog",
            "status": "skipped",
            "reason": f"no pending items found in {backlog_src}",
        })
        return

    for iteration, item in enumerate(backlog[:max_iter]):
        iter_log = {"iteration": iteration + 1, "item": item, "steps": []}
        failed = False
        for i, step in enumerate(steps):
            scoped = dict(step)
            scoped["task"] = f"{step['task']} [{item}]"
            step_result = _execute_step(scoped, i, exec_mode, timeout)
            iter_log["steps"].append(step_result)
            result["steps"].append(step_result)
            if step_result["status"] == "failed":
                failed = True
                break
        iter_log["status"] = "failed" if failed else "completed"
        result["loop"]["iterations"].append(iter_log)
        if failed:
            logger.warning("autonomous_loop: iteration %d failed on '%s', stopping",
                           iteration + 1, item)
            break


def _load_plan_backlog(plan_path):
    """Extract pending items from a PLAN.md backlog.

    Pending = unchecked task list entries ('- [ ] ...'). Completed entries
    ('- [x] ...') are skipped. Returns a list of item descriptions.
    """
    p = Path(plan_path)
    if not p.exists():
        return []
    items = []
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if s.startswith("- [ ]") or s.startswith("* [ ]"):
            items.append(s[5:].strip())
    return items


def _execute_step(step, index, exec_mode, timeout):
    """Execute a single orchestration step."""
    agent = step["agent"]
    task = step["task"]

    step_result = {
        "agent": agent,
        "task": task,
        "status": "pending",
        "started_at": datetime.now().isoformat(),
    }

    prompt_path = _get_agent_prompt(agent)
    if not prompt_path:
        step_result["status"] = "failed"
        step_result["error"] = f"Agent prompt not found: {agent}"
        return step_result

    if not exec_mode:
        step_result["status"] = "dry_run"
        step_result["prompt_path"] = prompt_path
        return step_result

    try:
        content = Path(prompt_path).read_text(encoding="utf-8")
        step_result["prompt_length"] = len(content)
        step_result["status"] = "completed"
        step_result["note"] = "Prompt loaded. LLM invocation delegated to orchestrator."
    except Exception as e:
        step_result["status"] = "failed"
        step_result["error"] = str(e)

    return step_result


def _record_run(result):
    """Record orchestration run in SQLite."""
    try:
        conn = _get_db()
        c = conn.cursor()
        # Ensure columns exist (migration for older DBs)
        try:
            c.execute("ALTER TABLE orchestrations ADD COLUMN agents TEXT")
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE orchestrations ADD COLUMN ended_at TEXT")
        except Exception:
            pass
        c.execute("""
            INSERT INTO orchestrations (pattern, agents, status, created_at, ended_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            result["pattern"],
            json.dumps([s["agent"] for s in result["steps"]]),
            result["status"],
            result["timestamp"],
            datetime.now().isoformat(),
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning("Failed to record orchestration: %s", e)


def show_status():
    """Show orchestration history."""
    try:
        conn = _get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM orchestrations ORDER BY id DESC LIMIT 10")
        rows = [dict(r) for r in c.fetchall()]
        conn.close()

        if not rows:
            print("No orchestration runs recorded.")
            return

        print("Recent orchestration runs:")
        for r in rows:
            print(f"  [{r['status']}] {r['pattern']} — {r['created_at']}")
            if r.get("agents"):
                agents = json.loads(r["agents"])
                print(f"    Agents: {', '.join(agents)}")
    except Exception as e:
        print(f"[ERROR] Could not read orchestration history: {e}")


def main():
    parser = argparse.ArgumentParser(description="Evol-DD Orchestration Engine")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("list", help="List available patterns")
    sub.add_parser("status", help="Show orchestration history")

    p = sub.add_parser("run", help="Run an orchestration pattern")
    p.add_argument("--pattern", required=True, help="Pattern name")
    p.add_argument("--exec", action="store_true", help="Execute (default: dry-run)")
    p.add_argument("--json", action="store_true", help="JSON output")
    p.add_argument("--timeout", type=int, default=None, help="Step timeout seconds")

    args = parser.parse_args()

    if args.cmd == "list":
        list_patterns(args.json if hasattr(args, 'json') else False)
    elif args.cmd == "run":
        sys.exit(run_pattern(args.pattern, args.exec, args.json, args.timeout))
    elif args.cmd == "status":
        show_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
