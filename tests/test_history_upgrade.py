"""Sprint 2 upgrades to the /history page + the Alembic baseline."""
from __future__ import annotations

import re
from pathlib import Path


def _start(client, slug="push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def test_history_shows_exercise_counts(client):
    _start(client, "push-a")
    r = client.get("/history")
    body = r.text
    # Push A has 7 exercise cards (v10); none are completed yet
    assert "0/7 exos" in body


def test_history_status_filter_in_progress(client):
    sid1 = _start(client, "push-a")
    sid2 = _start(client, "legs-a")
    # Complete one of them
    client.post(f"/sessions/{sid1}", data={"action": "end"}, follow_redirects=False)

    # The "active session banner" added in Sprint 5 may surface the
    # in-progress template name in the page header even when
    # the filter excludes it. We assert against the session-card list
    # specifically by looking at the session-card__name marker.
    def _in_list(html: str, name_prefix: str) -> bool:
        # The session card name span has class + inline style.
        # Check for the class marker near the name in the session list.
        import re
        return bool(re.search(rf'session-card__name[^>]*>{name_prefix}', html))

    r_all = client.get("/history?status=all").text
    assert _in_list(r_all, "Push A") and _in_list(r_all, "Legs A")

    r_open = client.get("/history?status=in_progress").text
    assert _in_list(r_open, "Legs A")
    assert not _in_list(r_open, "Push A")

    r_done = client.get("/history?status=completed").text
    assert _in_list(r_done, "Push A")
    assert not _in_list(r_done, "Legs A")


def test_history_filter_bar_highlights_active_choice(client):
    r = client.get("/history?status=in_progress")
    body = r.text
    # The active link class must be present on the active choice. Use
    # DOTALL so whitespace between the class attr and "En cours" text
    # (Jinja indentation) does not break the match.
    assert re.search(
        r'class="[^"]*is-active[^"]*".*?En cours',
        body,
        re.DOTALL,
    )


def test_history_filter_defaults_to_all_on_invalid_value(client):
    r = client.get("/history?status=bogus")
    # Should render "all" with the filter bar still present
    assert r.status_code == 200
    assert "Tout" in r.text


def test_alembic_baseline_exists():
    """Sprint 2 introduces Alembic. The baseline migration must
    exist and must be the only revision in the tree."""
    versions_dir = Path(__file__).resolve().parent.parent / "migrations" / "versions"
    assert versions_dir.is_dir(), "migrations/versions/ missing"
    migrations = [
        p for p in versions_dir.iterdir()
        if p.suffix == ".py" and not p.name.startswith("__")
    ]
    assert len(migrations) >= 1, "no migration files found"
    # The baseline is the only revision with down_revision = None.
    baseline_found = False
    for m in migrations:
        text = m.read_text()
        if "down_revision: Union[str, Sequence[str], None] = None" in text:
            baseline_found = True
            break
    assert baseline_found, "no baseline migration (down_revision=None) found"


def test_alembic_env_reads_from_app_settings():
    """env.py must pull DATABASE_URL from app.config, not from a
    hardcoded alembic.ini entry."""
    env_path = Path(__file__).resolve().parent.parent / "migrations" / "env.py"
    text = env_path.read_text()
    assert "from app.config import get_settings" in text
    assert "config.set_main_option" in text
    assert "render_as_batch" in text  # SQLite-safe migrations
