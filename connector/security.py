"""Hardening primitives for the TGL connector (slice 5).

Input size caps, input shape checks, and the session-count cap live
here so the tool layer stays readable. Every rejection raises ToolError
with a human-readable message: the calling agent may show it to a user,
so each one says what to do instead of just saying no.
"""

from mcp.server.mcpserver.exceptions import ToolError

# Hard caps on tool input sizes. Documents (SPEC.md, PLAN.md) get a
# generous 200KB; short texts (descriptions, questions, answers, goals)
# get 20KB. Over-limit input is refused before validation runs, so a
# hostile client cannot make the server chew through megabytes.
MAX_DOC_CHARS = 200_000
MAX_TEXT_CHARS = 20_000

# The session-count cap lives in sessions.py (the store enforces its own
# bound); see sessions.MAX_SESSIONS.


def check_text(value, name, limit):
    """Reject missing, non-text, empty, or oversized tool input.

    Raises ToolError naming the problem and the fix. Returns the value
    unchanged when it passes.
    """
    if not isinstance(value, str):
        raise ToolError(
            "The '%s' argument must be text, but it arrived as %s. Pass a "
            "string and try again." % (name, type(value).__name__)
        )
    if not value.strip():
        raise ToolError(
            "The '%s' argument is empty. Say what you mean in plain words "
            "and try again." % name
        )
    if len(value) > limit:
        raise ToolError(
            "The '%s' argument is too large (%d characters; the limit is "
            "%d). Shorten it and try again."
            % (name, len(value), limit)
        )
    return value
