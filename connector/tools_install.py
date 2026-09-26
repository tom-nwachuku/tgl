"""Slice 4 tool implementation: the tgl_install skill bundle.

The bundle is baked into the connector at build time: connector/
skill-bundle/ holds a copy of the canonical skill tree (SKILL.md,
templates, installer script, README) plus a VERSION file. This module
reads that baked copy, so what the tool serves is exactly what was
reviewed at build time.

Drift protection: tests/test_install.py compares every bundle file byte
for byte against the live skill tree at ~/workspace/skills/tgl/. If the
skill evolves, re-copy the tree into skill-bundle/ and refresh VERSION.
"""

import os

from mcp.server.mcpserver.exceptions import ToolError

BUNDLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skill-bundle")

BUNDLE_FILES = [
    "SKILL.md",
    "README.md",
    "VERSION",
    "install/tgl-install.py",
    "templates/SPEC-template.md",
    "templates/PLAN-template.md",
    "templates/LEDGER-template.md",
    "templates/release-checklist.md",
]

INSTRUCTIONS = (
    "Two ways to install TGL. Conversational: save these files where your "
    "Muse agent can read them, point the agent at them, and say "
    '"install TGL". The agent walks you through setup and the first-run '
    "tutorial. TUI: save the files, then run "
    "python3 install/tgl-install.py and follow the prompts "
    "(press h on any step for help)."
)


def _read_bundle():
    files = {}
    for path in BUNDLE_FILES:
        with open(os.path.join(BUNDLE_DIR, path), encoding="utf-8") as fh:
            files[path] = fh.read()
    return files


def install():
    """Return the TGL skill bundle and install instructions.

    Takes no session: installing is the no-commitment path and works
    before any plan session exists. A missing bundle is a server-side
    problem, so it surfaces as a clean ToolError, never a raw traceback.
    """
    try:
        files = _read_bundle()
    except OSError as exc:
        raise ToolError(
            "The TGL install bundle is unavailable on this server. Try "
            "again in a minute; if it persists, the server needs its "
            "bundle restored (details: %s)." % exc
        )
    return {"files": files, "instructions": INSTRUCTIONS}
