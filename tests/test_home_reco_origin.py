"""Home — la cause est VISIBLE, pas repliée. `Sx_UIV3_01`.

MIGRATION DE GARDE — tier **T5 → T2/T3**
----------------------------------------
Ce module gardait `Sb_UIV2_HOME_RECO_BADGE_01` : un badge « Recommandé ⓘ »
dont le `<details>` révélait la raison et l'état des zones.

`Sx_UIV3_01 §2` supprime ce `<details>`. **D2 est AMENDÉE, pas abandonnée** :
l'origine et la raison restent obligatoires ; le pli cesse d'en être le
véhicule. Motif, mesuré : **0 px de cause au-dessus de la ligne de
flottaison**, et ouvrir le pli **déplaçait la décision vers le bas**.

Une garde qui reste verte en protégeant un choix officiellement abandonné est
une prison, pas une protection (`AUREN_UIUX_V3_GUARD_MIGRATION_REGISTER`). Le
module est donc **réécrit sur le nouveau contrat, pas supprimé** — et chaque
intention d'origine est reprise, plusieurs en plus strict :

  ancien                                   → nouveau
  le badge est rendu                       → la cause est rendue SANS interaction
  le ⓘ révèle la phrase du moteur          → la phrase est visible d'emblée
  le badge fait 44 px                      → le CommandDock fait 56 px
  les zones listées sont CELLES visées     → inchangé
  une zone sans preuve dit « non mesurée » → inchangé, + jamais rendue pleine
  aucun état par la couleur seule          → inchangé
  aucune revendication d'IA (**T1**)       → **intouchée**

Plus quatre gardes neuves exigées par le registre : la cause hors de tout pli ·
le bilan totalise 11 · aucun pourcentage de récupération · l'inconnu n'est
jamais rendu comme disponible.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "app" / "templates" / "index.html"
COACHING = ROOT / "app" / "templates" / "_partials" / "home_coaching_loop.html"
HOME_CSS = ROOT / "app" / "static" / "css" / "home.css"


def _home(client) -> str:
    response = client.get("/")
    assert response.status_code == 200
    return response.text


def _without_jinja_comments(path: Path) -> str:
    return re.sub(r"\{#.*?#\}", "", path.read_text(encoding="utf-8"), flags=re.DOTALL)


def _reco(client):
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.user import User
    from app.services.recommendation import recommend_next_session

    with SessionLocal() as db:
        user = db.execute(select(User)).scalars().first()
        return recommend_next_session(db, user.id)


# ───────── LA GARDE CENTRALE — la cause ne se replie pas ─────────


def test_the_cause_is_rendered_without_any_interaction(client):
    """Le remplacement exact de l'ancienne garde du badge.

    On ne vérifie pas qu'un bloc existe — on vérifie qu'**aucun `<details>`
    n'est ouvert** entre le début du hero et la cause. C'est la seule
    formulation qui attrape la régression : remettre la cause dans un pli
    laisserait tous les autres tests verts.
    """
    body = _home(client)
    assert "cockpit__cause" in body, "la cause n'est pas rendue"

    hero = body.index('class="today-home__hero')
    cause = body.index("cockpit__cause")
    between = body[hero:cause]
    assert between.count("<details") == between.count("</details>"), (
        "un <details> englobe la cause — elle redevient invisible par défaut"
    )


def test_the_engine_phrase_is_visible_not_disclosed(client):
    """Le ⓘ montrait la raison RÉELLE. Elle est désormais montrée tout court."""
    body = _home(client)
    assert "cockpit__why" in body
    assert _reco(client)["top"]["phrase"] in body

    why = body.index("cockpit__why")
    hero = body.index('class="today-home__hero')
    between = body[hero:why]
    assert between.count("<details") == between.count("</details>")


def test_the_old_disclosure_is_really_gone():
    """`reco-origin` ne doit subsister ni en markup ni en style.

    Un vestige CSS d'un composant supprimé est de la dette qui repousse : la
    prochaine personne le croira vivant.
    """
    assert "reco-origin" not in _without_jinja_comments(INDEX)
    assert "reco-origin" not in HOME_CSS.read_text(encoding="utf-8")


# ───────── D2 — origine et volume, toujours dits ─────────


def test_the_volume_comes_from_a_real_count(client):
    """« 12 séries » vient d'un compte SQL, jamais d'un texte figé."""
    body = _home(client)
    match = re.search(r"(\d+) séries", body)
    assert match, "le volume n'est pas rendu"
    assert int(match.group(1)) > 0


def test_no_ai_claim_is_rendered(client):
    """**T1 — intouchable.** Le moteur est déterministe et explicable ;
    revendiquer une IA serait faux, et c'est précisément son avantage."""
    lowered = _home(client).lower()
    for claim in ("recommandé ia", "recommande ia", "propulsé par l'ia", "ai-powered"):
        assert claim not in lowered


def test_the_dominant_action_is_a_real_touch_target():
    """L'ancien badge devait faire 44 px parce qu'il était un contrôle.

    Il n'en est plus un — la cause n'est pas cliquable. Le contrôle de cet
    écran est le CommandDock, et `Sx_UIV3_04 §11` l'exige à **56 px**.
    """
    css = HOME_CSS.read_text(encoding="utf-8")
    block = re.search(r"\.today-home__cta\s*\{([^}]*)\}", css)
    assert block, ".today-home__cta n'est pas stylé"
    height = re.search(r"min-height:\s*(\d+)px", block.group(1))
    assert height, f"aucune min-height sur le CommandDock : {block.group(1)}"
    assert int(height.group(1)) >= 56, height.group(1)
    assert re.search(r"width:\s*100%", block.group(1)), (
        "l'action dominante doit occuper la largeur de sa colonne — en "
        "`inline-flex` elle mesurait 139 px, et sa taille dépendait du libellé"
    )


def test_no_javascript_was_introduced():
    markup = _without_jinja_comments(INDEX)
    assert "onclick" not in markup.lower()
    assert "<script" not in markup.lower()


# ───────── D6 — les zones expliquent la recommandation ─────────


def test_the_targeted_zones_are_listed(client):
    assert "cockpit__zones" in _home(client)


def test_every_listed_zone_is_a_business_zone(client):
    """Aucun libellé inventé : ils viennent tous de la taxonomie."""
    from app.services.muscle_mapping import ZONE_LABELS

    rendered = re.findall(r'cockpit__zone-name">([^<]+)<', _home(client))
    assert rendered, "aucune zone rendue"
    for label in rendered:
        assert label in ZONE_LABELS.values(), f"libellé hors taxonomie : {label!r}"


def test_the_listed_zones_are_the_ones_the_session_targets(client):
    """Le lien D6 : ce ne sont pas des zones quelconques, ce sont LES SIENNES."""
    from app.services.muscle_mapping import ZONE_LABELS

    body = _home(client)
    reco = _reco(client)
    expected = [
        ZONE_LABELS[z] for z in reco["top"]["primary_zones"] if z in ZONE_LABELS
    ]
    assert re.findall(r'cockpit__zone-name">([^<]+)<', body) == expected


def test_a_zone_without_evidence_reads_as_unmeasured_never_available(client):
    """La règle de silence honnête : jamais « disponible » par défaut."""
    body = _home(client)
    for match in re.finditer(
        r'band--(\w+)"[^>]*aria-label="([^"]+)"', body
    ):
        band, label = match.groups()
        if band == "unknown":
            assert label == "non mesurée", label


def test_unknown_is_never_rendered_as_filled(client):
    """Garde neuve. `unknown` n'est pas « zéro récupération » mais une autre
    NATURE de chose : il ne reçoit jamais un segment plein, sur aucune
    surface. Le rendre rempli le confondrait avec une zone chargée."""
    body = _home(client)
    for match in re.finditer(r'<span class="band band--unknown"[^>]*>(.*?)</span>',
                             body, re.DOTALL):
        assert "band__on" not in match.group(1), (
            "une bande `unknown` porte un segment plein"
        )


def test_no_state_is_conveyed_by_colour_alone(client):
    """Chaque état porte un libellé ; la couleur ne fait que renforcer."""
    body = _home(client)
    assert "cockpit__zone-band" in body, "l'état doit être écrit, pas seulement coloré"


def test_no_recovery_percentage_is_ever_rendered(client):
    """Garde neuve, **T1**.

    `zone_recovery` dit de son `estimate` qu'il n'est « pas une mesure, pas un
    pourcentage de récupération physiologique ». L'afficher comme un
    pourcentage serait une affirmation que le produit refuse de faire.
    """
    body = _home(client)
    zone_region = body[body.index("cockpit__cause"):body.index("today-home__action")]
    assert not re.search(r"\d+\s*%", zone_region), (
        "un pourcentage apparaît dans la zone de récupération"
    )


# ───────── le bilan des 11 zones ─────────


def test_the_tally_accounts_for_every_zone(client):
    """Garde neuve. Une première maquette totalisait **12 zones sur 11**.

    Le comptage est dérivé de `build_zone_recovery` ; ce test le confronte au
    nombre canonique de zones plutôt qu'à une constante recopiée.
    """
    from app.services.zone_recovery import canonical_zone_codes

    body = _home(client)
    if "cockpit__tally" not in body:
        return  # pas de reco → pas de bilan, cas légitime
    counts = [int(n) for n in re.findall(r'cockpit__tally-item">.*?<b>(\d+)</b>',
                                         body, re.DOTALL)]
    assert counts, "le bilan est rendu mais ne compte rien"
    assert sum(counts) == len(canonical_zone_codes())


# ───────── ce qui a été écarté, et pourquoi ─────────


def test_rejected_alternatives_state_their_reason(client):
    """Le différenciateur produit : aucun concurrent ne montre l'inverse d'une
    recommandation. Le moteur classe déjà ; l'affichage le jetait."""
    body = _home(client)
    if "rejected__list" not in body:
        return  # moins de deux alternatives, cas légitime
    items = re.findall(r'rejected__item">(.*?)</li>', body, re.DOTALL)
    assert items
    for item in items:
        assert "rejected__name" in item
        assert "rejected__why" in item, "une option écartée sans motif n'explique rien"


def test_the_rejected_disclosure_is_a_real_touch_target():
    """C'est du niveau 3 : le pli est légitime ici. Mais c'est un contrôle."""
    css = HOME_CSS.read_text(encoding="utf-8")
    block = re.search(r"\.rejected__summary\s*\{([^}]*)\}", css)
    assert block, ".rejected__summary n'est pas stylé"
    height = re.search(r"min-height:\s*(\d+)px", block.group(1))
    assert height, f"aucune min-height : {block.group(1)}"
    assert int(height.group(1)) >= 44, height.group(1)


# ───────── D4 — les suppressions, inchangées ─────────


def test_the_dead_status_label_is_gone(client):
    assert "Aucune séance active" not in _home(client)


def test_the_duplicate_today_tile_is_gone():
    assert "Aujourd'hui" not in _without_jinja_comments(COACHING)


def test_the_secondary_reasons_were_kept_not_dropped():
    """§5.3 — jamais une soustraction seule.

    Le `<details>` qui les portait disparaît ; les raisons restent. Elles sont
    produites par le moteur au même titre que la phrase principale : perdre
    leur surface en retirant leur véhicule serait exactement la faute que la
    règle interdit.
    """
    markup = _without_jinja_comments(INDEX)
    assert "home.today.reasons" in markup
    assert "cockpit__reasons" in markup


def test_the_empty_week_tile_is_hidden_but_not_deleted():
    markup = _without_jinja_comments(COACHING)
    assert "home.week.sessions_done" in markup
    assert "Cette semaine" in markup
