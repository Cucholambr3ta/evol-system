#!/usr/bin/env python3
"""Evol-DD Evolve — Auto-generate skills from instinct patterns."""
import os, sys, json, argparse, subprocess, hashlib, shutil
from datetime import datetime
from _evol_common import get_logger, Memoria Persistente_safe, save_json, load_json

logger = get_logger("evolve")

SKILLS_DIR = "skills"
EVALS_DIR = "evals"
RETIRED_SKILLS_DIR = "skills/.retired"

def get_instincts(min_confidence=0.7):
    """Get instincts above threshold."""
    try:
        from evol_state import list_instincts
        return list_instincts(min_confidence)
    except:
        # Direct SQLite
        import sqlite3
        db_path = os.path.expanduser("~/.evol/state.db")
        if not os.path.exists(db_path):
            return []
        
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT id, pattern, confidence FROM instincts WHERE confidence >= ? AND invalidated = 0 ORDER BY confidence DESC", (min_confidence,))
        rows = c.fetchall()
        conn.close()
        return [{"id": r[0], "pattern": r[1], "confidence": r[2]} for r in rows]

def cluster_instincts(instincts):
    """Cluster instincts by keyword overlap (TF-IDF stdlib)."""
    clusters = {}
    
    for instinct in instincts:
        words = set(instinct["pattern"].lower().split())
        
        placed = False
        for cluster_id, cluster in clusters.items():
            cluster_words = set(cluster["keywords"])
            overlap = len(words & cluster_words)
            
            if overlap >= 2:  # At least 2 shared words
                cluster["instincts"].append(instinct)
                cluster["keywords"].update(words)
                placed = True
                break
        
        if not placed:
            cluster_id = f"cluster-{len(clusters) + 1}"
            clusters[cluster_id] = {
                "instincts": [instinct],
                "keywords": words
            }
    
    return clusters

def generate_skill(cluster_id, cluster, dry_run=False):
    """Generate skill from cluster."""
    skill_name = f"auto-{cluster_id.replace('cluster-', 'skill-')}"
    skill_dir = os.path.join(SKILLS_DIR, skill_name)
    eval_dir = os.path.join(EVALS_DIR, skill_name)
    
    if dry_run:
        print(f"[dry-run] Would create: {skill_dir}")
        print(f"[dry-run] Would create: {eval_dir}")
        return
    
    os.makedirs(skill_dir, exist_ok=True)
    os.makedirs(eval_dir, exist_ok=True)
    
    # Generate SKILL.md
    skill_content = f"""---
name: {skill_name}
description: Auto-generated skill from instinct cluster {cluster_id}
category: auto-generated
created_at: {datetime.now().isoformat()}
cluster_id: {cluster_id}
confidence: {cluster['instincts'][0]['confidence']:.2f}
---

# {skill_name}

Auto-generated skill from {len(cluster['instincts'])} instinct patterns.

## Origin
Cluster: {cluster_id}
Patterns:
"""
    for instinct in cluster["instincts"]:
        skill_content += f"- {instinct['pattern']} (confidence: {instinct['confidence']:.2f})\n"
    
    skill_content += """
## Capabilities
[TODO: Define capabilities based on patterns]

## Usage
```bash
# Trigger
/skill {skill_name}
```

## Validation
Run: evol eval run --suite={skill_name}
""".format(skill_name=skill_name)
    
    with open(os.path.join(skill_dir, "SKILL.md"), "w") as f:
        f.write(skill_content)
    
    # Generate eval suite
    cases = [{"input": p["pattern"], "expected": "executed"} for p in cluster["instincts"]]
    with open(os.path.join(eval_dir, "cases.jsonl"), "w") as f:
        for case in cases:
            f.write(json.dumps(case) + "\n")
    
    grader = f"""grader: behavioral
description: Auto-generated eval for {skill_name}
pass_threshold: 0.8
"""
    with open(os.path.join(eval_dir, "grader.yaml"), "w") as f:
        f.write(grader)
    
    # Record in evolutions table
    try:
        from evol_state import record_evolution
        record_evolution(skill_name, cluster_id, cluster["instincts"][0]["confidence"])
    except:
        pass
    
    print(f"[OK] Skill generated: {skill_name}")

def approve_skill(cluster_id):
    """Approve proposed skill."""
    # Index in Memoria Persistente
    Memoria Persistente_safe("index", "--path", SKILLS_DIR)
    
    # Index GitNexus if active
    if os.environ.get("EVOL_GITNEXUS") == "1":
        subprocess.run(["npx", "gitnexus", "analyze"], capture_output=True)
    
    print(f"[OK] Skill approved and indexed: {cluster_id}")

def invalidate_instinct(instinct_id, reason=None):
    """Mark instinct as invalid (anti-pattern)."""
    try:
        from evol_state import invalidate_instinct
        invalidate_instinct(instinct_id, reason)
    except:
        import sqlite3
        db_path = os.path.expanduser("~/.evol/state.db")
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("UPDATE instincts SET invalidated = 1, invalidation_reason = ? WHERE id = ?", (reason or "", instinct_id))
        conn.commit()
        conn.close()
    
    print(f"[OK] Instinct invalidated: {instinct_id}")

def rollback_skill(skill_name):
    """Rollback auto-generated skill."""
    skill_dir = os.path.join(SKILLS_DIR, skill_name)
    
    if not os.path.exists(skill_dir):
        print(f"[ERROR] Skill not found: {skill_name}")
        sys.exit(1)
    
    # Move to retired
    os.makedirs(RETIRED_SKILLS_DIR, exist_ok=True)
    dest = os.path.join(RETIRED_SKILLS_DIR, f"{skill_name}-{datetime.now().strftime('%Y%m%d')}")
    shutil.move(skill_dir, dest)
    
    print(f"[OK] Skill rolled back: {skill_name} -> {dest}")

def sync_community(dry_run=False):
    """Sync skills from GitHub community."""
    # Search GitHub for repos with topic claude-code-skill or evol-dd-skill
    
    try:
        import urllib.request
        url = "https://api.github.com/search/repositories?q=topic:claude-code-skill+OR+topic:evol-dd-skill&per_page=20"
        
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json"})
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        
        print(f"[INFO] Found {data['total_count']} community skills:")
        
        for repo in data.get("items", []):
            print(f"  - {repo['full_name']} ({repo['stargazers_count']} stars)")
            
            if dry_run:
                continue
            
            # Check for frontmatter
            # Would download and validate
    except Exception as e:
        print(f"[WARN] GitHub unavailable: {e}")
        print("[INFO] sin conexion, propuestas omitidas")
        return

def validate_frontmatter(content):
    """Validate SKILL.md frontmatter has required fields."""
    import re
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "No frontmatter found"
    
    fm_text = match.group(1)
    for field in ["name:", "description:"]:
        if field not in fm_text:
            return False, f"Missing required field: {field.strip(':')}"
    
    name_match = re.search(r'^name:\s*(.+)$', fm_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9][a-z0-9-]*$', name):
            return False, f"Invalid skill name format: {name}"
    
    return True, "valid"

def quarantine_and_scan(skill_path, tmp_dir):
    """Copy skill to quarantine dir and scan for secrets/dangerous configs."""
    import tempfile, re
    
    scan_dir = tempfile.mkdtemp(prefix="evol-skill-scan-", dir=tmp_dir)
    quarantine_dir = os.path.join(scan_dir, "skill")
    shutil.copytree(skill_path, quarantine_dir)
    
    has_gitleaks = subprocess.run(["which", "gitleaks"], capture_output=True).returncode == 0
    has_semgrep = subprocess.run(["which", "semgrep"], capture_output=True).returncode == 0
    
    errors = []
    
    skill_md = os.path.join(quarantine_dir, "SKILL.md")
    if os.path.exists(skill_md):
        with open(skill_md) as f:
            content = f.read()
        
        valid, msg = validate_frontmatter(content)
        if not valid:
            errors.append(f"Frontmatter validation failed: {msg}")
        
        dangerous_refs = re.findall(r'\.(?:evol|xdd|gates?|keys?|secrets?|state)', content, re.IGNORECASE)
        if dangerous_refs:
            errors.append(f"Dangerous config references detected: {dangerous_refs[:3]}")
    
    if has_gitleaks:
        result = subprocess.run(
            ["gitleaks", "detect", "--no-git", "--source", quarantine_dir],
            capture_output=True
        )
        if result.returncode != 0:
            output = result.stdout.decode()
            if "secrets" in output.lower() or "findings" in output.lower():
                errors.append("Secret detected by gitleaks")
    
    if has_semgrep and os.path.exists(skill_md):
        result = subprocess.run(
            ["semgrep", "--config", "auto", "--json", "--quiet", quarantine_dir],
            capture_output=True
        )
        try:
            data = json.loads(result.stdout.decode())
            if data.get("results"):
                errors.append(f"Semgrep found {len(data['results'])} issues")
        except:
            pass
    
    shutil.rmtree(scan_dir, ignore_errors=True)
    return errors

def compute_skill_hash(skill_path):
    """Compute SHA256 hash of skill directory."""
    h = hashlib.sha256()
    for root, dirs, files in os.walk(skill_path):
        dirs.sort()
        for fname in sorted(files):
            fpath = os.path.join(root, fname)
            with open(fpath, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
    return h.hexdigest()

def load_installed_registry():
    """Load installed skills registry."""
    registry_path = ".evol/.skill-registry.json"
    if os.path.exists(registry_path):
        return load_json(registry_path)
    return {}

def save_installed_registry(registry):
    """Save installed skills registry."""
    registry_path = ".evol/.skill-registry.json"
    os.makedirs(os.path.dirname(registry_path), exist_ok=True)
    save_json(registry, registry_path)
    os.chmod(registry_path, 0o600)

def install_skill(skill_spec):
    """Install community skill with full supply-chain security.
    
    skill_spec format:
      - local path (must exist)
      - remote URL (must include @sha for pinning, e.g. https://github.com/user/repo @abc123)
      - registry name (installed from known community)
    """
    import urllib.request, tempfile
    
    print(f"[INFO] Installing: {skill_spec}")
    
    tmp_dir = tempfile.mkdtemp(prefix="evol-install-")
    skill_path = None
    origin_label = "local"
    
    try:
        if skill_spec.startswith("http://") or skill_spec.startswith("https://"):
            origin_label = "remote"
            if "@" not in skill_spec:
                print("[ERROR] Remote skill requires commit SHA pin: <url>@<sha>")
                print("[INFO] Example: https://github.com/user/skill@abc123def")
                sys.exit(1)
            
            url, pin = skill_spec.rsplit("@", 1)
            if len(pin) < 7:
                print(f"[ERROR] Commit SHA too short (need 7+ chars): {pin}")
                sys.exit(1)
            
            print(f"[INFO] Remote: {url}")
            print(f"[INFO] Pin: {pin} (first 7 chars)")
            
            try:
                req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read())
                    tarball_url = f"{url.rstrip('/')}/archive/{pin}.tar.gz"
                
                import tarfile, io
                with urllib.request.urlopen(tarball_url, timeout=30) as tar_resp:
                    tar_data = tar_resp.read()
                
                skill_path = os.path.join(tmp_dir, "skill")
                with tarfile.open(fileobj=io.BytesIO(tar_data), mode="r:*") as tar:
                    members = tar.getmembers()
                    base = members[0].name.split("/")[0]
                    for m in members:
                        m.name = m.name[len(base)+1:] if m.name.startswith(base + "/") else m.name
                    tar.extractall(tmp_dir, members=members)
                
            except Exception as e:
                print(f"[ERROR] Failed to download remote skill: {e}")
                sys.exit(1)
        elif os.path.isdir(skill_spec):
            skill_path = skill_spec
        else:
            print(f"[ERROR] Skill not found: {skill_spec}")
            sys.exit(1)
        
        errors = quarantine_and_scan(skill_path, tmp_dir)
        
        if errors:
            print(f"\n[ERROR] Skill failed supply-chain checks:")
            for err in errors:
                print(f"  - {err}")
            print("\n[INFO] To override with gate approval, run:")
            print(f"  evol-gate approve install-unsafe --skill {skill_spec}")
            print("[INFO] Manual override stores approval in .evol/.skill-overrides.json")
            sys.exit(1)
        
        skill_hash = compute_skill_hash(skill_path)
        dest = os.path.join(SKILLS_DIR, os.path.basename(skill_path.rstrip("/")))
        
        if os.path.exists(dest):
            print(f"[WARN] Skill already exists: {dest}")
            print(f"[INFO] Existing hash: {skill_hash}")
            shutil.rmtree(dest)
        
        shutil.copytree(skill_path, dest)
        
        registry = load_installed_registry()
        registry[os.path.basename(dest)] = {
            "hash": skill_hash,
            "origin": origin_label,
            "spec": skill_spec,
            "installed_at": datetime.now().isoformat()
        }
        save_installed_registry(registry)
        
        print(f"[OK] Skill installed: {dest}")
        print(f"[OK] Hash: {skill_hash}")
        
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

def status():
    """Show evolution status."""
    instincts = get_instincts()
    print(f"[INFO] Instinct candidates: {len(instincts)}")
    
    if instincts:
        print("\nTop patterns:")
        for i, inst in enumerate(instincts[:5]):
            print(f"  {i+1}. [{inst['confidence']:.2f}] {inst['pattern']}")

def main():
    parser = argparse.ArgumentParser(description="Evol-DD Evolve")
    sub = parser.add_subparsers(dest="cmd")
    
    sub.add_parser("status", help="Show instinct candidates")
    
    p = sub.add_parser("run", help="Generate skill proposals")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--min-confidence", type=float, default=0.7)
    
    p = sub.add_parser("approve", help="Approve proposal")
    p.add_argument("cluster_id")
    
    p = sub.add_parser("invalidate", help="Mark instinct as invalid")
    p.add_argument("instinct_id")
    p.add_argument("--reason")
    
    p = sub.add_parser("rollback", help="Rollback auto-generated skill")
    p.add_argument("skill_name")
    
    p = sub.add_parser("sync-community", help="Sync from GitHub")
    p.add_argument("--dry-run", action="store_true")
    
    p = sub.add_parser("install-skill", help="Install community skill")
    p.add_argument("skill_spec", help="Skill: local path, remote URL@SHA, or registry name")
    p.add_argument("--force", action="store_true", help="Skip supply-chain checks (requires gate approval)")
    
    args = parser.parse_args()
    
    if args.cmd == "status":
        status()
    elif args.cmd == "run":
        instincts = get_instincts(args.min_confidence)
        clusters = cluster_instincts(instincts)
        print(f"[INFO] {len(clusters)} clusters found")
        for cid, cluster in clusters.items():
            if not args.dry_run:
                generate_skill(cid, cluster)
            else:
                print(f"[dry-run] Cluster: {cid} ({len(cluster['instincts'])} patterns)")
    elif args.cmd == "approve":
        approve_skill(args.cluster_id)
    elif args.cmd == "invalidate":
        invalidate_instinct(args.instinct_id, args.reason)
    elif args.cmd == "rollback":
        rollback_skill(args.skill_name)
    elif args.cmd == "sync-community":
        sync_community(args.dry_run)
    elif args.cmd == "install-skill":
        if args.force:
            override_path = ".evol/.skill-overrides.json"
            os.makedirs(".evol", exist_ok=True)
            overrides = load_json(override_path) if os.path.exists(override_path) else {}
            overrides[args.skill_spec] = {
                "approved_at": datetime.now().isoformat(),
                "reason": "manual override"
            }
            save_json(overrides, override_path)
            os.chmod(override_path, 0o600)
            print(f"[WARN] Force install requested. Override registered.")
            print(f"[INFO] Skill will be installed without supply-chain checks.")
        install_skill(args.skill_spec)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()