"""Static informational pages for the TGL connector (slice 6).

GET /         connector info page (what TGL is, endpoint, tools, prompts)
GET /privacy  plain-language privacy policy
GET /terms    plain-language terms of service

All copy is plain HTML at a 5th-grade reading level, no em dashes.
The pages carry no user data and set no cookies.
"""

from starlette.responses import HTMLResponse

_GITHUB = "https://github.com/tom-nwachuku/tgl"
_ENDPOINT = "https://tgl.summitxdigital.com/mcp"

_CSS = """
body { font-family: system-ui, -apple-system, sans-serif; max-width: 640px;
       margin: 2em auto; padding: 0 1.2em; line-height: 1.6; color: #1a1a1a; }
h1 { font-size: 1.6em; } h2 { font-size: 1.2em; margin-top: 1.6em; }
code { background: #f0f0f0; padding: 0.1em 0.4em; border-radius: 4px; }
pre { background: #f0f0f0; padding: 1em; border-radius: 6px;
      overflow-x: auto; }
a { color: #0b5fff; }
"""

_TOOLS = [
    ("tgl_plan_start",
     "Start a Plan Mode session for your project. Returns a session id."),
    ("tgl_plan_log",
     "Log one grill question and answer to the session."),
    ("tgl_plan_goal",
     "Record the agreed goal. Closes the grilling round."),
    ("tgl_plan_spec",
     "Submit your SPEC.md. The server checks it and stores it."),
    ("tgl_plan_plan",
     "Submit your PLAN.md. The server checks it and stores it."),
    ("tgl_install",
     "Get the TGL skill files so you can install TGL in your Muse."),
]

_PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title><style>{css}</style></head>
<body>{body}</body></html>"""

_INDEX_BODY = """
<h1>TGL (Touch Grass Later)</h1>
<p>A free Muse connector for disciplined plan-then-execute development.
Say what you want to build, get grilled one question at a time, sign off
a written spec and plan, then build in reviewed slices.</p>

<h2>How to use it</h2>
<p>You do not need to install anything. Just talk to Muse:</p>
<pre>"TGL, plan a bookmarking app"
"Grill me on my app idea before I build it"
"install TGL so I can use it in every build"</pre>

<h2>MCP endpoint</h2>
<p>Agents connect here: <code>{endpoint}</code></p>

<h2>Tools</h2>
<ul>
{tools}
</ul>

<h2>Two paths</h2>
<p><strong>One-shot:</strong> run Plan Mode right here through the
connector. No install, no commitment.</p>
<p><strong>Install:</strong> call <code>tgl_install</code> to get the
skill files, then say "install TGL" to set it up in your Muse for
ongoing use.</p>

<h2>Links</h2>
<p><a href="{github}">TGL on GitHub</a><br>
<a href="/privacy">Privacy policy</a><br>
<a href="/terms">Terms of service</a></p>

<p>Run by SummitX Digital. Free to use, no account needed.</p>
"""

_PRIVACY_BODY = """
<h1>Privacy Policy</h1>
<p>Last updated: September 2026.</p>

<h2>What we store</h2>
<p>When you use TGL through this connector, we keep your plan session
while you are working: your project description, the grill questions
and answers, your goal, your spec, and your plan. We keep this in the
server's memory only. It is not saved to a disk or a database.</p>

<h2>What we do not collect</h2>
<p>We do not ask for accounts, names, emails, or payments. We do not
use tracking, analytics, or cookies. We do not sell or share your
session content with anyone.</p>

<h2>How long we keep it</h2>
<p>Sessions expire after 24 hours of no activity, then they are gone.
You can also just stop using the session and it will fade away on its
own.</p>

<h2>Who runs this</h2>
<p>SummitX Digital runs this connector. Questions: open an issue at
<a href="{github}">github.com/tom-nwachuku/tgl</a>.</p>
"""

_TERMS_BODY = """
<h1>Terms of Service</h1>
<p>Last updated: September 2026.</p>

<p>TGL is free to use. You do not need an account.</p>

<p>Use it for lawful work. Do not abuse the service, flood it with
requests, or feed it illegal content.</p>

<p>Sessions are temporary. They live in memory and expire after 24 hours
of no activity. Do not treat them as permanent storage.</p>

<p>The service comes with no warranty. SummitX Digital may change,
limit, or stop the service at any time.</p>

<p>Questions: open an issue at
<a href="{github}">github.com/tom-nwachuku/tgl</a>.</p>
"""


def _page(title, body):
    return HTMLResponse(
        _PAGE.format(title=title, css=_CSS, body=body.format(
            github=_GITHUB, endpoint=_ENDPOINT,
            tools="\n".join(
                "<li><code>%s</code>: %s</li>" % (name, desc)
                for name, desc in _TOOLS
            ),
        ))
    )


async def index(request):
    return _page("TGL (Touch Grass Later) - Muse connector", _INDEX_BODY)


async def privacy(request):
    return _page("TGL - Privacy Policy", _PRIVACY_BODY)


async def terms(request):
    return _page("TGL - Terms of Service", _TERMS_BODY)
