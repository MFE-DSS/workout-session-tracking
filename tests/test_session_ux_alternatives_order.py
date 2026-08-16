"""Sb_SESSION_UX_01.2b (F1) — Alternatives drawer below the console.

The "Adapter l'exercice" substitution drawer is moved below the set-logging
console (order: worked-area → console → alternatives → cues). Purely
structural: the block content (radios name="substituted_name", N1/N2/N3,
legacy fallback, `elif se.substituted_name`, same POST form) is byte-identical;
only its position changed.

Template-only, no-JS, no route/service/data/model change.
"""
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXERCISE_CARD = ROOT / "app" / "templates" / "_partials" / "exercise_card.html"
JS_DIR = ROOT / "app" / "static" / "js"


def _seed(db, user_id, n=2):
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot="alts-order",
        template_name_snapshot="Alternatives order test",
        started_at=datetime.now(UTC),
        status="in_progress",
    )
    for i in range(n):
        se = SessionExercise(
            exercise_code_snapshot=f"E{i + 1}",
            exercise_name_snapshot=f"Exercise {i + 1}",
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


def _body(client, n=2):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seed(db, user.id, n=n)
        sid = s.id
    r = client.get(f"/sessions/{sid}", follow_redirects=False)
    assert r.status_code == 200, r.text[:400]
    return r.text


# ───────── order in the template source ─────────
# (synthetic exercises have no computed substitutions, so the rendered drawer
#  may be absent; order is asserted on the template source where the block
#  literally lives.)


def _src():
    return EXERCISE_CARD.read_text(encoding="utf-8")


def test_console_before_alternatives_in_source():
    src = _src()
    console = src.find("session-focus__console-list")
    alts = src.find('session-focus__alternatives"')
    assert console != -1 and alts != -1
    assert console < alts, "console must come before the alternatives drawer"


def test_alternatives_before_cues_in_source():
    src = _src()
    alts = src.find('session-focus__alternatives"')
    cues = src.find('session-focus__cues"')
    assert alts != -1 and cues != -1
    assert alts < cues, "alternatives drawer must come before the cues block"


def test_console_before_full_worked_area_in_source():
    """Sb_UIV2_SESSION_FOCUS_02 — deuxième exemplaire de la même supersession.

    ANCIEN CONTRAT : `assert worked < console` — copie, dans ce fichier, de
    l'assertion directionnelle de `Sb_SESSION_UX_01.2`. Sa duplication est
    précisément ce qui rend une supersession coûteuse : l'invariant vivait à
    deux endroits sans que l'un référence l'autre.

    Même preuve mesurée et même décision opérateur que
    `test_console_before_full_worked_area` : la console passe devant, le
    panneau détaillé descend. Vérifié sur la SOURCE du gabarit, donc aucun
    `order` CSS ne peut la satisfaire.
    """
    src = _src()
    console = src.find("session-focus__console-list")
    worked = src.find("session-focus__body-slot")
    assert console != -1, "console list missing from template source"
    assert worked != -1, "full worked-area panel missing from template source"
    assert console < worked, (
        "console must precede the full worked-area panel in template source"
    )


def test_alternatives_block_present_once():
    src = _src()
    assert src.count('session-focus__alternatives"') == 1
    assert src.count("set sub_data = substitution_data") == 1


# ───────── substitution mechanism invariants (template source) ─────────


def test_same_post_form_action():
    src = _src()
    assert "update_exercise_card" in src


def test_substituted_name_radios_present():
    src = _src()
    assert 'name="substituted_name"' in src


def test_prescribed_option_present():
    src = _src()
    assert 'value="" {% if not se.substituted_name %}checked' in src


def test_n1_n2_n3_groups_present():
    src = _src()
    assert "sub-badge--n1" in src
    assert "sub-badge--n2" in src
    assert "sub-badge--n3" in src


def test_legacy_fallback_present():
    src = _src()
    assert "Legacy fallback" in src
    assert "{% for sub in subs %}" in src


def test_elif_substituted_name_present():
    src = _src()
    assert "{% elif se.substituted_name %}" in src
    assert "substitute-badge" in src


def test_can_sub_conditions_unchanged():
    src = _src()
    assert "{% if can_sub and (subs or total_grouped > 0) %}" in src
    assert "{% set can_sub = sub_data.get('can_substitute', False) %}" in src


# ───────── neighbouring features preserved ─────────


def test_console_before_cues_still_true():
    src = _src()
    assert src.find("session-focus__console-list") < src.find('session-focus__cues"')


def test_previous_load_hint_present():
    src = _src()
    assert "session-focus__console-row-prev" in src


def test_bodymap_silhouette_present():
    src = _src()
    assert "worked_area_body_map.html" in src


def test_sticky_cta_present(client):
    assert "session-focus__sticky-cta" in _body(client)


def test_set_inputs_present(client):
    body = _body(client)
    assert "_weight_kg" in body
    assert "_reps" in body


# ───────── non-goals ─────────


def test_no_js_added():
    src = _src()
    assert "addEventListener" not in src
    if JS_DIR.exists():
        assert not any("alternatives_order" in p.name.lower() for p in JS_DIR.glob("*.js"))
