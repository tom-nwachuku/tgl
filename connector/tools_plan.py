"""Slice 2 tool implementations: plan session tools + chain-of-command gates.

These are plain functions so they are easy to unit test. server.py
registers them as MCP tools. Errors are raised as exceptions with
human-readable messages: the calling agent may show them to users, so
each one says what to do instead of just saying no.
"""

import os

from mcp.server.mcpserver.exceptions import ToolError

from connector import security, sessions, validate

RECON_CHECKLIST = [
    "Read the project's memory and ledger before asking anything: MEMORY.md, "
    "a memory skill, the conversation context, or the project's own notes, "
    "plus LEDGER.md.",
    "Map the build as a design tree: every decision branches into the "
    "decisions that hang off it.",
    "Work the frontier: ask only the questions you can ask now without "
    "guessing at answers you have not heard yet. Recompute the frontier "
    "after each answer.",
    "One question at a time. Every bounded decision gets a tappable "
    "multiple-choice selector, always including your recommendation. "
    "Never dump a batch of questions as a text block.",
    "Finding facts is your job, never the human's: look it up yourself "
    "in files, tools, or connected services, or dispatch a lookup.",
    "Grill relentlessly until the frontier is empty and nothing is left "
    "silently assumed. Then write the agreed goal and record it with "
    "tgl_plan_goal. Do not generate SPEC.md or PLAN.md before the goal "
    "is recorded.",
]


def _unknown_session_error(session_id):
    return ("No active plan session found. It may have expired or been deleted. "
            "Start a new session with tgl_plan_start. Keep its private session id; "
            "a document read token cannot modify a session.")


def _check_id(session_id):
    security.check_text(session_id, "session_id", 128)


def plan_start(project_description):
    """Start a TGL Plan Mode session and return its id plus the recon checklist."""
    security.check_text(
        project_description, "project_description", security.MAX_TEXT_CHARS
    )
    session_id = sessions.create(project_description)
    return {"session_id": session_id, "recon_checklist": list(RECON_CHECKLIST),
            "notice": "Keep session_id private: it permits edits and deletion. Document links are separately shareable, read-only bearer links. Save files locally; sessions expire after 24 hours without a successful write and may end earlier on restart or capacity eviction. Use tgl_plan_delete when finished."}


def plan_log(session_id, question, answer):
    """Append one grill Q&A exchange to the session."""
    _check_id(session_id)
    security.check_text(question, "question", security.MAX_TEXT_CHARS)
    security.check_text(answer, "answer", security.MAX_TEXT_CHARS)
    result = sessions.log_qa(session_id, question, answer)
    if result is None:
        raise ToolError(_unknown_session_error(session_id))
    qa_count, _phase = result
    return {"ok": True, "qa_count": qa_count}


def plan_goal(session_id, goal):
    """Record the agreed written goal, closing Discuss. Refuses if the grill was skipped."""
    _check_id(session_id)
    security.check_text(goal, "goal", security.MAX_TEXT_CHARS)
    outcome = sessions.set_goal(session_id, goal)
    if outcome == "unknown":
        raise ToolError(_unknown_session_error(session_id))
    if outcome == "no_qa":
        raise ToolError(
            "Cannot record the goal yet: no grill questions have been answered "
            "in this session. TGL requires the grilling round first, one question "
            "at a time, until the frontier is empty. Log each exchange with "
            "tgl_plan_log, then call tgl_plan_goal with the agreed goal."
        )
    result = {"ok": True, "overwritten": outcome == "overwritten"}
    if outcome == "overwritten":
        result["note"] = (
            "Goal updated. The previous goal was replaced, not kept alongside it."
        )
    return result


def _doc_url(session_id, kind):
    base = os.environ.get("TGL_PUBLIC_BASE_URL", "https://tgl-summitx.fly.dev").rstrip("/")
    return "%s/docs/%s/%s" % (base, sessions.get(session_id)["read_token"], kind)


def plan_spec(session_id, spec_markdown):
    """Validate and store the SPEC.md. Refuses unless Discuss is closed
    (phase GOAL_SET): no spec before the grill is done and the goal recorded."""
    _check_id(session_id)
    security.check_text(spec_markdown, "spec_markdown", security.MAX_DOC_CHARS)
    session = sessions.get(session_id)
    if session is None:
        raise ToolError(_unknown_session_error(session_id))
    if session["phase"] != "GOAL_SET":
        raise ToolError(
            "Cannot accept the spec yet: the Discuss phase is still open for "
            "this session. TGL requires the grill first, one question at a "
            "time, until the frontier is empty, then the agreed goal. Log "
            "each exchange with tgl_plan_log, record the goal with "
            "tgl_plan_goal, and then resubmit the spec with tgl_plan_spec."
        )
    problems = validate.validate_spec(spec_markdown)
    if problems:
        raise ToolError(
            "The spec was not accepted:\n- " + "\n- ".join(problems)
            + "\nFix the items above and resubmit with tgl_plan_spec."
        )
    sessions.store_doc(session_id, "spec", spec_markdown)
    return {"ok": True, "url": _doc_url(session_id, "spec")}


def plan_plan(session_id, plan_markdown):
    """Validate and store the PLAN.md. Refuses unless a validated spec
    already exists for the session: plan follows spec, never precedes it."""
    _check_id(session_id)
    security.check_text(plan_markdown, "plan_markdown", security.MAX_DOC_CHARS)
    session = sessions.get(session_id)
    if session is None:
        raise ToolError(_unknown_session_error(session_id))
    if not session.get("spec"):
        raise ToolError(
            "Cannot accept the plan yet: no validated spec exists for this "
            "session. TGL plans from a structurally validated spec, so draft SPEC.md first, "
            "submit it with tgl_plan_spec, and then resubmit the plan with "
            "tgl_plan_plan."
        )
    problems = validate.validate_plan(plan_markdown)
    if problems:
        raise ToolError(
            "The plan was not accepted:\n- " + "\n- ".join(problems)
            + "\nFix the items above and resubmit with tgl_plan_plan."
        )
    sessions.store_doc(session_id, "plan", plan_markdown)
    return {"ok": True, "url": _doc_url(session_id, "plan")}


def plan_delete(session_id):
    """User-requested deletion; an absent session is already inaccessible."""
    _check_id(session_id)
    sessions.delete(session_id)
    return {"ok": True, "note": "The session and its hosted documents are inaccessible. Copies already saved or retained by Muse are separate."}
