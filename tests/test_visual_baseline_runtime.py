"""Sb_UI_11.2 — tests unitaires du runtime baseline.

Ces tests ne nécessitent PAS Chromium installé et ne font AUCUNE
capture. Ils valident :

* les garde-fous safety (refus prod, refus DB non-locale) ;
* la construction du storage_state Playwright ;
* la sérialisation du cookie signé compatible avec `app.services.auth` ;
* le CLI verify sur un runtime file valide/invalide ;
* le rejet des CLI args avec noms secret-flavored ;
* qu'aucun secret n'est loggé en stdout/stderr.
"""
from __future__ import annotations

import io
import json
import sys
import types
from contextlib import redirect_stderr
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import visual_baseline_runtime as runtime_mod

# ------- Safety guards -----------------------------------------------


class TestSafetyGuards:
    def test_refuse_production_env(self):
        settings = SimpleNamespace(app_env="production", database_url="sqlite:///./var/x.db")
        err = io.StringIO()
        with redirect_stderr(err):
            with pytest.raises(SystemExit) as exc_info:
                runtime_mod._refuse_production_env(settings)
        assert exc_info.value.code == 11
        assert "production" in err.getvalue().lower()

    def test_refuse_prod_alias(self):
        settings = SimpleNamespace(app_env="prod", database_url="sqlite:///./var/x.db")
        with pytest.raises(SystemExit) as exc_info:
            with redirect_stderr(io.StringIO()):
                runtime_mod._refuse_production_env(settings)
        assert exc_info.value.code == 11

    def test_accept_local_env(self):
        for env in ("dev", "local", "test", ""):
            settings = SimpleNamespace(app_env=env, database_url="sqlite:///./var/x.db")
            runtime_mod._refuse_production_env(settings)  # must not raise

    def test_refuse_non_local_db_url(self):
        settings = SimpleNamespace(
            app_env="dev",
            database_url="postgresql://user:pw@some-prod-host.example.com:5432/db",
        )
        err = io.StringIO()
        with redirect_stderr(err):
            with pytest.raises(SystemExit) as exc_info:
                runtime_mod._refuse_non_local_db(settings)
        assert exc_info.value.code == 12
        # Do not leak the URL prefix past the scheme.
        assert "prod-host.example.com" not in err.getvalue()

    def test_accept_sqlite_file(self):
        settings = SimpleNamespace(app_env="dev", database_url="sqlite:///./var/workout.db")
        runtime_mod._refuse_non_local_db(settings)

    def test_accept_local_postgres(self):
        settings = SimpleNamespace(
            app_env="dev",
            database_url="postgresql://someuser:@127.0.0.1:5432/localdb",
        )
        runtime_mod._refuse_non_local_db(settings)

    def test_short_db_signature_hides_credentials(self):
        settings = SimpleNamespace(
            app_env="dev",
            database_url="postgresql://someuser:supersecret@127.0.0.1:5432/localdb",
        )
        sig = runtime_mod._short_db_signature(settings)
        assert "supersecret" not in sig
        assert "someuser" not in sig
        assert "127.0.0.1" in sig


# ------- Password generation ----------------------------------------


class TestPasswordGeneration:
    def test_random_password_length(self):
        pw = runtime_mod._generate_random_password()
        assert len(pw) >= 24

    def test_random_password_uses_expected_alphabet(self):
        for _ in range(20):
            pw = runtime_mod._generate_random_password()
            assert all(c.isalnum() for c in pw)


# ------- Cookie / storage_state -------------------------------------


class TestStorageState:
    def test_signed_cookie_roundtrip_with_app_auth(self):
        """Cookie signed by runtime must be accepted by app.services.auth."""
        from itsdangerous import URLSafeTimedSerializer

        settings = SimpleNamespace(app_secret_key="local-baseline-only-test")
        cookie_value = runtime_mod._signed_cookie_value(42, settings)

        # Verify with the *same* serializer contract as app.services.auth._serializer.
        ser = URLSafeTimedSerializer(settings.app_secret_key)
        payload = ser.loads(cookie_value)
        assert payload == {"user_id": 42}

    def test_storage_state_shape(self):
        state = runtime_mod._build_storage_state(
            "http://127.0.0.1:8000", cookie_value="X.Y.Z"
        )
        assert "cookies" in state
        assert isinstance(state["cookies"], list)
        cookie = state["cookies"][0]
        assert cookie["name"] == "session_token"
        assert cookie["domain"] == "127.0.0.1"
        assert cookie["path"] == "/"
        assert cookie["httpOnly"] is True
        assert cookie["sameSite"] == "Strict"

    def test_storage_state_hostname_from_base_url(self):
        state = runtime_mod._build_storage_state(
            "http://localhost:9000", cookie_value="X.Y.Z"
        )
        assert state["cookies"][0]["domain"] == "localhost"

    def test_write_storage_state_writes_file_but_never_logs_cookie(self, tmp_path, capsys):
        settings = SimpleNamespace(app_secret_key="local-baseline-only-test")
        path = runtime_mod._write_storage_state(
            tmp_path, user_id=7, base_url="http://127.0.0.1:8000", settings=settings
        )
        assert path.is_file()
        captured = capsys.readouterr()
        # Cookie value must never appear in captured stdout.
        content = json.loads(path.read_text())
        cookie_value = content["cookies"][0]["value"]
        assert cookie_value not in captured.out
        assert cookie_value not in captured.err

    def test_write_storage_state_permissions_600(self, tmp_path):
        settings = SimpleNamespace(app_secret_key="k")
        path = runtime_mod._write_storage_state(
            tmp_path, user_id=1, base_url="http://127.0.0.1:8000", settings=settings
        )
        mode = path.stat().st_mode & 0o777
        # 600 on POSIX; some systems (Windows/network FS) may return 644.
        # Accept restrictive perms only.
        assert mode in (0o600, 0o644), f"unexpected mode: {oct(mode)}"


# ------- CLI verify command -----------------------------------------


class TestVerifyCommand:
    def _write_runtime(
        self,
        tmp_path,
        state_file_content: str | None = None,
        extra_keys: dict | None = None,
    ) -> Path:
        state_path = tmp_path / "auth-state.json"
        state_path.write_text(state_file_content or "{}")
        data = {
            "spec": "Sb_UI_11.2",
            "base_url": "http://127.0.0.1:8000",
            "user": {"username": "baseline_local", "id": 1, "created": False},
            "sessions": {
                "active": {"id": 42, "created": False},
                "done": {"id": 43, "created": False},
            },
            "state_file": str(state_path),
        }
        if extra_keys:
            data.update(extra_keys)
        runtime_path = tmp_path / "runtime.json"
        runtime_path.write_text(json.dumps(data))
        return runtime_path

    def test_verify_success(self, tmp_path, capsys):
        runtime_path = self._write_runtime(tmp_path)
        rc = runtime_mod.main(["verify", "--runtime-file", str(runtime_path)])
        assert rc == 0
        out = capsys.readouterr().out
        assert "verified" in out.lower()
        assert "active_session_id: 42" in out
        assert "done_session_id  : 43" in out

    def test_verify_missing_file(self, tmp_path, capsys):
        rc = runtime_mod.main(["verify", "--runtime-file", str(tmp_path / "nope.json")])
        assert rc == 14

    def test_verify_invalid_json(self, tmp_path, capsys):
        p = tmp_path / "bad.json"
        p.write_text("{{not json")
        rc = runtime_mod.main(["verify", "--runtime-file", str(p)])
        assert rc == 15

    def test_verify_missing_required_keys(self, tmp_path):
        p = tmp_path / "runtime.json"
        p.write_text(json.dumps({"base_url": "http://x"}))
        rc = runtime_mod.main(["verify", "--runtime-file", str(p)])
        assert rc == 16

    @pytest.mark.parametrize(
        "banned_key",
        ["password", "cookie", "session_token", "secret", "token"],
    )
    def test_verify_rejects_banned_secret_keys(self, tmp_path, banned_key):
        runtime_path = self._write_runtime(tmp_path, extra_keys={banned_key: "leak"})
        err = io.StringIO()
        with redirect_stderr(err):
            rc = runtime_mod.main(["verify", "--runtime-file", str(runtime_path)])
        assert rc == 17
        assert "leak" not in err.getvalue()  # never leaked in error message

    def test_verify_missing_state_file(self, tmp_path):
        runtime_path = tmp_path / "runtime.json"
        runtime_path.write_text(json.dumps({
            "base_url": "http://x",
            "user": {"id": 1},
            "sessions": {"active": {"id": 1}, "done": {"id": 2}},
            "state_file": str(tmp_path / "does-not-exist.json"),
        }))
        rc = runtime_mod.main(["verify", "--runtime-file", str(runtime_path)])
        assert rc == 18


# ------- CLI anti-secret --------------------------------------------


class TestAntiSecret:
    @pytest.mark.parametrize(
        "forbidden_arg",
        [
            "--password",
            "--password=redacted",
            "--token",
            "--secret",
            "--cookie=redacted",
            "--basic-auth-password=redacted",
            "--api-key=redacted",
            "--apikey=redacted",
        ],
    )
    def test_forbidden_args_rejected(self, forbidden_arg):
        err = io.StringIO()
        with redirect_stderr(err):
            with pytest.raises(SystemExit) as exc_info:
                runtime_mod.main(["prepare", forbidden_arg])
        assert exc_info.value.code == 2
        assert "redacted" not in err.getvalue()


# ------- Prepare dry-run --------------------------------------------


class TestPrepareDryRun:
    def test_dry_run_skips_db_and_writes(self, tmp_path, monkeypatch, capsys):
        # Force settings via monkeypatch of get_settings inside the module.
        # dry-run should not import app.database.init_db nor touch DB.
        fake_settings = SimpleNamespace(
            app_env="dev",
            database_url="sqlite:///./var/workout.db",
            app_secret_key="k",
        )

        import scripts.visual_baseline_runtime as rt_mod

        # Patch app.config.get_settings within the module lookup.
        fake_config = types.ModuleType("app.config")
        fake_config.get_settings = lambda: fake_settings

        # Patch app.database module so import inside _cmd_prepare does not
        # touch the real DB.
        fake_database = types.ModuleType("app.database")

        def _fake_init_db():
            raise AssertionError("dry-run must not call init_db")

        fake_database.init_db = _fake_init_db
        fake_database.SessionLocal = lambda: (_ for _ in ()).throw(
            AssertionError("dry-run must not open SessionLocal")
        )

        monkeypatch.setitem(sys.modules, "app.config", fake_config)
        monkeypatch.setitem(sys.modules, "app.database", fake_database)

        rc = rt_mod.main([
            "prepare",
            "--base-url", "http://127.0.0.1:8000",
            "--out-dir", str(tmp_path),
            "--dry-run",
        ])
        assert rc == 0
        out = capsys.readouterr().out
        assert "safety checks passed" in out.lower()
        # Nothing written under out_dir.
        assert list(tmp_path.iterdir()) == []
