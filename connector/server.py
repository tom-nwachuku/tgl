"""TGL connector MCP server (slices 1-4).

Exposes the MCP streamable HTTP endpoint at /mcp. Slice 2 registers the
plan session tools (tgl_plan_start, tgl_plan_log, tgl_plan_goal) and slice 3
adds spec/plan validation and storage (tgl_plan_spec, tgl_plan_plan), with
chain-of-command gates enforced in tools_plan. Slice 4 adds the skill
bundle tool (tgl_install): the canonical TGL skill served from a bundle
baked in at build time, no session required. No auth, no persistence
beyond the session store, no code execution.
"""

import uvicorn
from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route

from connector import pages, sessions, tools_install, tools_plan

server = MCPServer("tgl")


@server.tool()
def tgl_install() -> dict:
    """Return the TGL skill bundle (SKILL.md, templates, installer script)
    plus install instructions. No session required: installing is the
    no-commitment path."""
    return tools_install.install()


@server.tool()
def tgl_plan_start(project_description: str) -> dict:
    """Start a TGL Plan Mode session. Returns the session id plus the recon
    checklist the calling agent follows to grill genuine TGL."""
    return tools_plan.plan_start(project_description)


@server.tool()
def tgl_plan_log(session_id: str, question: str, answer: str) -> dict:
    """Log one grill Q&A exchange to the plan session."""
    return tools_plan.plan_log(session_id, question, answer)


@server.tool()
def tgl_plan_goal(session_id: str, goal: str) -> dict:
    """Record the agreed written goal, closing the Discuss phase. Refuses if
    no Q&A exchanges have been logged yet (no skipping the grill)."""
    return tools_plan.plan_goal(session_id, goal)


@server.tool()
def tgl_plan_spec(session_id: str, spec_markdown: str) -> dict:
    """Validate and store the SPEC.md, returning a shareable URL. Refuses
    unless the Discuss phase is closed (goal recorded): no spec before
    the grill."""
    return tools_plan.plan_spec(session_id, spec_markdown)


@server.tool()
def tgl_plan_plan(session_id: str, plan_markdown: str) -> dict:
    """Validate and store the PLAN.md, returning a shareable URL. Refuses
    unless a validated spec already exists for the session."""
    return tools_plan.plan_plan(session_id, plan_markdown)


def create_app():
    """Build the Starlette app: MCP over streamable HTTP at /mcp, static
    The SDK auto-enables DNS rebinding protection with a localhost-only
    allowlist when bound to 127.0.0.1, which would 421 every production
    request arriving with a public Host header behind the Fly proxy.
    This is a public, no-auth server (nothing to rebind against), so the
    protection is explicitly disabled, matching the SDK's default posture
    for non-localhost servers.
    """
    app = server.streamable_http_app(
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=False
        )
    )
    app.routes.append(Route("/", pages.index, methods=["GET"]))
    app.routes.append(Route("/privacy", pages.privacy, methods=["GET"]))
    app.routes.append(Route("/terms", pages.terms, methods=["GET"]))
    app.routes.append(
        Route("/docs/{session_id}/spec", _serve_doc("spec"), methods=["GET"])
    )
    app.routes.append(
        Route("/docs/{session_id}/plan", _serve_doc("plan"), methods=["GET"])
    )
    return app


def _serve_doc(kind):
    async def handler(request):
        session_id = request.path_params["session_id"]
        session = sessions.get(session_id)
        doc = session.get(kind) if session else None
        if not doc:
            return Response(
                "No stored %s for this session. It may have expired "
                "(sessions last 24 hours of inactivity)." % kind,
                status_code=404,
                media_type="text/plain",
            )
        return PlainTextResponse(doc, media_type="text/markdown")

    return handler


def main(host="127.0.0.1", port=8000):
    uvicorn.run(create_app(), host=host, port=port)


if __name__ == "__main__":
    main()
