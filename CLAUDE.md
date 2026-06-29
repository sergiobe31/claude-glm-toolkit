# CLAUDE.md — claude-glm-toolkit

This repo is the **claude-glm-toolkit** Claude Code plugin: a second model (**any OpenRouter model**,
GLM-5.2 by default, via the PAL MCP) plus the `/interceptor` and `/debate` skills. For *what it is*
and *how to run/verify it*, read `README.md` (Claude does not auto-load the README; this file is what
Claude auto-loads here).

## Living doc: `glm_collab.html`

`glm_collab.html` is a self-contained, visual map (English) of the Claude↔second-model collaboration
this plugin enables — organized for a newcomer's first glance: the role split (Claude
orchestrates/executes · the second model advises/contrasts), the two value levers (better prompts ·
second audit) plus a token-heavy-delegation bonus, the "verify, don't trust" discipline, a verified
real-cases section, and an "extend it" section. It opens **offline** (inline CSS, no CDN/JS).
Structure proposed by the second model; content authored & verified by Claude. Rewritten generic +
English on 2026-06-29 (it was a Spanish, GLM-specific version from 2026-06-25).

**Standing instruction — keep it growing, but ONLY with Sergio's consent:**

- Whenever the toolkit's collaboration surface expands — a **new skill**, a **new workflow/flow**, a
  **PAL tool put into real use**, or a **new verified real case** — **OFFER to update
  `glm_collab.html`**. Propose it; **never edit or commit it without Sergio's explicit "yes."**
- **Content discipline (the plugin's own golden rule):** factual content is authored/verified by
  Claude against ground truth (`file:line` / source / trace); GLM may do the visual design. A "real
  case" goes in **only if verified** — no fabricated examples. The page already labels glosa
  (commentary) differently from verified cases; preserve that honesty.
- When updating, keep it **self-contained** (inline CSS, no external deps) so it still opens offline.
