# Connected Codex Result → Local ARIS State (new)

The web page now supports a genuine **local intake** of a Codex research result: choose the already-exported JSON or paste the response, click **Save result to local ARIS workspace**, and then **Start review workflow (local checks)**. The runner uses the saved result as its input, records a SHA-256 checksum, extracts candidate mentions and source URLs, and writes unaccepted phase artifacts through the existing `tools/run_state.py`. AI reviewer, source fetches and claims verification remain unperformed.

## Update the existing Windows clone

Stop the old Python process using Ctrl+C first, then in PowerShell:

```powershell
$ErrorActionPreference = "Stop"
$branch = "prototype/aris-workflow-launcher-20261106"
$repo = "gergins/Auto-claude-code-research-in-sleep-forked"
$folder = Join-Path $HOME "Projects\ARIS-combined-workspace"
if (!(Test-Path $folder)) { $folder = Join-Path $HOME "Projects\ARIS-fork-demo" }
if (!(Test-Path (Join-Path $folder "tools\run_state.py"))) { throw "Existing ARIS fork directory not found" }
$ui = Join-Path $folder "prototypes\workflow-explorer"
foreach ($name in @("index.html","overnight_demo.py")) {
  $target = Join-Path $ui $name
  if (Test-Path $target) { Copy-Item $target "$target.bak" -Force }
  $url = "https://raw.githubusercontent.com/$repo/$branch/prototypes/workflow-explorer/$name"
  Invoke-WebRequest -Uri $url -OutFile $target
}
Set-Location $folder
$env:PYTHONUTF8 = "1"
python .\prototypes\workflow-explorer\overnight_demo.py
```

Open **http://127.0.0.1:8765/** (Ctrl+F5). Under **Capture Codex results**, choose the JSON you downloaded before (or paste the response), then click **Save result to local ARIS workspace**. Under **Live run monitor**, click **Start review workflow (local checks)**. Inspect the record hash, extracted candidate mentions and source URLs, actual run phase statuses and review gate.

**Local persistence**: the response is written to `~/.aris-research-workspace/records/latest.json` on your PC (user-profile path). It survives server restarts, though each new save replaces the `latest.json` copy; keep exported backups for multiple research runs. It is not uploaded to GitHub.

**Security**: server binds only 127.0.0.1:8765; local-only POST, JSON-only limit 128 KiB; no user-supplied filesystem path is evaluated; the result is treated as text, not executed. Do not paste passwords or private personal data. Test and browser verification are not yet confirmed.

**Evidence**: User-pasted claims remain unverified. The runner's final phase is `done` (code ran), **not `accepted`** (independently verified). It does not call Codex, Claude, GitHub, or external APIs. Actual autonomous research still needs a separately configured ARIS agent host, explicit model budgets/permissions and reviewer receipt verification.

---
## Windows fix: Run failed / Unicode charmap U+2192

If the monitor shows `Run failed` and activity shows `charmap codec can't encode character '\\u2192'`, the old launcher used Windows' default cp1252 for the ARIS child process. This is fixed in the prototype branch by forcing `PYTHONIOENCODING=utf-8` and `PYTHONUTF8=1` in the child subprocess.

Stop the current Python web server in its PowerShell window with **Ctrl+C**. To update just the launcher inside a clone that already has the prototype files, run:

```powershell
$ErrorActionPreference = "Stop"
$folder = Join-Path $HOME "Projects\ARIS-combined-workspace"
if (!(Test-Path (Join-Path $folder "prototypes\workflow-explorer\overnight_demo.py"))) { throw "Combined workspace not found at $folder" }
$uri = "https://raw.githubusercontent.com/gergins/Auto-claude-code-research-in-sleep-forked/prototype/aris-workflow-launcher-20261106/prototypes/workflow-explorer/overnight_demo.py"
$file = Join-Path $folder "prototypes\workflow-explorer\overnight_demo.py"
Invoke-WebRequest -Uri $uri -OutFile $file
Set-Location $folder
python .\prototypes\workflow-explorer\overnight_demo.py
```

Reopen http://127.0.0.1:8765/ (not the old monitor.html) and click Start bounded local demo. A new Python process resets the one-run-only state. If you used `Projects\ARIS-fork-demo` instead, replace `$folder` accordingly.

**Safety:** this updates only the launcher file inside that known local clone; no merge/deploy. If you edited that file yourself, back it up first. Only launch code you trust.

---
# ARIS Combined Research Workspace — Single Page

The former separate Workflow Explorer and monitor now appear on one browser page: `prototypes/workflow-explorer/index.html`.

Included: (1) all 87 documented ARIS skills and command generation, (2) a Codex/Claude result-pasting section with JSON export and unverified-evidence labels, (3) local live run-state monitoring using original `tools/run_state.py`.

## Run all three on Windows PowerShell

Clone into a **new** folder (no changes to existing local repositories):

```powershell
$ErrorActionPreference = "Stop"
$target = Join-Path $HOME "Projects\ARIS-combined-workspace"
git clone --depth 1 --branch prototype/aris-workflow-launcher-20261106 https://github.com/gergins/Auto-claude-code-research-in-sleep-forked.git $target
Set-Location $target
python .\prototypes\workflow-explorer\overnight_demo.py
```

Leave PowerShell open. Open **http://127.0.0.1:8765/** in your browser. The top navigation jumps to the skill catalog, **Capture Codex results**, and **Live run monitor**. Paste the prior LiveKit/Codex answer in Capture results. Click **Start bounded local demo** to see genuine ARIS phase tracking. Export a local JSON file when desired.

Opening `index.html` directly works for browsing/capture but the monitor remains offline. The legacy `monitor.html` now redirects to the combined page.

**Verified architecture only:** local source checks and real phase tracking. **Not executed:** AI research, independent Codex review, overnight tasks, GPU. Pasted results are not automatically analyzed or saved to GitHub. Run-state source exists on the fork; Windows end-to-end tests and exact-HEAD CI remain unverified.

Security: server is bound only to 127.0.0.1, no model calls, credentials, installations, uploads or deployments. Avoid pasting secrets. Stop server with Ctrl+C. Review code before running it.

---
# Previous catalog notes

Run locally: open `prototypes/workflow-explorer/index.html` in a modern browser. No installation or server needed. No external JavaScript, API keys, tracking or paid model calls.

## Inventory provenance and scope
- **87 skills** are populated from `docs/SKILLS_CATALOG.md`, cross-referenced with verified skill-to-skill dependency definitions from `tools/skill-groups.tsv` on the original fork baseline at commit `2901234ad2954cd2388ced8d3aed2ed9de42803a`.
- Each skill exposes its upstream title/summary, category, stated external requirements and direct skill dependencies, plus a link to its canonical `skills/<name>/SKILL.md`.
- This is **catalog coverage**, not installed/executed capability verification. External requirements can include paid APIs/GPU. It is a curated user interface over the existing ARIS research methodology, not a competing research runtime.
- The original ARIS source has 48 top-level tool entries, 11 MCP server directories, 19 template entries, 82 entries in the tests directory and five workflow files; existence does not establish successful execution.
- The full catalog is checked into this HTML for offline access. It must be regenerated/reconciled with the upstream catalog and dependency registry when the upstream fork changes, to avoid stale entries.
- The visual filters (Discover, Validate, Build, Publish, Improve) are prototype conveniences, not authoritative ARIS categorization. Original group names appear on skill cards.

## Interaction
1. Search across all 87 skills, including requirements, group names and dependency names; filter by workflow category.
2. Select a skill, provide a research task, configure effort/reviewer, copy invocation to a supported **installed** ARIS host.
3. Paste an externally obtained Codex/Claude response in **Capture research results**. Select evidence status.
4. Export an explicit JSON research record containing source skill, generated command, actual pasted response, and `review_status: not-independently-verified`. It is only a local file download, not a GitHub commit or database update.

## Why a pasted Codex answer is not an ARIS review receipt
The copied `/auto-review-loop` instruction is only a command string. Without a compatible environment recognizing the original ARIS skill and recording review-state artifacts, a model can answer as ordinary research. Never label that as the ARIS auto-review-loop successfully running. The real skill may write `review-stage/AUTO_REVIEW.md`, `REVIEW_STATE.json` and evidence of reviewer identity/results.

## Safety and validation
- No repo-wide installers or model services are launched by this file.
- The paste form may contain sensitive information. Do not paste secrets or user personal data; exported JSON is user-controlled.
- The exported status is explicitly self-reported and NEVER confers independent security approval.
- Accessibility and manual browser interaction tests, dynamic data updates, full external integration, Windows environment compatibility, and exact-HEAD CI are **pending**.
- Potential follow-up: run existing ARIS tests against the exact PR SHA once CI is available, and perform synthetic tests in a configured isolated host. Do not automatically install 87 skills or run GPU workloads.

## Manual smoke check
1. Open HTML locally: 87 skills should appear across Discover/Validate/Build/Publish/Improve filters.
2. Search `wiki`, `experiment`, `review`; results should narrow.
3. Pick `/auto-review-loop`; confirm dependencies displayed, source URL points at this fork.
4. Enter `proven open source for video relay service`, choose balanced + Codex and copy generated invocation.
5. Paste the previously obtained Codex answer; export JSON and inspect `review_status` and `execution_status`.
6. Test keyboard use, mobile width and empty-input warnings.
7. Review all findings before permitting model calls, execution or integration with other repositories.

Nothing merged/deployed and no spending or external execution initiated.
