# claude-glm-toolkit

A **Claude Code plugin** that gives Claude a *second model* — **GLM-5.2** (1M-token context, via
OpenRouter) — plus two skills, so Claude can collaborate with a model from a **different training
distribution**. The second model catches what self-review misses; the discipline below keeps it
honest.

> **This README is documentation for humans** (and for any agent you explicitly point at it).
> Claude does **not** read it at startup. What Claude auto-loads when the plugin is enabled is the
> two **skills** (their `SKILL.md`) and the **`.mcp.json`** (which starts the GLM server). This file
> exists to record *what this is* and *how to run/verify it*.

---

## What it gives you (the tools — no more, no less)

**1. A second model: GLM-5.2 via the bundled "PAL" MCP server.** Exposed as tools named
`mcp__plugin_claude-glm-toolkit_pal__*`. The full menu:

| Group | Tools |
|---|---|
| Think / decide | `chat` (free-form second opinion), `consensus` (structured for/against), `challenge` (devil's advocate on one claim), `thinkdeep`, `planner` |
| Code | `codereview`, `precommit`, `secaudit`, `testgen`, `refactor`, `debug`, `tracer`, `docgen`, `analyze` |
| Util | `listmodels`, `apilookup`, `version` |

**2. Two skills** (namespaced under the plugin):

- **`/claude-glm-toolkit:interceptor <idea>`** — turns a rough idea into a complete, ready-to-paste
  prompt: captures project context, diagnoses gaps, optionally has GLM draft/red-team the prompt,
  returns it for review. Advisory — it never executes the task.
- **`/claude-glm-toolkit:debate <decision>`** — Claude forms a position, GLM attacks it under an
  *evidence gate*, Claude adjudicates claim-by-claim, then synthesizes a verdict. Capped at 2–3
  rounds (debate amplifies shared bias after round 1).

---

## How the cross-model interaction actually works (the mechanism)

1. The plugin bundles an **MCP server** ("PAL", `BeehiveInnovations/pal-mcp-server`, run via `uvx`)
   that connects to **GLM-5.2 through OpenRouter** and exposes it as the tools above. When the plugin
   is enabled, Claude Code starts this server and the tools become callable by the main Claude.
2. **Division of labor:** the **main Claude orchestrates and gathers ground truth** — it has file,
   web, and repo access. **GLM reasons/critiques over what Claude passes it** (in the prompt, or as
   attached file paths). GLM has **no web/file browsing of its own**.
3. **The discipline (non-negotiable):** GLM's output is a *proposal*, never truth, until the main
   Claude **verifies it claim-by-claim** against ground truth (`file:line` / source / trace) and
   tags each as **REAL / SMELL / FALSE-POSITIVE / HALLUCINATION**. This is what turns a second model
   from a liability into an asset.
4. The two **skills are pre-built choreographies** of this loop — interceptor for prompt
   drafting/red-teaming, debate for an adversarial decision check.

So "interaction between models" = the main Claude calling the GLM tools, then **adjudicating** the
result. Never a blind hand-off.

---

## Install / start

**From inside Claude Code** (type these in the prompt; they start with `/`):
```
/plugin marketplace add /Users/sbe31/Desktop/claude-glm-toolkit
/plugin install claude-glm-toolkit@sergio-tools
```
→ You'll be prompted for your **OpenRouter API key** (stored in the macOS **keychain**, never in the
repo). → **Restart** Claude Code (or `/reload-plugins`) so the GLM server starts.

**If the interactive prompts don't surface** (it happened to us — the `/plugin install` /
`/plugin configure` dialogs didn't appear), use the CLI instead:
```
claude plugin install claude-glm-toolkit@sergio-tools --config openrouter_api_key=YOUR_KEY
```
The key still lands in the keychain because the manifest marks it `sensitive`.

**On another machine:** copy/clone this folder, then run the same commands. The only prerequisite is
**`uvx`** (the PAL server runs via `uvx`). Nothing else to set up.

## Verify it's live
```
claude mcp list | grep pal                          → plugin:claude-glm-toolkit:pal ... ✔ Connected
mcp__plugin_claude-glm-toolkit_pal__listmodels      → z-ai/glm-5.2 (1M context)
/claude-glm-toolkit:debate <a decision>             → the skill responds
```

## Use it day-to-day
- Stress-test a decision → `/claude-glm-toolkit:debate <the decision>`
- Polish a rough idea into a prompt → `/claude-glm-toolkit:interceptor <the idea>`
- Or just ask Claude: *"get GLM's second opinion on X"* / *"have GLM red-team Y"* — Claude calls the
  PAL tools and adjudicates the answer.

---

## Structure
```
claude-glm-toolkit/
├── .claude-plugin/marketplace.json            # the marketplace catalog ("sergio-tools")
└── plugins/claude-glm-toolkit/                # the self-contained plugin
    ├── .claude-plugin/plugin.json             # manifest + userConfig (openrouter_api_key, sensitive)
    ├── .mcp.json                              # PAL server: bare uvx, ${user_config.*}, ${CLAUDE_PLUGIN_ROOT}
    ├── skills/{interceptor,debate}/SKILL.md
    └── config/pal_openrouter_models.json      # GLM-5.2 @ 1M context (declared so PAL doesn't fall back to 32K)
```

## How it's built (record of decisions)
- Packaged as a **native Claude Code plugin**, not a hand-rolled repo + symlinks + install script.
  This was decided via a `/debate` session cross-checked against the official Claude Code docs: a
  plugin bundles skills + the MCP server + config as **one versioned, installable unit**, the MCP
  **auto-registers** on install, and the secret is handled natively.
- **Secret:** the OpenRouter key is a `userConfig` field with `"sensitive": true` → stored in the
  keychain, referenced in `.mcp.json` as `${user_config.openrouter_api_key}`. Never committed.
- **Config:** the 1M-context model registry is shipped in `config/` and referenced via
  `${CLAUDE_PLUGIN_ROOT}` (absolute path resolves per-machine at install time).
- **Portability:** PAL launches with **bare `uvx`** (resolves via `$PATH`), so it works across
  machines without hard-coded paths.

## Provenance (head repos)
- `BeehiveInnovations/pal-mcp-server` — the MCP server exposing GLM (run via `uvx`, not forked).
- `affaan-m/ECC` (MIT) — the `/interceptor` skeleton + SKILL conventions.
- `linshenkx/prompt-optimizer` (copyleft) — *patterns only* (the "modify-don't-execute" guard); no code copied.
- `Alex-R-A/llm-argumentation-protocol` (no license) — design inspiration for `/debate`; no code copied.

## Notes / recovery
- Editing a `SKILL.md` takes effect immediately; changes to `.mcp.json` / `plugin.json` need
  `/reload-plugins` or a restart.
- Cost: GLM via OpenRouter ≈ $0.95/M input, $3/M output — reach for it for heavy reading, a second
  training distribution, or red-teaming, not for trivial things you can do inline.
- This plugin **replaced an earlier scattered setup** (loose skills in `~/.claude/skills/` + a
  user-scope PAL server). Those originals were moved to `~/.claude/_pre_plugin_backup_20260625/`
  (recoverable) when the plugin took over.
