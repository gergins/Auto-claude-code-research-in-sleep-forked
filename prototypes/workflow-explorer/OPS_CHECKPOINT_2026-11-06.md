# ARIS Research Workspace — Operational Checkpoint

## User-confirmed Windows UI milestone — 2026-11-06

**Confirmed by user:** "it works" after installing the new `index.html` result-view selector and refreshing the locally hosted ARIS workspace. The selector operates in their Windows browser without restarting the Python server or losing the currently displayed Codex answer.

**Selector views:** Research report (default), Findings & evidence, Risks & next actions, Original Codex answer, Technical execution JSON. The first three views rearrange verbatim heading-based content from the existing completed Codex answer; they do **not** create new evidence, perform independent verification, or alter the underlying research text. Technical event JSON is still available for auditing.

**Exact source HEAD before this checkpoint update:** `c9982cc6ac1b846067e7c786427d4209ee5a106d`.

**User-confirmed scope:** Visible selector works. **Not independently verified:** usability of all five individual view outputs, research factual accuracy, source citations, independent cross-model review, persistent reports, overnight unattended operation, and current CI. Do not expand the success claim.

**Next safe milestones:** preserve/export final Codex research response as unverified artifact; improve the readable report only if evidence-backed; optionally add a provenance-aware report export and clearly separated approval gate; validate tests and exact-HEAD CI when available. Keep original ARIS source of truth and open-source reuse-first principle. No merge, deployment or spend without explicit approval.

---


**Saved:** 2026-11-06 (Europe/Stockholm)
**Repository:** https://github.com/gergins/Auto-claude-code-research-in-sleep-forked
**Working branch:** `prototype/aris-workflow-launcher-20261106`
**Review:** https://github.com/gergins/Auto-claude-code-research-in-sleep-forked/pull/1 (DRAFT; unmerged)
**Checkpoint baseline HEAD before this document:** `7b608ce9da664188262ef465dddd51ed3e2e58f3`

## Goal

Reuse the upstream ARIS research skills rather than build a separate research engine. Provide a single Windows-accessible ARIS Research Workspace where the user can browse 87 skill capabilities, capture Codex results, inspect local ARIS run-state, and optionally launch **real** bounded Codex-native ARIS research through installed, authenticated Codex CLI. Initially target open-source components for Deaf three-party VRS (LiveKit/LiveKit SIP, Janus, Jitsi) while keeping the workflow reusable for other research goals.

## Implemented on the draft branch

- `prototypes/workflow-explorer/index.html`: one-page capability catalog with Discover / Validate / Build / Publish / Improve filters, skill invocation generation, research result paste and JSON import/export, live local-state monitor, and separate real Codex execution controls (10/60/480-minute runtime choices, explicit consent, status, stop, readable result, event JSON).
- `prototypes/workflow-explorer/overnight_demo.py`: loopback-only local HTTP service at `http://127.0.0.1:8765/`. Saves captured Codex text to `~/.aris-research-workspace/records/latest.json`; reads and indexes known candidate names/source URLs without claiming verification. Tracks capture/inventory/dependencies/assessment/review gate using the **original upstream** `tools/run_state.py`; Windows UTF-8 subprocess fix applied. Endpoints for local and live modes, including capture.
- `prototypes/workflow-explorer/live_codex.py`: **opt-in real** Codex CLI subprocess, preflight for installed CLI and `codex login status`, copies Codex-native ARIS skill pack to isolated per-run working directory, fixed read-only Codex sandbox, allowlisted skill choices, prompt sent on stdin, maximum 10/60/480 minute wall-clock bounds, streaming status and final answer, process-tree stop, single active run, local run-summary output and response capture into existing research intake.
- `prototypes/workflow-explorer/LIVE_CODEX.md`: PowerShell setup and detailed execution constraints.
- `prototypes/workflow-explorer/README.md`, `MONITOR_DEMO.md`: operating and recovery instructions, local JSON handling and monitor boundaries.
- `tests/test_workflow_explorer_win_encoding.py`, `test_workflow_explorer_result_capture.py`, `test_workflow_explorer_live_codex.py`: source-level/regression tests added.

## Verification and known limitations

- GitHub source read-back confirmed relevant source files, controls, and endpoints; inline browser JavaScript parsed in a syntax-only check.
- **No verified successful Windows end-to-end execution** of the new live Codex adapter yet; run the 10-minute validation first.
- **No CI checks/workflow runs** returned for previous exact branch HEAD `7b608ce9da664188262ef465dddd51ed3e2e58f3`. The new checkpoint commit likewise must be checked before any readiness claim.
- Codex CLI login/credit availability on the user's machine **not proven**.
- Read-only sandbox deliberately prevents ARIS skill stages that require generated files, experiments, deployment, package installation, or external reviewer setups. Some full research-pipeline tasks therefore **block**, rather than run overnight to completion.
- A duration bound is **not a monetary/token budget**. Model calls may consume plan quota or credits. No guaranteed all-night completion, persistence across reboot, or autonomous recovery.
- A Codex self-review is same-family; **do not represent it as independent cross-family approval**. Local run-state `done` is execution-completeness, not `accepted`. Imported research is marked unverified. No source URLs/claims are automatically independently checked.
- Local storage replaces `records/latest.json` on each save; user should preserve exports before new runs. No automatic GitHub upload of captured research.

## Resume safely

1. Verify this repo/branch/PR and current exact HEAD. Leave `main` and other app repos unchanged. No merge/deploy/spend without permission.
2. On Windows, stop old local Python server (Ctrl+C). Update **three** files from the draft branch: `index.html`, `overnight_demo.py`, `live_codex.py`. Follow `LIVE_CODEX.md`; retain backup of local modifications.
3. Start `python .\prototypes\workflow-explorer\overnight_demo.py` from the ARIS fork root. Open `http://127.0.0.1:8765/` and hard refresh.
4. Confirm preflight `Codex CLI: found` and `Codex sign-in: ready`. If missing, install/sign in using the official Codex CLI workflow, without passing credentials through the website.
5. Authorize a **10-minute read-only** test of `research-lit` for the VRS open-source comparison; inspect real Codex events, final answer and any BLOCKED capability prerequisites.
6. If completed, use `Capture Codex result into ARIS`, then `Local monitor → Start review workflow (local checks)`. Verify local saved record/hash, candidate URL extraction, run-state and unverified labels.
7. Run `python -m unittest discover -s tests -p "test_workflow_explorer_*.py"` and Windows browser smoke tests; capture evidence/logs in PR before considering broader sessions.
8. Next engineering milestone: robust process lifecycle, crash/restart-safe resume, actual token/usage accounting and cost limits, independent reviewer evidence, and explicit approval of any write-capable execution. Reuse ARIS original components, not a parallel orchestration engine.

## Operator safety principles

- **Discover and reuse upstream before custom implementation**.
- **Read-only by default**, explicit consent before real model calls; keep requests bounded.
- **Declared evidence and provenance before acceptance**; never infer verified research from a CLI exit code or a generated JSON file.
- **No automatic merge, deployment, paid infrastructure, or modifications to VRS repositories**.
- No ongoing work is implied by this checkpoint; this is a durable GitHub snapshot, not an active scheduled job.
