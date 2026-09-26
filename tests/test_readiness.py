import asyncio
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import pytest
from starlette.testclient import TestClient
from mcp.server.mcpserver.exceptions import ToolError
from connector import sessions, tools_plan, tools_install
from connector.server import create_app
from connector import middleware

ROOT = Path(__file__).resolve().parents[1]
SPEC = '# What it is\nA small, local-only bookmarking application that keeps a title and URL for each saved item. The user can add a link, see the list, and remove a selected link.\n## Why\nThis dummy review fixture makes saving useful reading simple. It contains no personal information and must never send notifications or publish anything.\n'
PLAN = '# Plan\n' + '\n'.join('## Slice %s: %s\nFiles: app.py. Interfaces: local UI. Tests: empty and populated lists. Commands: run unit checks. Expected output: the selected behavior works. Review Focus: saved content remains local.\n' % (n, name) for n,name in [(1,'storage'),(2,'display')])

@pytest.fixture(autouse=True)
def reset():
    sessions.clear()
    yield
    sessions.clear()

def ready():
    sid = tools_plan.plan_start('Dummy bookmarking app')['session_id']
    tools_plan.plan_log(sid,'Who is this for?','One person')
    tools_plan.plan_goal(sid,'Save links locally')
    return sid

def test_workflow_gates_links_and_delete():
    sid=tools_plan.plan_start('Dummy')['session_id']
    with pytest.raises(ToolError): tools_plan.plan_goal(sid,'Goal')
    with pytest.raises(ToolError): tools_plan.plan_spec(sid,SPEC)
    tools_plan.plan_log(sid,'Audience?','Just me')
    tools_plan.plan_goal(sid,'Save links')
    with pytest.raises(ToolError): tools_plan.plan_plan(sid,PLAN)
    spec=tools_plan.plan_spec(sid,SPEC)
    plan=tools_plan.plan_plan(sid,PLAN)
    token=spec['url'].split('/')[-2]
    assert token != sid and sid not in spec['url']
    assert sessions.get_document(token,'spec') == SPEC
    assert sessions.get_document(sid,'spec') is None
    with pytest.raises(ToolError): tools_plan.plan_log(token,'attack','change')
    tools_plan.plan_delete(token)  # A read token cannot delete another session.
    assert sessions.get(sid)
    assert tools_plan.plan_delete(sid)['ok']
    assert sessions.get_document(token,'spec') is None
    assert tools_plan.plan_delete(sid)['ok']

def test_changed_goal_spec_or_qa_invalidates_downstream():
    sid=ready()
    tools_plan.plan_spec(sid,SPEC);tools_plan.plan_plan(sid,PLAN)
    tools_plan.plan_spec(sid,SPEC)
    assert sessions.get(sid)['plan'] == PLAN
    tools_plan.plan_spec(sid,SPEC+'New scope.')
    assert sessions.get(sid)['plan'] is None
    tools_plan.plan_goal(sid,'Different goal')
    assert sessions.get(sid)['spec'] is None
    tools_plan.plan_log(sid,'New question?','New answer')
    assert sessions.get(sid)['goal'] is None
    assert sessions.get(sid)['phase']=='DISCUSSING'

def test_retry_and_limits(monkeypatch):
    sid=ready()
    assert tools_plan.plan_log(sid,'Who is this for?','One person')['qa_count']==1
    assert sessions.get(sid)['goal']=='Save links locally'
    monkeypatch.setattr(sessions,'MAX_QA',1)
    with pytest.raises(ToolError):tools_plan.plan_log(sid,'Another?','Yes')
    monkeypatch.setattr(sessions,'MAX_SESSION_CHARS',20)
    with pytest.raises(ToolError):tools_plan.plan_goal(sid,'x'*21)
    monkeypatch.setattr(sessions,'MAX_SESSION_CHARS',1000)
    monkeypatch.setattr(sessions,'MAX_TOTAL_CHARS',1)
    with pytest.raises(ToolError):tools_plan.plan_start('new')
    with pytest.raises(ToolError):tools_plan.plan_start('x'*20001)

def test_expiration_sweep_and_capacity(monkeypatch):
    clock=[0];monkeypatch.setattr(sessions,'_now',lambda:clock[0])
    sid=ready();token=sessions.get(sid)['read_token']
    clock[0]=sessions.SESSION_TTL_SECONDS
    sessions.purge_expired()
    assert not sessions._store and not sessions._readers
    assert sessions.get_document(token,'spec') is None
    monkeypatch.setattr(sessions,'MAX_SESSIONS',1)
    a=sessions.create('a');b=sessions.create('b')
    assert sessions.get(a) is None and sessions.get(b)

def test_validation():
    sid=ready()
    with pytest.raises(ToolError):tools_plan.plan_spec(sid,'## What\nshort')
    with pytest.raises(ToolError):tools_plan.plan_spec(sid,SPEC+'```code```')
    tools_plan.plan_spec(sid,SPEC)
    with pytest.raises(ToolError):tools_plan.plan_plan(sid,'# Plan\nNo slices')
    with pytest.raises(ToolError):tools_plan.plan_plan(sid,PLAN.replace('Review Focus','Unreviewed'))

def test_bundle_and_installer(tmp_path):
    subprocess.run([sys.executable,'scripts/sync_bundle.py','--check'],cwd=ROOT,check=True)
    bundle=tools_install.install()
    assert {'docs/modes.md','docs/tutorial.md','LICENSE','MANIFEST.json'} <= set(bundle['files'])
    for mode,src in [('repo',ROOT),('bundle',ROOT/'connector/skill-bundle')]:
        dest=tmp_path/mode
        # Held-open stdin proves --yes is genuinely noninteractive.
        p=subprocess.Popen([sys.executable,str(src/'install/tgl-install.py'),'--yes','--no-color','--target',str(dest)],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        assert p.wait(timeout=10)==0
        p.stdin.close()
        assert (dest/'SKILL.md').read_bytes()==(ROOT/'SKILL.md').read_bytes()
        assert (dest/'docs/tutorial.md').exists()
        assert (dest/'LICENSE').exists()
        assert not (dest/'connector').exists()
        assert not (dest/'.venv').exists()
        assert len([p for p in dest.rglob('*') if p.is_file()])==10

def test_installer_missing_file_and_symlink(tmp_path):
    bundle=tmp_path/'source'
    import shutil
    shutil.copytree(ROOT/'connector/skill-bundle',bundle)
    (bundle/'docs/tutorial.md').unlink()
    dest=tmp_path/'dest'
    p=subprocess.run([sys.executable,str(bundle/'install/tgl-install.py'),'--yes','--target',str(dest)],capture_output=True)
    assert p.returncode==1 and not (dest/'SKILL.md').exists()
    dest.mkdir(exist_ok=True)
    external=tmp_path/'external';external.mkdir()
    (dest/'docs').symlink_to(external,target_is_directory=True)
    p=subprocess.run([sys.executable,str(ROOT/'install/tgl-install.py'),'--yes','--target',str(dest)],capture_output=True)
    assert p.returncode==1 and not list(external.iterdir())

def test_http_sdk_contract_and_read_protection():
    with TestClient(create_app()) as client:
        headers={'Accept':'application/json, text/event-stream'}
        counter=iter(range(1,100))
        def rpc(method,params):
            r=client.post('/mcp',headers=headers,json={'jsonrpc':'2.0','id':next(counter),'method':method,'params':params})
            assert r.status_code==200,r.text
            return r.json()['result']
        init=rpc('initialize',{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'test','version':'1'}})
        assert init['serverInfo']['name']=='tgl'
        listing=rpc('tools/list',{})
        assert len(listing['tools'])==7
        def call(name,args):return rpc('tools/call',{'name':name,'arguments':args})
        install=call('tgl_install',{})
        assert not install.get('isError')
        sid=call('tgl_plan_start',{'project_description':'Dummy'})['structuredContent']['session_id']
        assert call('tgl_plan_goal',{'session_id':sid,'goal':'Too early'})['isError']
        call('tgl_plan_log',{'session_id':sid,'question':'Who?','answer':'Me'})
        call('tgl_plan_goal',{'session_id':sid,'goal':'Local list'})
        result=call('tgl_plan_spec',{'session_id':sid,'spec_markdown':SPEC})['structuredContent']
        token=result['url'].split('/')[-2]
        r=client.get('/docs/'+token+'/spec')
        assert r.text==SPEC and r.headers['cache-control']=='no-store'
        assert r.headers['x-content-type-options']=='nosniff'
        assert client.get('/docs/'+sid+'/spec').status_code==404
        call('tgl_plan_delete',{'session_id':sid})
        assert client.get('/docs/'+token+'/spec').status_code==404
        assert client.post('/mcp',headers={**headers,'Host':'evil.invalid'},json={'jsonrpc':'2.0','id':100,'method':'tools/list'}).status_code==421
        assert client.post('/mcp',headers={**headers,'Origin':'https://evil.invalid'},json={'jsonrpc':'2.0','id':101,'method':'tools/list'}).status_code==403
        assert client.post('/mcp',content=b'x'*512001).status_code==413

def test_rate_limit_and_forwarded_header(monkeypatch):
    monkeypatch.setattr(middleware,'REQUESTS_PER_MINUTE',2)
    with TestClient(create_app()) as client:
        assert client.get('/').status_code==200
        assert client.get('/',headers={'X-Forwarded-For':'2.2.2.2','Fly-Client-IP':'3.3.3.3'}).status_code==200
        r=client.get('/',headers={'X-Forwarded-For':'4.4.4.4'})
        assert r.status_code==429 and r.headers['retry-after']=='60'

def test_chunked_body_is_bounded():
    from starlette.responses import PlainTextResponse
    async def run():
        reached=[];out=[]
        async def app(scope,receive,send):reached.append(True)
        messages=iter([{'type':'http.request','body':b'x'*300000,'more_body':True},{'type':'http.request','body':b'y'*300000,'more_body':False}])
        async def receive():return next(messages)
        async def send(message):out.append(message)
        await middleware.RequestLimits(app)({'type':'http','method':'POST','headers':[],'client':('local',0)},receive,send)
        assert not reached and out[0]['status']==413
    asyncio.run(run())

def test_limiter_window_rollover_and_global_limit(monkeypatch):
    clock=[60];monkeypatch.setattr(middleware.time,'monotonic',lambda:clock[0])
    monkeypatch.setattr(middleware,'REQUESTS_PER_MINUTE',2)
    monkeypatch.setattr(middleware,'GLOBAL_REQUESTS_PER_MINUTE',3)
    monkeypatch.setenv('FLY_APP_NAME','tgl-summitx')
    with TestClient(create_app()) as client:
        assert client.get('/',headers={'Fly-Client-IP':'1.1.1.1'}).status_code==200
        assert client.get('/',headers={'Fly-Client-IP':'2.2.2.2'}).status_code==200
        assert client.get('/',headers={'Fly-Client-IP':'1.1.1.1'}).status_code==200
        assert client.get('/',headers={'Fly-Client-IP':'3.3.3.3'}).status_code==429
        clock[0]=120
        assert client.get('/',headers={'Fly-Client-IP':'3.3.3.3'}).status_code==200


def test_total_storage_limit_preserves_existing_documents(monkeypatch):
    sid=ready();tools_plan.plan_spec(sid,SPEC)
    before=sessions._size(sessions.get(sid))
    monkeypatch.setattr(sessions,'MAX_TOTAL_CHARS',before+1)
    with pytest.raises(ToolError):tools_plan.plan_plan(sid,PLAN)
    assert sessions.get(sid)['spec']==SPEC
    assert sessions.get(sid)['plan'] is None
