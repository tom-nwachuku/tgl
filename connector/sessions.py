"""Plan session store for the TGL connector (slices 1 and 5).

In-memory only. No user data persists beyond the session: every session
expires after 24 hours of inactivity, and expired sessions read as
missing. The store holds the Q&A history so a plan session survives
across turns and agents. The store is capped at MAX_SESSIONS: past the
cap, creation evicts the oldest idle sessions first, so memory stays
bounded. All operations are synchronous with no awaits between
check-and-act, so the store is safe on uvicorn's single event loop.
"""

import time
import uuid

SESSION_TTL_SECONDS = 24 * 60 * 60

# Cap on concurrent sessions. Past this, creation evicts the oldest idle
# sessions first. Importable here (not only in security.py) so the store
# enforces its own bound and tests can monkeypatch it.
MAX_SESSIONS = 10_000

_now = time.monotonic

_store = {}


def _expired(session, now):
    return now - session["last_active_at"] > SESSION_TTL_SECONDS


def _purge_expired(now):
    for session_id in [sid for sid, s in _store.items() if _expired(s, now)]:
        del _store[session_id]


def _enforce_cap():
    """Evict the oldest idle sessions past MAX_SESSIONS.

    Keeps the in-memory store bounded no matter how fast sessions are
    created. Eviction is by last activity, so the sessions a user is
    actively grilling in are the last to go.
    """
    overflow = len(_store) - MAX_SESSIONS + 1
    if overflow <= 0:
        return
    oldest_first = sorted(_store.items(), key=lambda kv: kv[1]["last_active_at"])
    for session_id, _session in oldest_first[:overflow]:
        del _store[session_id]


def create(project_description):
    """Create a plan session. Returns the new session_id (a UUID).

    Expired sessions are purged first; past MAX_SESSIONS the oldest idle
    sessions are evicted, so the store never grows without bound.
    """
    now = _now()
    _purge_expired(now)
    _enforce_cap()
    session_id = uuid.uuid4().hex
    _store[session_id] = {
        "session_id": session_id,
        "project_description": project_description,
        "created_at": now,
        "last_active_at": now,
        "phase": "OPEN",
        "goal": None,
        "qa": [],
        "spec": None,
        "spec_stored_at": None,
        "plan": None,
        "plan_stored_at": None,
    }
    return session_id


def get(session_id):
    """Return the session dict, or None if unknown or expired."""
    now = _now()
    session = _store.get(session_id)
    if session is None:
        return None
    if _expired(session, now):
        del _store[session_id]
        return None
    return session


def touch(session_id):
    """Mark a session as active (resets the inactivity clock).

    Returns True if the session exists and is not expired, else False.
    """
    session = get(session_id)
    if session is None:
        return False
    session["last_active_at"] = _now()
    return True


def clear():
    """Empty the store. Used by tests."""
    _store.clear()


def log_qa(session_id, question, answer):
    """Append one grill Q&A exchange to the session.

    Returns (qa_count, phase), or None if the session is unknown/expired.
    The first logged exchange moves the session from OPEN to DISCUSSING.
    """
    session = get(session_id)
    if session is None:
        return None
    session["qa"].append({"question": question, "answer": answer})
    if session["phase"] == "OPEN":
        session["phase"] = "DISCUSSING"
    session["last_active_at"] = _now()
    return len(session["qa"]), session["phase"]


def set_goal(session_id, goal):
    """Record the agreed written goal on the session.

    Returns one of "ok", "overwritten", "no_qa", "unknown":
    - "ok": goal recorded, Discuss is now closed (phase GOAL_SET)
    - "overwritten": a goal already existed; it was replaced, never duplicated
    - "no_qa": refused, zero Q&A exchanges logged (the grill gate)
    - "unknown": refused, session unknown or expired
    """
    session = get(session_id)
    if session is None:
        return "unknown"
    if not session["qa"]:
        return "no_qa"
    overwritten = session["goal"] is not None
    session["goal"] = goal
    session["phase"] = "GOAL_SET"
    session["last_active_at"] = _now()
    return "overwritten" if overwritten else "ok"


def store_doc(session_id, kind, markdown):
    """Store a validated doc ("spec" or "plan") on the session.

    Records a wall-clock stored_at timestamp and refreshes the inactivity
    clock. Resubmission overwrites the previous doc. Returns True on
    success, False if the session is unknown or expired.
    """
    if kind not in ("spec", "plan"):
        raise ValueError("kind must be 'spec' or 'plan'")
    session = get(session_id)
    if session is None:
        return False
    session[kind] = markdown
    session[kind + "_stored_at"] = time.time()
    session["last_active_at"] = _now()
    return True
