"""Sb_SESSION_UX_01.3 (F2) — Previous-load readability on the active set row.

A discreet reminder of last session's load (« dernière : X kg · Y reps ») is
rendered ON the ACTIVE set row, at the exact point of input. Additive: the
existing « Référence précédente » console block is preserved. Silence when
there is no prior data (never an invented performance). Decorative
(aria-hidden); text source of truth unchanged.

Template/CSS only — no route/service/data/model change.
"""
from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

from tests.helpers import get_test_user_id

ROOT = Path(__file__).resolve().parent.parent
FOCUS_CSS = ROOT / "app" / "static" / "css" / "session_focus.css"
EXERCISE_CARD = ROOT / "app" / "templates" / "_partials" / "exercise_card.html"
JS_DIR = ROOT / "app" / "static" / "js"


def _new_session(client, slug: str = "push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    m = re.match(r"/sessions/(\d+)", r.headers["location"])
    return int(m.group(1))


def _insert_prior(client, *, exercise_code, exercise_name, work_sets, slug="push-a"):
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    with SessionLocal() as db:
        prior = WorkoutSession(
            template_id=None,
            template_slug_snapshot=slug,
            template_name_snapshot="Push A",
            user_id=get_test_user_id(),
            started_at=datetime.now(UTC) - timedelta(days=5),
            status="completed",
        )
        se = SessionExercise(
            template_exercise_id=None,
            exercise_code_snapshot=exercise_code,
            exercise_name_snapshot=exercise_name,
            position=1,
        )
        for i, ws in enumerate(work_sets, start=1):
            se.set_logs.append(
                SetLog(
                    kind="work",
                    set_index=i,
                    weight_kg=ws.get("weight_kg"),
                    reps=ws.get("reps"),
                    completed=ws.get("completed", True),
                )
            )
        prior.session_exercises.append(se)
        db.add(prior)
        db.commit()
        return prior.id


# ───────── in-row previous-load hint ─────────


def test_prev_load_hint_on_active_row_when_data(client):
    """**Migre T5 -> T3** par `UIV3_SESSION_EXECUTION_CONSOLE_01`.

    Le rappel vivait DANS la ligne de serie, en `aria-hidden`, double par un
    bloc « Reference precedente » plus haut. L'amendement A de l'operateur en
    fait un `DeltaReadout` unique, place juste AVANT le `SetInstrument` :
    « qu'est-ce que j'ai fait la derniere fois ? » est la question
    directement utile a la serie en cours, pas une donnee d'annexe.

    L'invariant conserve : **avec un historique, la reference est visible au
    point de saisie ; sans historique, on le DIT** - jamais un faux delta.
    """
    _insert_prior(
        client,
        exercise_code="E1",
        exercise_name="Incline Smith Press",
        work_sets=[{"weight_kg": 60.0, "reps": 10}, {"weight_kg": 62.5, "reps": 8}],
    )
    sid = _new_session(client, "push-a")
    body = client.get(f"/sessions/{sid}").text
    assert "console__delta-value" in body
    # MIGRÉ — l'étiquette est raccourcie à « Réf. » quand la cible et
    # la référence partagent une ligne (passe de densité).
    assert "Réf." in body


def test_prev_load_hint_absent_when_no_data(client):
    """No prior session ⇒ silence (never an invented performance)."""
    sid = _new_session(client, "push-a")
    body = client.get(f"/sessions/{sid}").text
    assert "console__delta-value" not in body
    assert "Première fois" in body, (
        "sans référence, le produit le dit — il ne laisse pas un vide"
    )


def test_the_reference_is_now_accessible_rather_than_decorative(client):
    """**Migre T5 -> T2, et le contrat s'INVERSE.**

    L'ancien rappel etait `aria-hidden` parce qu'il DOUBLAIT un bloc
    accessible situe ailleurs. Il n'y a plus de doublon : le `DeltaReadout`
    est la seule reference, donc il doit etre lisible par une technologie
    d'assistance. Le masquer reviendrait a retirer l'information aux
    lecteurs d'ecran.
    """
    _insert_prior(
        client,
        exercise_code="E1",
        exercise_name="Incline Smith Press",
        work_sets=[{"weight_kg": 60.0, "reps": 10}],
    )
    sid = _new_session(client, "push-a")
    body = client.get(f"/sessions/{sid}").text
    # MIGRÉ — le `DeltaReadout` partage sa ligne avec la cible : il est un
    # `<span>` dans `console__readout`, plus un `<p>` autonome.
    m = re.search(r'<span class="console__delta">(.*?)</span>\s*</p>',
                  body, re.DOTALL)
    assert m is not None, "le DeltaReadout n'est pas rendu"
    assert "aria-hidden" not in m.group(0), (
        "unique porteur de la référence : il ne peut pas être masqué"
    )


def test_the_reference_is_stated_exactly_once(client):
    """**Migre T5 -> T4.** Il y avait DEUX porteurs de la meme reference : le
    bloc « Reference precedente » et le rappel dans la ligne. Un seul
    subsiste - c'etait l'objet de la deduplication (`Sx_UIV3_02B` D5)."""
    _insert_prior(
        client,
        exercise_code="E1",
        exercise_name="Incline Smith Press",
        work_sets=[{"weight_kg": 60.0, "reps": 10}],
    )
    sid = _new_session(client, "push-a")
    body = client.get(f"/sessions/{sid}").text
    assert body.count("console__delta-value") == 1
    assert "Référence précédente" not in body, (
        "l'ancien doublon ne doit pas revenir"
    )


def test_prev_load_hint_only_on_the_active_card(client):
    """La reference n'apparait qu'une fois : sur la carte active."""
    _insert_prior(
        client,
        exercise_code="E1",
        exercise_name="Incline Smith Press",
        work_sets=[{"weight_kg": 60.0, "reps": 10}],
    )
    sid = _new_session(client, "push-a")
    body = client.get(f"/sessions/{sid}").text
    assert body.count("console__delta-value") == 1


# ───────── non-goals: no JS, no new colour ─────────


def test_no_raw_hex_in_the_reference_rule():
    """`CLAUDE.md` 5.4 - toute couleur est un token mesure de la palette.
    Un hex ecrit ici echapperait a l'escalier de contraste de `:root`."""
    css = FOCUS_CSS.read_text(encoding="utf-8")
    m = re.search(r"\.console__delta-value\s*\{([^}]*)\}", css)
    assert m is not None
    assert "#" not in m.group(1), m.group(1)
    assert "var(--t-" in m.group(1)


def test_no_js_added_for_prev_load():
    src = EXERCISE_CARD.read_text(encoding="utf-8")
    # le DeltaReadout est du SSR pur
    assert "console__delta" in src
    if JS_DIR.exists():
        assert not any("prev_load" in p.name.lower() for p in JS_DIR.glob("*.js"))
