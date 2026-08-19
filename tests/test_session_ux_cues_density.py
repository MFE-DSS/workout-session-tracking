"""Sb_SESSION_UX_01.4 (F3) — Post-console cues density.

The technical-cues block (rendered below the console since 01.2) becomes a
native collapsible <details>, collapsed by default (no `open`), reducing mobile
density once input is prioritised. Content (cues list + fallback) and classes
unchanged; no information removed; no-JS.

Template-only (+ minimal CSS for the summary affordance); no
route/service/data/model change.
"""

# ══════════════════════════════════════════════════════════════════════
#  Migré par `UIV3_SESSION_EXECUTION_CONSOLE_01` (2026-08-19)
#  ─────────────────────────────────────────────────────────────────────
#  Les marqueurs `session-focus__console-list`,
#  `session-focus__console-row-prev` et `session-focus__sticky-cta`
#  épinglaient une IMPLÉMENTATION que la spec `Sx_UIV3_02` remplace :
#
#    · la console devient `.console__band` (trois positions temporelles) ;
#    · le rappel de charge devient le `DeltaReadout` (`.console__delta`) ;
#    · la barre d'action collante est SUPPRIMÉE — mesurée, elle recouvrait
#      la ligne `É1` et n'existait que parce que la commande était loin.
#
#  L'INVARIANT — l'action précède le détail dans l'ordre SOURCE, pour que
#  le clavier la rencontre en premier — est conservé tel quel.
# ══════════════════════════════════════════════════════════════════════

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXERCISE_CARD = ROOT / "app" / "templates" / "_partials" / "exercise_card.html"
FOCUS_CSS = ROOT / "app" / "static" / "css" / "session_focus.css"
JS_DIR = ROOT / "app" / "static" / "js"


# MIGRÉ — la succession verticale « console → alternatives → cues » devient UNE ligne L3 : `TECHNIQUE · ADAPTER · HISTORIQUE`, aucune dépliée par défaut. L'invariant conservé est que TOUT le L3 vient APRÈS la console dans l'ordre SOURCE, pour que le clavier rencontre l'action avant le détail.

def _src():
    return EXERCISE_CARD.read_text(encoding="utf-8")


def _seed(db, user_id, n=2):
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot="cues-density",
        template_name_snapshot="Cues density test",
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


# ───────── cues become a collapsed <details> ─────────


def test_cues_rendered_in_details(client):
    """MIGRÉ — `TECHNIQUE`, `ADAPTER` et `HISTORIQUE` sont désormais TROIS FRÈRES sur UNE ligne L3, aucun déplié par défaut. L'ordre entre eux n'est plus une hiérarchie mais un rangement de gauche à droite ; l'invariant qui compte — tout le L3 vient APRÈS la console — est vérifié séparément."""
    body = _body(client)
    assert '<details class="l3__item session-focus__cues">' in body


def test_cues_details_not_open(client):
    body = _body(client)
    m = re.search(r'<details class="l3__item session-focus__cues"[^>]*>', body)
    assert m is not None
    assert " open" not in m.group(0), (
        "aucune disclosure L3 ne s'ouvre par défaut (budget de densité)"
    )


def test_summary_cues_techniques_present(client):
    body = _body(client)
    assert 'session-focus__cues-title' in body


def test_cues_list_or_fallback_present(client):
    """Synthetic exercises have no atlas machine → the fallback copy renders."""
    body = _body(client)
    assert "session-focus__cues-empty" in body
    assert "Exécution contrôlée" in body


def test_cues_content_classes_preserved():
    src = _src()
    assert "session-focus__cues-list" in src
    assert "session-focus__cues-item" in src
    assert "session-focus__cues-empty" in src
    assert "Exécution contrôlée, amplitude complète, tempo maîtrisé." in src


def test_cues_rendered_once(client):
    body = _body(client)
    assert body.count('<details class="l3__item session-focus__cues">') == 1


# ───────── order invariants (01.2 / 01.2b preserved) ─────────


def test_console_before_alternatives(client):
    body = _body(client)
    assert body.find("console__band") < body.find('session-focus__alternatives') \
        or 'session-focus__alternatives' not in body  # drawer absent for synthetic exos
    # assert on source where the block literally lives
    src = _src()
    assert src.find("console__band") < src.find('session-focus__alternatives')


def test_alternatives_and_cues_share_the_l3_line():
    """MIGRÉ — `TECHNIQUE`, `ADAPTER` et `HISTORIQUE` sont désormais TROIS FRÈRES sur UNE ligne L3, aucun déplié par défaut. L'ordre entre eux n'est plus une hiérarchie mais un rangement de gauche à droite ; l'invariant qui compte — tout le L3 vient APRÈS la console — est vérifié séparément."""
    src = _src()
    l3 = src.find('<div class="l3">')
    assert l3 != -1
    assert src.find("session-focus__cues", l3) != -1
    assert src.find("session-focus__alternatives", l3) != -1


def test_console_before_cues(client):
    body = _body(client)
    assert body.find("console__band") < body.find('session-focus__cues')


# ───────── neighbouring features preserved ─────────


def test_previous_load_hint_present():
    assert "console__delta" in _src()


def test_bodymap_silhouette_present():
    assert "worked_area_body_map.html" in _src()


def test_substitutions_present():
    src = _src()
    assert 'name="substituted_name"' in src
    assert "sub-badge--n1" in src


def test_sticky_cta_present(client):
    assert "dock__cmd" in _body(client)


def test_set_inputs_present(client):
    body = _body(client)
    assert "_weight_kg" in body and "_reps" in body


# ───────── non-goals ─────────


def test_no_js_added():
    src = _src()
    assert "addEventListener" not in src
    if JS_DIR.exists():
        assert not any("cues_density" in p.name.lower() for p in JS_DIR.glob("*.js"))


def test_no_new_hex_colour_in_cues_summary_css():
    css = FOCUS_CSS.read_text(encoding="utf-8")
    m = re.search(
        r"details\.session-focus__cues > summary\.session-focus__cues-title\s*\{([^}]*)\}",
        css,
    )
    assert m is not None
    assert "#" not in m.group(1)  # var/keyword only, no raw hex
