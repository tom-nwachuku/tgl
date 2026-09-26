"""Dummy-only MCP SDK journey. Creates one session, then explicitly deletes it.

Usage: python scripts/smoke_mcp.py https://host/mcp output.json
No real user data. Capabilities are not included in the saved receipt.
"""
import asyncio
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit, urljoin
import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

SPEC = '# What it is\nAdd keyboard navigation to an existing report screen in an isolated review fixture. A reviewer can move through visible rows with arrow keys and activate the focused row. No network, accounts, or actual user data are involved.\n## Why\nThis disposable feature request verifies the TGL planning transport without implementing or publishing a real product. A readable spec and sliced plan are the expected outputs.\n'
PLAN = '# Reviewer plan\n' + '\n'.join('## Slice %s: %s\nFiles: report-view.js. Interfaces: focused row index. Tests: empty list, first and last row. Commands: run local tests. Expected output: keyboard navigation follows the spec. Review Focus: no focus loss at list boundaries.\n' % (n,name) for n,name in [(1,'focus state'),(2,'keyboard interaction')])


def data(result):
    if result.is_error:
        raise AssertionError('Tool failed: '+str(result.content))
    if result.structured_content is not None:
        return result.structured_content
    return json.loads(next(x.text for x in result.content if getattr(x,'type',None)=='text'))


async def run(endpoint):
    receipt={'endpoint':endpoint,'mechanism':'official MCP Python SDK 2.2.0; dummy-only session','checks':{}}
    sid=None
    async with streamable_http_client(endpoint) as (read,write):
        async with ClientSession(read,write) as client:
            initialized=await client.initialize()
            receipt['server']=initialized.server_info.model_dump()
            tools=(await client.list_tools()).tools
            receipt['tools']=[t.name for t in tools]
            assert len(tools)==7
            bundle=data(await client.call_tool('tgl_install',{}))
            manifest=json.loads(bundle['files']['MANIFEST.json'])
            assert all(hashlib.sha256(bundle['files'][p].encode()).hexdigest()==digest for p,digest in manifest['files'].items())
            assert 'docs/tutorial.md' in bundle['files']
            receipt['checks']['complete_bundle_hashes']=True
            start=data(await client.call_tool('tgl_plan_start',{'project_description':'Disposable feature fixture: keyboard navigation in an existing report screen.'}))
            sid=start['session_id']
            try:
                rejected=await client.call_tool('tgl_plan_goal',{'session_id':sid,'goal':'Too early'})
                assert rejected.is_error
                receipt['checks']['goal_before_qa_rejected']=True
                args={'session_id':sid,'question':'Which keyboard behavior is in scope?','answer':'Arrow keys move row focus; Enter activates the focused row.'}
                assert data(await client.call_tool('tgl_plan_log',args))['qa_count']==1
                assert data(await client.call_tool('tgl_plan_log',args))['qa_count']==1
                data(await client.call_tool('tgl_plan_goal',{'session_id':sid,'goal':'Make the existing report screen usable with a keyboard.'}))
                spec=data(await client.call_tool('tgl_plan_spec',{'session_id':sid,'spec_markdown':SPEC}))
                plan=data(await client.call_tool('tgl_plan_plan',{'session_id':sid,'plan_markdown':PLAN}))
                token=urlsplit(spec['url']).path.split('/')[-2]
                assert sid != token and sid not in spec['url']
                rejected=await client.call_tool('tgl_plan_goal',{'session_id':token,'goal':'Must fail'})
                assert rejected.is_error
                receipt['checks']['read_token_cannot_modify']=True
                async with httpx.AsyncClient(follow_redirects=True) as http:
                    for kind,result,text in [('spec',spec,SPEC),('plan',plan,PLAN)]:
                        response=await http.get(result['url'])
                        assert response.status_code==200 and response.text==text
                        assert 'no-store' in response.headers['cache-control']
                        receipt['checks'][kind+'_readback']=True
                    assert (await http.get(urljoin(endpoint,'/docs/'+sid+'/spec'))).status_code==404
                receipt['checks']['write_id_cannot_read_doc_route']=True
            finally:
                data(await client.call_tool('tgl_plan_delete',{'session_id':sid}))
            async with httpx.AsyncClient() as http:
                assert (await http.get(spec['url'])).status_code==404
                assert (await http.get(plan['url'])).status_code==404
            data(await client.call_tool('tgl_plan_delete',{'session_id':sid}))
            receipt['checks']['deletion_and_idempotent_retry']=True
    receipt['passed']=True
    return receipt

if __name__=='__main__':
    receipt=asyncio.run(run(sys.argv[1]))
    Path(sys.argv[2]).write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
