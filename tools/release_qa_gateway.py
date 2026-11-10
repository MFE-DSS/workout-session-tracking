"""Temporary synthetic QA only: closed mobile API proxy, never a public app host."""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import time
from collections import deque
from pathlib import Path
from urllib.parse import unquote, urlsplit

import httpx
from starlette.applications import Starlette
from starlette.requests import ClientDisconnect, Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

MAX_BODY = 128 * 1024
MAX_RESPONSE = 4 * 1024 * 1024
BODY_TIMEOUT = 10
FORWARD_TIMEOUT = 25
HOP_HEADERS = frozenset({
    'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
    'te', 'trailer', 'transfer-encoding', 'upgrade', 'content-length', 'host',
    'forwarded', 'x-forwarded-for', 'x-forwarded-host', 'x-forwarded-proto',
    'cf-connecting-ip', 'accept-encoding',
})


def allowed_path(path: str) -> bool:
    if len(path) > 2048:
        return False
    parsed = urlsplit(path)
    if parsed.scheme or parsed.netloc or parsed.fragment:
        return False
    decoded = parsed.path
    for _ in range(3):
        decoded = unquote(decoded)
    return (
        decoded.startswith(('/api/mobile/v1/', '/api/mobile/v3/'))
        and '\\' not in decoded
        and not any(ord(c) < 32 for c in decoded)
        and not any(part in {'.', '..'} for part in decoded.split('/'))
    )


class WindowBudget:
    """Single-event-loop process budget; no account, token or IP storage."""

    def __init__(self, limit: int = 300):
        self.limit = limit
        self.times: deque[float] = deque()

    def allow(self, now: float) -> bool:
        while self.times and self.times[0] <= now - 60:
            self.times.popleft()
        if len(self.times) >= self.limit:
            return False
        self.times.append(now)
        return True


def failure(status: int, code: str) -> JSONResponse:
    return JSONResponse({'detail': {'error': code}}, status_code=status,
                        headers={'Cache-Control': 'no-store'})


def framing_error(request: Request) -> Response | None:
    lengths = request.headers.getlist('content-length')
    if len(lengths) > 1 or (lengths and 'transfer-encoding' in request.headers):
        return failure(400, 'qa_invalid_framing')
    try:
        if lengths and (int(lengths[0]) < 0 or int(lengths[0]) > MAX_BODY):
            return failure(413, 'qa_request_too_large')
    except ValueError:
        return failure(400, 'qa_invalid_framing')
    return None


async def read_body(request: Request) -> bytes | Response:
    body = bytearray()
    try:
        async with asyncio.timeout(BODY_TIMEOUT):
            async for chunk in request.stream():
                body.extend(chunk)
                if len(body) > MAX_BODY:
                    return failure(413, 'qa_request_too_large')
    except TimeoutError:
        return failure(408, 'qa_request_timeout')
    except ClientDisconnect:
        return failure(400, 'qa_client_disconnected')
    return bytes(body)


def auth_admission(path: str, body: bytes, access: dict) -> Response | None:
    """No arbitrary public account/email acquisition through this synthetic bench."""
    for _ in range(3):
        path = unquote(path)
    path = path.rstrip('/')
    if path not in {'/api/mobile/v1/auth/register', '/api/mobile/v1/auth/login'}:
        return None
    try:
        data = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        return failure(400, 'qa_invalid_auth_body')
    if not isinstance(data, dict):
        return failure(400, 'qa_invalid_auth_body')
    signup = path.endswith('/register')
    users = access.get('signup_users' if signup else 'login_users', [])
    if data.get('username') not in users:
        return failure(403, 'qa_assigned_test_account_required')
    if signup and ((data.get('email') is not None and data.get('email') != '') or
                   set(data) - {'username', 'password', 'password_confirm', 'email', 'device_label'}):
        return failure(403, 'qa_synthetic_registration_only')
    return None


async def forward(request: Request, body: bytes, backend_port: int) -> Response:
    nominated = {v.strip().lower() for v in request.headers.get('connection', '').split(',')}
    headers = {k: v for k, v in request.headers.items()
               if k.lower() not in HOP_HEADERS | nominated}
    headers['Accept-Encoding'] = 'identity'
    raw_path = request.scope['raw_path'].decode('ascii', errors='replace')
    query = request.scope.get('query_string', b'').decode('ascii', errors='replace')
    path = raw_path + ('?' + query if query else '')
    try:
        async with asyncio.timeout(FORWARD_TIMEOUT):
            async with httpx.AsyncClient(timeout=25, trust_env=False, follow_redirects=False) as client:
                async with client.stream(request.method, f'http://127.0.0.1:{backend_port}' + path,
                                         content=body, headers=headers) as upstream:
                    if 300 <= upstream.status_code < 400 and 'location' in upstream.headers:
                        return failure(502, 'qa_redirect_not_supported')
                    output = bytearray()
                    async for chunk in upstream.aiter_raw():
                        output.extend(chunk)
                        if len(output) > MAX_RESPONSE:
                            return failure(502, 'qa_upstream_response_too_large')
                    response_nominated = {v.strip().lower() for v in upstream.headers.get('connection', '').split(',')}
                    response_headers = {k: v for k, v in upstream.headers.items()
                                        if k.lower() not in HOP_HEADERS | response_nominated}
                    response_headers['Cache-Control'] = 'no-store'
                    return Response(bytes(output), status_code=upstream.status_code,
                                    headers=response_headers)
    except (httpx.HTTPError, TimeoutError):
        return failure(502, 'qa_upstream_unavailable')


def create_gateway(identity: dict, *, backend_port: int = 8140, access: dict | None = None) -> Starlette:
    """CLI fixes upstream to 8140; explicit loopback port permits real consumer tests."""
    if type(backend_port) is not int or not 1 <= backend_port <= 65535:
        raise ValueError('invalid loopback port')
    access = access or {}
    for group in ('signup_users', 'login_users'):
        values = access.get(group, [])
        if not isinstance(values, list) or any(
            not isinstance(v, str) or not re.fullmatch(r'qa02-[a-z0-9_-]{4,50}', v)
            for v in values
        ):
            raise ValueError('only explicitly assigned synthetic QA identities are allowed')
    if not set(access.get('signup_users', [])).issubset(access.get('login_users', [])):
        raise ValueError('every assigned signup must also be allowed to log in')
    budget = WindowBudget()
    active = 0
    public = {
        'schema_version': 'release-qa-identity/1.0.0',
        'data_scope': 'SYNTHETIC_ONLY',
        'backend_revision': identity.get('backend_sha'),
        'packaging_digest': identity.get('packaging_digest'),
        'inventory': identity.get('inventory'),
        'authority_generation_at_start': identity.get('authority', {}).get('generation'),
        'temporary': True,
    }

    async def route(request: Request) -> Response:
        nonlocal active
        if not budget.allow(time.monotonic()):
            return failure(429, 'qa_rate_limited')
        if request.url.path == '/__qa_identity' and request.method == 'GET':
            return JSONResponse(public, headers={'Cache-Control': 'no-store'})
        raw_path = request.scope.get('raw_path', b'').decode('ascii', errors='replace')
        if not allowed_path(raw_path):
            return failure(404, 'not_found')
        if active >= 8:
            return failure(503, 'qa_capacity_unavailable')
        error = framing_error(request)
        if error is not None:
            return error
        active += 1
        try:
            body = await read_body(request)
            if isinstance(body, Response):
                return body
            denied = auth_admission(raw_path, body, access)
            return denied if denied is not None else await forward(request, body, backend_port)
        finally:
            active -= 1

    return Starlette(routes=[Route('/{path:path}', route, methods=['GET', 'POST', 'PUT', 'PATCH'])])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--identity-receipt', type=Path, required=True)
    parser.add_argument('--access-receipt', type=Path, required=True)
    args = parser.parse_args()
    identity = json.loads(args.identity_receipt.read_text())
    access = json.loads(args.access_receipt.read_text())
    if identity.get('app_env') != 'test' or identity.get('production') is not False:
        raise ValueError('refuse non-test upstream receipt')
    import uvicorn

    uvicorn.run(create_gateway(identity, access=access), host='127.0.0.1', port=8141,
                access_log=False, proxy_headers=False, timeout_keep_alive=5,
                limit_concurrency=12, timeout_graceful_shutdown=10)


if __name__ == '__main__':
    main()
