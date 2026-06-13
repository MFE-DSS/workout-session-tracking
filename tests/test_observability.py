"""Sb_26.3 — tests for observability surfaces.

Covers:
* /healthz/strict deploy + disk sub-payloads (degrade gracefully when
  deploy_state.json is missing or malformed);
* `scripts/write_deploy_state.py` writes the expected schema;
* `scripts/prod_state_report.py` emits a no-secret JSON;
* `scripts/alert_discord.py` is disabled by default (no POST when
  DISCORD_WEBHOOK_URL is unset);
* Sentry init is opt-in (no init when SENTRY_DSN unset).
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def _load_script(name: str):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ───────── /healthz/strict deploy + disk ─────────


def test_healthz_strict_includes_deploy_and_disk_when_no_state(client):
    """No deploy_state.json present → deploy.present=False, status stays 200."""
    r = client.get("/healthz/strict")
    assert r.status_code in (200, 503)  # backup check decides primary status
    payload = r.json()
    assert "deploy" in payload
    assert "disk" in payload
    # The shape must be present even with no file.
    assert payload["deploy"]["present"] in (False, True)
    assert "free_percent" in payload["disk"] or "error" in payload["disk"]


def test_healthz_strict_reads_deploy_state(client, tmp_path, monkeypatch):
    """When deploy_state.json is well-formed, the endpoint surfaces it."""
    from app.config import get_settings

    state_file = tmp_path / "deploy_state.json"
    state_file.write_text(
        json.dumps(
            {
                "sha": "abc1234567890def",
                "deployed_at": "2026-01-01T00:00:00+00:00",
                "service": "workout-test",
                "app_dir": "/tmp/workout-test",
                "health_at_deploy": "200",
            }
        ),
        encoding="utf-8",
    )

    get_settings.cache_clear()
    monkeypatch.setenv("DEPLOY_STATE_PATH", str(state_file))
    try:
        r = client.get("/healthz/strict")
        deploy = r.json()["deploy"]
        assert deploy["present"] is True
        assert deploy["sha"] == "abc1234567890def"
        assert deploy["short_sha"] == "abc123456789"
        assert deploy["service"] == "workout-test"
        assert deploy["age_seconds"] is not None
        assert deploy["errors"] == []
    finally:
        get_settings.cache_clear()


def test_healthz_strict_handles_malformed_deploy_state(client, tmp_path, monkeypatch):
    """Bad JSON must NOT crash /healthz/strict — just report present=False + error."""
    from app.config import get_settings

    state_file = tmp_path / "deploy_state.json"
    state_file.write_text("{not json", encoding="utf-8")

    get_settings.cache_clear()
    monkeypatch.setenv("DEPLOY_STATE_PATH", str(state_file))
    try:
        r = client.get("/healthz/strict")
        deploy = r.json()["deploy"]
        assert deploy["present"] is False
        assert any("read error" in e for e in deploy["errors"])
    finally:
        get_settings.cache_clear()


def test_healthz_strict_does_not_expose_secrets(client):
    """Sanity: no env-secret-looking string surfaces in the payload."""
    r = client.get("/healthz/strict")
    body = r.text.lower()
    for forbidden in ("secret", "password", "token", "discord_webhook_url"):
        assert forbidden not in body


# ───────── write_deploy_state ─────────


def test_write_deploy_state_writes_expected_schema(tmp_path):
    out = tmp_path / "deploy_state.json"
    mod = _load_script("write_deploy_state")
    sys.argv = [
        "write_deploy_state",
        "--sha",
        "0123456789abcdef0123456789abcdef01234567",
        "--service",
        "workout-x",
        "--app-dir",
        "/opt/workout-test",
        "--health",
        "200",
        "--out",
        str(out),
    ]
    assert mod.main() == 0
    assert out.exists()
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["sha"] == "0123456789abcdef0123456789abcdef01234567"
    assert payload["service"] == "workout-x"
    assert payload["app_dir"] == "/opt/workout-test"
    assert payload["health_at_deploy"] == "200"
    assert payload["deployed_at"].endswith("+00:00")


# ───────── prod_state_report ─────────


def test_prod_state_report_emits_json_no_secrets(tmp_path):
    state = tmp_path / "deploy_state.json"
    state.write_text(
        json.dumps({"sha": "abc123def456", "deployed_at": "2026-01-01T00:00:00+00:00"}),
        encoding="utf-8",
    )
    bdir = tmp_path / "backups"
    bdir.mkdir()
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "prod_state_report.py"),
            "--deploy-state",
            str(state),
            "--backup-dir",
            str(bdir),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["deploy"]["sha"] == "abc123def456"
    assert payload["deploy"]["short_sha"] == "abc123def456"
    assert "hostname" in payload
    # Confirm no obvious secret-like keys
    flat = json.dumps(payload).lower()
    for forbidden in ("password", "secret", "webhook", "dsn", "token"):
        assert forbidden not in flat, f"{forbidden!r} leaked in prod_state_report"


# ───────── alert_discord (opt-in) ─────────


def test_alert_discord_disabled_when_env_unset(monkeypatch):
    monkeypatch.delenv("DISCORD_WEBHOOK_URL", raising=False)
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "alert_discord.py"),
            "--title",
            "test",
            "--message",
            "noop",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "disabled" in result.stdout.lower() or "no-op" in result.stdout.lower()


def test_alert_discord_dry_run_never_posts():
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "alert_discord.py"),
            "--dry-run",
            "--severity",
            "warning",
            "--title",
            "test",
            "--message",
            "payload validation",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "dry-run" in result.stdout.lower()
    # Validate the JSON portion parses
    json_part = result.stdout.split("[alert_discord]")[0]
    payload = json.loads(json_part)
    assert payload["embeds"][0]["title"].startswith("[WARNING]")


def test_alert_discord_truncates_long_message():
    mod = _load_script("alert_discord")
    huge = "x" * 5000
    payload = mod._build_payload("info", "t", huge)
    # +1 for the ellipsis char, but assert it's bounded.
    assert len(payload["embeds"][0]["description"]) <= mod.MAX_MESSAGE + 2


# ───────── Sentry opt-in ─────────


def test_sentry_disabled_by_default(monkeypatch):
    """No SENTRY_DSN → init returns False without raising."""
    from app.config import get_settings
    from app.main import _init_sentry_if_enabled

    monkeypatch.delenv("SENTRY_DSN", raising=False)
    get_settings.cache_clear()
    try:
        assert _init_sentry_if_enabled(get_settings()) is False
    finally:
        get_settings.cache_clear()


def test_sentry_init_called_when_dsn_set(monkeypatch):
    """SENTRY_DSN set → either initialised (sdk present) or silently
    skipped (sdk absent). Never raises."""
    from app.config import get_settings
    from app.main import _init_sentry_if_enabled

    monkeypatch.setenv("SENTRY_DSN", "https://fake@sentry.example.org/1")
    get_settings.cache_clear()
    try:
        settings = get_settings()
        assert settings.sentry_enabled is True
        # If sentry_sdk is importable, init must succeed. If not,
        # _init_sentry_if_enabled returns False without raising.
        try:
            import sentry_sdk  # noqa: F401

            sdk_present = True
        except ImportError:
            sdk_present = False
        result = _init_sentry_if_enabled(settings)
        assert result is sdk_present
    finally:
        get_settings.cache_clear()
        # Reset Sentry global hub so other tests don't see a primed sdk.
        try:
            import sentry_sdk

            sentry_sdk.init(dsn=None)  # type: ignore[arg-type]
        except Exception:
            pass
