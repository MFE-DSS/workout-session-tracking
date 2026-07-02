"""Sb_UI_11.1 + Sb_UI_11.2 — tests CLI capture.

Aucun test ne dépend de Playwright installé. Tous les tests utilisent
`--dry-run` ou vérifient le rejet argparse.

Sb_UI_11.2 ajoute des tests pour le support `--runtime-file`.
"""
from __future__ import annotations

import io
import json
import os
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import pytest

from scripts.visual_baseline_capture import (
    _load_runtime_file,
    _resolve_route,
    _resolve_state_file,
    main,
)


class TestDryRun:
    def test_dry_run_p0_lists_all_p0_captures(self, tmp_path, monkeypatch):
        monkeypatch.delenv("AUREN_BASELINE_USERNAME", raising=False)
        monkeypatch.delenv("AUREN_BASELINE_PASSWORD", raising=False)
        out = io.StringIO()
        with redirect_stdout(out):
            rc = main(
                [
                    "--dry-run",
                    "--priority",
                    "P0",
                    "--out-dir",
                    str(tmp_path),
                ]
            )
        assert rc == 0
        text = out.getvalue()
        # 8 P0 entries × 2 viewports = 16 planned
        assert "16 capture(s) planned" in text
        for slug in (
            "home-authenticated",
            "home-no-active-session",
            "session-detail-active",
            "session-detail-done",
            "progression",
            "profile",
            "login",
            "register",
        ):
            assert slug in text, f"P0 dry-run must mention {slug!r}"

    def test_dry_run_does_not_create_output_files(self, tmp_path, monkeypatch):
        monkeypatch.delenv("AUREN_BASELINE_USERNAME", raising=False)
        out_dir = tmp_path / "baseline"
        with redirect_stdout(io.StringIO()):
            rc = main(
                [
                    "--dry-run",
                    "--priority",
                    "P0",
                    "--out-dir",
                    str(out_dir),
                ]
            )
        assert rc == 0
        # Rien ne doit être créé.
        assert not out_dir.exists(), "dry-run must not create output files"

    def test_dry_run_mobile_only(self, tmp_path, monkeypatch):
        monkeypatch.delenv("AUREN_BASELINE_USERNAME", raising=False)
        out = io.StringIO()
        with redirect_stdout(out):
            rc = main(
                [
                    "--dry-run",
                    "--priority",
                    "P0",
                    "--viewport",
                    "mobile",
                    "--out-dir",
                    str(tmp_path),
                ]
            )
        assert rc == 0
        text = out.getvalue()
        # 8 P0 mobile only = 8 planned
        assert "8 capture(s) planned" in text
        assert "/mobile-" in text
        assert "/desktop-" not in text


class TestAntiSecret:
    @pytest.mark.parametrize(
        "forbidden_arg",
        [
            "--password",
            "--password=redacted",
            "--token",
            "--token=redacted",
            "--secret",
            "--basic-auth-password=redacted",
            "--api-key=redacted",
            "--apikey=redacted",
            "-password",
        ],
    )
    def test_forbidden_args_rejected_with_systemexit_2(self, forbidden_arg):
        err = io.StringIO()
        with redirect_stderr(err):
            with pytest.raises(SystemExit) as exc_info:
                main(["--dry-run", forbidden_arg])
        assert exc_info.value.code == 2, "CLI must reject secret-flavored args with exit code 2"
        # Ne pas révéler la valeur dans stderr — juste le nom.
        stderr_text = err.getvalue()
        assert "redacted" not in stderr_text, "CLI must never log arg values"
        assert "forbidden name segment" in stderr_text

    def test_env_vars_never_logged_by_status_line(self, tmp_path, monkeypatch):
        # Set credential-style env vars with a canary value.
        # Only USERNAME/PASSWORD are true credentials; session IDs are
        # public data (they get substituted into URLs deliberately).
        # The canary check therefore focuses on the credential vars.
        canary = "CREDENTIAL_CANARY_MUST_NEVER_LEAK_XYZ_123"
        monkeypatch.setenv("AUREN_BASELINE_USERNAME", canary)
        monkeypatch.setenv("AUREN_BASELINE_PASSWORD", canary)
        # Session IDs use a distinct value so we can separately assert
        # they are NOT treated as secrets and ARE substituted in dry-run.
        session_id_value = "999"
        monkeypatch.setenv("AUREN_BASELINE_ACTIVE_SESSION_ID", session_id_value)
        monkeypatch.setenv("AUREN_BASELINE_DONE_SESSION_ID", session_id_value)

        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = main(
                [
                    "--dry-run",
                    "--priority",
                    "P0",
                    "--out-dir",
                    str(tmp_path),
                ]
            )
        assert rc == 0
        # Credential canary MUST NEVER appear.
        assert canary not in out.getvalue(), (
            "credential canary env value leaked to stdout"
        )
        assert canary not in err.getvalue(), (
            "credential canary env value leaked to stderr"
        )
        # Status line MUST report 'set' vs 'missing'.
        assert "AUREN_BASELINE_USERNAME=<set>" in out.getvalue()
        assert "AUREN_BASELINE_PASSWORD=<set>" in out.getvalue()
        # Session IDs SHOULD be substituted into routes (they are not
        # secrets — they are DB fixture identifiers).
        assert f"/sessions/{session_id_value}" in out.getvalue()

    def test_env_vars_missing_status(self, tmp_path, monkeypatch):
        monkeypatch.delenv("AUREN_BASELINE_USERNAME", raising=False)
        monkeypatch.delenv("AUREN_BASELINE_PASSWORD", raising=False)
        monkeypatch.delenv("AUREN_BASELINE_ACTIVE_SESSION_ID", raising=False)
        monkeypatch.delenv("AUREN_BASELINE_DONE_SESSION_ID", raising=False)

        out = io.StringIO()
        with redirect_stdout(out):
            rc = main(
                [
                    "--dry-run",
                    "--priority",
                    "P0",
                    "--out-dir",
                    str(tmp_path),
                ]
            )
        assert rc == 0
        text = out.getvalue()
        assert "AUREN_BASELINE_USERNAME=<missing>" in text
        assert "AUREN_BASELINE_PASSWORD=<missing>" in text


class TestStrictMode:
    def test_strict_p0_fails_when_active_session_missing(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AUREN_BASELINE_USERNAME", "someuser")
        monkeypatch.setenv("AUREN_BASELINE_PASSWORD", "somepass")
        monkeypatch.delenv("AUREN_BASELINE_ACTIVE_SESSION_ID", raising=False)
        monkeypatch.setenv("AUREN_BASELINE_DONE_SESSION_ID", "42")

        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = main(
                [
                    "--dry-run",
                    "--strict-p0",
                    "--priority",
                    "P0",
                    "--out-dir",
                    str(tmp_path),
                ]
            )
        assert rc == 4, "strict mode must exit 4 when required env vars missing"
        # Aucune valeur env dans stderr.
        assert "someuser" not in err.getvalue()
        assert "somepass" not in err.getvalue()

    def test_strict_p0_passes_when_all_env_set(self, tmp_path, monkeypatch):
        monkeypatch.setenv("AUREN_BASELINE_USERNAME", "u")
        monkeypatch.setenv("AUREN_BASELINE_PASSWORD", "p")
        monkeypatch.setenv("AUREN_BASELINE_ACTIVE_SESSION_ID", "1")
        monkeypatch.setenv("AUREN_BASELINE_DONE_SESSION_ID", "2")

        out = io.StringIO()
        with redirect_stdout(out):
            rc = main(
                [
                    "--dry-run",
                    "--strict-p0",
                    "--priority",
                    "P0",
                    "--out-dir",
                    str(tmp_path),
                ]
            )
        assert rc == 0


class TestPlaywrightNotRequiredForDryRun:
    def test_dry_run_works_without_playwright_import(self, tmp_path, monkeypatch):
        # Empêche l'import de playwright pendant ce test — dry-run doit encore réussir.
        monkeypatch.setitem(sys.modules, "playwright", None)  # type: ignore[arg-type]
        monkeypatch.setitem(sys.modules, "playwright.sync_api", None)  # type: ignore[arg-type]
        out = io.StringIO()
        with redirect_stdout(out):
            rc = main(
                [
                    "--dry-run",
                    "--priority",
                    "P0",
                    "--out-dir",
                    str(tmp_path),
                ]
            )
        assert rc == 0, "dry-run must never import playwright"


# ------- Sb_UI_11.2 : --runtime-file --------------------------------


class TestRuntimeFileLoading:
    def test_load_runtime_none_returns_none(self):
        assert _load_runtime_file(None) is None

    def test_load_runtime_missing_file_exits_5(self, tmp_path):
        with pytest.raises(SystemExit) as exc_info:
            with redirect_stderr(io.StringIO()):
                _load_runtime_file(str(tmp_path / "nope.json"))
        assert exc_info.value.code == 5

    def test_load_runtime_invalid_json_exits_6(self, tmp_path):
        p = tmp_path / "bad.json"
        p.write_text("{{{not json")
        with pytest.raises(SystemExit) as exc_info:
            with redirect_stderr(io.StringIO()):
                _load_runtime_file(str(p))
        assert exc_info.value.code == 6

    @pytest.mark.parametrize(
        "banned",
        ["password", "cookie", "session_token", "secret", "token"],
    )
    def test_load_runtime_banned_key_exits_7(self, tmp_path, banned):
        p = tmp_path / "runtime.json"
        p.write_text(json.dumps({banned: "leak", "base_url": "http://x"}))
        with pytest.raises(SystemExit) as exc_info:
            err = io.StringIO()
            with redirect_stderr(err):
                _load_runtime_file(str(p))
        assert exc_info.value.code == 7

    def test_load_runtime_valid_returns_dict(self, tmp_path):
        p = tmp_path / "runtime.json"
        data = {
            "base_url": "http://127.0.0.1:8000",
            "user": {"id": 1},
            "sessions": {"active": {"id": 42}, "done": {"id": 43}},
            "state_file": "var/visual-baseline/auth-state.json",
        }
        p.write_text(json.dumps(data))
        loaded = _load_runtime_file(str(p))
        assert loaded == data


class TestResolveRoute:
    def _runtime(self, active_id: int = 42, done_id: int = 43) -> dict:
        return {
            "sessions": {
                "active": {"id": active_id},
                "done": {"id": done_id},
            }
        }

    def test_runtime_replaces_active_placeholder(self):
        route = _resolve_route(
            "/sessions/${AUREN_BASELINE_ACTIVE_SESSION_ID}",
            runtime=self._runtime(active_id=99),
        )
        assert route == "/sessions/99"

    def test_runtime_replaces_done_placeholder(self):
        route = _resolve_route(
            "/sessions/${AUREN_BASELINE_DONE_SESSION_ID}",
            runtime=self._runtime(done_id=77),
        )
        assert route == "/sessions/77"

    def test_env_fallback_when_no_runtime(self, monkeypatch):
        monkeypatch.setenv("AUREN_BASELINE_ACTIVE_SESSION_ID", "13")
        route = _resolve_route(
            "/sessions/${AUREN_BASELINE_ACTIVE_SESSION_ID}",
            runtime=None,
        )
        assert route == "/sessions/13"

    def test_runtime_wins_over_env(self, monkeypatch):
        monkeypatch.setenv("AUREN_BASELINE_ACTIVE_SESSION_ID", "13")
        route = _resolve_route(
            "/sessions/${AUREN_BASELINE_ACTIVE_SESSION_ID}",
            runtime=self._runtime(active_id=99),
        )
        assert route == "/sessions/99"

    def test_no_placeholder_pass_through(self):
        assert _resolve_route("/profile") == "/profile"


class TestResolveStateFile:
    def test_explicit_cli_wins(self, tmp_path):
        rt = {"state_file": "runtime-state.json"}
        assert _resolve_state_file("cli-state.json", rt) == "cli-state.json"

    def test_runtime_used_when_no_cli(self):
        rt = {"state_file": "runtime-state.json"}
        assert _resolve_state_file(None, rt) == "runtime-state.json"

    def test_none_when_both_absent(self):
        assert _resolve_state_file(None, None) is None
        assert _resolve_state_file(None, {}) is None


class TestRuntimeFileInDryRun:
    def _write_runtime(self, tmp_path) -> Path:
        p = tmp_path / "runtime.json"
        p.write_text(json.dumps({
            "base_url": "http://127.0.0.1:8000",
            "user": {"id": 1},
            "sessions": {"active": {"id": 42}, "done": {"id": 43}},
            "state_file": str(tmp_path / "auth-state.json"),
        }))
        return p

    def test_dry_run_with_runtime_resolves_session_ids(self, tmp_path, monkeypatch):
        monkeypatch.delenv("AUREN_BASELINE_USERNAME", raising=False)
        monkeypatch.delenv("AUREN_BASELINE_PASSWORD", raising=False)
        monkeypatch.delenv("AUREN_BASELINE_ACTIVE_SESSION_ID", raising=False)
        monkeypatch.delenv("AUREN_BASELINE_DONE_SESSION_ID", raising=False)
        runtime_path = self._write_runtime(tmp_path)

        out = io.StringIO()
        with redirect_stdout(out):
            rc = main([
                "--dry-run",
                "--priority", "P0",
                "--out-dir", str(tmp_path / "out"),
                "--runtime-file", str(runtime_path),
            ])
        assert rc == 0
        text = out.getvalue()
        assert "Runtime source: runtime.json" in text
        assert "route=/sessions/42" in text
        assert "route=/sessions/43" in text

    def test_strict_p0_relaxed_when_runtime_provided(self, tmp_path, monkeypatch):
        # Env vars totally absent, but runtime file provides IDs → strict passes.
        monkeypatch.delenv("AUREN_BASELINE_USERNAME", raising=False)
        monkeypatch.delenv("AUREN_BASELINE_PASSWORD", raising=False)
        monkeypatch.delenv("AUREN_BASELINE_ACTIVE_SESSION_ID", raising=False)
        monkeypatch.delenv("AUREN_BASELINE_DONE_SESSION_ID", raising=False)
        runtime_path = self._write_runtime(tmp_path)

        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = main([
                "--dry-run",
                "--strict-p0",
                "--priority", "P0",
                "--out-dir", str(tmp_path / "out"),
                "--runtime-file", str(runtime_path),
            ])
        # strict-p0 should NOT fail when runtime provides the IDs.
        assert rc == 0, f"strict-p0 with runtime file should pass. stderr={err.getvalue()}"

    def test_missing_runtime_file_exits_5(self, tmp_path):
        with pytest.raises(SystemExit) as exc_info:
            with redirect_stderr(io.StringIO()):
                main([
                    "--dry-run",
                    "--priority", "P0",
                    "--out-dir", str(tmp_path),
                    "--runtime-file", str(tmp_path / "does-not-exist.json"),
                ])
        assert exc_info.value.code == 5
