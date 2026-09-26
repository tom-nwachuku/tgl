# TGL Connector (v1.1) — SPEC.md

*Plan Mode measures twice. Attack Mode cuts once.*

Status: original goal approved September 25. September 26 readiness corrections are implemented in this branch; deployment and submission are separate gates. API.md is the current implemented contract.

## Written goal (agreed)

TGL becomes a listed Meta connector: a free, no-auth MCP server at
tgl.summitxdigital.com exposing Plan Mode workflow tools plus a
skill-install path, letting any Muse user run disciplined plan-then-execute
development one-shot or installed.

## What it is

A Meta connector (MCP server) that makes TGL usable inside Muse without
installing anything, plus a conversational install path for users who want TGL
persistently. The submission unit the platform reviews: a hosted service
Muse can call, not the skill files.

## The problem it solves

TGL v1 ships as a skill: clone the repo or point your agent at it. That is
friction for a developer who just wants to try disciplined planning once.
The connector removes it: ask Muse to create a custom integration with the hosted endpoint, then plan
the project. A native directory listing requires Meta approval. Love it, and one prompt installs the skill for ongoing use.

## The two runtime paths (Tom's design, 2026-09-25)

When a user invokes TGL through the connector, Muse offers the choice:

- **One-shot:** run Plan Mode right here via the connector's tools. No
  install, no commitment. Easy first touch.
- **Install:** fetch the skill bundle and install TGL into the user's Muse
  for ongoing use.

This is a runtime choice presented to the user, not a build-time either/or.
The connector exposes both capabilities.

## What the connector does (v1 scope: Plan Mode only)

The skill remains the intelligence (grilling discipline, spec shape, plan
shape, templates). The connector provides what a skill alone cannot:

- **Session state:** plan sessions with Q&A history that survive across
  turns and agents.
- **Chain of command as a service:** the server refuses spec generation
  before Discuss completes, and plan generation before a spec exists. Real
  gates, enforced server-side, not vibes.
- **Document validation and storage:** SPEC.md and PLAN.md checked against
  required structure, stored, returned as shareable URLs.
- **Skill delivery:** the canonical skill bundle (SKILL.md, templates,
  installer) served from the build-time bundle with a verified SHA-256 file manifest.

Out of scope for v1: Attack Mode tools (server-side execution agents are a
harder security review), red-team-as-a-service, user accounts, persisted
projects across sessions.

## MCP tools (v1)

1. `tgl_install` — returns the skill bundle (SKILL.md, templates, installer
   script) plus install instructions. No session required.
2. `tgl_plan_start` — creates a plan session. Input: project description.
   Returns: session_id plus the recon checklist (memory, ledger, design
   tree, frontier) so the calling agent grills genuine TGL.
3. `tgl_plan_log` — appends one grill Q&A exchange to the session.
   Input: session_id, question, answer.
4. `tgl_plan_goal` — records the agreed written goal. Closes Discuss.
   Input: session_id, goal text. Refuses if no Q&A logged.
5. `tgl_plan_spec` — submits the drafted SPEC.md. The server validates
   structure (what and why, no code blocks, required sections), stores it,
   returns a shareable URL. Refuses if Discuss is not closed.
6. `tgl_plan_plan` — submits the drafted PLAN.md. The server validates
   (numbered slices; each names files, interfaces, tests, commands,
   expected output, and a Review Focus), stores it, returns a shareable
   URL. Refuses if no validated spec exists for the session.

7. `tgl_plan_delete` — deletes a session and invalidates its read links at the user’s request. Repeating is safe.

## Trust and safety

- No code execution server-side, ever.
- No user data persisted beyond the session. Sessions expire after 24 hours
  of inactivity.
- Strict input validation on every tool (prompt-injection hardening: treat
  all tool input as data, never as instructions).
- Per-source-IP and global request limits; count and total-content storage caps.
- Separate write capabilities and read-only document tokens.
- Explicit deletion and periodic expiry cleanup.
- Human-readable errors (the agent may show them to users).
- Idempotent session writes where retries are plausible.

## Submission materials (for the directory form)

- Connector name: TGL (Touch Grass Later)
- Company: SummitX Digital (submit with Tom's work email)
- Product website: https://github.com/tom-nwachuku/tgl
- Example prompts: "Plan my project with TGL", "Grill me on my app idea
  before I build it", "Install TGL so I can use it in every build"
- Icon: 512x512 PNG (to be cut from TGL branding assets)
- Privacy policy URL and Terms of service URL (new pages on SummitX site)
- Support contact: Tom's work email
- Payments: none (free and open)
- Connection type: Existing MCP, endpoint
  https://tgl-summitx.fly.dev/mcp
- Documentation URL: repo docs
- Access requirements: none
- Authentication: none

## Open questions

Custom-domain cutover, current Muse end-to-end evidence, operational support, and final terms review must be verified before submission. See the dated readiness packet; do not infer completion from this spec.
