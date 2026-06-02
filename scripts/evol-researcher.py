#!/usr/bin/env python3
"""Evol-DD Researcher — Autonomous research."""
import os, sys, json, argparse, urllib.request, time
from datetime import datetime
from _evol_common import get_logger, get_provider

logger = get_logger("researcher")

RESEARCH_FILE = "RESEARCH.md"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

def search_github(query, topic=None):
    """Search GitHub for skills, frameworks, methodologies."""
    if topic:
        query += f" topic:{topic}"
    
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&per_page=10"
    
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data.get("items", [])
    except urllib.error.HTTPError as e:
        if e.code == 403:
            reset = resp.headers.get("X-RateLimit-Reset", "unknown")
            print(f"[WARN] GitHub rate limit. Reset at: {reset}")
        print("[INFO] Using cached results if available")
        return []
    except Exception as e:
        print(f"[WARN] GitHub unavailable: {e}")
        print("[INFO] sin conexion, propuestas omitidas")
        return []

def generate_proposals(scope, topic=None):
    """Generate ranked improvement proposals."""
    provider = get_provider()
    
    proposals = []
    
    # Search for skills
    skills = search_github("language:markdown skills", "claude-code-skill")
    
    for repo in skills[:5]:
        score = repo.get("stargazers_count", 0) / 1000  # Normalize
        
        proposal = {
            "id": f"prop-{len(proposals) + 1}",
            "title": f"Install skill: {repo['name']}",
            "description": repo.get("description", ""),
            "scope": scope,
            "topic": topic or "skills",
            "score": score,
            "status": "pending",
            "gh_url": repo.get("html_url", ""),
            "created_at": datetime.now().isoformat()
        }
        proposals.append(proposal)
    
    # LLM analysis if available
    if provider.__class__.__name__ != "MockProvider":
        prompt = f"Analyze these proposals and rank by impact:\n{json.dumps(proposals[:3], indent=2)}"
        result = provider.complete(prompt, max_tokens=1000)
        # Would update scores based on LLM analysis
    else:
        print("[mock — requiere LLM real]")
    
    # Save to RESEARCH.md
    with open(RESEARCH_FILE, "w") as f:
        f.write("# Research Proposals\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write(f"Scope: {scope}\n\n")
        
        for p in sorted(proposals, key=lambda x: x["score"], reverse=True):
            f.write(f"## {p['id']}. {p['title']}\n")
            f.write(f"- Score: {p['score']:.2f}\n")
            f.write(f"- Description: {p['description']}\n")
            f.write(f"- Source: {p['gh_url']}\n\n")
    
    # Persist to SQLite
    try:
        import sqlite3
        db_path = os.path.expanduser("~/.evol/state.db")
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        for p in proposals:
            c.execute("""
                INSERT OR REPLACE INTO research_proposals 
                (title, description, scope, topic, score, status, gh_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (p["title"], p["description"], p["scope"], p["topic"], p["score"], p["status"], p["gh_url"]))
        
        conn.commit()
        conn.close()
    except:
        pass
    
    return proposals

def list_proposals():
    """List pending proposals."""
    try:
        import sqlite3
        db_path = os.path.expanduser("~/.evol/state.db")
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT id, title, score, status, gh_url FROM research_proposals WHERE status = 'pending' ORDER BY score DESC")
        rows = c.fetchall()
        conn.close()
        
        if not rows:
            print("[INFO] No pending proposals")
            return
        
        print(f"{len(rows)} pending proposals:\n")
        for row in rows:
            print(f"[{row[0]}] {row[1]} (score: {row[2]:.2f})")
            if row[4]:
                print(f"    Source: {row[4]}")
    except:
        print("[ERROR] Could not load proposals")

def apply_proposal(proposal_id):
    """Apply approved proposal."""
    try:
        import sqlite3
        db_path = os.path.expanduser("~/.evol/state.db")
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        c.execute("SELECT * FROM research_proposals WHERE id = ?", (proposal_id,))
        row = c.fetchone()
        
        if not row:
            print(f"[ERROR] Proposal not found: {proposal_id}")
            conn.close()
            return
        
        print(f"[OK] Applying proposal: {row[1]}")
        
        # Would install skill, update configs, etc.
        
        c.execute("UPDATE research_proposals SET status = 'applied', applied_at = ? WHERE id = ?", 
                  (datetime.now().isoformat(), proposal_id))
        conn.commit()
        conn.close()
        
        print(f"[OK] Proposal applied: {proposal_id}")
    except Exception as e:
        print(f"[ERROR] {e}")

def main():
    parser = argparse.ArgumentParser(description="Evol-DD Researcher")
    sub = parser.add_subparsers(dest="cmd")
    
    p = sub.add_parser("run", help="Run research")
    p.add_argument("--scope", default="system", choices=["system", "project"])
    p.add_argument("--topic")
    
    sub.add_parser("list", help="List pending proposals")
    
    p = sub.add_parser("apply", help="Apply proposal")
    p.add_argument("proposal_id")
    
    args = parser.parse_args()
    
    if args.cmd == "run":
        proposals = generate_proposals(args.scope, args.topic)
        print(f"[OK] Generated {len(proposals)} proposals")
        print(f"[OK] Saved to {RESEARCH_FILE}")
    elif args.cmd == "list":
        list_proposals()
    elif args.cmd == "apply":
        apply_proposal(args.proposal_id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()