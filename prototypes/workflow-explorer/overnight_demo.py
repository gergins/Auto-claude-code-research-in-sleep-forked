#!/usr/bin/env python3
"""ARIS offline run-state demonstration. Local-only, no model calls or installation."""
from __future__ import annotations
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
ARIS_STATE_TOOL = ROOT / "tools" / "run_state.py"
RUN_ID = "offline-demo"
WORK = Path(tempfile.mkdtemp(prefix="aris-overnight-demo-"))
LOCK = threading.Lock()
DATA = {"mode": "OFFLINE_REAL_STATE_DEMO", "status": "idle", "phase": None,
        "logs": [], "run_id": RUN_ID, "work_dir": str(WORK),
        "started_at": None, "ended_at": None, "run_state": None,
        "review": "NOT_PERFORMED", "model_calls": 0, "cost": 0}

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def log(message):
    with LOCK:
        DATA["logs"].append({"time": now(), "message": message})

def state_cmd(*args):
    proc = subprocess.run([sys.executable, str(ARIS_STATE_TOOL), *map(str, args)],
                          capture_output=True, text=True, encoding="utf-8",
                          timeout=15, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    return proc.stdout

def update_state():
    file = WORK / ".aris" / "runs" / (RUN_ID + ".json")
    if file.is_file():
        with LOCK:
            DATA["run_state"] = json.loads(file.read_text(encoding="utf-8"))

def phase(name, work, label):
    with LOCK:
        DATA["phase"] = name
    state_cmd("set", WORK, RUN_ID, name, "running")
    update_state()
    log(label + " — executing")
    time.sleep(0.7)
    result = work()
    artifact = WORK / (name + ".json")
    artifact.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    state_cmd("set", WORK, RUN_ID, name, "done", "--artifact", str(artifact))
    update_state()
    log(label + " — completed (NOT independently accepted)")

def inventory():
    from pathlib import Path
    files = sorted((ROOT / "skills").glob("*/SKILL.md"))
    catalog = (ROOT / "docs" / "SKILLS_CATALOG.md").read_text(encoding="utf-8")
    return {"skill_files": len(files),
            "examples": [f.parent.name for f in files[:8]],
            "catalog_mentions_auto_review": "/auto-review-loop" in catalog,
            "scope": "read-only local source inspection"}

def dependencies():
    table = (ROOT / "tools" / "skill-groups.tsv").read_text(encoding="utf-8")
    rows = [line.split("\t") for line in table.splitlines() if line.startswith("skill\t")]
    review = next((line for line in rows if line[1] == "auto-review-loop"), None)
    return {"skill_rows": len(rows), "auto_review_dependencies": review[3].split(",") if review else [],
            "scope": "source dependency listing only"}

def review_gate():
    return {"review_status": "PENDING", "reason": "No reviewer invoked in offline demo.",
            "acceptance": "BLOCKED", "model_calls": 0,
            "next_step": "Run ARIS in configured Codex CLI or Claude Code and capture actual review receipts."}

def worker():
    try:
        with LOCK:
            DATA.update(status="running", started_at=now(), ended_at=None, phase=None, logs=[],
                        review="NOT_PERFORMED", run_state=None)
        log("Started real ARIS run-state tracker in temporary local directory.")
        state_cmd("start", WORK, RUN_ID, "--phases", "inventory,dependencies,review_gate",
                  "--executor", "deterministic-offline-demo")
        update_state()
        phase("inventory", inventory, "Scan existing skill files")
        phase("dependencies", dependencies, "Inspect original dependency registry")
        phase("review_gate", review_gate, "Check independent review gate")
        with LOCK:
            DATA.update(status="finished_unreviewed", phase=None, ended_at=now())
        log("Demonstration finished. Review remains pending: NO false acceptance.")
    except Exception as exc:
        log("Error: " + str(exc))
        with LOCK:
            DATA.update(status="failed", ended_at=now())

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return
    def send(self, status, body, content_type):
        content = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)
    def do_GET(self):
        path = urlsplit(self.path).path
        if path in ("/", "/monitor.html"):
            file = Path(__file__).with_name("monitor.html")
            self.send(200, file.read_bytes(), "text/html; charset=utf-8")
        elif path == "/api/status":
            with LOCK:
                snapshot = json.loads(json.dumps(DATA))
            self.send(200, json.dumps(snapshot).encode("utf-8"), "application/json")
        else:
            self.send(404, b"Not found", "text/plain")
    def do_POST(self):
        if urlsplit(self.path).path != "/api/start":
            self.send(404, b"Not found", "text/plain"); return
        origin = self.headers.get("Origin", "")
        if origin and origin not in ("http://127.0.0.1:8765", "http://localhost:8765"):
            self.send(403, b"Invalid Origin", "text/plain"); return
        with LOCK:
            if DATA["status"] != "idle":
                self.send(409, b"Demo can only run once per server session. Restart the server to reset.", "text/plain")
                return
            DATA["status"] = "starting"
        threading.Thread(target=worker, daemon=True).start()
        self.send(202, b'{"started":true}', "application/json")

if __name__ == "__main__":
    if not ARIS_STATE_TOOL.is_file():
        raise SystemExit("Run inside the full ARIS fork: missing tools/run_state.py")
    server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    print("ARIS Offline Monitor: http://127.0.0.1:8765", flush=True)
    print("No model calls. No paid services. Ctrl+C stops the demo server.", flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
