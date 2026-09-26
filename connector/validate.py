"""Pure validation functions for SPEC.md and PLAN.md (slice 3).

No I/O, no session state, no dependencies beyond the standard library.
Each validator returns a list of human-readable problem strings; an
empty list means the document is valid. The tool layer turns problems
into ToolError messages. Rules are structural, not strict: a good spec
or plan must pass, so the checks look for shape (headings, slices,
review focus, length), never for specific content.
"""

import re

MIN_DOC_CHARS = 200
MIN_PLAN_SLICES = 2

_WHAT_HEADING = re.compile(r"^#{1,6}\s+.*\bwhat\b", re.IGNORECASE | re.MULTILINE)
_WHY_HEADING = re.compile(r"^#{1,6}\s+.*\bwhy\b", re.IGNORECASE | re.MULTILINE)
_SLICE_LINE = re.compile(
    r"^\s*(#{1,6}\s+)?(slice\s+\d+|\d+[.)])", re.IGNORECASE | re.MULTILINE
)
_REVIEW_FOCUS = re.compile(r"review focus", re.IGNORECASE)

# Every slice must name these fields (substring match, case-insensitive).
# "expected output" and "review focus" are matched as phrases; the rest as
# stems so "Files:" and "files" both hit.
_SLICE_FIELDS = (
    ("files", re.compile(r"file", re.IGNORECASE)),
    ("interfaces", re.compile(r"interface", re.IGNORECASE)),
    ("tests", re.compile(r"test", re.IGNORECASE)),
    ("commands", re.compile(r"command", re.IGNORECASE)),
    ("expected output", re.compile(r"expected output", re.IGNORECASE)),
    ("Review Focus", re.compile(r"review focus", re.IGNORECASE)),
)


def validate_spec(markdown):
    """Check the shape of a SPEC.md. Returns a list of problems (empty = valid)."""
    text = markdown or ""
    problems = []
    if len(text.strip()) < MIN_DOC_CHARS:
        problems.append(
            "The spec is too short (%d characters, at least %d needed). "
            "A real spec says what the thing is and why it exists, which "
            "takes more than a tweet. Flesh it out and resubmit." % (
                len(text.strip()), MIN_DOC_CHARS)
        )
    if not _WHAT_HEADING.search(text):
        problems.append(
            'No "what" section found. Add a heading like "## What it is" '
            "that says what you are building."
        )
    if not _WHY_HEADING.search(text):
        problems.append(
            'No "why" section found. Add a heading like "## Why" '
            "that says why this build matters."
        )
    if "```" in text:
        problems.append(
            "Fenced code blocks (```) are not allowed in the spec. Plan "
            "Mode is what and why, no code: describe the behavior in words. "
            "The code comes in Attack Mode."
        )
    return problems


def count_slices(markdown):
    """Count numbered slice lines in a PLAN.md."""
    return len(_SLICE_LINE.findall(markdown or ""))


def count_review_focus(markdown):
    """Count case-insensitive 'review focus' mentions in a PLAN.md."""
    return len(_REVIEW_FOCUS.findall(markdown or ""))


def _slice_sections(markdown):
    """Split a PLAN.md into (slice_number, section_text) at slice lines."""
    matches = list(_SLICE_LINE.finditer(markdown or ""))
    sections = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
        num = re.search(r"\d+", match.group(0))
        sections.append((num.group(0) if num else str(i + 1), markdown[start:end]))
    return sections


def _missing_slice_fields(section_text):
    """Return the names of required fields absent from one slice section."""
    return [
        name for name, pattern in _SLICE_FIELDS if not pattern.search(section_text)
    ]


def validate_plan(markdown):
    """Check the shape of a PLAN.md. Returns a list of problems (empty = valid)."""
    text = markdown or ""
    problems = []
    if len(text.strip()) < MIN_DOC_CHARS:
        problems.append(
            "The plan is too short (%d characters, at least %d needed). "
            "A real plan names its slices with files, tests, and commands, "
            "which takes more than a paragraph. Flesh it out and resubmit." % (
                len(text.strip()), MIN_DOC_CHARS)
        )
    slices = count_slices(text)
    if slices < MIN_PLAN_SLICES:
        problems.append(
            "Found %d numbered slice(s); a plan needs at least %d. Put each "
            "slice on its own line, like '## Slice 1: name' or '1. name', "
            "and resubmit." % (slices, MIN_PLAN_SLICES)
        )
    else:
        for num, section in _slice_sections(text):
            missing = _missing_slice_fields(section)
            if missing:
                problems.append(
                    "Slice %s does not name its %s. Every slice must name "
                    "its files, interfaces, tests, commands, expected "
                    "output, and Review Focus. Add the missing %s and "
                    "resubmit." % (num, ", ".join(missing), ", ".join(missing))
                )
    return problems
