"""Sb_DOGFOOD_01.3 — Compact mobile overload placeholder.

Feedback dogfood : dans la console de saisie, les placeholders cible chiffrés
sont rendus DANS les inputs (pas de span unité séparé). Sur mobile étroit, un
placeholder long (ex. "≈ 102.5" ou "≈ 6-10") devient trop large / trop lourd.

Correctif (Option B légère) :
  - formatter `_build_overload_placeholder` compacté : "102.5" / "6-10" / "6"
    (valeur nue, sans le préfixe "≈ ") ;
  - règle CSS mobile `::placeholder` ciblée sur la ligne active porteuse d'un
    placeholder d'overload (`.set-row--has-overload-placeholder`) ;
  - AUCUN `value=` prérempli, AUCUN changement d'engine / historique /
    substitution, AUCUN span unité (Option C différée), AUCUN JS.

Le placeholder reste une indication légère : jamais une valeur, jamais un
préremplissage, jamais une contrainte.
"""
from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARD = ROOT / "app" / "templates" / "_partials" / "exercise_card.html"
CSS = ROOT / "app" / "static" / "css" / "session_focus.css"


# ───────── formatter : valeur compacte, sans unité inline, sans ≈ ─────────


def test_weight_placeholder_is_compact_without_kg_and_without_approx():
    """Placeholder poids compact : "102.5" — ne contient ni "kg" ni "≈"."""
    from app.routers.sessions import _build_overload_placeholder
    from app.services.overload_engine import OverloadHint

    h = OverloadHint(
        state="progress", engine_version=1, target_weight_kg=102.5,
        target_reps_min=6, target_reps_max=10, reasons=(),
    )
    ph = _build_overload_placeholder(h)
    assert ph["weight"] == "102.5"
    assert "kg" not in ph["weight"].lower()
    assert "≈" not in ph["weight"]


def test_reps_placeholder_is_compact_without_reps_word_and_without_approx():
    """Placeholder reps compact : "6-10" — ne contient ni "reps" ni "≈"."""
    from app.routers.sessions import _build_overload_placeholder
    from app.services.overload_engine import OverloadHint

    h = OverloadHint(
        state="progress", engine_version=1, target_weight_kg=100.0,
        target_reps_min=6, target_reps_max=10, reasons=(),
    )
    ph = _build_overload_placeholder(h)
    assert ph["reps"] == "6-10"
    assert "reps" not in ph["reps"].lower()
    assert "rep" not in ph["reps"].lower()
    assert "≈" not in ph["reps"]


def test_long_weight_target_is_covered_and_short():
    """Le format long type 102.5 est couvert et reste court (≤ 6 chars)."""
    from app.routers.sessions import _build_overload_placeholder
    from app.services.overload_engine import OverloadHint

    h = OverloadHint(
        state="progress", engine_version=1, target_weight_kg=102.5,
        target_reps_min=8, target_reps_max=12, reasons=(),
    )
    ph = _build_overload_placeholder(h)
    assert ph["weight"] == "102.5"
    # aucun préfixe / suffixe qui allonge : la valeur nue tient dans un input étroit
    assert len(ph["weight"]) <= 6
    assert re.fullmatch(r"\d+(\.\d+)?", ph["weight"])


def test_none_target_stays_none():
    """Pas de cible chiffrée → None (défensif) : aucun placeholder inventé."""
    from app.routers.sessions import _build_overload_placeholder
    from app.services.overload_engine import OverloadHint

    h = OverloadHint(
        state="unknown", engine_version=1, target_weight_kg=None,
        target_reps_min=None, target_reps_max=None, reasons=(),
    )
    assert _build_overload_placeholder(h) is None


# ───────── CSS : règle mobile ::placeholder ciblée ─────────


def test_css_has_targeted_mobile_placeholder_rule():
    """Le CSS contient une règle mobile `::placeholder` ciblée sur la ligne
    d'overload, sous un breakpoint mobile étroit."""
    src = CSS.read_text(encoding="utf-8")
    # règle ::placeholder ciblée sur la row porteuse du placeholder d'overload
    assert "set-row--has-overload-placeholder" in src
    m = re.search(
        r"@media\s*\(max-width:\s*(380|390|400)px\)\s*\{[^}]*"
        r"set-row--has-overload-placeholder[^}]*::placeholder",
        src,
        re.DOTALL,
    )
    assert m, "expected a mobile @media rule targeting the overload row ::placeholder"


def test_css_mobile_rule_does_not_shrink_tap_target():
    """La règle mobile réduit la typo placeholder mais NE déclare PAS de
    min-height / height (tap target WCAG) : elle ne cible que `::placeholder`
    et ne touche donc pas le tap target ni l'anti-zoom iOS de l'input."""
    src = CSS.read_text(encoding="utf-8")
    # isoler le corps { … } de NOTRE règle ::placeholder ciblée (déclarations
    # uniquement, pas le commentaire au-dessus)
    m = re.search(
        r"set-row--has-overload-placeholder[^{]*::placeholder\s*\{([^}]*)\}",
        src,
        re.DOTALL,
    )
    assert m, "targeted ::placeholder rule not found"
    declarations = m.group(1)
    # aucune déclaration de hauteur / tap target dans le corps de la règle
    assert not re.search(r"\bmin-height\s*:", declarations)
    assert not re.search(r"\bheight\s*:", declarations)
    # la règle réduit bien la taille du texte placeholder
    assert re.search(r"\bfont-size\s*:", declarations)


# ───────── rendu HTML : placeholders sont bien des placeholders, pas des values ─────────


def _seed_progress(db, user_id):
    from app.models.catalog import RepTarget, TemplateExercise, WorkoutTemplate
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    t = WorkoutTemplate(slug=f"mph-{user_id}", name="Mobile PH", kind="strength")
    db.add(t)
    db.flush()
    te = TemplateExercise(
        template_id=t.id, position=1, code="A1", name="Back squat",
        set_scheme="3×6-10",
    )
    db.add(te)
    db.flush()
    db.add(RepTarget(template_exercise_id=te.id, set_index=1, min_reps=6, max_reps=10))
    db.flush()
    now = datetime.now(UTC)
    for k in range(2):
        past = WorkoutSession(
            user_id=user_id, template_id=t.id, template_slug_snapshot=t.slug,
            template_name_snapshot=t.name, started_at=now - timedelta(days=7 * (k + 1)),
            ended_at=now - timedelta(days=7 * (k + 1)), status="completed",
            global_state="good", concentration="high",
        )
        pse = SessionExercise(
            template_exercise_id=te.id, exercise_code_snapshot="A1",
            exercise_name_snapshot="Back squat", position=1, success_score=100,
        )
        pse.set_logs.append(
            SetLog(kind="work", set_index=1, weight_kg=100.0, reps=10, completed=True)
        )
        past.session_exercises.append(pse)
        db.add(past)
    cur = WorkoutSession(
        user_id=user_id, template_id=t.id, template_slug_snapshot=t.slug,
        template_name_snapshot=t.name, started_at=now, status="in_progress",
    )
    se = SessionExercise(
        template_exercise_id=te.id, exercise_code_snapshot="A1",
        exercise_name_snapshot="Back squat", position=1,
    )
    se.set_logs.append(
        SetLog(kind="work", set_index=1, weight_kg=None, reps=None, completed=False)
    )
    cur.session_exercises.append(se)
    db.add(cur)
    db.commit()
    db.refresh(cur)
    return cur


def _render(client, sid):
    r = client.get(f"/sessions/{sid}", follow_redirects=False)
    assert r.status_code == 200, r.text[:300]
    return r.text


def test_rendered_targets_are_placeholders_only_never_values(client):
    """La cible compacte "102.5" apparaît UNIQUEMENT comme placeholder,
    jamais dans un value= (jamais de préremplissage)."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        s = _seed_progress(db, db.query(User).first().id)
        sid = s.id

    body = _render(client, sid)
    # compact target présent en placeholder
    assert 'placeholder="102.5"' in body
    assert 'placeholder="6-10"' in body
    # jamais en value= : le set actif reste vide
    assert 'value="102.5"' not in body
    assert 'value="6-10"' not in body
    # l'input poids du set actif reste value="" (pas de pré-remplissage)
    assert re.search(r'name="set_\d+_weight_kg"[^>]*value=""', body)
    assert re.search(r'name="set_\d+_reps"[^>]*value=""', body)


def test_no_approx_prefix_in_rendered_placeholders(client):
    """Plus aucun "≈" dans les placeholders cible rendus (compact mobile)."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        s = _seed_progress(db, db.query(User).first().id)
        sid = s.id

    body = _render(client, sid)
    for m in re.finditer(r'placeholder="([^"]*)"', body):
        assert "≈" not in m.group(1)


# ───────── garde wording exercise_card.html ─────────


def test_no_repere_wording_added_to_card():
    """Sb_DOGFOOD_01.3 n'introduit aucune occurrence "Repère"/"repère"."""
    src = CARD.read_text(encoding="utf-8")
    assert "Repère" not in src and "repère" not in src
