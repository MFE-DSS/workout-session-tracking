"""Candidate parent composition, not an isolated include_router consumer."""


def _library_paths(routes, prefix=''):
    """Read flat or included routers, retaining duplicates so the guard can fail."""
    for route in routes:
        inner = getattr(route, 'original_router', None)
        if inner is not None:
            yield from _library_paths(inner.routes, prefix + route.include_context.prefix)
        else:
            path = prefix + getattr(route, 'path', '')
            if path.startswith('/api/mobile/v1/me/library'):
                yield path


def test_library_parent_mount_is_unique_and_classified(client):
    paths = list(_library_paths(client.app.routes))
    assert sorted(paths) == sorted([
        '/api/mobile/v1/me/library', '/api/mobile/v1/me/library/items/{source_ref}',
        '/api/mobile/v1/me/library/start',
    ])
    response = client.get('/api/mobile/v1/me/library', headers={'X-Auren-Library-Contract': 'owned-library/1.0.0'})
    assert response.status_code == 401
    assert response.headers['cache-control'] == 'no-store'


def test_library_configuration_defaults_do_not_authorize_acquisition():
    from app.config import Settings

    s = Settings(_env_file=None)
    assert s.library_controlled_test_enabled is False
    assert s.library_backend_identity == ''
    assert s.library_signing_key.get_secret_value() == ''


def test_library_mount_guard_retains_duplicate_inclusions():
    from fastapi import APIRouter, FastAPI

    router = APIRouter()

    async def endpoint():
        return {}

    router.add_api_route('/library', endpoint, methods=['GET'])
    app = FastAPI()
    app.include_router(router, prefix='/api/mobile/v1/me')
    app.include_router(router, prefix='/api/mobile/v1/me')
    assert list(_library_paths(app.routes)) == [
        '/api/mobile/v1/me/library', '/api/mobile/v1/me/library',
    ]
