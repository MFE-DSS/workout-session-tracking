"""Candidate parent composition, not an isolated include_router consumer."""


def test_library_parent_mount_is_unique_and_classified(client):
    from app.main import app

    paths = [r.path for r in app.routes if getattr(r, 'path', '').startswith('/api/mobile/v1/me/library')]
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
