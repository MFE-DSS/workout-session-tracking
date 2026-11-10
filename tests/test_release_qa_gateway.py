"""A real loopback upstream proves QA proxy bytes, headers and closed routing."""
import asyncio
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import httpx
import pytest

import tools.release_qa_gateway as gateway_module
from tools.release_qa_gateway import MAX_BODY, WindowBudget, allowed_path, create_gateway


@pytest.mark.parametrize('path', [
    '/admin', '/docs', '/api/mobile/v2/me', '//evil.test/api/mobile/v1/me',
    'https://evil.test/api/mobile/v1/me', '/api/mobile/v1/../admin',
    '/api/mobile/v1/%2e%2e/admin', '/api/mobile/v1/%252e%252e/admin',
    '/api/mobile/v1/%5cadmin', '/api/mobile/v1/%00',
])
def test_gateway_rejects_non_mobile_or_traversing_path(path):
    assert not allowed_path(path)


@pytest.mark.parametrize('path', [
    '/api/mobile/v1/auth/login', '/api/mobile/v3/me/first-session-requests/abc-123',
])
def test_gateway_preserves_canonical_mobile_path(path):
    assert allowed_path(path)


@pytest.fixture
def upstream():
    calls = []

    class Echo(BaseHTTPRequestHandler):
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length', '0')))
            calls.append((self.path, body, self.headers.get('If-Match'), self.headers.get('Authorization')))
            if self.path.endswith('/slow'):
                self.send_response(200)
                self.send_header('Content-Length', '20')
                self.end_headers()
                try:
                    for _ in range(20):
                        self.wfile.write(b'x')
                        self.wfile.flush()
                        time.sleep(0.01)
                except (BrokenPipeError, ConnectionResetError):
                    pass  # Expected when the tested total deadline closes the connection.
                return
            self.send_response(307 if self.path.endswith('/redirect') else 200)
            if self.path.endswith('/redirect'):
                self.send_header('Location', 'https://spignos.com')
            self.send_header('Content-Type', 'application/json')
            self.send_header('Connection', 'X-QA-Private')
            self.send_header('X-QA-Private', 'synthetic-hop-header')
            self.send_header('X-Auren-Contract', self.headers.get('X-Auren-Contract', ''))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Echo)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server.server_port, calls
    server.shutdown()
    server.server_close()
    thread.join()


@pytest.mark.anyio
async def test_gateway_real_upstream_preserves_command_bytes_and_contract(upstream):
    port, calls = upstream
    app = create_gateway({}, backend_port=port)
    body = b'{ "request_id": "same-key", "setting": {"value":8.5,"unit":"kg"} }'
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='https://qa.invalid') as c:
        r = await c.post('/api/mobile/v3/me/blueprint/observations', content=body, headers={
            'Content-Type': 'application/json', 'If-Match': '7',
            'Authorization': 'Bearer synthetic-test-token', 'X-Auren-Contract': 'first-session-runtime/3.0.0',
        })
    assert r.status_code == 200 and r.content == body
    assert r.headers['X-Auren-Contract'] == 'first-session-runtime/3.0.0'
    assert calls == [('/api/mobile/v3/me/blueprint/observations', body, '7', 'Bearer synthetic-test-token')]


@pytest.mark.anyio
async def test_gateway_rejects_large_or_ambiguous_write_before_upstream(upstream):
    port, calls = upstream
    async with httpx.AsyncClient(transport=httpx.ASGITransport(create_gateway({}, backend_port=port)), base_url='https://qa.invalid') as c:
        assert (await c.post('/api/mobile/v1/auth/login', content=b'x' * (MAX_BODY + 1))).status_code == 413
        assert (await c.post('/api/mobile/v1/auth/login', content=b'{}', headers={'Content-Length': '2', 'Transfer-Encoding': 'chunked'})).status_code == 400
        assert (await c.post('/admin', content=b'{}')).status_code == 404
    assert not calls


@pytest.mark.anyio
async def test_gateway_times_out_slow_request_body(upstream, monkeypatch):
    port, calls = upstream
    monkeypatch.setattr(gateway_module, 'BODY_TIMEOUT', 0.01, raising=False)

    async def slow():
        yield b'{'
        await asyncio.sleep(0.1)
        yield b'}'

    async with httpx.AsyncClient(transport=httpx.ASGITransport(create_gateway({}, backend_port=port)), base_url='https://qa.invalid') as c:
        r = await c.post('/api/mobile/v1/auth/login', content=slow())
    assert r.status_code == 408
    assert not calls


@pytest.mark.anyio
async def test_gateway_unavailable_upstream_has_no_scientific_success_or_denial():
    server = ThreadingHTTPServer(('127.0.0.1', 0), BaseHTTPRequestHandler)
    port = server.server_port
    server.server_close()
    async with httpx.AsyncClient(transport=httpx.ASGITransport(create_gateway({}, backend_port=port)), base_url='https://qa.invalid') as c:
        r = await c.get('/api/mobile/v3/me/first-session-handoff')
    assert r.status_code == 502
    assert r.json() == {'detail': {'error': 'qa_upstream_unavailable'}}


@pytest.mark.anyio
async def test_gateway_identity_is_a_redacted_captured_receipt():
    app = create_gateway({'backend_sha': 'a' * 40, 'packaging_digest': 'b' * 64,
        'authority': {'generation': 1}, 'database': '/private/path', 'secret': 'never publish'})
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='https://qa.invalid') as c:
        r = await c.get('/__qa_identity')
    assert r.status_code == 200
    assert r.json()['backend_revision'] == 'a' * 40
    assert r.json()['authority_generation_at_start'] == 1
    assert '/private/path' not in r.text and 'never publish' not in r.text


def test_gateway_budget_limits_burst_without_permanent_lockout():
    budget = WindowBudget(limit=2)
    assert budget.allow(0) and budget.allow(1)
    assert not budget.allow(2)
    assert budget.allow(61)


@pytest.mark.anyio
async def test_gateway_admits_only_assigned_synthetic_signup_without_email(upstream):
    port, calls = upstream
    access = {'signup_users': ['qa02-assigned'], 'login_users': ['qa02-assigned']}
    app = create_gateway({}, backend_port=port, access=access)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='https://qa.invalid') as c:
        for body in [{'username': 'arbitrary-person', 'email': ''},
                     {'username': 'qa02-assigned', 'email': 'person@example.test'}]:
            r = await c.post('/api/mobile/v1/auth/register', json=body)
            assert r.status_code == 403
        assert not calls
        body = b'{"username":"qa02-assigned","email":"","password":"synthetic-only"}'
        r = await c.post('/api/mobile/v1/auth/register', content=body,
                         headers={'Content-Type': 'application/json'})
        assert r.status_code == 200 and r.content == body
        assert calls[-1][1] == body


@pytest.mark.anyio
async def test_gateway_auth_closed_by_default_and_unknown_login_never_reaches_backend(upstream):
    port, calls = upstream
    async with httpx.AsyncClient(transport=httpx.ASGITransport(create_gateway({}, backend_port=port)), base_url='https://qa.invalid') as c:
        for path in ['/api/mobile/v1/auth/register', '/api/mobile/v1/auth/login',
                     '/api/mobile/v1/auth/%72egister', '/api/mobile/v1/auth/%2572egister',
                     '/api/mobile/v1/auth/register/']:
            assert (await c.post(path, json={'username': 'ordinary-person'})).status_code == 403
    assert not calls


@pytest.mark.anyio
async def test_gateway_never_redirects_native_consumer_to_another_host(upstream):
    port, _ = upstream
    async with httpx.AsyncClient(transport=httpx.ASGITransport(create_gateway({}, backend_port=port)), base_url='https://qa.invalid') as c:
        r = await c.post('/api/mobile/v1/redirect', content=b'{}')
    assert r.status_code == 502
    assert 'location' not in r.headers


@pytest.mark.anyio
async def test_gateway_total_deadline_bounds_slow_progress(upstream, monkeypatch):
    port, _ = upstream
    monkeypatch.setattr(gateway_module, 'FORWARD_TIMEOUT', 0.03, raising=False)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(create_gateway({}, backend_port=port)), base_url='https://qa.invalid') as c:
        r = await c.post('/api/mobile/v3/slow', content=b'{}')
    assert r.status_code == 502
    assert r.json() == {'detail': {'error': 'qa_upstream_unavailable'}}


@pytest.mark.anyio
async def test_gateway_removes_response_connection_nominated_headers(upstream):
    port, _ = upstream
    async with httpx.AsyncClient(transport=httpx.ASGITransport(create_gateway({}, backend_port=port)), base_url='https://qa.invalid') as c:
        r = await c.post('/api/mobile/v3/echo', content=b'{}')
    assert r.status_code == 200
    assert 'x-qa-private' not in r.headers
