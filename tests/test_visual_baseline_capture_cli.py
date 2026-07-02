"""Sb_UI_11.1 — tests CLI capture (dry-run, anti-secret, strict mode).

Aucun test ne dépend de Playwright installé. Tous les tests utilisent
`--dry-run` ou vérifient le rejet argparse.
"""
from __future__ import annotations

import io
import os
import sys
from contextlib import redirect_stderr, redirect_stdout

import pytest

from scripts.visual_baseline_capture import main


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
        # Set env vars with a canary value; assert canary NEVER appears in stdout.
        canary = "CANARY_MUST_NEVER_LEAK_XYZ_123"
        monkeypatch.setenv("AUREN_BASELINE_USERNAME", canary)
        monkeypatch.setenv("AUREN_BASELINE_PASSWORD", canary)
        monkeypatch.setenv("AUREN_BASELINE_ACTIVE_SESSION_ID", canary)
        monkeypatch.setenv("AUREN_BASELINE_DONE_SESSION_ID", canary)

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
        assert canary not in out.getvalue(), "canary env value leaked to stdout"
        assert canary not in err.getvalue(), "canary env value leaked to stderr"
        # But status line MUST report 'set' vs 'missing'.
        assert "AUREN_BASELINE_USERNAME=<set>" in out.getvalue()
        assert "AUREN_BASELINE_PASSWORD=<set>" in out.getvalue()

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
