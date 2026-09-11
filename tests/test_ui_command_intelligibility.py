"""`R4` · `Q-C` · `Q-E` — les commandes disent ce qu'elles font.

POURQUOI CETTE GARDE EXISTE
---------------------------
Trois retours d'opérateur sur le rendu du viseur, tous du même ordre : **un
libellé qui décrit une position n'est pas une information.**

* `R4` — « PASSER À E2 » ne dit pas ce qu'on va faire. Le code de position est
  connu du produit, pas de l'utilisateur.
* `Q-C` — marquer les échauffements comme faits fabriquerait des données
  d'entraînement que personne n'a produites. Un échauffement non fait n'est
  pas un échauffement fait — et c'est la garde la plus importante de ce
  fichier, parce que l'erreur inverse serait invisible et définitive.

  ⚠ `UI-CP2.1` a rendu `Q-C` **sans objet plutôt que contredite** : elle
  encadrait la sortie d'échauffement, et il n'y a plus de sortie parce qu'il
  n'y a plus de porte. Rien n'est écrit, parce qu'il n'y a plus d'obstacle à
  contourner. L'interdiction d'écrire, elle, survit intacte — recentrée sur
  la traversée ordinaire de l'exercice.
* `Q-E` — « Push A — Pecs épaisseur + Delts + Triceps » est un nom de
  GABARIT : il décrit ce que le programme contient, pas ce qu'on travaille.

Ces tests vérifient le **comportement rendu**, pas la forme des chaînes dans
le code : un libellé assemblé à deux endroits diverge, et c'est ce qui rendait
la garde de source insuffisante.
"""

from __future__ import annotations

import html
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
    """État minimal en `WARMUP`, sans base : on teste le libellé, pas le flux.

    ⚠ `UI-CP2.1` — le montage portait `[warmup, work]` et ne rendait donc plus
    `WARMUP` du tout : la garde restait verte en observant un état de travail,
    ce que son nom démentait. Le seul échauffement souverain qui subsiste est
    celui d'un exercice sans série de travail.
    """
    class _SL:
        def __init__(self, kind, idx, completed=False):
            self.kind, self.set_index, self.completed = kind, idx, completed
            self.id, self.weight_kg, self.reps = idx, None, None

    class _SE:
        set_logs = [_SL("warmup", 1)]
        template_exercise = None

    return build_console_state(
        _SE(), next_code="E2", next_name="Chest Press machine"
    )


# ───────────────── `Q-C` — sauter n'écrit RIEN ─────────────────


def test_traversing_the_exercise_writes_no_warmup(client):
    """⚠ RECIBLÉE par `UI-CP2.1` — elle observait un paramètre supprimé.

    Elle passait encore, et ne mesurait plus rien : `?skipwarm=1` n'existe
    plus, et un paramètre inconnu est ignoré. Une garde qui interroge un
    objet disparu rend vert par construction — c'est la forme la plus
    silencieuse de garde qui ne garde rien.

    L'enjeu, lui, n'a pas bougé et il est le cœur de `Q-C` : **un échauffement
    non fait n'est pas un échauffement fait.** Il est même plus exposé
    qu'avant — puisque l'utilisateur traverse désormais tout l'exercice sans
    jamais toucher le tiroir, rien ne doit s'y écrire en son nom.

    ⚠ Portée exacte, parce que la surestimer serait le défaut que ce fichier
    combat : on vérifie que **la consultation est inerte**. Un `GET` n'écrit
    jamais, quel que soit le contrôle qui l'a produit ; c'est
    `test_the_warmup_drawer_carries_no_submit_control` qui tient l'autre
    moitié, et il la tient par construction. Les deux ensemble tiennent
    l'invariant ; séparément, aucun ne suffit.
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

    r = client.get(f"/sessions/{session_id}?active={se_id}")
    assert r.status_code == 200

    assert snapshot() == before, (
        "consulter l'exercice a MODIFIÉ des séries — un échauffement non fait "
        "ne doit jamais devenir un échauffement fait"
    )


def test_the_instrument_opens_on_the_work_set_with_no_parameter_at_all(client):
    """⚠ SUPERSÈDE `test_skipping_the_warmup_moves_the_instrument_to_the_work_set`.

    L'ancienne garde exigeait que `?skipwarm=1` ait un effet visible. Elle
    tenait donc l'existence même de la porte — or `UI-CP2.1` retire la porte,
    sur constat d'usage : le saut ne survivait pas au rechargement, parce que
    l'intention vivait dans l'URL et que `Q-C` interdit de l'écrire en base.

    La remplaçante est **plus forte, et c'est la plainte de l'opérateur prise
    au mot** : il ne faut plus AUCUN paramètre. L'exercice s'ouvre sur sa
    première série de travail, et un rechargement nu n'y renvoie pas
    l'échauffement.
    """
    session_id = _start(client)
    se_id = _exercises(session_id)[0][0]

    nu = client.get(f"/sessions/{session_id}?active={se_id}").text
    assert 'data-console-state="warmup"' not in nu, (
        "l'exercice s'ouvre encore sur l'échauffement — c'est la porte que "
        "`UI-CP2.1` retire"
    )
    assert 'data-console-state="current_set"' in nu, nu[:0]

    # Et le rechargement — le geste exact qui ramenait l'échauffement.
    encore = client.get(f"/sessions/{session_id}?active={se_id}").text
    assert 'data-console-state="warmup"' not in encore, (
        "un simple rechargement a ramené l'échauffement"
    )


def test_the_warmup_drawer_carries_no_submit_control():
    """⚠ SUPERSÈDE `test_the_skip_is_a_link_not_a_submission`.

    Le risque que l'ancienne garde tenait est intact, seul son porteur a
    changé. Un `<button type="submit">` **à l'emplacement de l'échauffement**
    soumettrait la carte entière au passage — et `_persist_set_values` écrit
    alors les séries que porte le DOM. L'ancienne garde le tenait pour le
    bouton de saut ; le tiroir d'échauffement occupe désormais cette place.

    Le tiroir reste SAISISSABLE — c'est là qu'on s'échauffe, et `UI-CP2.1`
    n'a retiré que son caractère obligatoire. Ce qu'il ne doit pas porter,
    c'est une commande qui enregistre : elle serait une porte déguisée.

    Structurel et non comportemental, et c'est assumé : le risque vit dans le
    CONTRÔLE, pas dans la requête qu'il produit.
    """
    from pathlib import Path

    card = (
        Path(__file__).resolve().parent.parent
        / "app/templates/_partials/exercise_card.html"
    )
    markup = re.sub(r"\{#.*?#\}", "", card.read_text(encoding="utf-8"), flags=re.DOTALL)
    m = re.search(r"<details class=\"warmup-recap.*?</details>", markup, re.DOTALL)
    assert m, "le tiroir d'échauffement a disparu du gabarit"
    drawer = m.group(0)
    assert "type=\"submit\"" not in drawer, (
        "un submit dans le tiroir enregistrerait la carte entière"
    )
    assert "<button" not in drawer, (
        "aucune commande dans le tiroir : l'échauffement n'est plus une étape "
        "qu'on franchit"
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


# ───────────────── `Q-D` — le fil ne perd rien ─────────────────


def test_the_thread_keeps_every_fact_the_cards_carried(client):
    """`Q-D = B` / `§5.3` — **une compaction, pas une soustraction.**

    Les six exercices en attente passent de cartes pleines à des rangées.
    L'arbitrage était explicite : le fil doit REPRENDRE ce que les cartes
    portaient, pas l'effacer.

    Ce test ne fait pas confiance à cette intention : il vérifie que chaque
    fait est encore rendu, exercice par exercice — le code, le nom, et
    l'avancement. Ce sont les trois que la carte annonçait en premier rang.
    """
    session_id = _start(client)
    exercises = _exercises(session_id)
    # ⚠ `unescape` : Jinja échappe l'apostrophe en `&#39;`, donc
    # « Écarté arrière d'épaule câble » ne se trouve JAMAIS tel quel dans le
    # HTML. Sans cela la garde signalait un nom perdu qui était bien rendu —
    # un faux positif qui aurait fait chercher un défaut inexistant.
    body = html.unescape(client.get(f"/sessions/{session_id}").text)

    # Le premier exercice est ACTIF : il n'est pas dans le fil.
    missing = []
    for _se_id, code, name in exercises[1:]:
        if code not in body:
            missing.append(f"code {code}")
        if name not in body:
            missing.append(f"nom {name}")
    assert missing == [], f"le fil a perdu : {missing}"

    # ⚠ `UI-CP2` — LE FIL N'EXISTE PLUS, ET C'EST LE CŒUR DE LA REFONTE.
    #
    # `Q-D` avait compacté six cartes en six rangées, et exigeait à juste
    # titre que la compaction ne soit pas une soustraction. A+ va au bout : la
    # surface primaire se recompose avec l'ÉTAT, et six performances passées
    # empilées ne servent pas la question « que fais-je maintenant ».
    #
    # `§5.3` tient toujours, et c'est ce qui est vérifié : l'avancement de
    # chaque exercice reste porté — par le nom accessible des pastilles
    # d'orientation — et sa « dernière fois » l'atteint dans SA console, au
    # point de décision, en un lien.
    for _se_id, code, _name in exercises[1:]:
        assert f'aria-label="{code} —' in body, (
            f"l'avancement de {code} n'est plus annoncé"
        )
    assert "séries" in body, "l'avancement a quitté l'orientation"


def test_the_thread_row_is_still_a_whole_target(client):
    """La rangée entière reste le lien.

    C'est ce qui autorise à retirer le plancher de 44 px de la ligne
    d'identité : la cible est le parent. Si la rangée cessait d'être un lien,
    on aurait retiré un plancher sans que rien ne le remplace.
    """
    session_id = _start(client)
    body = client.get(f"/sessions/{session_id}").text
    # `UI-CP2` — le porteur change, la propriété reste : l'accès à un autre
    # exercice est un LIEN, et sa cible tactile est portée par la boîte de
    # 44 px de la pastille (vérifié sur la feuille de style dans
    # `test_ui_cp2_execution_aplus`).
    assert re.search(
        r'<a[^>]*class="[^"]*xc-strip__pip', body
    ), "l'accès aux autres exercices n'est plus un lien"


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
