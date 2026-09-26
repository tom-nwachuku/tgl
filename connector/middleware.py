"""Request limits at the HTTP boundary. No request body or capability logging."""
import hashlib
import ipaddress
import os
import time
from collections import OrderedDict
from starlette.responses import PlainTextResponse

MAX_BODY_BYTES = 512_000
REQUESTS_PER_MINUTE = 120
GLOBAL_REQUESTS_PER_MINUTE = 1200
MAX_CALLERS = 4096


class RequestLimits:
    def __init__(self, app):
        self.app = app
        self.callers = OrderedDict()
        self.global_window = (-1, 0)
        self.salt = os.urandom(32)

    def _caller(self, scope):
        address = (scope.get('client') or ('unknown', 0))[0]
        # Fly overwrites this header. Trust it only in the Fly deployment;
        # direct/local callers cannot opt in by sending Forwarded headers.
        if os.environ.get('FLY_APP_NAME') == 'tgl-summitx':
            headers = dict(scope.get('headers', []))
            try:
                address = str(ipaddress.ip_address(headers.get(b'fly-client-ip', b'').decode()))
            except ValueError:
                pass
        return hashlib.sha256(self.salt + address.encode()).digest()

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        window = int(time.monotonic() // 60)
        if self.global_window[0] != window:
            self.callers.clear()
        caller = self._caller(scope)
        _, count = self.callers.get(caller, (window, 0))
        gw, global_count = self.global_window
        if gw != window:
            global_count = 0
        if count >= REQUESTS_PER_MINUTE or global_count >= GLOBAL_REQUESTS_PER_MINUTE or (caller not in self.callers and len(self.callers) >= MAX_CALLERS):
            return await PlainTextResponse('Request limit reached. Retry in one minute.', 429, headers={'Retry-After':'60'})(scope, receive, send)
        self.callers[caller] = (window, count + 1)
        self.global_window = (window, global_count + 1)
        # Bound actual streamed bytes, not just the caller's Content-Length.
        if scope['method'] in ('POST', 'PUT', 'PATCH'):
            body = bytearray()
            while True:
                message = await receive()
                if message['type'] == 'http.disconnect':
                    return
                body.extend(message.get('body', b''))
                if len(body) > MAX_BODY_BYTES:
                    return await PlainTextResponse('Request body too large. Shorten the input.', 413)(scope, receive, send)
                if not message.get('more_body'):
                    break
            sent = False
            original_receive = receive
            async def bounded_receive():
                nonlocal sent
                if not sent:
                    sent = True
                    return {'type':'http.request', 'body':bytes(body), 'more_body':False}
                return await original_receive()
            receive = bounded_receive
        async def private_send(message):
            if message['type'] == 'http.response.start':
                message['headers'] = list(message.get('headers', [])) + [
                    (b'cache-control', b'no-store'), (b'x-content-type-options', b'nosniff'),
                    (b'referrer-policy', b'no-referrer'), (b'x-robots-tag', b'noindex, nofollow'),
                ]
            await send(message)
        await self.app(scope, receive, private_send)
