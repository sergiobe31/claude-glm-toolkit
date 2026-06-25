# claude-glm-toolkit

A Claude Code **plugin** packaging a cross-model collaboration setup: a second model
(**GLM-5.2**, 1M-token context) via the **PAL MCP**, plus two skills — **`/interceptor`**
(idea → ready-to-paste prompt) and **`/debate`** (adversarial chamber) — and the discipline of
**claim-by-claim adjudication** (the second model's output is never accepted unverified).

This repo is a single-plugin **marketplace** (`sergio-tools`). Installing it auto-registers the
PAL MCP server (no manual `claude mcp add`) and prompts once for your OpenRouter API key, which is
stored in your system keychain — never committed.

## Install

```
/plugin marketplace add /Users/sbe31/Desktop/claude-glm-toolkit
/plugin install claude-glm-toolkit@sergio-tools
```

On enable you'll be prompted for your **OpenRouter API key** (sensitive → keychain). Then restart
Claude Code (or `/reload-plugins`) so the MCP server starts.

Verify:
```
claude mcp list | grep pal          # → pal ... ✔ Connected
/claude-glm-toolkit:debate          # skills are namespaced under the plugin
mcp__pal__listmodels                # → z-ai/glm-5.2 ... 1M context
```

## What you get

- **Second model (GLM-5.2 via PAL).** Tools `mcp__pal__*`: `chat` (second opinion), `challenge`
  (devil's advocate on a claim), `consensus` (structured for/against), `thinkdeep`, `codereview`,
  `listmodels`, etc. 1M-context config in `config/pal_openrouter_models.json`. GLM has **no web/file
  browsing** — you gather facts; it reasons over what you pass (prompt or `absolute_file_paths`).
- **`/claude-glm-toolkit:interceptor <idea>`** — captures project context, diagnoses gaps,
  optionally has GLM draft/red-team the prompt, returns it for review. Advisory (never executes).
  A project may add a `.claude/interceptor.md` map for sharper, project-specific prompts.
- **`/claude-glm-toolkit:debate <decision>`** — you form a position, GLM attacks under an evidence
  gate, you adjudicate claim-by-claim, synthesize a verdict. Capped at 2–3 rounds.
- **The discipline.** Classify every second-model claim against ground truth: REAL / SMELL /
  FALSE-POSITIVE / HALLUCINATION. Verify line numbers & claims yourself.

## Structure

```
claude-glm-toolkit/
├── .claude-plugin/marketplace.json            # the marketplace catalog
├── plugins/claude-glm-toolkit/                # the self-contained plugin
│   ├── .claude-plugin/plugin.json             # manifest (+ userConfig: openrouter_api_key)
│   ├── .mcp.json                              # PAL server (bare uvx, ${user_config.*}, ${CLAUDE_PLUGIN_ROOT})
│   ├── skills/{interceptor,debate}/SKILL.md
│   └── config/pal_openrouter_models.json      # GLM-5.2 @ 1M context
└── docs/GLM_COLLAB_reference.md               # background manifest
```

## Head repos (provenance)
- `BeehiveInnovations/pal-mcp-server` — the MCP server exposing GLM (run via `uvx`, not forked).
- `affaan-m/ECC` (MIT) — `/interceptor` skeleton + SKILL conventions.
- `linshenkx/prompt-optimizer` (copyleft) — patterns only (modify-don't-execute guard), no code copied.
- `Alex-R-A/llm-argumentation-protocol` (no license) — design inspiration for `/debate`, no code copied.

## Notes
- Editing a `SKILL.md` takes effect immediately; changes to `.mcp.json`/`plugin.json` need
  `/reload-plugins` or a restart.
- GLM via OpenRouter ≈ $0.95/M input, $3/M output — reach for it for heavy reading / a second
  training distribution / red-teaming, not for things you can do inline.
- Supersedes the earlier scattered `~/.claude` setup (user-scope PAL + loose skills + GLM_COLLAB.md).
