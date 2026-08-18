"""Sb_UIV2_HOME_RECO_BADGE_01 — le hero dit QUOI, le ⓘ dit POURQUOI.

CE QUE CETTE TRANCHE AFFIRME
----------------------------
Deux décisions validées, rendues exécutables :

**D2** — la recommandation annonce son origine. Le badge « Recommandé » porte le
volume et un ⓘ qui révèle la **vraie phrase du moteur**, calculée par
`recommendation.py` depuis toujours et jamais affichée. Interdit absolu :
revendiquer une IA — le moteur est déterministe et explicable, et c'est son
avantage.

**D6** — le cycle de ce produit est piloté par la **récupération**, pas par un
calendrier. L'état des zones n'est donc pas une vignette posée à côté de la
recommandation : c'est **son explication**. Ces tests pinnent le lien.

**D4** — trois suppressions, et la règle qui les gouverne : on retire le
doublon, jamais l'information.
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


# ───────────── D2 — le badge d'origine ─────────────

def test_the_badge_is_rendered(client):
    body = _home(client)
    assert "reco-origin__badge" in body
    assert "Recommandé" in body


def test_the_badge_states_the_volume(client):
    """« 21 séries » — le volume vient d'un compte réel, pas d'un texte figé."""
    body = _home(client)
    match = re.search(r'reco-origin__volume">(\d+) séries<', body)
    assert match, "le volume n'est pas rendu"
    assert int(match.group(1)) > 0


def test_the_info_reveals_the_engine_phrase(client):
    """Le ⓘ montre la raison RÉELLE, pas une formule d'habillage."""
    from app.services.recommendation import recommend_next_session

    body = _home(client)
    assert "reco-origin__why" in body

    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.execute(select(User)).scalars().first()
        reco = recommend_next_session(db, user.id)
    assert reco["top"]["phrase"] in body


def test_the_disclosure_needs_no_javascript():
    """`<details>` natif : le ⓘ s'ouvre sans script, comme tout le reste du produit."""
    markup = _without_jinja_comments(INDEX)
    assert "<details class=\"reco-origin\">" in markup
    assert "onclick" not in markup.lower()


def test_the_badge_is_a_real_touch_target():
    """D1 rang 2 : c'est un contrôle, donc ≥ 44 px."""
    css = HOME_CSS.read_text(encoding="utf-8")
    block = css[css.index(".reco-origin__badge"):css.index(".reco-origin__label")]
    assert "min-height: 44px" in block


def test_no_ai_claim_is_rendered(client):
    """D2, interdiction dure. Vérifiée sur le HTML SERVI, pas sur le template."""
    lowered = _home(client).lower()
    for claim in ("recommandé ia", "recommande ia", "propulsé par l'ia", "ai-powered"):
        assert claim not in lowered


# ───────────── D6 — l'état corporel explique la recommandation ─────────────

def test_the_targeted_zones_are_listed(client):
    body = _home(client)
    assert "reco-origin__zones" in body


def test_every_listed_zone_is_a_business_zone(client):
    """Aucun libellé inventé : ils viennent tous de la taxonomie."""
    from app.services.muscle_mapping import ZONE_LABELS

    body = _home(client)
    rendered = re.findall(r'reco-origin__zone-name">([^<]+)<', body)
    assert rendered, "aucune zone rendue"
    for label in rendered:
        assert label in ZONE_LABELS.values(), f"libellé hors taxonomie : {label!r}"


def test_the_listed_zones_are_the_ones_the_session_targets(client):
    """Le lien D6 : ce ne sont pas des zones quelconques, ce sont LES SIENNES."""
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.user import User
    from app.services.muscle_mapping import ZONE_LABELS
    from app.services.recommendation import recommend_next_session

    body = _home(client)
    with SessionLocal() as db:
        user = db.execute(select(User)).scalars().first()
        reco = recommend_next_session(db, user.id)

    expected = [ZONE_LABELS[z] for z in reco["top"]["primary_zones"] if z in ZONE_LABELS]
    rendered = re.findall(r'reco-origin__zone-name">([^<]+)<', body)
    assert rendered == expected


def test_a_zone_without_evidence_reads_as_unmeasured_never_available(client):
    """La règle de silence honnête : jamais « disponible » par défaut."""
    body = _home(client)
    for match in re.finditer(
        r'reco-origin__zone--(\w+)">\s*<span[^>]*>([^<]+)</span>\s*<span[^>]*>([^<]+)<',
        body,
    ):
        band, _, band_label = match.groups()
        if band == "unknown":
            assert band_label == "non mesurée"


def test_no_state_is_conveyed_by_colour_alone():
    """Contrat BodyMap : chaque état porte un libellé, la couleur ne fait que renforcer."""
    markup = _without_jinja_comments(INDEX)
    assert "reco-origin__zone-band" in markup, "l'état doit être écrit, pas seulement coloré"


# ───────────── D4 — les suppressions ─────────────

def test_the_dead_status_label_is_gone(client):
    assert "Aucune séance active" not in _home(client)


def test_the_duplicate_today_tile_is_gone():
    """Le hero portait déjà « Aujourd'hui » ; la vignette le répétait."""
    assert "Aujourd'hui" not in _without_jinja_comments(COACHING)


def test_the_secondary_reasons_were_kept_not_dropped():
    """On retire le doublon, pas l'information : elles vivent dans le ⓘ."""
    markup = _without_jinja_comments(INDEX)
    assert "home.today.reasons" in markup
    assert "reco-origin__reasons" in markup


def test_the_empty_week_tile_is_hidden_but_not_deleted():
    """« Pas encore de séance » n'apprend rien ; 3 séances, si."""
    markup = _without_jinja_comments(COACHING)
    assert "home.week.sessions_done" in markup
    assert "Cette semaine" in markup, "la vignette doit revenir dès qu'il y a un signal"
