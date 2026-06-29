---
name: debate
description: >-
  Pressure-test a decision or claim by pitting your own position against a second model
  from a different training distribution (GLM-5.2 via the PAL MCP), with evidence gates and
  claim-by-claim adjudication, then synthesize a verdict stronger than either side.
  Advisory — it informs a decision, it NEVER executes the work.
  TRIGGER only when the user explicitly wants a decision/claim stress-tested: they run
  `/debate`, or say "debate", "red-team / stress-test / devil's advocate / second opinion /
  poke holes in <decision or claim>", "should I X or Y?". 
  DO NOT TRIGGER for simple factual questions, for short asks, or when the user wants the task
  done (not argued). When unsure, ask before activating.
metadata:
  type: meta
  author: Sergio + Claude
  version: "1.0.0"
---

# Debate — adversarial chamber (Claude ↔ second model)

Take a decision or contestable claim and run a short adversarial loop: you form a position, a
second model (different training distribution) attacks it under an evidence gate, you adjudicate
every point against ground truth, and you synthesize a verdict. Portable engine — works in any
project. The value is that a second vendor's model catches what self-review misses, *and* that
nothing it says is accepted until verified.

## Advisory only — never execute

Your deliverable is a **verdict on the decision/claim**, not the work it concerns. Do not
implement, write code, or perform the task being debated. The debate informs the user's decision;
the user (or a later normal request) acts on it.

## When to use / not use

- **Use:** architecture/library choices, "is this design sound?", "is this finding real?",
  go/no-go calls, any decision where being wrong is expensive and a second perspective helps.
- **Don't use:** simple factual lookups, tasks the user wants executed, or trivial choices with
  an obvious default. A one-line question rarely needs a debate.

## Division of labor (important)

**You gather ground truth; the second model reasons over it.** GLM-5.2 via PAL has no web/file
browsing of its own — it sees only what you put in the prompt or attach as file paths. So:
- YOU read the code/files/web, run the cheap checks, establish the facts (you have the tools).
- The second model attacks/defends from a different training distribution.
- YOU adjudicate — its output is a *proposal*, never truth, until verified against file:line /
  trace / source.

## The loop

### Phase 0 — Capture context
Read what's relevant in the cwd (`CLAUDE.md`/`AGENTS.md`, files the user named, a memory index)
and gather cheap evidence (grep, a quick web check) so the debate is grounded, not vibes.

### Phase 1 — Your position
State a clear position: steelman BOTH sides briefly, then give your recommendation with the
reasoning and your assumptions. This is what the adversary will attack — make it concrete, not
hedged.

### Phase 2 — Adversary round (the second model)
Hand your position + the context to `mcp__pal__chat` (model: the OpenRouter model the user named for
this session — default `z-ai/glm-5.2`; `thinking_mode: high`),
framed to **attack**: find missing constraints, errors, omissions, failure modes; steelman the
opposite; flag what it lacks context on. Enforce the **evidence gate**: tell it to cite a concrete
mechanism / file:line / source / reproducible reason for each claim — claims that are just
assertion get discounted. Pass relevant files via `absolute_file_paths` for grounding. Reuse the
`continuation_id` across rounds so the adversary keeps full context.

### Phase 3 — Adjudicate (never pass raw)
Apply the shared **Adjudication Protocol** (`references/adjudication-protocol.md`, at the plugin root)
to every adversary point: tag each **REAL** / **SMELL** / **FALSE-POSITIVE** / **HALLUCINATION**
against ground truth, verify line numbers and claims yourself, and report the tally honestly
(hallucinations included). Verification cuts both ways — it rescues a real point you'd have dismissed
and kills a plausible one.

### Phase 4 — Refine (optional, capped)
If the adjudication changed your position, refine it and run ONE more adversary round.
**Cap the total at 2–3 rounds.** Debate amplifies shared bias after the first round
(arXiv 2505.19477); the cross-vendor pairing (Claude + GLM share little training) mitigates this
but doesn't remove it — so stop early and flag if the two models start agreeing for agreement's
sake (convergence can be groupthink, not truth).

### Phase 5 — Synthesis
Deliver a verdict that is stronger than either opening position: what survived, what each side
**conceded**, the decisive evidence, and the open dissents. Make the recommendation explicit.

## Guards
- Advisory-only (informs, doesn't execute).
- Evidence gate (mechanism/file:line/source or discounted).
- Round cap 2–3 (bias amplification).
- Adjudication discipline (the second model's output is never accepted unverified).
- Flag model convergence as a possible artifact, not proof.
- **Cross-vendor check:** the value rests on a *different-vendor* second model (GLM by default). If the
  configured/chosen model is the **same vendor** as you (e.g. an `anthropic/*` model via OpenRouter),
  say so up front — the different-distribution benefit is largely lost and it degrades toward a
  self-adversarial pass. Prefer a non-Anthropic model for a real debate.
- If PAL is unavailable, run a **self-adversarial** pass (you argue the opposite side as hard as
  you can) and say explicitly that no second model was used.

## Output (present in this structure)
1. **Position** — your recommendation + reasoning + assumptions.
2. **Adversary's strongest points — adjudicated** — each tagged REAL/SMELL/FP/HALLUCINATION with
   the verification.
3. **Verdict** — the synthesis, what each side conceded, decisive evidence, open dissents.
4. **Footer** — `> Want another round, a different framing, or a normal request to act on this?`

Respond in the user's language.

## Optional — persist the deliberation
If the user wants a record, write the debate to `.claude/deliberations/<slug>.md` (position →
adjudicated points → verdict). Useful for auditability and for resuming a decision later.

## Provenance (design notes)
Loop structure adapts the evidence-gate / decision-framing / deliberation-persistence ideas from
`Alex-R-A/llm-argumentation-protocol` (skills-based cross-vendor debate). The claim-by-claim
adjudication is the project's own cross-model discipline (memory `feedback_cross_model_adjudication`).
Round-cap rationale: arXiv 2505.19477 (debate amplifies bias after round 1). Runs over the PAL MCP
(`mcp__pal__*`), the same second-model channel as the `interceptor` skill.
