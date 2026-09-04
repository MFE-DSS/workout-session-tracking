"""`R4` · `Q-C` · `Q-E` — les commandes disent ce qu'elles font.

POURQUOI CETTE GARDE EXISTE
---------------------------
Trois retours d'opérateur sur le rendu du viseur, tous du même ordre : **un
libellé qui décrit une position n'est pas une information.**

* `R4` — « PASSER À E2 » ne dit pas ce qu'on va faire. Le code de position est
  connu du produit, pas de l'utilisateur.
* `Q-C` — « sauter l'échauffement » manquait, et doit être une **pure
  navigation** : marquer les échauffements comme faits fabriquerait des
  données d'entraînement que personne n'a produites. Un échauffement sauté
  n'est pas un échauffement fait — et c'est la garde la plus importante de ce
  fichier, parce que l'erreur inverse serait invisible et définitive.
* `Q-E` — « Push A — Pecs épaisseur + Delts + Triceps » est un nom de
  GABARIT : il décrit ce que le programme contient, pas ce qu'on travaille.

Ces tests vérifient le **comportement rendu**, pas la forme des chaînes dans
le code : un libellé assemblé à deux endroits diverge, et c'est ce qui rendait
la garde de source insuffisante.
"""

from __future__ import annotations

import re

import pytest
from sqlalchemy import select

from app.services.console_state import build_console_state, secondary_for


def _start(client, slug: str = "push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    assert r.status_code in (302, 303), r.status_code
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def _exercises(session_id: int):
    from app.database import SessionLocal
    from app.models.session import SessionExercise

    with SessionLocal() as db:
        return [
            (se.id, se.exercise_code_snapshot,
             se.substituted_name or se.exercise_name_snapshot)
            for se in db.execute(
                select(SessionExercise)
                .where(SessionExercise.session_id == session_id)
                .order_by(SessionExercise.position.asc())
            ).scalars().all()
        ]


def _warmup_state(session_id: int):
    """L'état console du premier exercice, échauffement en attente."""
    from app.database import SessionLocal
    from app.models.session import SessionExercise

    with SessionLocal() as db:
        se = db.execute(
            select(SessionExercise)
            .where(SessionExercise.session_id == session_id)
            .order_by(SessionExercise.position.asc())
            .limit(1)
        ).scalars().first()
        db.refresh(se, ["set_logs"])
        return build_console_state(se, next_code="E2", next_name="Chest Press machine")


# ───────────────── `R4` — la sortie nomme sa destination ─────────────────


def test_the_exercise_exit_names_the_next_exercise(client):
    session_id = _start(client)
    exercises = _exercises(session_id)
    assert len(exercises) >= 2, "séance trop courte pour tester la sortie"
    next_name = exercises[1][2]

    body = client.get(f"/sessions/{session_id}").text
    assert "EXERCICE SUIVANT" in body, "le libellé d'intention a disparu"
    assert next_name in body, (
        f"la destination « {next_name} » n'est pas rendue — la commande est "
        "revenue à un code de position"
    )


def test_the_exit_label_no_longer_carries_a_position_code():
    """« PASSER À E2 » ne doit plus exister comme libellé."""
    state = _warmup_state_stub()
    labels = [s["label"] for s in secondary_for(state)]
    offenders = [lbl for lbl in labels if re.search(r"PASSER À\s+E\d", lbl)]
    assert offenders == [], offenders


def _warmup_state_stub():
    """État minimal en `WARMUP`, sans base : on teste le libellé, pas le flux."""
    class _SL:
        def __init__(self, kind, idx, completed=False):
            self.kind, self.set_index, self.completed = kind, idx, completed
            self.id, self.weight_kg, self.reps = idx, None, None

    class _SE:
        set_logs = [_SL("warmup", 1), _SL("work", 1)]
        template_exercise = None

    return build_console_state(
        _SE(), next_code="E2", next_name="Chest Press machine"
    )


# ───────────────── `Q-C` — sauter n'écrit RIEN ─────────────────


def test_skipping_the_warmup_writes_nothing(client):
    """Le CHEMIN de saut n'écrit rien.

    ⚠ Portée exacte, parce que la surestimer serait le défaut que ce fichier
    combat : ce test vérifie que **la requête `?skipwarm=1` est inerte**. Il
    ne peut pas, à lui seul, prouver que le CONTRÔLE l'est — un `GET` n'écrit
    jamais, quel que soit le bouton qui l'a produit.

    C'est `test_the_skip_is_a_link_not_a_submission` qui porte cette
    seconde moitié, et il la porte **par construction** : un lien ne
    sérialise aucun formulaire. Les deux ensemble tiennent l'invariant ;
    séparément, aucun ne suffit.

    L'enjeu : un échauffement sauté n'est pas un échauffement fait. Une
    sortie qui écrirait fabriquerait des séries que personne n'a exécutées,
    et le produit afficherait exactement ce qu'on attendait de lui.
    """
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog

    session_id = _start(client)
    se_id = _exercises(session_id)[0][0]

    def snapshot():
        with SessionLocal() as db:
            return {
                sl.id: (sl.weight_kg, sl.reps, sl.completed)
                for sl in db.execute(
                    select(SetLog)
                    .join(SessionExercise,
                          SetLog.session_exercise_id == SessionExercise.id)
                    .where(SessionExercise.session_id == session_id)
                ).scalars().all()
            }

    before = snapshot()
    assert before, "aucune série — la garde tournerait à vide"

    r = client.get(f"/sessions/{session_id}?active={se_id}&skipwarm=1")
    assert r.status_code == 200

    assert snapshot() == before, (
        "sauter l'échauffement a MODIFIÉ des séries — c'est une pure "
        "navigation, elle ne doit rien écrire"
    )


def test_skipping_the_warmup_moves_the_instrument_to_the_work_set(client):
    """Sans effet visible, le paramètre serait décoratif."""
    session_id = _start(client)
    se_id = _exercises(session_id)[0][0]

    plain = client.get(f"/sessions/{session_id}?active={se_id}").text
    skipped = client.get(f"/sessions/{session_id}?active={se_id}&skipwarm=1").text

    assert 'data-console-state="warmup"' in plain, plain[:0]
    assert 'data-console-state="warmup"' not in skipped, (
        "`skipwarm=1` n'a pas déplacé l'instrument — le paramètre ne fait rien"
    )


def test_the_skip_is_a_link_not_a_submission():
    """**La moitié qui prouve vraiment quelque chose.**

    Un lien ne sérialise aucun formulaire : il ne peut PAS écrire, par
    construction. Un `<button type="submit">` au même endroit soumettrait la
    carte entière au passage — et `_persist_set_values` écrase alors toutes
    les séries de l'exercice avec ce que porte le DOM.

    C'est structurel et non comportemental, et c'est assumé : le
    comportement se teste sur une requête, or ici le risque vit dans le
    CONTRÔLE qui la produit.
    """
    from pathlib import Path

    card = (
        Path(__file__).resolve().parent.parent
        / "app/templates/_partials/exercise_card.html"
    )
    markup = re.sub(r"\{#.*?#\}", "", card.read_text(encoding="utf-8"), flags=re.DOTALL)
    m = re.search(r"s\.kind == 'skip_warmup'.*?\{% elif", markup, re.DOTALL)
    assert m, "la branche `skip_warmup` a disparu du gabarit"
    branch = m.group(0)
    assert "<a " in branch, "la sortie d'échauffement doit être un LIEN"
    assert "type=\"submit\"" not in branch, (
        "un submit enregistrerait le formulaire — la sortie doit être inerte"
    )


# ───────────────── `Q-E` — le bandeau dit le travail du moment ─────────────


def test_the_banner_shows_the_code_and_not_the_template_prose(client):
    session_id = _start(client)
    body = client.get(f"/sessions/{session_id}").text
    m = re.search(r'class="[^"]*session-head__code[^"]*"[^>]*>([^<]+)<', body)
    assert m, "le code de séance n'est plus rendu"
    code = m.group(1).strip()
    assert code, "code vide"
    assert "+" not in code, (
        f"« {code} » porte encore l'énumération du gabarit — c'est ce que "
        "`Q-E` retire du premier rang"
    )


def test_the_full_template_name_is_never_lost(client):
    """`§5.3` — le nom change de rang, il ne disparaît pas.

    Il doit rester atteignable : `title` (souris) ET le panneau `⋯` (tactile).
    """
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    session_id = _start(client)
    with SessionLocal() as db:
        full = db.get(WorkoutSession, session_id).template_name_snapshot

    body = client.get(f"/sessions/{session_id}").text
    assert full in body, (
        f"le nom complet « {full} » n'apparaît nulle part — c'est une "
        "soustraction, et §5.3 l'interdit"
    )


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Push A — Pecs épaisseur + Delts + Triceps", "Push A"),
        ("Pull B – Dos largeur + Biceps", "Pull B"),
        ("Legs - Quadriceps", "Legs"),
        ("Full Body", "Full Body"),          # aucun séparateur : rien à couper
        ("", ""),
    ],
)
def test_the_code_derivation_never_invents(name, expected):
    """Sans séparateur, on rend le nom TEL QUEL.

    Fabriquer un code court par troncature arbitraire inventerait une donnée —
    c'était l'objection écrite dans la feuille de style, et elle reste valable
    partout où la dérivation ne s'applique pas.
    """
    from app.routers.sessions import _session_head

    assert _session_head(name, None)["code"] == expected


# ───────────────── `R9` — le panneau dit ce qu'il contient ─────────────────


def test_the_panel_is_named_recommandation_and_reads_as_operable(client):
    """`R9` — « on ne comprend pas que "technique" est opérable ».

    Le déclencheur était du TEXTE NU : marqueur natif masqué, aucun cadre,
    aucun chevron. Le mot « Technique » n'annonçait par ailleurs que la
    moitié de ce que le panneau contient.
    """
    session_id = _start(client)
    body = client.get(f"/sessions/{session_id}").text
    assert "Recommandation" in body, "le panneau n'est plus nommé"
    assert "Technique</summary>" not in body, "l'ancien libellé subsiste"
    assert "l3__item--reco" in body, (
        "le panneau n'est plus marqué comme portant une lecture système"
    )


def test_the_engine_guidance_leads_the_recommendation_panel():
    """Un panneau nommé « recommandation » qui commence par autre chose ment
    sur son ordre.

    Vérifié à la SOURCE et non au rendu : la guidance n'apparaît que si le
    moteur a produit une recommandation — sur une séance neuve (« première
    fois »), il n'y en a aucune, et le test passerait à vide sur le rendu.
    """
    from pathlib import Path

    card = (
        Path(__file__).resolve().parent.parent
        / "app/templates/_partials/exercise_card.html"
    )
    src = re.sub(r"\{#.*?#\}", "", card.read_text(encoding="utf-8"), flags=re.DOTALL)
    body = src.split("l3__body machine-panel__body", 1)[1]
    guidance = body.find("session-focus__guidance")
    machine = body.find("machine-panel__title")
    zone = body.find("session-focus__worked-area-title")
    assert guidance > 0, "la guidance a disparu du panneau"
    assert guidance < machine, "la recommandation ne vient pas en premier"
    assert machine < zone, "l'ordre technique → zone travaillée a changé"


def test_the_guidance_appears_exactly_once():
    """Elle a été REMONTÉE, pas copiée.

    Un déplacement fait à moitié laisserait deux blocs identiques dans le
    même panneau — et personne ne le verrait, puisque le second serait
    simplement plus bas.
    """
    from pathlib import Path

    card = (
        Path(__file__).resolve().parent.parent
        / "app/templates/_partials/exercise_card.html"
    )
    src = re.sub(r"\{#.*?#\}", "", card.read_text(encoding="utf-8"), flags=re.DOTALL)
    assert src.count('class="session-focus__guidance"') == 1, (
        "la guidance est rendue plus d'une fois — déplacement fait à moitié"
    )


def test_an_unmapped_zone_is_silent_rather_than_qualified():
    """Trois exercices sur sept d'une séance type ne sont pas mappés.

    Écrire « À qualifier » ferait passer une absence de donnée pour une
    information — et le bandeau est la ligne la plus lue du produit.
    """
    from app.routers.sessions import _session_head

    assert _session_head("Push A — X", None)["zone"] is None
    assert _session_head("Push A — X", {"status": "unmapped"})["zone"] is None
    assert _session_head(
        "Push A — X", {"status": "mapped", "primary_label": "Pectoraux"}
    )["zone"] == "Pectoraux"
