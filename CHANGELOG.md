# Changelog

All notable changes to this project are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions are the `version` field of
`plugins/cross-model-toolkit/.claude-plugin/plugin.json`. Dates from git history.

## [1.3.0] — 2026-09-02

### Changed
- **Renamed the project `claude-glm-toolkit` → `cross-model-toolkit`.** The old name misdescribed
  the toolkit twice: it is not GLM-only (any OpenRouter model works per call) and not Claude-only
  (the same engine runs under Kimi Code CLI). Plugin directory, manifest, marketplace entry, docs
  and `glm_collab.html` → `cross_model_collab.html` renamed accordingly. The GitHub repo rename
  redirects the old URL.

### Added
- `openai/gpt-5.6-sol-pro` to the curated registry overlay: 1.05M context, 128K output, multimodal,
  configurable reasoning (verified against OpenRouter `/api/v1/models` on 2026-08-09). Now **6
  models** flagged `supports_extended_thinking`.
- `docs/kimi-code-variant.md` — how to run the same engine under Kimi Code CLI (bootstrapper
  script, key from `.env`, user-scope skills), including the maintenance rule for keeping both
  setups in sync.
- CI workflow (`.github/workflows/ci.yml`): validates all JSON manifests and runs
  `build_registry.py --check` so a stale generated registry fails the build.
- `build_registry.py --diff PATH` — sync check that compares a fresh build's `models` array against
  an external registry copy (e.g. the Kimi Code variant's), with field-level drift reporting.
- Fork-side smoke tests (`pal-mcp-server@0081c16`, branch `openrouter-reasoning`): 6 mocked unit
  tests for the reasoning patch in the default suite plus a live test runnable via the manual
  `smoke-openrouter-reasoning` workflow. Finding from that work, now fixed: `tencent/hy3:free` left the
  OpenRouter free tier (404 as of 2026-09-02) — the overlay entry was updated to the paid slug
  `tencent/hy3` (262K ctx, 128K output, $0.132/M in, $0.528/M out, re-verified against
  `/api/v1/models` on 2026-09-02).

## [1.2.7] — 2026-07-29

### Added
- Graph-grounding section in the shared references for graphify-mapped codebases.

## [1.2.6] — 2026-07-29

### Changed
- The OpenRouter registry is now a **generated artifact**: `scripts/build_registry.py` builds
  `config/pal_openrouter_models.json` from the upstream bundled registry (at the PAL SHA pinned in
  `.mcp.json`) plus the hand-maintained `config/pal_registry_overlay.json`. `--check` mode for CI.

## [1.2.5] — 2026-07-29

### Changed
- Shared PAL call conventions extracted from the skills into `references/`; documented
  `challenge`/`consensus` usage.

## [1.2.4] — 2026-07-29

### Fixed
- Re-pinned the PAL fork to `e4ffd36` — pins `mcp<2.0.0` (SDK 2.0 removed the low-level
  `Server.list_tools` decorator and broke the server).

## [1.2.0] — 2026-07-11

### Added
- `tencent/hy3:free` (262K, free tier, reasoning) to the registry — later same-day flag fix
  (`json_mode` / `function_calling` had been mis-set from a truncated `supported_parameters`).
- `minimax/minimax-m3` (1M, multimodal, reasoning) — 2026-07-11.
- `moonshotai/kimi-k3` (1M, reasoning-mandatory) — 2026-07-17.
- `deepseek/deepseek-v4-pro` (1M, reasoning) — 2026-07-10; fork re-pinned to include
  `include_reasoning`.

## [1.0.0] — 2026-06-25

### Added
- Initial release: native Claude Code plugin bundling the PAL MCP server (any OpenRouter model,
  GLM-5.2 by default) + `/interceptor` (idea→prompt) + `/debate` (adversarial chamber), with
  keychain-backed `openrouter_api_key` and the claim-by-claim adjudication discipline.
- 2026-06-29: made model-agnostic (`DEFAULT_MODEL=auto`, no allowlist), generic English landing
  page, MIT license + CREDITS for public sharing.
- 2026-06-30: **GLM-5.2 at its full 1M context, wired by default** via the superset registry
  (`OPENROUTER_MODELS_CONFIG_PATH`) — PAL no longer falls back to its generic 32K window.
- 2026-06-30: **OpenRouter reasoning** via a minimal SHA-pinned PAL fork mapping `thinking_mode`
  onto OpenRouter's `reasoning` field (xhigh by default for GLM).
