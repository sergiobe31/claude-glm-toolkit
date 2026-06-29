# Credits & Attribution

This toolkit stands on other people's work. This file separates — as honestly as I can — **what was
already built (and by whom)** from **what is original to this project**. If you only read one thing,
read the TL;DR.

## TL;DR

- The second-model **engine** — the PAL MCP server and *all* of its tools — is **not mine**. It's
  [`BeehiveInnovations/pal-mcp-server`](https://github.com/BeehiveInnovations/pal-mcp-server), run
  as-is via `uvx`. This is the single biggest functional piece of the toolkit.
- The **`/interceptor` skeleton** and its SKILL conventions came from
  [`affaan-m/ECC`](https://github.com/affaan-m/ECC) (MIT).
- **`/debate`'s loop design** was adapted (ideas, not code) from
  [`Alex-R-A/llm-argumentation-protocol`](https://github.com/Alex-R-A/llm-argumentation-protocol).
- The **"modify, don't execute" guard** is a pattern from
  [`linshenkx/prompt-optimizer`](https://github.com/linshenkx/prompt-optimizer) (no code copied).
- **What is original here:** the *packaging* into a native Claude Code plugin, the *GLM 1M-context
  fix*, the *claim-by-claim cross-model adjudication discipline*, and the *two skills as written* plus
  the *documentation* — authored by **Sergio together with Claude** (Anthropic's Claude Code).

---

## What comes from other repositories (NOT original to this project)

### 1. The second model itself — `BeehiveInnovations/pal-mcp-server` — *the biggest piece*

Everything that actually talks to the second model (GLM-5.2 by default) — every `mcp__…_pal__*` tool (`chat`, `consensus`,
`challenge`, `thinkdeep`, `planner`, `codereview`, `precommit`, `secaudit`, `testgen`, `refactor`,
`debug`, `tracer`, `docgen`, `analyze`, `listmodels`, `apilookup`, `version`) — is the **PAL MCP
server**. This project **does not fork, vendor, or modify it**: `.mcp.json` launches it straight from
its upstream git repo via `uvx`. None of that code is mine.

- Source: https://github.com/BeehiveInnovations/pal-mcp-server
- How it's used here: invoked as-is via `uvx --from git+…`; see `plugins/claude-glm-toolkit/.mcp.json`.
- License: per the upstream repo — not redistributed here, so its own terms apply.

### 2. `/interceptor` skeleton & SKILL conventions — `affaan-m/ECC` (MIT)

The structure/scaffolding of the `interceptor` skill and the SKILL.md conventions are **adapted from
ECC**. The pipeline, rubric and guards *as written* were reworked for this toolkit (by Sergio +
Claude), but the bones come from ECC and the credit belongs there.

- Source: https://github.com/affaan-m/ECC
- License: **MIT** — its copyright/permission notice should travel with any substantial reuse.

### 3. "Modify, don't execute" guard — `linshenkx/prompt-optimizer` (copyleft)

The discipline that the prompt-building skill **produces a prompt and never obeys it** is a *pattern*
borrowed from prompt-optimizer. **Idea only — no code was copied**, so the copyleft terms attach to
their code, not to this repo.

- Source: https://github.com/linshenkx/prompt-optimizer
- License: copyleft — relevant only if you copy their **code** (this project doesn't).

### 4. `/debate` loop design — `Alex-R-A/llm-argumentation-protocol` (no license)

The debate loop adapts the **evidence-gate / decision-framing / deliberation-persistence** ideas from
this protocol (skills-based cross-vendor debate). **Design inspiration only — no code copied.** Note
the upstream repo states **no license** (i.e. all rights reserved), so do not copy its code without
permission; ideas/design are what was reused here.

- Source: https://github.com/Alex-R-A/llm-argumentation-protocol

### External reference (not a dependency)

- **arXiv 2505.19477** — the basis for `/debate`'s 2–3 round cap (debate amplifies shared bias after
  round 1). Cited, not incorporated.

---

## What IS original to this project (Sergio, with Claude)

These are the parts written for this toolkit. They were authored by **Sergio in pairing with Claude**
(Anthropic's Claude Code) — the SKILL files already record this as `author: Sergio + Claude`.

1. **Packaging as a native Claude Code plugin.** Assembling the PAL server + the two skills + the
   model config into one versioned, installable unit, with the secret handled natively:
   - `.claude-plugin/marketplace.json` — the marketplace catalog.
   - `plugins/claude-glm-toolkit/.claude-plugin/plugin.json` — the manifest + the `userConfig`
     `openrouter_api_key` marked `sensitive` (→ system keychain, never in the repo).
   - `plugins/claude-glm-toolkit/.mcp.json` — the wiring: `${user_config.openrouter_api_key}`,
     `DEFAULT_MODEL=auto`, and bare `uvx` for portability (the `OPENROUTER_ALLOWED_MODELS` allowlist and
     the `${CLAUDE_PLUGIN_ROOT}` registry path were removed in the model-agnostic shift — see item 2).
   - *This is what makes "bring your own key, never share mine" work by design.*

2. **The GLM-5.2 1M-context fix** — `plugins/claude-glm-toolkit/config/pal_openrouter_models.json`.
   Diagnosed that PAL falls back to a generic 32K window for models it doesn't know
   (`providers/openrouter.py:_lookup_capabilities`), which was silently capping GLM. Declared
   `z-ai/glm-5.2` with its real **1,048,576**-token window so the registry hit bypasses the fallback.
   This is original troubleshooting + fix, not borrowed. *Now shipped as an **opt-in**: the default
   `.mcp.json` no longer wires it (the custom registry **replaces** PAL's bundled one, which would cap
   every other model at 32K), so any OpenRouter model keeps its correct window and GLM users opt in
   for the full 1M.*

3. **The cross-model adjudication discipline** — the rule that GLM's output is a *proposal, never
   truth*, until verified claim-by-claim against ground truth (`file:line` / source / trace) and
   tagged **REAL / SMELL / FALSE-POSITIVE / HALLUCINATION**, plus the division of labor (Claude
   gathers ground truth and has the tools; GLM reasons over what it's given; Claude adjudicates). This
   methodology — not any single line of code — is what turns a generic second-model bridge into
   something safe to rely on.

4. **The two skills as written** — `skills/interceptor/SKILL.md` and `skills/debate/SKILL.md`. Built
   on the upstream bones credited above, but the actual phases, rubric, guards, evidence gate,
   round-cap and adjudication wiring as they stand here are this project's.

5. **The documentation** — `README.md`, `CLAUDE.md`, this `CREDITS.md`, and the *brief* behind
   `glm_collab.html` (the visual map: Claude wrote & verified the factual content, GLM-5.2 did the
   visual design — a collaboration artifact, labeled as such).

---

## Honest scale check

It would be wrong to read this repo as "I built a second-model collaboration engine." The heavy
lifting of *actually talking to a second model* belongs to **pal-mcp-server**, and the two skills grew
from other people's skeletons and designs. My contribution is the **integration, the 1M-context fix,
the adjudication discipline, and the documentation** — the layer that turns a generic MCP bridge into
a disciplined, installable Claude + GLM workflow where the second model is verified rather than
trusted. That layer is real and is mine (with Claude); the engine underneath is theirs. Credit to all
of the above.

---

## Licenses at a glance

| Project | Role here | License | Obligation when you share this repo |
|---|---|---|---|
| **This toolkit** | the plugin + config + skills + docs | **MIT** (see [LICENSE](LICENSE)) | keep the MIT notice |
| `pal-mcp-server` | the second-model engine (run via `uvx`) | upstream's own | not redistributed here — see its repo |
| `affaan-m/ECC` | `/interceptor` skeleton | **MIT** | preserve ECC's copyright/permission notice on substantial reuse |
| `prompt-optimizer` | "modify-don't-execute" pattern | copyleft | none — pattern only, no code copied |
| `llm-argumentation-protocol` | `/debate` loop design | **none stated** (all rights reserved) | don't copy its code; ideas/design only were reused |

The MIT `LICENSE` covers **only this project's own original parts** (the plugin packaging, the
1M-context config, the cross-model adjudication discipline, the two skills as written, and the docs).
It does **not** relicense the third-party work above — each upstream keeps its own terms.

If you build on this toolkit, keep this file and the `LICENSE` intact, and respect each upstream
project's own terms.
