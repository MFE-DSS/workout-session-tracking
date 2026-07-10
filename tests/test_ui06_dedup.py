"""Sx_UI_06 / Sb_UI_06.1 — information density dedup (exercise card).

Locks the de-densification of the exercise card, per the accepted spec
(docs/strategy/Sx_UI_06_INFO_DENSITY_DEDUP_SPEC.md):

- **D1** : the previous-session load (« Dernière fois ») is no longer shown on
  the ACTIVE card — its info lives once in the console « Référence précédente »,
  closest to the input cells. It STILL renders on non-active cards (no info loss).
- **D2** : the target (« Cible ») no longer has its own head block
  (`exercise-card__scheme`) nor its own console row; the target suggestion lives
  ONLY as the input placeholder.

Guarantees the redundancy is gone WITHOUT weakening the logging contract
(input names, form, no-JS) and WITHOUT losing information on non-active cards.
"""
from __future__ import annotations

import re


def _new_session(client, slug: str = "push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    m = re.match(r"/sessions/(\d+)", r.headers["location"])
    return int(m.group(1))


def _body(client) -> str:
    sid = _new_session(client)
    r = client.get(f"/sessions/{sid}", follow_redirects=False)
    assert r.status_code == 200, r.text[:300]
    return r.text


# ───────── D1 : previous load — active vs non-active ─────────


def test_active_card_has_no_last_time_block(client):
    """The active card carries the previous load ONLY via the console
    « Référence précédente », not the redundant « Dernière fois » head block."""
    body = _body(client)
    # console reference exists (previous load surface on the active card)
    assert "session-focus__console-ref--prev" in body
    assert "Référence précédente" in body


def test_last_time_block_still_present_on_non_active_cards(client):
    """No info loss: non-active cards keep « Dernière fois » (they have no
    console). A fresh session has 1 active + N-1 non-active cards, so the
    block still renders at least once."""
    body = _body(client)
    assert "Dernière fois" in body  # non-active cards keep it


def test_previous_load_not_duplicated_on_active_card(client):
    """The « Référence précédente » console row is the single home of the
    previous load near the inputs; the console does not also render a
    « Dernière fois » label inside itself."""
    body = _body(client)
    # console block present…
    assert "session-focus__console-refs" in body
    # …and the reference label used in the console is the console one.
    assert "Référence précédente" in body


# ───────── D2 : target lives only in the input placeholder ─────────


def test_scheme_head_block_removed(client):
    body = _body(client)
    assert "exercise-card__scheme" not in body


def test_target_console_row_removed(client):
    body = _body(client)
    assert "session-focus__console-ref--target" not in body
    assert "Objectif à qualifier" not in body


def test_target_lives_in_input_placeholder(client):
    """The target suggestion survives as the input placeholder (kg / reps or
    an overload suggestion), closest to the action."""
    body = _body(client)
    assert 'placeholder="kg"' in body or 'placeholder="reps"' in body


# ───────── logging contract preserved (no-JS, input names) ─────────


def test_logging_input_names_unchanged(client):
    body = _body(client)
    assert "weight_kg" in body and "reps" in body


def test_console_still_present(client):
    body = _body(client)
    assert "session-focus__console" in body
    assert "Référence précédente" in body


# ───────── Sb_UI_06.2 : Worked Area density cleanup (D3) ─────────


def _known_body(client) -> str:
    """Render a session whose active exercise is a KNOWN catalog exercise
    (maps to real zones) so the Worked Area shows primary + assistants."""
    from datetime import UTC, datetime

    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession
    from app.models.user import User

    with SessionLocal() as db:
        uid = db.query(User).first().id
        s = WorkoutSession(
            user_id=uid, template_slug_snapshot="wa", template_name_snapshot="wa",
            started_at=datetime.now(UTC), status="in_progress",
        )
        se = SessionExercise(
            exercise_code_snapshot="E1",
            exercise_name_snapshot="Chest Press machine",  # → pecs / triceps
            position=1,
        )
        se.set_logs.append(SetLog(kind="work", set_index=1, completed=False))
        s.session_exercises.append(se)
        db.add(s)
        db.commit()
        db.refresh(s)
        sid = s.id
    r = client.get(f"/sessions/{sid}", follow_redirects=False)
    assert r.status_code == 200
    return r.text


def test_worked_area_chip_removed(client):
    """The decorative zone chip (raw code) is gone; the text label remains."""
    body = _known_body(client)
    assert "session-focus__body-zone-chip" not in body
    assert "Pectoraux" in body  # readable primary label kept


def test_worked_area_primary_shown_once(client):
    """Known exercise: the primary zone label appears once in the Worked Area
    (no chip + label duplication)."""
    body = _known_body(client)
    assert body.count("Pectoraux") == 1


def test_worked_area_assistants_shown_when_present(client):
    body = _known_body(client)
    assert "Triceps" in body
    assert "session-focus__worked-area-row--secondary" in body


def test_worked_area_no_empty_qualifier_repetition_on_known(client):
    """Known exercise with real zones: « À qualifier » must not appear at all
    in the Worked Area (no empty stabilizer / assistants slot)."""
    body = _known_body(client)
    assert "À qualifier" not in body
    assert "session-focus__worked-area-row--stabilizer" not in body


def _unknown_body(client) -> str:
    """Render a session whose active exercise is UNKNOWN (no mapping, no
    atlas) so the Worked Area shows the qualifier fallback."""
    from datetime import UTC, datetime

    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession
    from app.models.user import User

    with SessionLocal() as db:
        uid = db.query(User).first().id
        s = WorkoutSession(
            user_id=uid, template_slug_snapshot="wa-u", template_name_snapshot="wa-u",
            started_at=datetime.now(UTC), status="in_progress",
        )
        se = SessionExercise(
            exercise_code_snapshot="E1",
            exercise_name_snapshot="Zzz mouvement non répertorié",  # → unknown
            position=1,
        )
        se.set_logs.append(SetLog(kind="work", set_index=1, completed=False))
        s.session_exercises.append(se)
        db.add(s)
        db.commit()
        db.refresh(s)
        sid = s.id
    r = client.get(f"/sessions/{sid}", follow_redirects=False)
    assert r.status_code == 200
    return r.text


def test_worked_area_unknown_qualifier_once(client):
    """Unknown exercise: « À qualifier » renders exactly once (carried by the
    primary row); empty assistant/stabilizer slots are not rendered."""
    body = _unknown_body(client)
    assert body.count("À qualifier") == 1
    assert "session-focus__worked-area-row--secondary" not in body
    assert "session-focus__worked-area-row--stabilizer" not in body


def test_worked_area_resolution_path_in_data_only(client):
    """resolution_path stays a data-* attribute (debug/smoke); it is never a
    visible user badge (« db_lookup » / « substring_fallback »)."""
    body = _known_body(client)
    assert "data-resolution-path=" in body
    # not surfaced as visible technical text
    assert ">db_lookup<" not in body
    assert ">substring_fallback<" not in body


def test_worked_area_note_short_non_medical(client):
    body = _body(client)
    assert "session-focus__worked-area-note" in body
    assert "non médical" in body
