# Real ARIS research through Codex CLI — opt-in preview

This is an **initial real execution adapter**, not a complete autonomous ARIS research runtime. It runs a *selected Codex-native ARIS skill* through the installed Codex CLI. It does not run all 87 skills or magically perform missing experiments/reviewers. Read-only constraints can block particular skill stages. All claims remain unverified unless backed by independently checked evidence.

## Supported features

- Readiness: checks `codex` on PATH, `codex login status` and original Codex skill pack in the fork.
- Allowlisted skill selection: `research-lit`, `comm-lit-review`, `idea-discovery`, `auto-review-loop`, `research-wiki`, `research-pipeline`.
- One live model run at a time, explicitly authorized through the website; choose **10, 60 or 480 minutes** maximum.
- Isolated run folder under `~/.aris-research-workspace/live-runs/<run_id>/` with **copied original ARIS Codex-native skill pack and shared references**. No original repository modification.
- Codex CLI `codex exec --json --sandbox read-only --skip-git-repo-check -C <isolated dir> -` with goal supplied on **standard input**.
- Live status, events, readable completed answer, explicit Stop action and process-tree termination (including Windows `codex.cmd` children).
- On completion, **Capture Codex result into ARIS** stores the final assistant message locally in `~/.aris-research-workspace/records/latest.json`, marked **not independently verified**. Run the existing Local Monitor to index candidates and URLs using ARIS's actual `run_state.py`.
- Local-only HTTP server on `127.0.0.1:8765`; no webhook, remote exposure, GitHub upload, automatic merge or deploy.

## Update your existing Windows project

Stop the old ARIS Python server in its PowerShell window (Ctrl+C). Open a new PowerShell window and run:

```powershell
$ErrorActionPreference = "Stop"
$repo = "gergins/Auto-claude-code-research-in-sleep-forked"
$branch = "prototype/aris-workflow-launcher-20261106"

$folder = Join-Path $HOME "Projects\ARIS-combined-workspace"
if (!(Test-Path (Join-Path $folder "tools\run_state.py"))) {
    $folder = Join-Path $HOME "Projects\ARIS-fork-demo"
}
if (!(Test-Path (Join-Path $folder "tools\run_state.py"))) {
    throw "ARIS local clone not found. Follow README.md to clone first."
}
$ui = Join-Path $folder "prototypes\workflow-explorer"
foreach ($name in @("index.html","overnight_demo.py","live_codex.py")) {
    $file = Join-Path $ui $name
    if (Test-Path $file) { Copy-Item $file "$file.bak" -Force }
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/$repo/$branch/prototypes/workflow-explorer/$name" -OutFile $file
}
Set-Location $folder
$env:PYTHONUTF8 = "1"
python .\prototypes\workflow-explorer\overnight_demo.py
```

Keep the server terminal open. Go to **http://127.0.0.1:8765/** and refresh with Ctrl+F5. Scroll to **Run a real ARIS skill with Codex CLI**.

### Codex prerequisites

The **browser Codex chat** and **local Codex CLI** are different execution contexts. Local execution requires Codex CLI installed and signed in on the same Windows PC. Check:

```powershell
codex --version
codex login status
```

If the first fails, refer to the official Codex CLI installation guide (https://learn.chatgpt.com/docs/codex/cli). For a Windows/npm installation, `npm install -g @openai/codex` is one supported method if Node/npm are already installed. After installation run `codex login` and complete the interactive sign-in. **Do not paste authentication tokens into this website or ChatGPT.**

### First real research test

1. Choose **Research literature (start here)**.
2. Retain the VRS goal or enter your own question.
3. Choose **10 minutes** for the first validation.
4. Read and check the authorization box (real model usage may consume plan quota/API credits; the adapter cannot impose a monetary budget).
5. Click **Start real Codex research**. Observe status and the execution event stream.
6. If it completes, view **Codex research answer**.
7. Click **Capture Codex result into ARIS**; then in **Local monitor** click **Start review workflow (local checks)** to inspect saved candidates and source URLs.
8. Click **Stop research** if you want to terminate the live run.

For an overnight attempt, choose 480 minutes deliberately, keep PC and terminal running, and consider applicable token/credit limits. **A maximum runtime is not a monetary cap.** A Windows sleep/reboot or a closed Python process can interrupt the run. There is no automatic background recovery.

## Security / verification boundaries

- No bypass of Codex approvals or sandboxing; fixed read-only sandbox; original skill sources are copied into an isolated per-run directory.
- The selected skill may require writing papers, experiments or results, third-party models, network access or tools the read-only runner cannot provide. It must report **BLOCKED** rather than imply the full ARIS skill executed.
- No independent reviewer is provisioned by this adapter. `review_status: not-independently-verified`, `acceptance: not-accepted` persist even if Codex exits with code zero.
- Full execution JSONL and final response are displayed locally; `run-summary.json` is written to the isolated per-run folder after exit. This is not a guaranteed crash-proof or cost-bounded service.
- User-supplied goal is sent through stdin, not via a shell command or argument; selected skills and runtime durations are allowlisted. Stop attempts to terminate the CLI process tree.
- Source code was verified in GitHub and inline browser JavaScript was syntax-checked. **Actual Windows end-to-end run and CI tests are not yet confirmed.**

## Testing

From repo root:

```powershell
python -m unittest discover -s tests -p "test_workflow_explorer_*.py"
```

These contract tests do not make model calls. Some existing broader ARIS tests may need additional dependencies; the command above only selects this prototype's tests.

## Operational next milestone

Once the 10-minute run is confirmed on Windows, implement monitored **real workflow phase receipts**, bounded resource/token counters (if exposed by CLI), controlled workspace-write for experiments only with separate explicit approval, independent cross-model review routing and actual interruption/recovery. Do not mark this initial CLI bridge as fully capable of overnight research-pipeline or verified acceptance.
