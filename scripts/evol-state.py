#!/usr/bin/env python3
"""Evol-DD State Store — SQLite-based instincts and session tracking."""
import sqlite3, os, sys, json, argparse
from datetime import datetime, timedelta
from _evol_common import get_state_db, get_data_dir, get_logger, save_json, load_json

logger = get_logger("state")

def get_db():
    db_path = get_state_db()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    os.chmod(os.path.dirname(db_path), 0o700)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database schema."""
    conn = get_db()
    c = conn.cursor()
    
    # Base tables for Evol-DD runtime state.
    c.execute("""
        CREATE TABLE IF NOT EXISTS instincts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern TEXT UNIQUE NOT NULL,
            context TEXT,
            confidence REAL DEFAULT 0.5,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            invalidated BOOLEAN DEFAULT 0,
            invalidation_reason TEXT
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS instinct_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instinct_id INTEGER,
            session_id TEXT,
            triggered BOOLEAN DEFAULT 0,
            outcome TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (instinct_id) REFERENCES instincts(id)
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS sprints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'active',
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS orchestrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern TEXT NOT NULL,
            agents TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS evolutions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instinct_id INTEGER,
            skill_name TEXT UNIQUE,
            cluster_id TEXT,
            status TEXT DEFAULT 'proposed',
            confidence REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved_at TIMESTAMP,
            rolled_back_at TIMESTAMP,
            FOREIGN KEY (instinct_id) REFERENCES instincts(id)
        )
    """)
    
    # NEW tables (Evol-DD specific)
    c.execute("""
        CREATE TABLE IF NOT EXISTS agent_lifecycle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT DEFAULT 'ephemeral',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            retired_at TIMESTAMP,
            sessions_used INTEGER DEFAULT 0,
            retired BOOLEAN DEFAULT 0,
            recalled BOOLEAN DEFAULT 0,
            recalled_at TIMESTAMP,
            expires_after_days INTEGER,
            created_for_task TEXT
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS research_proposals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            scope TEXT DEFAULT 'system',
            topic TEXT,
            score REAL DEFAULT 0.0,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            applied_at TIMESTAMP,
            gh_url TEXT,
            scan_skipped BOOLEAN DEFAULT 0
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info("Database initialized at %s", get_state_db())

def record_instinct(pattern, context=None, confidence=0.5, source=None):
    """Record or update an instinct pattern."""
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO instincts (pattern, context, confidence, source, last_seen)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(pattern) DO UPDATE SET
            confidence = ?,
            context = COALESCE(?, context),
            last_seen = CURRENT_TIMESTAMP
    """, (pattern, context, confidence, source, confidence, context))
    conn.commit()
    conn.close()

def list_instincts(min_confidence=0.0, include_invalidated=False):
    """List instincts above threshold."""
    conn = get_db()
    c = conn.cursor()
    query = "SELECT * FROM instincts WHERE confidence >= ?"
    if not include_invalidated:
        query += " AND invalidated = 0"
    query += " ORDER BY confidence DESC"
    c.execute(query, (min_confidence,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def evolve_status():
    """Show evolution proposals status."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT status, COUNT(*) as count FROM evolutions GROUP BY status")
    rows = c.fetchall()
    conn.close()
    return {r["status"]: r["count"] for r in rows}

def prune_instincts(days=90):
    """Remove instincts not seen in N days."""
    conn = get_db()
    c = conn.cursor()
    cutoff = datetime.now() - timedelta(days=days)
    c.execute("DELETE FROM instincts WHERE last_seen < ? AND invalidated = 0", (cutoff,))
    deleted = c.rowcount
    conn.commit()
    conn.close()
    return deleted

def stats():
    """Show database stats."""
    conn = get_db()
    c = conn.cursor()
    tables = ["instincts", "instinct_sessions", "sprints", "orchestrations", "evolutions", "agent_lifecycle", "research_proposals"]
    result = {}
    for t in tables:
        c.execute(f"SELECT COUNT(*) as cnt FROM {t}")
        result[t] = c.fetchone()["cnt"]
    conn.close()
    return result

def main():
    parser = argparse.ArgumentParser(description="Evol-DD State Store")
    sub = parser.add_subparsers(dest="cmd")
    
    sub.add_parser("init", help="Initialize database")
    sub.add_parser("stats", help="Show stats")
    
    p = sub.add_parser("record-instinct", help="Record instinct pattern")
    p.add_argument("--pattern", required=True)
    p.add_argument("--context", default=None)
    p.add_argument("--confidence", type=float, default=0.5)
    p.add_argument("--source", default=None)
    
    p = sub.add_parser("list", help="List instincts")
    p.add_argument("--min-confidence", type=float, default=0.0)
    p.add_argument("--include-invalidated", action="store_true")
    
    sub.add_parser("evolve", help="Show evolution status")
    p = sub.add_parser("prune", help="Prune old instincts")
    p.add_argument("--days", type=int, default=90)
    
    args = parser.parse_args()
    
    if args.cmd == "init":
        init_db()
        print("OK")
    elif args.cmd == "stats":
        for k, v in stats().items():
            print(f"{k}: {v}")
    elif args.cmd == "record-instinct":
        record_instinct(args.pattern, args.context, args.confidence, args.source)
        print(f"Recorded: {args.pattern}")
    elif args.cmd == "list":
        for row in list_instincts(args.min_confidence, args.include_invalidated):
            print(f"[{row['confidence']:.2f}] {row['pattern']}")
    elif args.cmd == "evolve":
        for k, v in evolve_status().items():
            print(f"{k}: {v}")
    elif args.cmd == "prune":
        print(f"Pruned: {prune_instincts(args.days)}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
