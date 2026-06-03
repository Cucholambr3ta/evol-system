#!/usr/bin/env python3
"""Evol-DD Flow Gate — Executable declarative flows."""
import os, sys, json, argparse
from _evol_common import get_logger, get_provider, EVOL_VERSION

logger = get_logger("flow")

def run_flow(flow_def, provider=None):
    """Execute flow: seq or parallel."""
    if provider is None:
        provider = get_provider()
    
    pattern = flow_def.get("pattern", "seq")
    steps = flow_def.get("steps", [])
    
    results = []
    if pattern == "parallel":
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
            futures = {ex.submit(run_step, s, provider): s for s in steps}
            for f in concurrent.futures.as_completed(futures):
                results.append(f.result())
    else:
        for step in steps:
            results.append(run_step(step, provider))
    return results

def run_step(step, provider):
    return {"step": step.get("name"), "status": "ok", "output": f"[mock] {step.get('prompt', '')}"}

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    
    p = sub.add_parser("run", help="Run flow")
    p.add_argument("--flow", required=True, help="Flow JSON file")
    p.add_argument("--dry-run", action="store_true")
    
    args = parser.parse_args()
    
    if args.cmd == "run":
        with open(args.flow) as f:
            flow_def = json.load(f)
        
        if args.dry_run:
            print(f"[dry-run] Would run: {flow_def.get('pattern')} with {len(flow_def.get('steps', []))} steps")
        else:
            results = run_flow(flow_def)
            for r in results:
                print(f"[{r['step']}] {r['status']}")

if __name__ == "__main__":
    main()
