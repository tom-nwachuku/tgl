"""Public service facts, privacy notice, and existing service terms."""
import html
import os
from starlette.responses import HTMLResponse

GITHUB = 'https://github.com/tom-nwachuku/tgl'
SITE = 'https://developers.summitxdigital.com/tgl/'
STYLE = '''body{font-family:system-ui,sans-serif;max-width:720px;margin:3em auto;padding:0 1.3em;line-height:1.65;color:#032031;background:#eeebe7}h1,h2{line-height:1.2}a{color:#09747e}code{overflow-wrap:anywhere}li{margin:.6em 0}'''


def page(title, body):
    return HTMLResponse('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TGL | '+title+'</title><style>'+STYLE+'</style><body><p><a href="'+SITE+'">TGL by Sendable Studios</a></p><h1>'+title+'</h1>'+body+'<p><a href="/">Connector</a> · <a href="/privacy">Privacy</a> · <a href="/terms">Terms</a></p></body></html>')


async def index(request):
    base = html.escape(os.environ.get('TGL_PUBLIC_BASE_URL','https://tgl-summitx.fly.dev').rstrip('/'))
    return page('Touch Grass Later', '''<p>Turn an app idea into a written goal, a spec, and a plan you can review before building.</p>
<p>The hosted connector keeps temporary planning state and delivers the TGL skill files. Muse asks the questions and drafts the documents. This service does not execute builds.</p>
<h2>Start with Muse</h2><p>Ask Muse to connect to <code>'''+base+'''/mcp</code> and use TGL to plan a personal bookmarking app, one question at a time. This is a custom integration until Meta approves a directory listing. No one-click directory installation is claimed.</p>
<p>For the full workflow, give Muse <a href="'''+GITHUB+'''">the repository</a> and say “install TGL.” After it reads back SKILL.md, start Plan Mode. Save and review SPEC.md and PLAN.md, approve their versions, then ask the installed skill to guide the build in reviewed slices. Approval is an instruction Muse follows, not a permission interlock in this server.</p>
<h2>Tools</h2><ul><li><code>tgl_install</code>: return the complete skill bundle and integrity manifest.</li><li><code>tgl_plan_start</code>: create a planning session.</li><li><code>tgl_plan_log</code>: record one question and answer.</li><li><code>tgl_plan_goal</code>: record the goal after at least one answer.</li><li><code>tgl_plan_spec</code>: validate structure and store a spec.</li><li><code>tgl_plan_plan</code>: validate structure and store a plan after a spec.</li><li><code>tgl_plan_delete</code>: delete a session at the user's request.</li></ul>
<h2>Access and limits</h2><p>No TGL account, payment, or API key is needed. Hosted access has no TGL fee today. Muse access is separate. Requests are limited to 120 per minute per source IP and 1,200 per minute for this instance. Shared networks may share a limit. Request bodies are limited to 512,000 bytes; short inputs to 20,000 characters; documents to 200,000 characters. Each session holds up to 200 Q&amp;A exchanges and 1,000,000 content characters. This instance holds up to 1,000 sessions and 16,000,000 content characters.</p>
<p>Keep the session id private: it permits edits and deletion. Shareable document links allow anyone who has them to read those documents. They do not permit edits. Sessions expire after 24 hours without a successful write; reads do not extend them. Restart, redeploy, or capacity eviction may remove them sooner. Save your documents locally.</p>
<p>Run by Sendable Studios, the developer brand of Summit X Digital LLC. <a href="mailto:team@summitxdigital.com">Contact support</a>.</p>''')


async def privacy(request):
    return page('Privacy notice', '''<p>Updated September 26, 2026.</p>
<h2>Who operates TGL</h2><p>Sendable Studios is the developer brand of Summit X Digital LLC. Contact <a href="mailto:team@summitxdigital.com">team@summitxdigital.com</a> for privacy, deletion, or support requests. Office: 5900 Balcones Drive, Suite #24136, Austin, TX 78731.</p>
<h2>Data used for your request</h2><p>Muse sends the project description, questions and answers, goal, spec, and plan that you choose to use with the connector. We process this content to provide your planning session and document links. Do not include passwords, credentials, or confidential personal information.</p>
<p>The application holds planning content in server memory. It does not save planning sessions to a database or application data files. It does not ask for names, email addresses, accounts, or payment details. Your text may still contain personal information if you put it there.</p>
<h2>Who can access it</h2><p>Fly.io hosts the service and processes requests to run it. Muse receives tool results under Meta's own privacy terms. Anyone holding a document link can read that document. Anyone holding the private session id can change or delete the session. Share only the read links, and only with people you intend to have access.</p>
<h2>Retention and deletion</h2><p>After 24 hours without a successful write, a session becomes inaccessible. The application removes expired state within its next one-minute sweep. Reads do not reset the timer. A restart, redeploy, or capacity eviction can remove a session earlier. Ask Muse to call <code>tgl_plan_delete</code> with your private session id to remove it immediately. The delete operation makes hosted links inaccessible too. It cannot remove copies you, recipients, or Meta already saved.</p>
<p>Disconnecting a custom integration is not automatically reported to this unauthenticated service. Delete your session before disconnecting. If you need help deleting data, contact our support email privately; do not post a session id in a public issue.</p>
<h2>Service records</h2><p>The application does not intentionally log request bodies or document URLs, use tracking cookies, or run analytics. For request limits it holds a salted hash of the caller IP in memory for a one-minute window, cleared on subsequent traffic. Hosting and network providers may keep operational records under their own policies. This notice does not promise that no infrastructure logs exist.</p>
<p>We do not sell planning content or use it to train models. Privacy or deletion requests sent by email create separate correspondence needed to answer you. Meta's retention and use of Muse conversations are governed by <a href="https://muse.ai/privacy">Meta's privacy notice</a>.</p>''')


async def terms(request):
    return page('Terms of service', '''<p>Updated September 26, 2026.</p>
<p>TGL's source is MIT licensed. Hosted access has no TGL fee today and does not need a TGL account. Muse access is separate.</p>
<p>Use it for lawful work. Do not abuse the service, flood it with requests, or provide illegal content.</p>
<p>Sessions are temporary. They expire after 24 hours without a successful write and may end sooner on restart, redeploy, or capacity eviction. Save your work. Document links are readable by anyone who has them; keep private session ids to yourself.</p>
<p>The hosted connector provides planning support and skill files. It does not execute builds or enforce human approval. Review documents and actions in your agent before proceeding.</p>
<p>The service comes with no warranty. Summit X Digital LLC may change, limit, or stop the service at any time.</p>
<p>Questions: <a href="mailto:team@summitxdigital.com">team@summitxdigital.com</a>. For public code issues, use <a href="'''+GITHUB+'''/issues">GitHub</a>. Never include private session ids or sensitive content in an issue.</p>''')
