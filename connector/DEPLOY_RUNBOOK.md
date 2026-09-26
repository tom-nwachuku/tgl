# TGL Connector Deploy Runbook

Staged by slice 6. Nothing here has been run: the runtime choice, the
DNS change, and the deploy itself are Tom's decisions.

## What this deploys

The TGL connector: a free, no-auth MCP server exposing 6 tools
(`tgl_plan_start`, `tgl_plan_log`, `tgl_plan_goal`, `tgl_plan_spec`,
`tgl_plan_plan`, `tgl_install`), plus static pages (`/`, `/privacy`,
`/terms`) and stored-doc routes (`/docs/<session_id>/spec|plan`).

Source: `~/workspace/tgl/connector/`. Pinned deps in
`requirements.txt` (mcp 2.2.0, uvicorn 0.54.0, starlette 1.7.0).

## Step 1: Tom picks the runtime (his decision)

The image is a plain Python container listening on `$PORT` (default
8000). Any host that runs containers works: a small VPS, Fly.io,
Railway, Render, or the existing SummitX host. There is no database
and no state to migrate: sessions live in memory and expire after 24
hours of inactivity.

## Step 2: build the image

From `~/workspace/tgl/connector/`:

```
docker build -t tgl-connector .
```

## Step 3: run it

```
docker run -d --name tgl-connector -e PORT=8000 -p 8000:8000 tgl-connector
```

## Step 4: DNS (Tom's decision)

Create an A record for `tgl.summitxdigital.com` pointing at the host's
public IP. DNS is on Cloudflare, so proxy the record (orange cloud) to
get TLS at `https://tgl.summitxdigital.com` with no extra setup.

## Step 5: verify

Replace the host below with the real one once DNS resolves.

```bash
BASE=https://tgl.summitxdigital.com

# Static pages
curl -s -o /dev/null -w "%{http_code}\n" $BASE/
curl -s -o /dev/null -w "%{http_code}\n" $BASE/privacy
curl -s -o /dev/null -w "%{http_code}\n" $BASE/terms
# expect 200, 200, 200

# MCP initialize
curl -s -X POST $BASE/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"verify","version":"1"}}}' \
  -D - -o /tmp/init.out | grep -i mcp-session-id
# expect a session id; save it as SID

# list_tools shows all 6 tools
SID=<session id from above>
curl -s -X POST $BASE/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H "mcp-session-id: $SID" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
# expect tgl_plan_start, tgl_plan_log, tgl_plan_goal,
# tgl_plan_spec, tgl_plan_plan, tgl_install

# tgl_install returns the bundle with no session
curl -s -X POST $BASE/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H "mcp-session-id: $SID" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"tgl_install","arguments":{}}}' \
  | grep -o 'SKILL.md'
# expect SKILL.md in the bundle
```

Full plan-session smoke (start, log, goal, spec, plan) against
production: run the same tool calls in order over MCP. A spec needs a
"what" heading and a "why" heading with 200+ characters and no code
blocks; a plan needs 2+ numbered slices, each naming files,
interfaces, tests, commands, expected output, and a Review Focus.

## Rollback

Stop the container (`docker stop tgl-connector`) and remove the DNS
record. No data is lost: sessions are ephemeral by design.

## After deploy: slice 7 (Tom's approval)

Submit at https://muse.ai/platform with:
- Endpoint: https://tgl.summitxdigital.com/mcp
- Icon: `connector/assets/tgl-icon-512.png` (512x512 PNG)
- Privacy: https://tgl.summitxdigital.com/privacy
- Terms: https://tgl.summitxdigital.com/terms
- Docs: https://github.com/tom-nwachuku/tgl
- Auth: none. Payments: none. Access requirements: none.
