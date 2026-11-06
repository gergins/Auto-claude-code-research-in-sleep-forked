# ARIS Workflow Explorer — fork-only prototype

Run locally: open `prototypes/workflow-explorer/index.html` in a modern browser. No installation or server is needed. No dependencies, cookies, API keys, external JavaScript, tracking or paid model calls.

## What it is
A browser-based **read-only launcher** for real `skills/<name>/SKILL.md` workflows already in this fork. It exposes a curated 16-skill subset from the actual ARIS catalog, search and domain filters, input, documented effort/reviewer choices, original source links, and a copyable invocation for a supported installed ARIS host.

The application does **not** execute ARIS. Running ARIS still requires following upstream `SETUP_GUIDE.md` and configuring a supported AI coding environment and reviewer. Some skills need GPU, model/API services or installed tools. Treat costs and tool permissions as unapproved until deliberately configured.

## Testing and safety
- Static single HTML file with embedded CSS/JS and no third-party runtime dependencies.
- No remote API requests, installation, account handling, secret collection, file mutation, shell execution, or automatic agents.
- Generated command syntax comes from `AGENT_GUIDE.md`; actual acceptance/behavior must be checked against the target SKILL.md and configured host.
- Source links point to `main` for usability and can change with upstream updates; pin an exact commit for reproducible evaluations.
- Prototype is NOT a full list of 87 ARIS skills and should not be represented as such.
- Browser smoke test, automated accessibility test, upstream runtime integration and exact-HEAD CI remain **unverified**.
- Do not merge/deploy until reviewed.

## Prototype acceptance checks (manual)
1. Open local HTML without a server; page renders with 16 curated skills.
2. Search `experiment` and filter `Validate`; choices narrow appropriately.
3. Select `Experiment Plan`, enter a description, set `lite`; generated command begins `/experiment-plan` and references the user input.
4. The original skill link opens `skills/experiment-plan/SKILL.md` on this fork.
5. Copy button copies the generated invocation over HTTPS or via fallback on local browser.
6. Use keyboard Tab/Enter/Space and check responsive layout at phone width.

## Next
Only after validating the real prototype, consider adding: all catalog data extracted from real canonical skill specs; a safe read-only GitHub discovery tool; and a permissioned backend that can run a constrained single skill with explicit costs and independent review. Prefer ARIS's existing runtime instead of recreating an agent platform.
