# Adjudication Protocol

The shared discipline for working with the second model (via the PAL MCP). Its output is a
**proposal, never truth**, until verified. Any skill — or any ad-hoc second-model call — that
consumes the second model's output applies this protocol at its verification step.

## The rule — never pass the second model's output through unverified

Check every claim against ground truth (`file:line` / source / trace / the real project) and tag it:

- **REAL** — verified true → fold it in.
- **SMELL** — plausible but not yet checked → name the exact check it needs before relying on it.
- **FALSE-POSITIVE** — checked and wrong → drop it, and say why.
- **HALLUCINATION** — invented file / fact / line → drop it, and count it in the tally.

## Principles

- **Verification cuts both ways.** It rescues a real point you'd have dismissed *and* kills a
  plausible-but-wrong one. Verify line numbers and claims yourself — don't take them on assertion.
- **Report the tally honestly**, hallucinations included. The count is part of the deliverable.
- **You gather ground truth; the second model only reasons over what you hand it.** Establishing the
  facts is your job, not its. It has no file/web access of its own.

## How each skill applies it

The protocol is the same; the material differs.

- **`/debate`** applies it to the adversary's points (Phase 3).
- **`/interceptor`** applies it to the drafted / red-teamed prompt (Phase 5).

A new skill that consumes second-model output should reference this file rather than restate the
protocol — keep one source of truth.
