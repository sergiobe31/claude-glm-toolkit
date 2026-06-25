# Claude + GLM-5.2 collaboration — portable capabilities manifest

> **For any Claude Code chat, in any project on this machine.** If you were pointed here, this
> file tells you what cross-model tooling is available globally and how to **verify you can access
> it**. Run the Access Check first; if anything fails, see "If access is missing".
> Last verified: 2026-06-24.

## TL;DR — what you have
- A **second model**, GLM-5.2 (1M-token context), as a thinking/adversary partner via the **PAL MCP**.
- Two **user-scope skills** available in *every* project: **`/interceptor`** (idea → ready-to-paste
  prompt) and **`/debate`** (adversarial chamber).
- A **discipline**: the second model's output is a *proposal*, never truth, until you verify it.

## Access check (run these)
1. **PAL connected?** `claude mcp list | grep pal` → expect `pal: ... ✔ Connected`.
2. **GLM tools present?** PAL exposes `mcp__pal__*` (`chat`, `consensus`, `challenge`, `thinkdeep`,
   `listmodels`, …). If they appear as deferred tools, load with `ToolSearch` query
   `select:mcp__pal__chat`.
3. **1M context (not 32K)?** `mcp__pal__listmodels` should show `z-ai/glm-5.2 … 1M context`.
   Config lives at `~/.claude/pal_openrouter_models.json` (`context_window: 1048576`).
4. **Skills present?** `ls ~/.claude/skills/` → expect `interceptor` and `debate` (user-scope →
   usable in any project).

If 1–4 pass, you have full access. Use the capabilities below.

## Capabilities

### 1. Second model — GLM-5.2 via the PAL MCP
- **What:** `BeehiveInnovations/pal-mcp-server` registered at **USER scope** in `~/.claude.json`,
  restricted (via `OPENROUTER_ALLOWED_MODELS`) to OpenRouter model **`z-ai/glm-5.2`** (1M ctx).
- **Tools:** `mcp__pal__chat` (free-form / second opinion), `challenge` (force critical re-exam of
  a claim), `consensus` (structured for/against debate), `thinkdeep` (deep multi-step reasoning),
  `listmodels`.
- **Use for:** heavy multi-file reading (1M ctx), a second opinion from a *different training
  distribution*, red-teaming a design or finding.
- **CRITICAL:** GLM has **no web/file browsing** — it sees only what you put in the `prompt` or pass
  via `absolute_file_paths`. **You** gather the facts (you have the tools); it reasons over them.

### 2. `/interceptor` — idea → ready-to-paste prompt
- `~/.claude/skills/interceptor/SKILL.md`. Turns a rough idea into a complete prompt: captures
  project context (reads `CLAUDE.md` + any `.claude/interceptor.md` map), diagnoses gaps, optionally
  has GLM draft/red-team the prompt, and returns it **for your review** (advisory — never executes).
- A project may add a `.claude/interceptor.md` with its sharp component/invariant map.

### 3. `/debate` — adversarial chamber
- `~/.claude/skills/debate/SKILL.md`. Pressure-tests a decision/claim: you form a position, GLM
  attacks it under an **evidence gate**, you **adjudicate** claim-by-claim, then synthesize a
  verdict. Capped at 2–3 rounds (bias amplification). Falls back to self-adversarial if PAL is down.

### 4. The discipline (applies to all of the above)
The second model's output is **never accepted unverified**. Classify each claim against ground truth
(file:line / trace / source): **REAL · SMELL (needs a check) · FALSE-POSITIVE · HALLUCINATION**.
Verification cuts both ways — it rescues real points and kills plausible-but-wrong ones.

### 5. Full PAL tool menu (not just `chat`)
`mcp__pal__*`, all running on `z-ai/glm-5.2`. Load any via `ToolSearch` query `select:mcp__pal__<name>`.
- **Think / decide:** `chat` (free-form, second opinion), `consensus` (multi-stance for/against debate),
  `challenge` (force critical re-exam of one claim), `thinkdeep` (deep multi-step), `planner`.
- **Code:** `codereview`, `precommit`, `secaudit`, `testgen`, `refactor`, `debug`, `tracer`, `docgen`, `analyze`.
- **Util:** `listmodels`, `apilookup`, `version`, `clink`.

### 6. When to reach for GLM (and when not)
GLM calls cost money (~$0.95/M in, $3/M out) and add latency. Reach for it when the task benefits from a
**different training distribution** or **1M-ctx heavy reading**: auditing a large codebase, red-teaming a
design/finding, a second opinion on a hard call, drafting/critiquing a prompt, reviewing a big script.
**Don't** for things you can do inline cheaply (a grep, a small edit, a fact you can verify yourself).
Default: gather + decide inline; escalate to GLM for depth or adversarial value.

### Multi-round with GLM
Reuse the `continuation_id` returned by any `mcp__pal__*` call to thread a multi-turn conversation — GLM keeps
full context across calls (verified: it recalled a prior proposal across turns). Use for debate rounds / deep-dives.

## Recipes
- **Heavy-read audit (Manager):** `mcp__pal__chat` with `absolute_file_paths=[…]`; ask for findings with
  file:line; then adjudicate each against the code.
- **Prompt build:** `/interceptor <idea>` → a reviewable prompt.
- **Adversarial decision:** `/debate <decision>` → your position → GLM attacks → you adjudicate → verdict.
- **Code review by a second model:** `mcp__pal__codereview` (or pass the file to `chat`); then YOU adjudicate —
  never merge on GLM's say-so.

## Head repos (provenance — verified 2026-06-24)
- **`BeehiveInnovations/pal-mcp-server`** — the MCP server exposing GLM (Apache-2.0; GitHub flags its
  LICENSE as non-standard). We *run* it via `uvx`, we don't fork it.
- **`affaan-m/ECC`** — **MIT**. Source of the `/interceptor` skeleton (`skills/prompt-optimizer/
  SKILL.md`) and SKILL conventions. Safe to adapt.
- **`linshenkx/prompt-optimizer`** — copyleft (AGPL-style; GitHub NOASSERTION). **Patterns only**
  (the "modify-don't-execute" guard, iterate/compare modes) — no code copied.
- **`Alex-R-A/llm-argumentation-protocol`** — no clear license. **Design inspiration** for `/debate`
  (evidence gates, deliberation persistence) — no code copied.

## If access is missing
- **PAL not listed:** register at user scope —
  `claude mcp add-json pal '<json>' --scope user`, where `<json>` runs `uvx --from
  git+https://github.com/BeehiveInnovations/pal-mcp-server.git pal-mcp-server` with env
  `OPENROUTER_API_KEY` (an OpenRouter key — required), `OPENROUTER_ALLOWED_MODELS=z-ai/glm-5.2`,
  `OPENROUTER_MODELS_CONFIG_PATH=/Users/sbe31/.claude/pal_openrouter_models.json`,
  `DEFAULT_MODEL=auto`. Then **restart Claude** (MCP config is read at startup).
- **PAL listed but shows 32K context:** ensure `OPENROUTER_MODELS_CONFIG_PATH` points to
  `~/.claude/pal_openrouter_models.json` (which declares 1M), then restart.
- **Skills missing:** they live in `~/.claude/skills/{interceptor,debate}/SKILL.md`.

## Caveats
- PAL config changes only take effect on **Claude restart** (registry read at startup) — e.g.
  `claude --continue` from the project directory.
- PAL appends an `AGENT'S TURN:` boilerplate to each response — ignore it.
- GLM's private reasoning (CoT) does **not** persist across turns — only the visible text does. For
  incremental reasoning across rounds, serialize your conclusions into the visible response.
- This file is the **portable user-facing manifest**. The full build log / decisions live in the
  `rule_extraction` project memory (`project_claude_glm_collab_env.md`).
