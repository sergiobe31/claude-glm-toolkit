#!/usr/bin/env python3
"""Build config/pal_openrouter_models.json (stdlib only).

Generated artifact = upstream PAL OpenRouter registry + this plugin's curated overlay:

- Base: conf/openrouter_models.json of sergiobe31/pal-mcp-server, fetched at the SHA pinned in
  .mcp.json (so the registry can never drift from the server the plugin actually runs).
- Overlay: config/pal_registry_overlay.json — the only file edited by hand. Its "models" entries
  are appended to (or replace, by model_name) the base; its "overrides" are field-level patches
  applied to base entries by model_name.

Usage:
  python3 scripts/build_registry.py          # regenerate and write the registry
  python3 scripts/build_registry.py --check  # exit 1 if the committed file differs (CI)
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
MCP_JSON = PLUGIN_ROOT / ".mcp.json"
OVERLAY_JSON = PLUGIN_ROOT / "config" / "pal_registry_overlay.json"
OUT_JSON = PLUGIN_ROOT / "config" / "pal_openrouter_models.json"
RAW_URL = "https://raw.githubusercontent.com/sergiobe31/pal-mcp-server/{sha}/conf/openrouter_models.json"


def read_pinned_sha():
    args = json.loads(MCP_JSON.read_text())["mcpServers"]["pal"]["args"]
    for arg in args:
        m = re.search(r"pal-mcp-server\.git@([0-9a-f]{40})", arg)
        if m:
            return m.group(1)
    sys.exit("error: no pinned pal-mcp-server SHA found in .mcp.json")


def build():
    sha = read_pinned_sha()
    with urllib.request.urlopen(RAW_URL.format(sha=sha), timeout=30) as r:
        base = json.loads(r.read().decode("utf-8"))
    overlay = json.loads(OVERLAY_JSON.read_text())

    models = base["models"]
    by_name = {m["model_name"]: m for m in models}
    for name, patch in overlay.get("overrides", {}).items():
        if name not in by_name:
            sys.exit(f"error: overlay override targets unknown base model {name!r}")
        by_name[name].update(patch)
    for entry in overlay["models"]:
        name = entry["model_name"]
        if name in by_name:  # replace in place, keep position
            models[[m["model_name"] for m in models].index(name)] = entry
        else:
            models.append(entry)

    flagged = sorted(m["model_name"] for m in models if m.get("supports_extended_thinking"))
    overridden = sorted(overlay.get("overrides", {}))
    out = {
        "_README": {
            "purpose": "SUPERSET OpenRouter registry wired by default via OPENROUTER_MODELS_CONFIG_PATH in .mcp.json. PAL loads exactly ONE registry file and REPLACES its bundled one (providers/registries/base.py:42-44), so this file must contain BOTH PAL's bundled models AND our curated entries — otherwise the other models would lose their correct context windows.",
            "generated_by": "GENERATED FILE — do not edit by hand. Built by scripts/build_registry.py; edit config/pal_registry_overlay.json instead and re-run the script.",
            "provenance": f"Base = conf/openrouter_models.json of sergiobe31/pal-mcp-server @ {sha} (the SHA pinned in .mcp.json, branch openrouter-reasoning), fetched at build time. Overlay = config/pal_registry_overlay.json: {len(overlay['models'])} curated model entries + field overrides on {len(overridden)} base models.",
            "why_glm": "The plugin's headline feature is GLM-5.2 at its full 1,048,576-token window. Without this file GLM falls back to PAL's generic ~32K (providers/openrouter.py:_lookup_capabilities), capping per-call file budget to ~3.5K tokens. With 1M declared here, per-call file budget becomes ~268K (window x0.8 content x0.4 files x0.8 guard; utils/model_context.py + utils/file_utils.py:843-850).",
            "reasoning_policy": f"{len(flagged)} models have supports_extended_thinking:true — {', '.join(flagged)} — so by default those {len(flagged)} get OpenRouter reasoning (the fork maps PAL thinking_mode -> reasoning effort; max -> xhigh). The overlay also forces supports_extended_thinking:false on {len(overridden)} base models that upstream ships with the flag true (upstream default; our fork's reasoning for those models is unverified), keeping the shipped reasoning default limited to the verified entries. Flip flags in the overlay, not here.",
            "resync_instructions": "After bumping the PAL SHA in .mcp.json or editing config/pal_registry_overlay.json, run: python3 scripts/build_registry.py. Use --check in CI to fail if the committed registry differs from a fresh build.",
            "glm_entry_verified": "z-ai/glm-5.2 confirmed on OpenRouter /api/v1/models: single slug, context_length 1,048,576, no separate [1m] variant. Verified 2026-06-30.",
            "base_model_count": len(base["models"]),
            "overlay_model_count": len(overlay["models"]),
            "overlay_override_count": len(overridden),
        },
        "models": models,
    }
    text = json.dumps(out, indent=2, ensure_ascii=False) + "\n"
    json.loads(text)  # validate before touching disk
    return text


def main():
    text = build()
    if "--check" in sys.argv[1:]:
        current = OUT_JSON.read_text() if OUT_JSON.exists() else ""
        if current == text:
            print(f"OK: {OUT_JSON.name} is up to date")
            return
        print(f"FAIL: {OUT_JSON.name} differs from a fresh build — run scripts/build_registry.py")
        sys.exit(1)
    OUT_JSON.write_text(text)
    print(f"wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
