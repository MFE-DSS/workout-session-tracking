"""Tests for scripts/reco_calibration_report.py (Sb_13)."""
from __future__ import annotations

import os
import subprocess
import sys
from datetime import UTC
from pathlib import Path

from tests.helpers import get_test_user_id

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _run(args: list[str]) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    # Inherit DATABASE_URL from the test fixture so the script hits the
    # same DB the client populated.
    return subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts/reco_calibration_report.py")] + args,
        cwd=str(PROJECT_ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_script_runs_on_empty_db(client):
    r = _run(["--days", "7"])
    assert r.returncode == 0, r.stderr
    assert "SPIGNOS" in r.stdout
    assert "reco_acceptance_rate" in r.stdout
    assert "alt_click_rate" in r.stdout
    assert "bypass_rate" in r.stdout


def test_script_counts_creation_sources(client):
    """Seed 3 sessions with different creation_source values and verify
    the breakdown lines show the right counts."""
    import re

    # Mix of sources + one session with no source.
    for slug, src in [
        ("push-a", "reco_top"),
        ("pull-a", "reco_top"),
        ("legs-a", "launcher"),
        ("push-b", None),
    ]:
        data = {"template_slug": slug}
        if src is not None:
            data["creation_source"] = src
        r = client.post("/sessions", data=data, follow_redirects=False)
        # Immediately complete so the session lands in the window.
        sid = int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))
        # Mark completed via direct DB touch — simpler than running the
        # full feedback form.
        from datetime import datetime

        from app.database import SessionLocal
        from app.models.session import WorkoutSession

        with SessionLocal() as db:
            s = db.get(WorkoutSession, sid)
            s.status = "completed"
            s.ended_at = datetime.now(UTC)
            s.concentration = "high"
            s.global_state = "good"
            db.commit()

    r = _run(["--days", "7"])
    assert r.returncode == 0, r.stderr
    out = r.stdout
    # Expect 4 sessions in window total.
    assert "Sessions (window)     : 4" in out
    # reco_top appears twice.
    assert "reco_top  :    2" in out
    # launcher once.
    assert "launcher  :    1" in out
    # One unknown source (pre-Sb_13 style fallback).
    assert "with unknown source : 1" in out


def test_script_with_user_filter_mentions_phrases_section(client):
    """Running with --user-id should activate the phrase sampling block,
    even if empty."""
    uid = get_test_user_id()
    r = _run(["--days", "7", "--user-id", str(uid)])
    assert r.returncode == 0, r.stderr
    assert "Top phrases" in r.stdout
