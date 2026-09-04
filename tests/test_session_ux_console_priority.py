"""Sb_SESSION_UX_01.2 (F1) — Active console priority.

On the ACTIVE card, the set-logging console now renders BEFORE the technical
cues block (the always-visible block that previously pushed input down).
Option A (light repriorisation): cues are moved AFTER the console. The
alternatives drawer (collapsed <details>, form-critical) is intentionally left
in place. Order on active card: worked-area → (alternatives, collapsed) →
console → cues.

Template-only, no-JS, no route/service/data/model change. Same POST form, same
input names, value="" strict, server-derived completion, sticky CTA, rest timer
and BodyMap silhouette preserved.
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

from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXERCISE_CARD = ROOT / "app" / "templates" / "_partials" / "exercise_card.html"
JS_DIR = ROOT / "app" / "static" / "js"


# MIGRÉ — la succession verticale « console → alternatives → cues » devient UNE ligne L3 : `TECHNIQUE · ADAPTER · HISTORIQUE`, aucune dépliée par défaut. L'invariant conservé est que TOUT le L3 vient APRÈS la console dans l'ordre SOURCE, pour que le clavier rencontre l'action avant le détail.

def _seed(db, user_id, n=2):
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot="console-priority",
        template_name_snapshot="Console priority test",
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


# ───────── order on the active card ─────────


def test_console_before_cues(client):
    body = _body(client)
    console = body.find("console__band")
    cues = body.find("session-focus__cues")
    assert console != -1 and cues != -1
    assert console < cues, "console must render before technical cues"


def test_console_before_full_worked_area(client):
    """Sb_UIV2_SESSION_FOCUS_02 — supersession explicite, direction inversée.

    ANCIEN CONTRAT (`test_worked_area_before_console`, Sb_SESSION_UX_01.2) :

        assert worked < console, "worked area (Zone travaillée) stays before console"

    PREUVE DE DOGFOOD MESURÉE (mobile 360×640, harnais stateful, géométrie
    Playwright réelle, sans scroll) :

        série courante ........ 1355 px  → fold 2.1  (HORS viewport)
        Zone travaillée ....... 521 px   → fold 0.8  (DANS le viewport)

    Autrement dit le panneau secondaire occupait le premier écran pendant que
    l'action primaire tombait deux écrans plus bas.

    SUPERSESSION OPÉRATEUR EXPLICITE : l'ordre historique est superseded pour
    l'UI de séance active. Nouvelle hiérarchie : identité → console → action
    primaire → détail secondaire (Zone travaillée, machine, alternatives).
    La supersession porte UNIQUEMENT sur l'ordre d'affichage ; aucune
    sémantique métier des composants n'est touchée.

    NOUVEAU CONTRAT : ordre de SOURCE, pas ordre visuel. L'assertion lit le
    HTML rendu, donc un `order` CSS ne peut pas la satisfaire — c'est
    délibéré : la navigation clavier doit rencontrer l'action avant le
    détail, ce qu'un réordonnancement purement visuel casserait.
    """
    body = _body(client)
    console = body.find("console__band")
    worked = body.find("session-focus__body-slot")
    assert console != -1, "console list missing"
    assert worked != -1, "full worked-area panel missing — it must still exist"
    assert console < worked, (
        "the logging console must render BEFORE the full worked-area panel "
        "in source order (superseded Sb_SESSION_UX_01.2 ordering)"
    )


def test_compact_target_precedes_the_console(client):
    """Le contexte de cible compact reste, lui, AVANT la console.

    Contexte de cible ≠ visualisation détaillée : la ligne d'une ligne
    accompagne l'identité, le panneau descend. Sans cette garde, « descendre
    la Zone travaillée » pourrait silencieusement emporter le contexte utile.
    """
    body = _body(client)
    compact = body.find("console__target")
    console = body.find("console__band")
    assert compact != -1, "compact target context missing"
    assert compact < console, "compact target belongs with the exercise identity"


def test_cues_still_present(client):
    """MIGRÉ deux fois, et c'est la seconde qui compte.

    Les cues ont d'abord quitté le flux pour la ligne L3 sous « Technique » —
    le mot « cues » était un anglicisme au milieu d'une interface française.

    `R9` / `Q-A = C` (opérateur, 2026-09-04) : le panneau contenait DÉJÀ les
    deux moitiés — ce que le moteur propose et comment bien exécuter — mais
    n'annonçait que la seconde. Il s'appelle donc **RECOMMANDATION**.

    Ce qui est gardé ici ne change pas : les cues n'ont pas quitté le produit.
    """
    body = _body(client)
    assert "session-focus__cues" in body
    assert "Recommandation" in body, "le déclencheur du panneau a disparu"


def test_cues_rendered_once(client):
    """No duplicate cues block (moved, not copied)."""
    body = _body(client)
    assert body.count('session-focus__cues"') == 1


# ───────── invariants preserved ─────────


def test_set_inputs_present(client):
    body = _body(client)
    assert "_weight_kg" in body
    assert "_reps" in body


def test_alternatives_still_in_form():
    """Alternatives drawer preserved (left in place, form-critical). Checked in
    the template source: synthetic exercises have no computed substitutions, so
    the drawer only renders for real catalog exercises — but the mechanism
    (substituted_name radios) must remain present and unchanged."""
    src = EXERCISE_CARD.read_text(encoding="utf-8")
    assert 'name="substituted_name"' in src
    assert "l3__item" in src


def test_sticky_cta_present(client):
    body = _body(client)
    assert "dock__cmd" in body


def test_rest_timer_rendered(client):
    body = _body(client)
    # rest timer partial renders on the active card
    assert "rest" in body.lower()


def test_bodymap_silhouette_preserved(client):
    body = _body(client)
    assert "wa-silhouettes" in body


# ───────── non-goals ─────────


def test_no_js_added():
    src = EXERCISE_CARD.read_text(encoding="utf-8")
    assert "addEventListener" not in src
    if JS_DIR.exists():
        assert not any("console_priority" in p.name.lower() for p in JS_DIR.glob("*.js"))


def test_no_orphan_machine_var():
    """The old hero _machine (only consumed by cues) is removed to avoid dead
    code; cues re-resolve _cues_machine locally after the console."""
    src = EXERCISE_CARD.read_text(encoding="utf-8")
    # the cues block uses the locally re-resolved var
    assert "_machine_top" in src
    # the old hero assignment `{% set _machine = ` is gone
    assert "{% set _machine =" not in src
