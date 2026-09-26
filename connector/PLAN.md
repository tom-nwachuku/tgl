# TGL Connector (v1.1) — PLAN.md

Status: APPROVED by Tom 2026-09-25. Attack Mode launched same day.
Spec: SPEC.md in this directory.

Slices are small enough to verify in one pass. One subagent per slice,
fresh context, commanding-agent review before the next begins.

## Slice 1: MCP server scaffold + session store

- Files: `connector/server.py`, `connector/sessions.py`,
  `connector/tests/test_sessions.py`
- Interfaces: MCP server (Python `mcp` SDK) exposing a `/mcp` endpoint;
  `sessions.create(project_description) -> session_id`;
  `sessions.get(session_id)`; TTL 24h, expired sessions purged.
- Tests: create returns an id; get round-trips; expired session reads as
  missing; concurrent sessions isolated.
- Commands: `python -m pytest connector/tests/test_sessions.py`
- Expected output: all tests pass; server boots locally and answers MCP
  handshake.
- Review Focus: a real user would hammer start twice and expect two
  separate sessions, then come back tomorrow and expect yesterday's to be
  gone. Also: what happens when the project description is 50,000
  characters of pasted logs?

## Slice 2: Plan session tools + chain-of-command gates

- Files: `connector/tools_plan.py`, `connector/tests/test_gates.py`
- Interfaces: `tgl_plan_start`, `tgl_plan_log`, `tgl_plan_goal` as MCP
  tools; gate state machine per session: OPEN -> DISCUSSING -> GOAL_SET.
  `tgl_plan_goal` refuses when no Q&A logged; tools after GOAL_SET keep
  working (spec phase is slice 3).
- Tests: goal with zero logged Q&A is refused with a human-readable error;
  log-then-goal succeeds; double goal overwrites with warning, never
  duplicates.
- Commands: `python -m pytest connector/tests/test_gates.py`
- Expected output: all tests pass; refusal messages read clearly when
  surfaced in chat.
- Review Focus: a real user would try to skip the grilling ("just write
  the spec"). The gate must hold, and the refusal must tell them what to
  do instead of just saying no.

## Slice 3: Spec and plan validation + storage

- Files: `connector/validate.py`, `connector/store.py`,
  `connector/tests/test_validate.py`
- Interfaces: `tgl_plan_spec(session_id, spec_markdown) -> url`;
  `tgl_plan_plan(session_id, plan_markdown) -> url`. Validators: spec has
  what/why sections and no fenced code blocks; plan has numbered slices,
  each naming files, interfaces, tests, commands, expected output, and a
  Review Focus. `tgl_plan_spec` refuses unless GOAL_SET;
  `tgl_plan_plan` refuses unless a validated spec exists.
- Tests: valid docs accepted and retrievable by URL; spec with code
  blocks rejected; plan with a sliceless blob rejected; wrong-order calls
  refused.
- Commands: `python -m pytest connector/tests/test_validate.py`
- Expected output: all tests pass; stored docs render as clean markdown
  at their URLs.
- Review Focus: a real user would paste a 200-line "spec" that is really
  a feature wishlist, and a "plan" that is one paragraph. Validation must
  catch both without being so strict that a good spec fails.

## Slice 4: Skill bundle tool

- Files: `connector/tools_install.py`,
  `connector/tests/test_install.py`
- Interfaces: `tgl_install() -> {files, instructions}`. Bundle built
  from the published repo at the v1 tag: SKILL.md, templates, installer
  script. Byte-checked against the tag at build time.
- Tests: bundle file list matches the v1 tag tree; SKILL.md frontmatter
  intact; instructions mention both install paths (conversational and TUI).
- Commands: `python -m pytest connector/tests/test_install.py`
- Expected output: all tests pass; installing from the bundle yields a
  working skill.
- Review Focus: a real user would install mid-grill and expect the local
  skill and the connector session to agree. Also: the bundle must never
  drift from the published tag.

## Slice 5: Hardening + red team

- Files: `connector/security.py`, `connector/tests/test_security.py`,
  red-team record in LEDGER.md
- Interfaces: input size caps, per-caller rate limits, prompt-injection
  test corpus (tool input attempting instruction override).
- Tests: oversized input rejected; injection attempts treated as data;
  rate limit trips and recovers; error messages leak no internals.
- Commands: `python -m pytest connector/tests/`
- Expected output: full suite green, including slices 1-4.
- Review Focus: the red-team agent plays adversary against the running
  server: gate bypass attempts, session confusion between two users,
  malicious markdown in spec submissions. Record what broke.

## Slice 6: Deploy + submission materials

**Requires Tom's explicit approval:** DNS for tgl.summitxdigital.com and
the deploy itself.

- Files: `connector/Dockerfile` (or platform config), deploy runbook,
  `assets/tgl-icon-512.png`, SummitX privacy page, SummitX terms page,
  docs page for the MCP endpoint.
- Interfaces: `https://tgl.summitxdigital.com/mcp` live; docs URL live.
- Tests: end-to-end MCP call against production; install bundle served
  from production matches the tag; privacy/terms pages load.
- Commands: deploy per runbook; `curl` health checks.
- Expected output: live endpoint, green checks, materials staged.
- Review Focus: a real reviewer at Meta will hit the endpoint cold. It
  must answer fast, fail clearly, and need no account.

## Slice 7: Submit to the directory

**Requires Tom's explicit approval:** the actual form submission.

- Action: complete the three-step form at https://muse.ai/platform
  (Overview, Technical specs, Review) with the staged materials; agree to
  the Muse Connector Terms; submit.
- Expected output: submission confirmed, in the review queue.
- Review Focus: none, this is the ship step. Log the after-action entry.

## Sign-off record

- [x] Tom approved SPEC.md (v1.1) — 2026-09-25 ("Attack mode")
- [x] Tom approved PLAN.md (v1.1) — 2026-09-25 ("Attack mode")
- [ ] Date: 2026-09-25
