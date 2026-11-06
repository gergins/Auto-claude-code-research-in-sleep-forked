#!/usr/bin/env python3
"""ARIS offline run-state demonstration and combined browser workspace. Local-only; no AI model calls."""
from __future__ import annotations
import hashlib
import json
import os
import re
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
RUN_ID = "research-review-demo"
RECORD_DIR = Path.home() / ".aris-research-workspace" / "records"
MAX_BODY = 131072
WORK = Path(tempfile.mkdtemp(prefix="aris-overnight-demo-"))
LOCK = threading.Lock()
DATA = {"mode": "OFFLINE_REAL_STATE_DEMO", "status": "idle", "phase": None,
        "logs": [], "run_id": RUN_ID, "work_dir": str(WORK),
        "started_at": None, "ended_at": None, "run_state": None,
        "review": "NOT_PERFORMED", "model_calls": 0, "cost": 0,
        "record": None, "assessment": None}

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def log(message):
    with LOCK:
        DATA["logs"].append({"time": now(), "message": message})

def state_cmd(*args):
    # Explicit UTF-8 is needed on Windows: ARIS run_state prints Unicode glyphs.
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    proc = subprocess.run([sys.executable, str(ARIS_STATE_TOOL), *map(str, args)],
                          capture_output=True, text=True, encoding="utf-8",
                          env=env, timeout=15, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    return proc.stdout


def load_record():
    """Use the locally captured record, never user-controlled filesystem paths."""
    file = RECORD_DIR / "latest.json"
    if not file.is_file():
        return None
    data = json.loads(file.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("result"), str):
        return None
    return data


def metadata(record):
    content = record["result"].encode("utf-8")
    return {"skill": record.get("skill", "unknown"),
            "sha256": hashlib.sha256(content).hexdigest(),
            "characters": len(record["result"]),
            "review_status": "not-independently-verified",
            "execution_status": record.get("execution_status", "unverified"),
            "saved_locally": True,
            "storage": str(RECORD_DIR / "latest.json")}


def store_record(payload):
    if not isinstance(payload, dict):
        raise ValueError("Expected a JSON research record.")
    content = payload.get("result")
    if not isinstance(content, str) or not content.strip() or len(content) > 100000:
        raise ValueError("Research response must contain 1–100000 text characters.")
    skill = payload.get("skill", "auto-review-loop")
    if not isinstance(skill, str) or not re.fullmatch(r"[a-z0-9-]{1,64}", skill):
        raise ValueError("Invalid skill name.")
    # Preserve the source response, but never promote a user-provided verdict.
    record = {"schema_version": "0.2", "kind": "external-research-output",
              "source": "user-imported-codex-result", "imported_at": now(),
              "skill": skill,
              "invocation": str(payload.get("invocation", ""))[:2000],
              "execution_status": "unverified",
              "review_status": "not-independently-verified",
              "result": content}
    RECORD_DIR.mkdir(parents=True, exist_ok=True)
    # Atomic write; no executable user data; local user-owned folder.
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=RECORD_DIR,
                                      delete=False, suffix=".tmp") as f:
        staged = Path(f.name)
        json.dump(record, f, ensure_ascii=False, indent=2)
    staged.replace(RECORD_DIR / "latest.json")
    return metadata(record)


def assess_record():
    """Deterministic, non-AI extraction. Source links are not verified."""
    record = load_record()
    if record is None:
        raise ValueError("No captured research record to assess.")
    txt = record["result"]
    urls = list(dict.fromkeys(re.findall(r"https?://[^\\s<>\\]\\)\\\"']+", txt)))[:30]
    named = [x for x in ["LiveKit", "Janus", "Jitsi", "Jigasi", "RFC 9248"]
             if x.casefold() in txt.casefold()]
    result = {"source_sha256": metadata(record)["sha256"],
              "mentions": named, "candidate_urls": urls,
              "source_links_checked": False, "claims_independently_verified": False,
              "conclusion": "Captured and indexed; external verification still required.",
              "action": "Review named candidates and verify evidence with an authorized researcher."}
    with LOCK:
        DATA["assessment"] = result
    return result

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
        log("Started ARIS tracker with locally saved Codex research record.")
        state_cmd("start", WORK, RUN_ID, "--phases", "captured_result,inventory,dependencies,assessment,review_gate",
                  "--executor", "deterministic-offline-demo")
        update_state()
        phase("captured_result", lambda: metadata(load_record()), "Load saved Codex research result")
        phase("inventory", inventory, "Scan existing skill files")
        phase("dependencies", dependencies, "Inspect original dependency registry")
        phase("assessment", assess_record, "Index candidate names and source URLs without web verification")
        phase("review_gate", review_gate, "Check independent review gate")
        with LOCK:
            DATA.update(status="finished_unreviewed", phase=None, ended_at=now())
        log("Research record captured and indexed. Verification and independent review remain pending.")
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
            file = Path(__file__).with_name("index.html")
            self.send(200, file.read_bytes(), "text/html; charset=utf-8")
        elif path == "/api/status":
            with LOCK:
                snapshot = json.loads(json.dumps(DATA))
            self.send(200, json.dumps(snapshot).encode("utf-8"), "application/json")
        else:
            self.send(404, b"Not found", "text/plain")
    def do_POST(self):
        endpoint = urlsplit(self.path).path
        if endpoint not in ("/api/start", "/api/research"):
            self.send(404, b"Not found", "text/plain"); return
        origin = self.headers.get("Origin", "")
        host = self.headers.get("Host", "")
        if (host not in ("127.0.0.1:8765", "localhost:8765") or
            (origin and origin not in ("http://127.0.0.1:8765", "http://localhost:8765"))):
            self.send(403, b"Local requests only", "text/plain"); return
        if endpoint == "/api/research":
            length = self.headers.get("Content-Length", "")
            if not length.isdigit() or int(length) < 2 or int(length) > MAX_BODY:
                self.send(413, b"Invalid or oversized JSON", "text/plain"); return
            if not self.headers.get("Content-Type", "").startswith("application/json"):
                self.send(415, b"JSON required", "text/plain"); return
            with LOCK:
                if DATA["status"] in ("starting", "running"):
                    self.send(409, b"Cannot replace research while a run is active", "text/plain"); return
            try:
                payload = json.loads(self.rfile.read(int(length)))
                info = store_record(payload)
                with LOCK:
                    DATA["record"] = info
                log("Saved user-provided research record locally (unverified).")
            except (ValueError, UnicodeError) as exc:
                self.send(400, str(exc), "text/plain"); return
            self.send(200, json.dumps({"saved": True, "record": info}), "application/json")
            return
        with LOCK:
            if DATA["status"] != "idle":
                self.send(409, b"Run already started; restart server to reset.", "text/plain")
                return
            if DATA["record"] is None:
                self.send(409, b"Import or save Codex research result before starting.", "text/plain")
                return
            DATA["status"] = "starting"
        threading.Thread(target=worker, daemon=True).start()
        self.send(202, b'{"started":true}', "application/json")

if __name__ == "__main__":
    if not ARIS_STATE_TOOL.is_file():
        raise SystemExit("Run inside the full ARIS fork: missing tools/run_state.py")
    existing = load_record()
    if existing is not None:
        DATA["record"] = metadata(existing)
    server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    print("ARIS Combined Research Workspace: http://127.0.0.1:8765", flush=True)
    print("No model calls. No paid services. Ctrl+C stops the demo server.", flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
