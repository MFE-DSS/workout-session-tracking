"""Sb_SESSION_UX_01.2b (F1) — Alternatives drawer below the console.

The "Adapter l'exercice" substitution drawer is moved below the set-logging
console (order: worked-area → console → alternatives → cues). Purely
structural: the block content (radios name="substituted_name", N1/N2/N3,
legacy fallback, `elif se.substituted_name`, same POST form) is byte-identical;
only its position changed.

Template-only, no-JS, no route/service/data/model change.
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
    console = src.find("console__band")
    alts = src.find('session-focus__alternatives')
    assert console != -1 and alts != -1
    assert console < alts, "console must come before the alternatives drawer"


def test_alternatives_and_cues_are_siblings_on_the_l3_line():
    """MIGRÉ — `TECHNIQUE`, `ADAPTER` et `HISTORIQUE` sont désormais TROIS FRÈRES sur UNE ligne L3, aucun déplié par défaut. L'ordre entre eux n'est plus une hiérarchie mais un rangement de gauche à droite ; l'invariant qui compte — tout le L3 vient APRÈS la console — est vérifié séparément."""
    src = _src()
    l3 = src.find('<div class="l3">')
    end = src.find("</div>", src.find("Historique</a>"))
    assert l3 != -1, "la ligne L3 n'existe plus"
    line = src[l3:end]
    for marker in ("session-focus__cues", "session-focus__alternatives",
                   "Historique"):
        assert marker in line, marker
    console = src.find('<div class="console"')
    assert console < l3, "tout le L3 vient APRÈS la console"


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
    console = src.find("console__band")
    worked = src.find("session-focus__body-slot")
    assert console != -1, "console list missing from template source"
    assert worked != -1, "full worked-area panel missing from template source"
    assert console < worked, (
        "console must precede the full worked-area panel in template source"
    )


def test_alternatives_block_present_once():
    src = _src()
    # MIGRÉ — la classe vit maintenant sur le `<details>` de la ligne L3,
    # avec ses modificateurs ; elle reste écrite UNE fois.
    # Le BLOC est écrit une fois ; ses enfants (`-label`, `-role`)
    # portent le même préfixe, d'où le comptage sur le `<details>`.
    assert src.count('class="l3__item session-focus__alternatives') == 1
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
    """**Migré** — la garde exigeait la CHAÎNE « Legacy fallback », qui est un
    commentaire. Un commentaire n'est pas un comportement : le supprimer
    faisait rougir la garde alors que le repli fonctionnait, et le conserver
    l'aurait laissée verte si le repli avait disparu.

    Elle épingle désormais le repli lui-même : quand aucun groupe N1/N2/N3
    n'existe (exercices hors périmètre du moteur), la liste plate reste
    rendue et reste postable.
    """
    src = _src()
    assert "{% if total_grouped == 0 %}" in src
    assert "{% for sub in subs %}" in src
    assert 'name="substituted_name" value="{{ sub }}"' in src


def test_elif_substituted_name_present():
    """MIGRÉ — la branche `elif` devient un `else` qui CONSERVE la valeur en
    champ masqué avant d'afficher le badge. C'est plus sûr que l'ancien
    contrat : sans ce `preserve`, masquer le sélecteur effacerait la
    substitution au premier POST."""
    src = _src()
    assert "{% if se.substituted_name %}" in src
    assert "substitute-badge" in src
    assert "preserve('substituted_name', se.substituted_name)" in src


def test_can_sub_conditions_unchanged():
    src = _src()
    assert "{% if can_sub and (subs or total_grouped > 0) %}" in src
    assert "{% set can_sub = sub_data.get('can_substitute', False) %}" in src


# ───────── neighbouring features preserved ─────────


def test_console_before_cues_still_true():
    src = _src()
    assert src.find("console__band") < src.find('session-focus__cues')


def test_previous_load_hint_present():
    src = _src()
    assert "console__delta" in src


def test_bodymap_silhouette_present():
    src = _src()
    assert "worked_area_body_map.html" in src


def test_sticky_cta_present(client):
    assert "dock__cmd" in _body(client)


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
