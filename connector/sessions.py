"""Ephemeral, bounded planning state. Async tool wrappers serialize operations.

The write capability is never present in document URLs. Read tokens cannot
be used as session ids. All state disappears on restart; run one process.
"""
import secrets
import time
from mcp.server.mcpserver.exceptions import ToolError

SESSION_TTL_SECONDS = 24 * 60 * 60
MAX_SESSIONS = 1_000
MAX_QA = 200
MAX_SESSION_CHARS = 1_000_000
MAX_TOTAL_CHARS = 16_000_000
_now = time.monotonic
_store = {}
_readers = {}


def _size(session):
    return sum(len(session.get(k) or '') for k in ('project_description', 'goal', 'spec', 'plan')) + sum(len(q['question']) + len(q['answer']) for q in session['qa'])


def delete(session_id):
    session = _store.pop(session_id, None)
    if session:
        _readers.pop(session['read_token'], None)
    return session is not None


def purge_expired():
    now = _now()
    for sid, session in list(_store.items()):
        if now - session['last_active_at'] >= SESSION_TTL_SECONDS:
            delete(sid)


def _check_capacity(session, delta):
    purge_expired()
    if _size(session) + delta > MAX_SESSION_CHARS:
        raise ToolError('This session has reached its storage limit. Save your documents and start a new session.')
    if sum(_size(s) for s in _store.values()) + delta > MAX_TOTAL_CHARS:
        raise ToolError('The service is at its storage limit. Save your work and retry later or use the installed skill locally.')


def create(project_description):
    purge_expired()
    while len(_store) >= MAX_SESSIONS:
        delete(min(_store, key=lambda sid: _store[sid]['last_active_at']))
    session = {
        'session_id': secrets.token_urlsafe(32),
        'read_token': secrets.token_urlsafe(32),
        'project_description': project_description,
        'created_at': _now(), 'last_active_at': _now(),
        'phase': 'OPEN', 'goal': None, 'qa': [], 'spec': None,
        'spec_stored_at': None, 'plan': None, 'plan_stored_at': None,
    }
    _check_capacity(session, 0)
    # The new session is not yet in _store.
    if sum(_size(s) for s in _store.values()) + _size(session) > MAX_TOTAL_CHARS:
        raise ToolError('The service is at its storage limit. Retry later or use the installed skill locally.')
    sid = session['session_id']
    _store[sid] = session
    _readers[session['read_token']] = sid
    return sid


def get(session_id):
    session = _store.get(session_id)
    if session and _now() - session['last_active_at'] >= SESSION_TTL_SECONDS:
        delete(session_id)
        return None
    return session


def get_document(read_token, kind):
    session = get(_readers.get(read_token))
    return session.get(kind) if session else None


def touch(session_id):
    session = get(session_id)
    if not session:
        return False
    session['last_active_at'] = _now()
    return True


def clear():
    _store.clear()
    _readers.clear()


def _invalidate(session, *kinds):
    for kind in kinds:
        session[kind] = None
        session[kind + '_stored_at'] = None


def log_qa(session_id, question, answer):
    session = get(session_id)
    if not session:
        return None
    item = {'question': question, 'answer': answer}
    # An immediate transport retry must not duplicate the last exchange.
    if session['qa'] and session['qa'][-1] == item:
        touch(session_id)
        return len(session['qa']), session['phase']
    if len(session['qa']) >= MAX_QA:
        raise ToolError('This session has 200 question-and-answer exchanges. Save your work and start a new session.')
    _check_capacity(session, len(question) + len(answer))
    session['qa'].append(item)
    session['goal'] = None
    _invalidate(session, 'spec', 'plan')
    session['phase'] = 'DISCUSSING'
    touch(session_id)
    return len(session['qa']), session['phase']


def set_goal(session_id, goal):
    session = get(session_id)
    if not session:
        return 'unknown'
    if not session['qa']:
        return 'no_qa'
    overwritten = session['goal'] is not None
    _check_capacity(session, len(goal) - len(session['goal'] or ''))
    if session['goal'] != goal:
        _invalidate(session, 'spec', 'plan')
    session['goal'] = goal
    session['phase'] = 'GOAL_SET'
    touch(session_id)
    return 'overwritten' if overwritten else 'ok'


def store_doc(session_id, kind, markdown):
    if kind not in ('spec', 'plan'):
        raise ValueError('kind must be spec or plan')
    session = get(session_id)
    if not session:
        return False
    _check_capacity(session, len(markdown) - len(session[kind] or ''))
    if kind == 'spec' and session['spec'] != markdown:
        _invalidate(session, 'plan')
    session[kind] = markdown
    session[kind + '_stored_at'] = time.time()
    touch(session_id)
    return True
