"""TGL planning and skill delivery. No server-side build execution."""

import asyncio
from typing import Any
from contextlib import asynccontextmanager, suppress

import uvicorn
from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route

from connector import pages, sessions, tools_install, tools_plan
from connector.middleware import RequestLimits

server = MCPServer("tgl", version="1.1.0", website_url="https://developers.summitxdigital.com/tgl/", instructions="Plan and deliver skill files only. Keep session ids private. Save documents, obtain the user’s approval, and use the installed skill for builds. Delete sessions only at the user’s request.")


@server.tool(structured_output=True)
async def tgl_install() -> dict[str, Any]:
    """Return the TGL skill bundle (SKILL.md, templates, installer script)
    plus install instructions. No session required: installing is the
    no-commitment path."""
    return tools_install.install()


@server.tool(structured_output=True)
async def tgl_plan_start(project_description: str) -> dict[str, Any]:
    """Start a TGL Plan Mode session. Returns the session id plus the recon
    checklist the calling agent follows to grill genuine TGL."""
    return tools_plan.plan_start(project_description)


@server.tool(structured_output=True)
async def tgl_plan_log(session_id: str, question: str, answer: str) -> dict[str, Any]:
    """Log one grill Q&A exchange to the plan session."""
    return tools_plan.plan_log(session_id, question, answer)


@server.tool(structured_output=True)
async def tgl_plan_goal(session_id: str, goal: str) -> dict[str, Any]:
    """Record the agreed written goal, closing the Discuss phase. Refuses if
    no Q&A exchanges have been logged yet (no skipping the grill)."""
    return tools_plan.plan_goal(session_id, goal)


@server.tool(structured_output=True)
async def tgl_plan_spec(session_id: str, spec_markdown: str) -> dict[str, Any]:
    """Validate and store the SPEC.md, returning a shareable URL. Refuses
    unless the Discuss phase is closed (goal recorded): no spec before
    the grill."""
    return tools_plan.plan_spec(session_id, spec_markdown)


@server.tool(structured_output=True)
async def tgl_plan_plan(session_id: str, plan_markdown: str) -> dict[str, Any]:
    """Validate and store the PLAN.md, returning a shareable URL. Refuses
    unless a validated spec already exists for the session."""
    return tools_plan.plan_plan(session_id, plan_markdown)


@server.tool(structured_output=True)
async def tgl_plan_delete(session_id: str) -> dict[str, Any]:
    """Delete a planning session and make its document links inaccessible.
    Only call when the user asks to delete their session. Requires the
    private session id, never a shared read link. Repeating is harmless."""
    return tools_plan.plan_delete(session_id)


def create_app():
    """One process, stateless MCP transport, bounded ephemeral planning state."""
    app = server.streamable_http_app(
        stateless_http=True,
        json_response=True,
        max_request_body_size=512_000,
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=["tgl.summitxdigital.com", "tgl-summitx.fly.dev",
                           "localhost:*", "127.0.0.1:*", "[::1]:*", "testserver"],
            allowed_origins=["https://tgl.summitxdigital.com", "https://tgl-summitx.fly.dev"],
        ),
    )
    original_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def lifespan(app):
        async def sweep():
            while True:
                sessions.purge_expired()
                await asyncio.sleep(60)
        async with original_lifespan(app):
            task = asyncio.create_task(sweep())
            try:
                yield
            finally:
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task

    app.router.lifespan_context = lifespan
    app.add_middleware(RequestLimits)
    app.routes.extend([
        Route("/", pages.index, methods=["GET"]),
        Route("/privacy", pages.privacy, methods=["GET"]),
        Route("/terms", pages.terms, methods=["GET"]),
        Route("/docs/{read_token}/spec", _serve_doc("spec"), methods=["GET"]),
        Route("/docs/{read_token}/plan", _serve_doc("plan"), methods=["GET"]),
    ])
    return app


def _serve_doc(kind):
    async def handler(request):
        read_token = request.path_params["read_token"]
        doc = sessions.get_document(read_token, kind)
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
    uvicorn.run(create_app(), host=host, port=port, access_log=False)


if __name__ == "__main__":
    main()
