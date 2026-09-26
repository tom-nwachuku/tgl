# TGL connector 1.1

TGL is a Muse-native developer harness for disciplined, spec-driven software development. Plan Mode reads project context, works through decisions, and produces SPEC.md and a sliced PLAN.md for human sign-off. Attack Mode uses fresh subagents, slice review, progress reports, red-team verification in the real interface, and a release ledger. [The complete workflow](../SKILL.md) is the product.

This hosted MCP service is its installation and planning companion: it delivers the complete skill bundle, stores temporary planning state, and checks document structure. The installed skill directs the workflow using Muse's own tools and permissions. The server does not draft with a model, execute builds, sign approvals, or access connected accounts.

## Connection

HTTPS MCP Streamable HTTP at `https://tgl-summitx.fly.dev/mcp`. No TGL account, OAuth, API key, or payment. The intended custom domain is `tgl.summitxdigital.com`; use it only after live DNS/TLS verification. `TGL_PUBLIC_BASE_URL` controls returned document URLs.

The transport is stateless and returns JSON. MCP initialize, tools/list, and tools/call work through the official Python MCP SDK 2.2.0. Planning state is separate from transport sessions. Client code must handle MCP isError results and HTTP 413/429 responses; a successful HTTP status does not establish a successful tool call. Retry 429 after Retry-After; do not blindly replay a session-creation request after an ambiguous transport failure.

Before Meta directory approval, ask Muse to create a custom integration from this URL. Muse builds a client in its cloud environment. This is not a native directory installation. Do not invent a settings field for arbitrary MCP servers. Muse access and permissions are supplied by Meta.

## Tools

| Tool | Arguments | Result / effect |
|---|---|---|
| tgl_install | none | Complete skill files, manifest, version, install instructions. Does not install files itself. |
| tgl_plan_start | project_description | Private session_id, recon checklist, retention and sharing notice. |
| tgl_plan_log | session_id, question, answer | Records one Q&A. An immediate identical retry is deduplicated. New answers invalidate the goal and documents. |
| tgl_plan_goal | session_id, goal | Requires at least one Q&A. A changed goal invalidates both documents. |
| tgl_plan_spec | session_id, spec_markdown | Requires goal. At least 200 characters, What and Why headings, no fenced code. Changed spec invalidates plan. |
| tgl_plan_plan | session_id, plan_markdown | Requires spec. At least 200 characters and two numbered slices, each with files, interfaces, tests, commands, expected output and Review Focus. |
| tgl_plan_delete | session_id | Makes the session and links inaccessible. Call only for a user-requested deletion. Repeating succeeds. |

Document validation is structural. It does not verify quality, correctness, ownership, legal compliance, or human approval. The Muse conversation handles review and approval before the installed skill guides a build.

## Data, permissions and limits

The private session id is a 256-bit random write capability. It permits mutation and deletion. Shareable document URLs contain a separate 256-bit random read token. Anyone holding a read link can read that session's documents but cannot use it to mutate or delete the session. Tokens are bearer capabilities, not accounts; a leaked write id cannot be recovered safely, so delete the session and start again. No directory of sessions is exposed.

Sessions live in one process's memory. After 24 hours without a successful write they become inaccessible; a one-minute background sweep removes expired state. Reads do not refresh expiry. Restart, redeploy or oldest-idle capacity eviction can end sessions earlier. Save documents locally. Delete before disconnecting: this no-auth custom service receives no provider disconnect event. Saved copies and Muse history have separate retention.

Limits per instance: 1,000 planning sessions; 200 Q&A entries per session; 1,000,000 content characters per session; 16,000,000 content characters total; short inputs 20,000 characters; each document 200,000 characters; request body 512,000 bytes. These units are intentional: characters and bytes are different. At the session-count cap, the oldest idle session is evicted. At a storage limit, the write fails with an actionable error.

HTTP limits: 120 requests/minute per source IP and 1,200/minute globally, fixed windows. Shared networks and proxies can share a limit. No distributed denial-of-service guarantee is made. Fly-Client-IP is trusted only in the Fly deployment; Cloudflare must remain DNS-only for this service. [Fly's header documentation](https://www.fly.io/docs/networking/request-headers/).

All responses use no-store, no-referrer, nosniff and noindex headers. Uvicorn access logs are disabled so bearer document URLs do not appear there. No application request-body logging, analytics or cookies. Hosting/network operational records are separate; see `/privacy`. Host and Origin validation is enabled for the two supported public domains. HTTPS is terminated by Fly Proxy; direct port access is not exposed publicly.

## Portable skill installation

The bundle contains 10 product files, VERSION and MANIFEST.json. It includes both guides, all four templates, the installer, README, SKILL.md and MIT license. Hashes are verified before delivery. Save all returned paths under an isolated directory, inspect SKILL.md, then run `python3 install/tgl-install.py --yes --target YOUR_SKILL_FOLDER` in that directory. Python 3.8+ is sufficient for the installer. Read the actual installed SKILL.md before claiming success.

The installer copies only its explicit 10-file manifest, refuses missing files and symlink destinations, and verifies destination bytes. It does not copy server files, environments or arbitrary checkout contents. Existing named product files are overwritten on an authorized upgrade; unrelated destination files are preserved. It does not register itself with a proprietary Muse directory.

## Verification

From repository root: install `connector/requirements.txt` plus pytest, run `python scripts/sync_bundle.py --check`, then `python -m pytest -q`. `scripts/smoke_mcp.py` provides a dummy-only SDK journey for staging/live verification, including a read-token mutation rejection and explicit cleanup.
