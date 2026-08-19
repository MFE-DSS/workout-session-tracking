"""Sb_32.next — Worked Area consumes body_map_descriptor (Sx_32).

First visible consumer of ``body_map_descriptor``: the Focus Mode Worked
Area now renders the body zone actually resolved by the Sx_32 mapping
(primary + secondary labels), with an explicit "À qualifier" state for
unknown exercises — SSR, no-JS, no medical claim, no consumer/model change.

Asserts:
- the session_detail route injects a body_map_descriptor per session exercise
- a known exercise renders its real primary zone label
- a known exercise with secondaries renders the assistants labels
- an unknown exercise renders "À qualifier"
- no forbidden medical wording
- content is present in the initial HTML (no-JS)
- Focus Mode contracts preserved (logging inputs, rest timer, substitution)
- the body_map_descriptor / muscle_mapping services are untouched by this sprint
- no model / migration / schema file touched
- Auren Terminal worked-area classes preserved
- accessibility: named section + textual labels (not color-only)
"""
from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXERCISE_CARD = ROOT / "app" / "templates" / "_partials" / "exercise_card.html"

# Affirmative medical claims that must never appear. NB: the prudent
# disclaimer "non diagnostic médical" is explicitly WANTED (it negates a
# medical claim), so we do not blacklist the bare "diagnostic médical".
FORBIDDEN_MEDICAL = [
    "muscle activé",
    "activation musculaire",
    "corrige ta posture",
    "biomécanique certifiée",
]


def _seed(db, user_id, names: list[str]):
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot="worked-area-desc",
        template_name_snapshot="Worked area descriptor test",
        started_at=datetime.now(UTC),
        status="in_progress",
    )
    for i, name in enumerate(names):
        se = SessionExercise(
            exercise_code_snapshot=f"E{i + 1}",
            exercise_name_snapshot=name,
            position=i + 1,
        )
        se.set_logs.append(
            SetLog(kind="work", set_index=1, weight_kg=None, reps=None, completed=False)
        )
        s.session_exercises.append(se)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def _render(client, session_id: int) -> str:
    r = client.get(f"/sessions/{session_id}", follow_redirects=False)
    assert r.status_code == 200, r.text[:400]
    return r.text


def _db(client):
    from app.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    user = db.query(User).first()
    return db, user.id


# ───────── 1. route injects descriptor ─────────


def test_route_injects_body_map_descriptor(client):
    """The route must build a body_map_descriptor per exercise and pass it
    to the template context (resolution path attribute is rendered)."""
    db, uid = _db(client)
    s = _seed(db, uid, ["Chest Press machine"])
    db.close()
    html = _render(client, s.id)
    assert "data-resolution-path=" in html


# ───────── 2-3. known exercise → real zones ─────────


def test_known_exercise_renders_primary_zone_label(client):
    db, uid = _db(client)
    s = _seed(db, uid, ["Chest Press machine"])  # → pecs / Pectoraux
    db.close()
    html = _render(client, s.id)
    assert "Pectoraux" in html
    assert "Zone travaillée" in html


def test_known_exercise_renders_secondary_assistants(client):
    db, uid = _db(client)
    s = _seed(db, uid, ["Chest Press machine"])  # secondary → triceps / Triceps
    db.close()
    html = _render(client, s.id)
    assert "Triceps" in html
    assert "Assistants" in html


# ───────── 4. unknown → À qualifier ─────────


def test_unknown_exercise_renders_a_qualifier(client):
    db, uid = _db(client)
    s = _seed(db, uid, ["Exercice totalement inconnu zzz"])
    db.close()
    html = _render(client, s.id)
    assert "À qualifier" in html


# ───────── 5. no medical wording ─────────


def test_no_forbidden_medical_wording(client):
    db, uid = _db(client)
    s = _seed(db, uid, ["Chest Press machine", "Exercice inconnu zzz"])
    db.close()
    html = _render(client, s.id).lower()
    for term in FORBIDDEN_MEDICAL:
        assert term.lower() not in html, term
    # prudent non-medical note is present (Sb_UI_06.2: shortened microcopy
    # « Estimation — repère, non médical »).
    assert "non médical" in html


# ───────── 6. no-JS: content in initial HTML ─────────


def test_worked_area_present_in_initial_html_no_js(client):
    db, uid = _db(client)
    s = _seed(db, uid, ["Chest Press machine"])
    db.close()
    html = _render(client, s.id)
    # server-rendered, no data fetch needed
    assert "session-focus__worked-area" in html
    assert "Pectoraux" in html


# ───────── 7. Focus Mode contracts preserved ─────────


def test_focus_mode_contracts_preserved(client):
    db, uid = _db(client)
    s = _seed(db, uid, ["Chest Press machine"])
    db.close()
    html = _render(client, s.id)
    # logging console still present (active card cockpit)
    # MIGRÉ — la console devient `.console` / `.console__band`.
    assert 'class="console"' in html
    assert "weight_kg" in html and "reps" in html  # set logging inputs
    # worked area list rows still present
    assert "session-focus__worked-area-list" in html
    # rest timer contract preserved (data-* attributes)
    # MIGRÉ — le minuteur n'existe QUE dans l'état `REST` (`§7.2`), ce qui
    # est la correction du défaut `D3`. Hors repos, son absence EST le
    # contrat. La commande dominante, elle, est toujours là.
    assert "data-rest-display" not in html
    assert "dock__cmd" in html


# ───────── 8-10. isolation (services / models untouched) ─────────


def _changed() -> list[str]:
    out = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=str(ROOT), capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    return [p.strip() for p in out if p.strip()]


def test_body_map_descriptor_service_untouched():
    assert "app/services/body_map_descriptor.py" not in _changed()


def test_muscle_mapping_untouched():
    assert "app/services/muscle_mapping.py" not in _changed()


def test_no_model_migration_schema_touched():
    for p in _changed():
        assert not p.startswith("app/models/"), p
        assert not p.startswith("migrations/"), p
        assert p != "data/schema_snapshot.sql", p


# ───────── 11-12. Auren Terminal classes + a11y ─────────


def test_auren_terminal_worked_area_classes_preserved():
    src = EXERCISE_CARD.read_text(encoding="utf-8")
    # Sb_UI_06.2 — the decorative `body-zone-chip` (raw code, aria-hidden,
    # redundant with the text label) is removed by the density cleanup. The
    # structural Auren Terminal classes remain.
    for cls in (
        "session-focus__worked-area",
        "session-focus__worked-area-row--primary",
        "session-focus__worked-area-row--secondary",
    ):
        assert cls in src, cls
    assert "session-focus__body-zone-chip" not in src  # decorative chip removed


def test_worked_area_accessible_named_section(client):
    db, uid = _db(client)
    s = _seed(db, uid, ["Chest Press machine"])
    db.close()
    html = _render(client, s.id)
    # section carries an aria-label and textual role labels (not color-only)
    assert 'aria-label="Zone travaillée estimée"' in html
    assert "Principal" in html
    assert "Assistants" in html


# ───────── 13. text smoke on active session ─────────


def test_text_smoke_active_session_renders_active_zone(client):
    """Only the ACTIVE card renders the cockpit Worked Area (Sx_UI_04.3
    contract). The active exercise (first non-completed) shows its real
    resolved zone; the non-active one is compacted (no worked area)."""
    db, uid = _db(client)
    s = _seed(db, uid, ["Chest Press machine", "Curl incliné haltères"])
    db.close()
    html = _render(client, s.id)
    # active = first exercise → Pectoraux rendered in the worked area
    assert "Pectoraux" in html
    assert html.count("session-focus__worked-area ") == 1  # active card only


# ───────── 14. fallback when descriptor absent/unknown ─────────


def test_fallback_unknown_is_clean_not_anxious(client):
    db, uid = _db(client)
    s = _seed(db, uid, ["Zzz mouvement non répertorié"])
    db.close()
    html = _render(client, s.id)
    # unknown renders the neutral qualifier, still a proper worked-area slot
    assert "À qualifier" in html
    assert "session-focus__worked-area" in html
