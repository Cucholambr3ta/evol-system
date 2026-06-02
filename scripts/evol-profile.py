#!/usr/bin/env python3
"""Evol-DD Profile CLI — Profile management tool."""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
PROFILES_MANIFEST = REPO_ROOT / "manifests" / "install-profiles.json"
MODULES_MANIFEST = REPO_ROOT / "manifests" / "install-modules.json"
FRAMEWORK_VERSION = "0.1.0-dev"


def load_manifest(path):
    with open(path) as f:
        return json.load(f)


def resolve_modules(profile_id, profiles):
    seen = set()
    modules = []

    def resolve(pid):
        if pid in seen:
            return
        seen.add(pid)
        p = next((x for x in profiles if x["id"] == pid), None)
        if not p:
            return
        if "extends" in p:
            resolve(p["extends"])
        modules.extend(p.get("modules", []))

    resolve(profile_id)
    return modules


def cmd_list(args):
    if not PROFILES_MANIFEST.exists():
        print("[error] Profiles manifest not found", file=sys.stderr)
        return 1

    data = load_manifest(PROFILES_MANIFEST)

    if args.json:
        print(json.dumps(data, indent=2))
        return 0

    print("Available profiles:")
    for p in data["profiles"]:
        print(f"  {p['id']:12} - {p['description']}")
    return 0


def cmd_show(args):
    profile_yml = Path.cwd() / "evol.profile.yml"

    if args.path:
        profile_yml = Path(args.path).resolve() / "evol.profile.yml"

    if not profile_yml.exists():
        print("[error] evol.profile.yml not found", file=sys.stderr)
        return 1

    with open(profile_yml) as f:
        content = f.read()

    if args.json:
        import yaml
        try:
            data = yaml.safe_load(content)
            print(json.dumps(data, indent=2))
        except Exception as e:
            print(f"[error] YAML parse failed: {e}", file=sys.stderr)
            return 1
    else:
        print(content)

    return 0


def cmd_explain(args):
    if not PROFILES_MANIFEST.exists() or not MODULES_MANIFEST.exists():
        print("[error] Manifests not found", file=sys.stderr)
        return 1

    profiles_data = load_manifest(PROFILES_MANIFEST)
    modules_data = load_manifest(MODULES_MANIFEST)

    profile_id = args.profile
    profiles = profiles_data["profiles"]
    all_modules = resolve_modules(profile_id, profiles)

    if not all_modules:
        print(f"[error] Unknown profile: {profile_id}", file=sys.stderr)
        return 1

    if args.json:
        result = {"profile": profile_id, "modules": all_modules}
        module_info = {}
        for m in all_modules:
            m_info = modules_data["modules"].get(m, {})
            module_info[m] = {"description": m_info.get("description", "N/A")}
        result["module_details"] = module_info
        print(json.dumps(result, indent=2))
        return 0

    print(f"Profile: {profile_id}")
    print(f"Modules: {len(all_modules)}")
    print()
    for m in sorted(all_modules):
        desc = modules_data["modules"].get(m, {}).get("description", "No description")
        print(f"  - {m}: {desc}")

    return 0


def cmd_init(args):
    dest = Path(args.path).resolve() if args.path else None

    if not dest:
        print("[error] Destination path required", file=sys.stderr)
        return 1

    init_script = REPO_ROOT / "scripts" / "evol-init.sh"
    if not init_script.exists():
        print(f"[error] Init script not found: {init_script}", file=sys.stderr)
        return 1

    profile = args.profile or "core"
    cmd = ["bash", str(init_script), str(dest), f"--profile={profile}"]

    result = subprocess.run(cmd, cwd=REPO_ROOT)
    return result.returncode


def cmd_upgrade(args):
    profile_yml = Path.cwd() / "evol.profile.yml"

    if not profile_yml.exists():
        print("[error] No evol.profile.yml in current directory", file=sys.stderr)
        return 1

    if not PROFILES_MANIFEST.exists():
        print("[error] Profiles manifest not found", file=sys.stderr)
        return 1

    profiles_data = load_manifest(PROFILES_MANIFEST)
    new_profile = args.profile

    new_modules = set(resolve_modules(new_profile, profiles_data["profiles"]))
    if not new_modules:
        print(f"[error] Unknown profile: {new_profile}", file=sys.stderr)
        return 1

    try:
        import yaml
        with open(profile_yml) as f:
            current = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"[error] Cannot read evol.profile.yml: {e}", file=sys.stderr)
        return 1

    current_modules = set(current.get("modules", []))
    added = new_modules - current_modules

    if not added:
        print(f"[info] Profile '{new_profile}' modules already installed")
        return 0

    current_modules.update(added)
    current["profile"] = new_profile
    current["modules"] = sorted(list(current_modules))

    with open(profile_yml, "w") as f:
        yaml.dump(current, f, default_flow_style=False)

    print(f"[ok] Added {len(added)} modules from profile '{new_profile}'")
    return 0


def cmd_validate(args):
    profile_yml = Path.cwd() / "evol.profile.yml"

    if args.path:
        profile_yml = Path(args.path).resolve() / "evol.profile.yml"

    if not profile_yml.exists():
        print("[error] evol.profile.yml not found", file=sys.stderr)
        return 1

    if not PROFILES_MANIFEST.exists() or not MODULES_MANIFEST.exists():
        print("[error] Manifests not found", file=sys.stderr)
        return 1

    profiles_data = load_manifest(PROFILES_MANIFEST)
    modules_data = load_manifest(MODULES_MANIFEST)

    try:
        import yaml
        with open(profile_yml) as f:
            data = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"[error] YAML parse failed: {e}", file=sys.stderr)
        return 1

    profile_id = data.get("profile")
    if not profile_id:
        print("[error] No 'profile' field in evol.profile.yml", file=sys.stderr)
        return 1

    profile_ids = [p["id"] for p in profiles_data["profiles"]]
    if profile_id not in profile_ids:
        print(f"[error] Unknown profile: {profile_id}", file=sys.stderr)
        return 1

    expected_modules = set(resolve_modules(profile_id, profiles_data["profiles"]))
    actual_modules = set(data.get("modules", []))
    known_module_ids = set(modules_data["modules"].keys())

    missing = expected_modules - actual_modules
    unknown = actual_modules - expected_modules
    invalid = actual_modules - known_module_ids

    errors = []
    warnings = []

    if missing:
        errors.append(f"Missing modules: {', '.join(sorted(missing))}")
    if unknown:
        warnings.append(f"Extra modules not in profile: {', '.join(sorted(unknown))}")
    if invalid:
        errors.append(f"Unknown modules: {', '.join(sorted(invalid))}")

    if args.json:
        result = {
            "profile": profile_id,
            "valid": len(errors) == 0,
            "missing_modules": sorted(list(missing)),
            "extra_modules": sorted(list(unknown)),
            "invalid_modules": sorted(list(invalid)),
            "errors": errors,
            "warnings": warnings
        }
        print(json.dumps(result, indent=2))
        return 0 if len(errors) == 0 else 1

    if errors:
        for e in errors:
            print(f"[error] {e}")
        return 1

    if warnings:
        for w in warnings:
            print(f"[warn] {w}")

    print(f"[ok] Profile '{profile_id}' is valid")
    return 0


def cmd_downgrade(args):
    if not args.force:
        print("[blocked] Downgrade requires --force flag for safety")
        print("This will remove modules not in the target profile")
        print("Use: evol profile downgrade <profile> --force")
        return 1

    print("[info] Downgrade is not yet implemented")
    print("Use 'evol profile upgrade <profile>' to add modules instead")
    return 0


def main():
    parser = argparse.ArgumentParser(prog="evol-profile")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.set_defaults(func=lambda _: parser.print_help())

    subparsers = parser.add_subparsers(dest="command")

    p_list = subparsers.add_parser("list", help="List available profiles")
    p_list.set_defaults(func=cmd_list)

    p_show = subparsers.add_parser("show", help="Show current evol.profile.yml")
    p_show.add_argument("--path", help="Project path")
    p_show.set_defaults(func=cmd_show)

    p_explain = subparsers.add_parser("explain", help="Explain modules for a profile")
    p_explain.add_argument("profile", help="Profile name")
    p_explain.set_defaults(func=cmd_explain)

    p_init = subparsers.add_parser("init", help="Initialize project with profile")
    p_init.add_argument("path", nargs="?", help="Destination path")
    p_init.add_argument("profile", nargs="?", default="core", help="Profile name")
    p_init.set_defaults(func=cmd_init)

    p_upgrade = subparsers.add_parser("upgrade", help="Upgrade to a profile (additive)")
    p_upgrade.add_argument("profile", help="Profile name")
    p_upgrade.set_defaults(func=cmd_upgrade)

    p_validate = subparsers.add_parser("validate", help="Validate evol.profile.yml")
    p_validate.add_argument("--path", help="Project path")
    p_validate.set_defaults(func=cmd_validate)

    p_downgrade = subparsers.add_parser("downgrade", help="Downgrade profile (blocked)")
    p_downgrade.add_argument("profile", help="Profile name")
    p_downgrade.add_argument("--force", action="store_true", help="Bypass safety block")
    p_downgrade.set_defaults(func=cmd_downgrade)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())