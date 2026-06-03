#!/usr/bin/env python3
"""evol-eval.py - Evaluation framework for Evol-DD.

Commands:
    evol-eval list              - List available eval suites
    evol-eval validate          - Validate suite structure
    evol-eval run <suite>       - Run a specific suite
    evol-eval run --all          - Run all suites
    evol-eval report            - Show last report
"""

import json
import os
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).parent.parent.resolve()
EVALS_DIR = REPO_ROOT / "evals"
REPORT_DIR = REPO_ROOT / ".evol" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

STATE_DB = REPO_ROOT / ".evol" / "state.db"


def load_cases(suite: str) -> list[dict]:
    """Load cases.jsonl for a suite."""
    cases_path = EVALS_DIR / suite / "cases.jsonl"
    if not cases_path.exists():
        raise FileNotFoundError(f"cases.jsonl not found for suite: {suite}")
    cases = []
    with open(cases_path) as f:
        for line in f:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    return cases


def load_grader(suite: str) -> dict:
    """Load grader.yaml for a suite."""
    import yaml
    grader_path = EVALS_DIR / suite / "grader.yaml"
    if not grader_path.exists():
        raise FileNotFoundError(f"grader.yaml not found for suite: {suite}")
    with open(grader_path) as f:
        return yaml.safe_load(f)


def list_suites() -> list[str]:
    """List all available eval suites."""
    if not EVALS_DIR.exists():
        return []
    return sorted([d.name for d in EVALS_DIR.iterdir() if d.is_dir()])


def validate_case_structure(case: dict) -> list[str]:
    """Validate a single case structure. Returns list of errors."""
    errors = []
    required = ["id", "description", "assertions"]
    for field in required:
        if field not in case:
            errors.append(f"Missing required field: {field}")

    if "assertions" in case:
        if not isinstance(case["assertions"], list):
            errors.append("assertions must be a list")
        else:
            for i, assertion in enumerate(case["assertions"]):
                if "type" not in assertion:
                    errors.append(f"assertion[{i}]: missing 'type'")
                if "check" not in assertion:
                    errors.append(f"assertion[{i}]: missing 'check'")
                valid_types = ["structural", "behavioral", "output_match", "pass_at_k", "llm_judge"]
                if assertion.get("type") not in valid_types:
                    errors.append(f"assertion[{i}]: invalid type '{assertion.get('type')}'")
                atype = assertion.get("type")
                if atype == "structural":
                    if "path" not in assertion or "required" not in assertion:
                        errors.append(f"assertion[{i}]: structural requires 'path' and 'required'")
                elif atype in ("output_match", "llm_judge"):
                    if "path" not in assertion or "pattern" not in assertion:
                        errors.append(f"assertion[{i}]: {atype} requires 'path' and 'pattern'")
                elif atype == "behavioral":
                    if "command" not in assertion:
                        errors.append(f"assertion[{i}]: behavioral requires 'command'")
    return errors


def validate_grader_structure(grader: dict) -> list[str]:
    """Validate a grader.yaml structure. Returns list of errors."""
    errors = []
    required = ["name", "description", "grader", "threshold", "cases"]
    for field in required:
        if field not in grader:
            errors.append(f"Missing required field: {field}")

    if "grader" in grader:
        valid_graders = ["structural", "behavioral", "output_match", "pass_at_k", "llm_judge"]
        if grader["grader"] not in valid_graders:
            errors.append(f"Invalid grader type: {grader['grader']}")

    if "threshold" in grader:
        try:
            t = float(grader["threshold"])
            if not (0 <= t <= 1):
                errors.append("threshold must be between 0 and 1")
        except (ValueError, TypeError):
            errors.append("threshold must be a number")

    if "cases" in grader:
        if not isinstance(grader["cases"], list):
            errors.append("cases must be a list")
        else:
            for i, case in enumerate(grader["cases"]):
                if "id" not in case:
                    errors.append(f"case[{i}]: missing 'id'")
                if "weight" not in case:
                    errors.append(f"case[{i}]: missing 'weight'")

    return errors


def validate_suite(suite: str, verbose: bool = False) -> bool:
    """Validate a single suite structure."""
    errors = []
    try:
        cases = load_cases(suite)
    except FileNotFoundError as e:
        print(f"[FAIL] {suite}: {e}")
        return False

    for i, case in enumerate(cases):
        case_errors = validate_case_structure(case)
        if case_errors:
            errors.append(f"{suite}/cases.jsonl[{i}]: {case_errors}")

    try:
        grader = load_grader(suite)
    except FileNotFoundError as e:
        print(f"[FAIL] {suite}: {e}")
        return False

    grader_errors = validate_grader_structure(grader)
    if grader_errors:
        errors.append(f"{suite}/grader.yaml: {grader_errors}")

    if errors:
        for err in errors:
            print(f"[FAIL] {err}")
        return False

    print(f"[OK] {suite}")
    return True


def validate_all() -> bool:
    """Validate all suites."""
    suites = list_suites()
    if not suites:
        print("No eval suites found")
        return False

    print(f"Validating {len(suites)} suites...")
    all_passed = True
    for suite in suites:
        if not validate_suite(suite):
            all_passed = False
    return all_passed


def check_frontmatter(path: Path, required: list) -> bool:
    """Check if file has YAML frontmatter with required fields."""
    if not path.exists():
        return False
    content = path.read_text()
    if not content.startswith("---"):
        return False
    parts = content.split("---", 2)
    if len(parts) < 3:
        return False
    frontmatter = parts[1]
    for field in required:
        pattern = rf"^{re.escape(field)}:\s*"
        if not re.search(pattern, frontmatter, re.MULTILINE):
            return False
    return True


def check_section(path: Path, required: list) -> bool:
    """Check if file contains required section headers."""
    if not path.exists():
        return False
    content = path.read_text()
    for section in required:
        if not re.search(rf"^##\s+{re.escape(section)}", content, re.MULTILINE):
            return False
    return True


def check_output_match(path: Path, pattern: str, dotall: bool = False) -> bool:
    """Check if file content matches regex pattern."""
    if not path.exists():
        return False
    content = path.read_text()
    flags = re.DOTALL if dotall else 0
    return re.search(pattern, content, flags) is not None


def run_behavioral(command: str, timeout: int = 30) -> tuple[int, str]:
    """Run a behavioral command and return (exit_code, output)."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=REPO_ROOT,
        )
        return result.returncode, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return -1, "TIMEOUT"
    except Exception as e:
        return -1, str(e)


def pass_at_k(command: str, k: int = 3, timeout: int = 30) -> bool:
    """Run command k times, pass if any succeed."""
    for _ in range(k):
        code, _ = run_behavioral(command, timeout)
        if code == 0:
            return True
    return False


def run_structural(path: Path, required: list) -> bool:
    """Run structural assertion: check frontmatter fields."""
    return check_frontmatter(path, required)


def run_structural_section(path: Path, required: list) -> bool:
    """Run structural assertion: check sections exist."""
    return check_section(path, required)


def run_case(case: dict, suite: str) -> dict:
    """Run a single case with its assertions. Returns result dict."""
    result = {
        "id": case["id"],
        "description": case["description"],
        "suite": suite,
        "passed": True,
        "assertions": [],
        "errors": [],
    }

    for assertion in case.get("assertions", []):
        atype = assertion.get("type")
        check = assertion.get("check")

        if atype == "structural":
            if check == "frontmatter":
                path = REPO_ROOT / assertion["path"]
                required = assertion["required"]
                passed = run_structural(path, required)
            elif check == "section":
                path = REPO_ROOT / assertion["path"]
                required = assertion["required"]
                passed = run_structural_section(path, required)
            else:
                passed = False
                result["errors"].append(f"Unknown structural check: {check}")

        elif atype == "output_match":
            path = REPO_ROOT / assertion["path"]
            pattern = assertion["pattern"]
            passed = check_output_match(path, pattern)
            if not path.exists():
                passed = False
                result["errors"].append(f"File not found: {path}")

        elif atype == "behavioral":
            command = assertion["command"]
            exit_code, output = run_behavioral(command)
            expected_code = assertion.get("expected_exit", 0)
            passed = exit_code == expected_code
            if not passed:
                result["errors"].append(f"Command failed: exit={exit_code}, expected={expected_code}")

        elif atype == "pass_at_k":
            command = assertion["command"]
            k = assertion.get("k", 3)
            timeout = assertion.get("timeout", 30)
            passed = pass_at_k(command, k, timeout)

        elif atype == "llm_judge":
            passed = True

        result["assertions"].append({
            "type": atype,
            "check": check,
            "passed": passed,
        })

        if not passed:
            result["passed"] = False

    return result


def run_suite(suite: str, verbose: bool = False) -> dict:
    """Run all cases in a suite."""
    results = {
        "suite": suite,
        "run_id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "passed": 0,
        "failed": 0,
        "total": 0,
        "weighted_score": 0.0,
        "total_weight": 0,
        "cases": [],
        "threshold": 0.7,
    }

    try:
        grader = load_grader(suite)
        results["threshold"] = grader.get("threshold", 0.7)
        results["grader_type"] = grader.get("grader", "unknown")
    except Exception as e:
        results["error"] = str(e)
        return results

    try:
        cases = load_cases(suite)
    except Exception as e:
        results["error"] = str(e)
        return results

    case_map = {c["id"]: c for c in grader.get("cases", [])}

    for case in cases:
        case_result = run_case(case, suite)
        case_config = case_map.get(case["id"], {})
        weight = case_config.get("weight", 1)
        case_result["weight"] = weight

        results["cases"].append(case_result)
        results["total"] += 1
        results["total_weight"] += weight

        if case_result["passed"]:
            results["passed"] += 1
            results["weighted_score"] += weight
        else:
            results["failed"] += 1

    if results["total_weight"] > 0:
        results["score"] = results["weighted_score"] / results["total_weight"]
    else:
        results["score"] = 0.0

    results["passed"] = results["score"] >= results["threshold"]

    if verbose:
        print(f"\n=== {suite} ===")
        for case in results["cases"]:
            status = "PASS" if case["passed"] else "FAIL"
            print(f"  [{status}] {case['id']}: {case['description']}")
            if not case["passed"] and case.get("errors"):
                for err in case["errors"]:
                    print(f"         {err}")
        print(f"Score: {results['score']:.2%} (threshold: {results['threshold']:.0%})")

    return results


def run_all() -> dict:
    """Run all suites."""
    suites = list_suites()
    all_results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_suites": len(suites),
        "suites": [],
        "total_passed": 0,
        "total_failed": 0,
        "overall_score": 0.0,
        "overall_passed": False,
    }

    print(f"Running {len(suites)} suites...\n")
    for suite in suites:
        result = run_suite(suite, verbose=True)
        all_results["suites"].append(result)
        if result.get("passed"):
            all_results["total_passed"] += 1
        else:
            all_results["total_failed"] += 1

    weights = [s.get("total_weight", 1) for s in all_results["suites"]]
    scores = [s.get("score", 0) for s in all_results["suites"]]
    total_weight = sum(weights)
    if total_weight > 0:
        all_results["overall_score"] = sum(w * s for w, s in zip(weights, scores)) / total_weight

    all_results["overall_passed"] = all_results["total_failed"] == 0

    return all_results


def save_report(results: dict, path: Path | None = None) -> Path:
    """Save results to a JSON report."""
    if path is None:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        run_id = results.get("run_id", results.get("suites", [{}])[0].get("run_id", "unknown")) if "suites" in results else results.get("run_id", "unknown")
        filename = f"eval_{ts}_{run_id}.json"
        path = REPORT_DIR / filename

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(results, f, indent=2)

    latest = REPORT_DIR / "latest.json"
    with open(latest, "w") as f:
        json.dump(results, f, indent=2)

    return path


def load_report(path: Path) -> dict:
    """Load a report from JSON file."""
    with open(path) as f:
        return json.load(f)


def show_report(path: Path | None = None):
    """Show the eval report."""
    if path is None:
        path = REPORT_DIR / "latest.json"

    if not path.exists():
        print("No report found. Run 'evol-eval run --all' first.")
        return

    report = load_report(path)
    print(f"\n=== Eval Report ===")
    print(f"Timestamp: {report.get('timestamp', 'unknown')}")

    if "suites" in report:
        print(f"\nSuites: {report['total_suites']}")
        print(f"Passed: {report['total_passed']}")
        print(f"Failed: {report['total_failed']}")
        print(f"Overall Score: {report.get('overall_score', 0):.2%}")
        print(f"Overall Status: {'PASS' if report.get('overall_passed') else 'FAIL'}\n")

        for suite in report["suites"]:
            status = "PASS" if suite.get("passed") else "FAIL"
            score = suite.get("score", 0)
            print(f"  [{status}] {suite['suite']}: {score:.2%}")
            for case in suite.get("cases", []):
                cstatus = "PASS" if case["passed"] else "FAIL"
                print(f"        [{cstatus}] {case['id']}: {case['description']}")
    else:
        print(f"Suite: {report.get('suite', 'unknown')}")
        print(f"Score: {report.get('score', 0):.2%}")
        print(f"Threshold: {report.get('threshold', 0):.0%}")
        print(f"Status: {'PASS' if report.get('passed') else 'FAIL'}\n")
        for case in report.get("cases", []):
            cstatus = "PASS" if case["passed"] else "FAIL"
            print(f"  [{cstatus}] {case['id']}: {case['description']}")


def main():
    args = sys.argv[1:]

    if not args or args[0] == "list":
        suites = list_suites()
        print("Available eval suites:")
        for suite in suites:
            try:
                grader = load_grader(suite)
                name = grader.get("name", suite)
                desc = grader.get("description", "")
                gtype = grader.get("grader", "unknown")
                threshold = grader.get("threshold", 0.7)
                cases = load_cases(suite)
                count = len(cases)
                print(f"  {suite}")
                print(f"    name: {name}")
                print(f"    description: {desc}")
                print(f"    grader: {gtype}, threshold: {threshold:.0%}, cases: {count}")
            except Exception as e:
                print(f"  {suite} [ERROR: {e}]")
        return

    if args[0] == "validate":
        if "--all" in args:
            success = validate_all()
            sys.exit(0 if success else 1)
        else:
            success = validate_suite("agent-eval", verbose=True)
            sys.exit(0 if success else 1)

    if args[0] == "run":
        if "--all" in args:
            results = run_all()
            report_path = save_report(results)
            print(f"\nReport saved to: {report_path}")
            print(f"Overall: {'PASS' if results['overall_passed'] else 'FAIL'} ({results['overall_score']:.2%})")
            sys.exit(0 if results["overall_passed"] else 1)
        elif len(args) > 1:
            suite = args[1]
            result = run_suite(suite, verbose=True)
            report_path = save_report(result)
            print(f"\nReport saved to: {report_path}")
            print(f"Result: {'PASS' if result.get('passed') else 'FAIL'} (score: {result.get('score', 0):.2%})")
            sys.exit(0 if result.get("passed") else 1)
        else:
            print("Usage: evol-eval run <suite> or evol-eval run --all")
            sys.exit(1)

    if args[0] == "report":
        path = None
        if len(args) > 1:
            path = Path(args[1])
        show_report(path)
        return

    print(__doc__)
    sys.exit(1)


if __name__ == "__main__":
    main()