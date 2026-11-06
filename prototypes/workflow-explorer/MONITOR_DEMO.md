# ARIS Offline Run-State Monitor (M1 demonstration)

This is a **real local execution demonstration using ARIS's existing tools/run_state.py**, NOT a simulated AI-review outcome, NOT an AI research runner, and NOT an overnight autonomous model task. It runs deterministic source checks and shows genuine phase transitions in a browser. The browser/server do not make model calls, incur API costs, or install anything.

## Windows PowerShell — first run

Open PowerShell (not Administrator). Requires git and Python already installed.

```powershell
$ErrorActionPreference = "Stop"
$folder = Join-Path $HOME "Projects\ARIS-fork-demo"
$repo = "https://github.com/gergins/Auto-claude-code-research-in-sleep-forked.git"
$branch = "prototype/aris-workflow-launcher-20261106"

if (!(Test-Path $folder)) {
    git clone --branch $branch --single-branch $repo $folder
}
Set-Location $folder

# Confirm required source is present. Do not run anything from another repository.
if (!(Test-Path ".\tools\run_state.py")) { throw "Missing ARIS tool" }
if (!(Test-Path ".\prototypes\workflow-explorer\overnight_demo.py")) { throw "Missing demo" }

# Leave this terminal open while using the monitor.
python .\prototypes\workflow-explorer\overnight_demo.py
```

Open http://127.0.0.1:8765 in your browser. Click **Start monitored demo**.

If `python` does not work, try `py -3 .\prototypes\workflow-explorer\overnight_demo.py`.

For subsequent updates, from the same clone (with no local edits):
`git fetch origin prototype/aris-workflow-launcher-20261106`. Inspect changes and advance the local branch only after review; do not reset any uncommitted work.

## What the demo genuinely does

1. Creates a temporary directory on your Windows machine.
2. Calls the original `tools/run_state.py start` to initialize a three-phase run.
3. Calls the original `tools/run_state.py set` for `running` and `done` as it scans local skills and reads `tools/skill-groups.tsv`.
4. Records a **pending independent review** rather than creating false acceptance records.
5. Displays real status JSON and timestamped log messages through a local-only HTTP server.
6. Leaves temporary result files on the machine until removed by the user/OS.
7. Stops the server on Ctrl+C. It does not run overnight automatically.

The phases are **inventory**, **dependencies** and **review_gate**, not genuine AI literature analysis. A real ARIS research run requires a properly installed host, model/reviewer credentials and configured budget limits. Its `auto-review-loop` is internally iterative and should NOT be wrapped in an external timer.

## Security & limitations
- HTTP server binds only to `127.0.0.1:8765`, not to the network interface.
- POST /api/start launches one bounded local demo per process; no arbitrary command execution or caller-supplied shell args.
- Server executes only the repository's existing `tools/run_state.py` via Python subprocess. Inspect the fork source before running.
- No background persistence: the server runs while terminal is open.
- No independent review, no real model inference, no GPU use, no deployment, no secrets.
- Port 8765 must be free. If occupied, stop the other application; do not expose the demo publicly.
- Browser and Windows end-to-end execution have not been confirmed. Run a manual local smoke test.
- Source integration intentionally respects the upstream status vocabulary: done does not mean accepted.

## Next gated step
After confirming the monitor runs on Windows, determine whether a supported *installed ARIS host* can export machine-readable run state/receipts. Only then add a permissioned adapter to show real live research progress. Preserve independent authorization for model/API costs, filesystem writes and review acceptance.
