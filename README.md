# claude-glm-toolkit

A **Claude Code plugin** that gives Claude a *second model* — **any OpenRouter model** (GLM-5.2 by
default) — plus two skills, so Claude can collaborate with a model from a **different training
distribution**. The second model catches what self-review misses; the discipline below keeps it
honest.

> **This README is documentation for humans** (and for any agent you explicitly point at it).
> Claude does **not** read it at startup. What Claude auto-loads when the plugin is enabled is the
> two **skills** (their `SKILL.md`) and the **`.mcp.json`** (which starts the GLM server). This file
> exists to record *what this is* and *how to run/verify it*.

---

## What it gives you (the tools — no more, no less)

**1. A second model via the bundled "PAL" MCP server** (any OpenRouter model; GLM-5.2 by default). Exposed as tools named
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

1. The plugin bundles an **MCP server** ("PAL", run via `uvx`) that connects to **OpenRouter**
   (GLM-5.2 by default; **any** OpenRouter model works — see *Choosing the second model*) and exposes
   it as the tools above. PAL runs as a **minimal fork** (`sergiobe31/pal-mcp-server`, pinned by SHA)
   whose only change is a one-file patch enabling OpenRouter reasoning — see *Reasoning* below and
   **[CREDITS.md](CREDITS.md)**. When the plugin is enabled, Claude Code starts this server and the
   tools become callable by the main Claude.
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

### Reasoning

GLM-5.2 runs with **OpenRouter reasoning enabled** — the fork maps PAL's per-call `thinking_mode`
(minimal/low/medium/high/max) onto OpenRouter's `reasoning` effort, and prepends the model's
`<reasoning>` trace to its answer. Claude calls GLM at **xhigh** (`thinking_mode: max`) by default and
dials down for trivial tasks.

It's **generalizable but opt-in per model**: only models with `supports_extended_thinking: true` in
`config/pal_openrouter_models.json` get reasoning. By default that's **only `z-ai/glm-5.2`** — every
other model is byte-identical to upstream PAL. To enable reasoning for another OpenRouter model, flip
its flag to `true`; to disable GLM's, flip it to `false`.

---

## Install / start

> **Bring your own key.** This plugin ships *no* API key. Each user supplies their **own** OpenRouter
> key at install time; it's stored in *their* system keychain, never in the repo. So sharing this repo
> never exposes anyone's key. Who built what is spelled out in **[CREDITS.md](CREDITS.md)**.

**From inside Claude Code** (type these in the prompt; they start with `/`):
```
/plugin marketplace add https://github.com/sergiobe31/claude-glm-toolkit
/plugin install claude-glm-toolkit@sergio-tools
```
→ You'll be prompted for **your own OpenRouter API key** (get one at openrouter.ai; stored in your
system **keychain**, never in the repo). → **Restart** Claude Code (or `/reload-plugins`) so the GLM
server starts.

**If the interactive prompts don't surface** (it happened to us — the `/plugin install` /
`/plugin configure` dialogs didn't appear), use the CLI instead:
```
claude plugin install claude-glm-toolkit@sergio-tools --config openrouter_api_key=YOUR_KEY
```
The key still lands in the keychain because the manifest marks it `sensitive`.

**Prerequisites:** **`uvx`** (the PAL server runs via `uvx`) and an **OpenRouter account** with a
little credit. Nothing else to set up.

> Maintainer / local dev: `marketplace add` also accepts a local path, e.g.
> `/plugin marketplace add /path/to/claude-glm-toolkit`.

## Verify it's live
```
claude mcp list | grep pal                          → plugin:claude-glm-toolkit:pal ... ✔ Connected
mcp__plugin_claude-glm-toolkit_pal__listmodels      → the OpenRouter catalog (gpt-5, gemini-2.5-pro, claude-*, grok-4, …)
/claude-glm-toolkit:debate <a decision>             → the skill responds
```

## Use it day-to-day
- Stress-test a decision → `/claude-glm-toolkit:debate <the decision>`
- Polish a rough idea into a prompt → `/claude-glm-toolkit:interceptor <the idea>`
- Or just ask Claude: *"get GLM's second opinion on X"* / *"have **gpt-5** red-team Y"* — Claude calls
  the PAL tools, with the model you name, and adjudicates the answer.

---

## Choosing the second model

This toolkit is **not locked to GLM** — PAL runs with `DEFAULT_MODEL=auto`, which means *you name the
model per call* and **any OpenRouter model works**:

- **Name it in the request:** *"get **openai/gpt-5**'s opinion on X"*, *"have
  **google/gemini-2.5-pro** red-team Y"*. The skills default to `z-ai/glm-5.2` if you don't name one.
- **Why it just works:** PAL's bundled registry already knows the common models (`openai/gpt-5`,
  `google/gemini-2.5-pro`, `anthropic/claude-*`, `x-ai/grok-4`, `deepseek/*`, …) with their real
  context windows. A model PAL doesn't know **still works** — it just uses a generic ~32K window
  (verified: `providers/openrouter.py:_lookup_capabilities`).
- **No cost guard:** there's no `OPENROUTER_ALLOWED_MODELS` allowlist, so PAL will use whatever model
  you (or a skill) name — including expensive ones. To hard-limit to one model for cost safety, add
  `"OPENROUTER_ALLOWED_MODELS": "your/model"` back to `.mcp.json`.
- **GLM at 1M:** PAL doesn't ship GLM's true 1M window, so by default GLM runs at the generic ~32K.
  For GLM's full 1M context, opt in via `config/pal_openrouter_models.json` (see that file's notes; it
  *replaces* the bundled registry, so use it only when GLM is your sole model). Most second-opinion
  uses don't need 1M.
- **`/debate` caveat:** its value comes from a *different-vendor* model. Point it at an `anthropic/*`
  model and it becomes Claude-vs-Claude — the different-distribution benefit is largely lost.

---

## Structure
```
claude-glm-toolkit/
├── README.md                                  # this file (humans)
├── CREDITS.md                                 # who built what — borrowed vs original
├── LICENSE                                    # MIT (covers the original parts; see CREDITS.md)
├── CLAUDE.md                                  # what Claude auto-loads here (incl. glm_collab.html upkeep rule)
├── glm_collab.html                            # visual map of the collaboration (offline; see CLAUDE.md)
├── .claude-plugin/marketplace.json            # the marketplace catalog ("sergio-tools")
└── plugins/claude-glm-toolkit/                # the self-contained plugin
    ├── .claude-plugin/plugin.json             # manifest + userConfig (openrouter_api_key, sensitive)
    ├── .mcp.json                              # PAL server: bare uvx, ${user_config.openrouter_api_key}, DEFAULT_MODEL=auto
    ├── references/adjudication-protocol.md     # the verify-don't-trust protocol both skills share
    ├── skills/{interceptor,debate}/SKILL.md
    └── config/pal_openrouter_models.json      # GLM-5.2 @ 1M context — OPT-IN (not wired by default; see Choosing the second model)
```

## How it's built (record of decisions)
- Packaged as a **native Claude Code plugin**, not a hand-rolled repo + symlinks + install script.
  This was decided via a `/debate` session cross-checked against the official Claude Code docs: a
  plugin bundles skills + the MCP server + config as **one versioned, installable unit**, the MCP
  **auto-registers** on install, and the secret is handled natively.
- **Secret:** the OpenRouter key is a `userConfig` field with `"sensitive": true` → stored in the
  keychain, referenced in `.mcp.json` as `${user_config.openrouter_api_key}`. Never committed.
- **Model choice:** PAL runs with `DEFAULT_MODEL=auto` and **no** `OPENROUTER_ALLOWED_MODELS`, so the
  caller names the model per call and **any** OpenRouter model works. This was decided via a GLM
  consult adjudicated against PAL's own source (the engine, not memory) — see *Choosing the second
  model*.
- **Config:** the 1M-context GLM registry is shipped in `config/` as an **opt-in** — the default
  `.mcp.json` no longer wires it, so any OpenRouter model keeps its correct window. Enable it via
  `${CLAUDE_PLUGIN_ROOT}` only when GLM is your sole model (it *replaces* PAL's bundled registry).
- **Portability:** PAL launches with **bare `uvx`** (resolves via `$PATH`), so it works across
  machines without hard-coded paths.

## Credits & license

This toolkit is built on other people's work, and it matters to be clear about which parts.
**Full, honest breakdown in [CREDITS.md](CREDITS.md).** The short version:

**Already built by others (not original here):**
- `BeehiveInnovations/pal-mcp-server` — the entire second-model **engine** (all the `pal` tools). Run
  as-is via `uvx`, not forked. *This is the biggest piece, and it isn't mine.*
- `affaan-m/ECC` (MIT) — the `/interceptor` **skeleton** + SKILL conventions.
- `linshenkx/prompt-optimizer` (copyleft) — the "modify-don't-execute" guard, *as a pattern* (no code copied).
- `Alex-R-A/llm-argumentation-protocol` (no license) — `/debate`'s loop **design**, *as inspiration* (no code copied).

**Original to this project (Sergio, with Claude):**
- The **packaging** as a native Claude Code plugin (marketplace + manifest + keychain-backed key + MCP wiring).
- The GLM-5.2 **1M-context fix** (`config/pal_openrouter_models.json`) — diagnosed and declared so PAL stops falling back to 32K; now shipped **opt-in** (any model is the default).
- The **claim-by-claim adjudication discipline** (REAL / SMELL / FALSE-POSITIVE / HALLUCINATION) that makes the second model safe to rely on.
- The two **skills as written** and all the **docs** (README, CLAUDE.md, the `glm_collab.html` brief).

Licensed **MIT** — see [LICENSE](LICENSE).

## Possible extensions (not built)
- **Project-map bootstrapper** — a skill that scans the repo and writes `.claude/interceptor.md` (the
  component map / invariants that `/interceptor` Phase 0 already reads). Deferred on purpose: it mainly
  pays off on large or team repos; for small projects `/interceptor`'s inline Phase-0 scan is enough.
  Modeled on ECC's `brand-voice` producer→schema→consumer pattern if anyone wants to build it.

## Notes / recovery
- Editing a `SKILL.md` takes effect immediately; changes to `.mcp.json` / `plugin.json` need
  `/reload-plugins` or a restart.
- Cost: GLM via OpenRouter ≈ $0.95/M input, $3/M output as of 2026 (other models vary — check
  openrouter.ai for current pricing; with no allowlist there's no cost ceiling). Reach for the second
  model for heavy reading, a second training distribution, or red-teaming, not for trivial things you
  can do inline.
- This plugin **replaced an earlier scattered setup** (loose skills + a user-scope PAL server), now
  consolidated into one versioned, installable unit.
