"""`UX4_02` / TRAIN 2 tranche B — le corpus commun, contextualisé.

CE QUE CES GARDES FERMENT
--------------------------
`OPERATOR_DECISION` **C8** pose une contrainte que rien dans le rendu ne
signale quand on la franchit : **aucun moteur de recommandation opaque,
contexte de plan explicite uniquement**. Un classement discret, un gabarit
masqué, un score inventé — tout cela produit une page qui a l'air très bien.

Les gardes portent donc sur les cinq façons de franchir la ligne :

  1. **LE CORPUS SE RÉTRÉCIT** — un gabarit disparaît sans que l'utilisateur
     l'ait demandé.
  2. **LE CORPUS SE RÉORDONNE** — un tri « pertinence » est un classement, donc
     un jugement, donc un moteur.
  3. **UNE ZONE EST INVENTÉE** — l'annotation cesse de venir du résolveur
     canonique et devient une paraphrase du champ `focus`, qui est du texte
     libre.
  4. **UNE PRIORITÉ EST DEVINÉE** — la marque « déclarée » apparaît sans
     déclaration.
  5. **LE FILTRE DEVIENT UNE DÉCISION DU PRODUIT** — appliqué sans demande, ou
     sans moyen d'en sortir.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIB_TPL = ROOT / "app/templates/library.html"
SERVICE = ROOT / "app/services/template_zone_context.py"

LIBRARY_URL = "/library"
#: `lats` est la zone de l'axe déclaré `back_width` — le couple sert de témoin
#: dans les deux sens (fait résolu ↔ déclaration).
ZONE = "lats"
ZONE_LABEL = "Dos largeur"
AXIS = "back_width"


def _executable(src: str) -> str:
    """Source sans docstrings NI commentaires.

    Une garde qui interdit le mot « score » et scanne la prose échoue sur le
    paragraphe qui explique justement qu'on ne calcule aucun score. C'est
    arrivé au premier jet de ce fichier.
    """
    body = re.sub(r'"""[\s\S]*?"""', " ", src)
    return "\n".join(line.split("#", 1)[0] for line in body.splitlines())


def _cards(html: str) -> list[str]:
    """Une carte = du marqueur d'ouverture au marqueur suivant.

    ⚠ PAS une expression jusqu'au premier `</li>`. Les zones sont rendues dans
    une liste IMBRIQUÉE : une telle expression coupait la carte avant ses
    zones, et deux gardes passaient alors pour la mauvaise raison — l'une
    constatait l'absence du texte libre dans un fragment tronqué avant lui.
    Trouvé parce qu'une troisième garde, elle, a échoué.
    """
    # ⚠ Le marqueur inclut la variante de type. `<li class="template-card`
    # seul attrapait AUSSI les `template-card__zone` — les éléments de zone que
    # cette tranche vient d'ajouter — et découpait des fragments qui n'étaient
    # pas des cartes. Un préfixe de classe n'est pas un sélecteur.
    marker = '<li class="template-card template-card--'
    end = "</form>"
    out = []
    for part in html.split(marker)[1:]:
        assert end in part, "carte sans formulaire de démarrage — borne caduque"
        out.append(marker + part.split(end, 1)[0] + end)
    return out


def _slugs(html: str) -> list[str]:
    """Slugs dans l'ORDRE DE RENDU — l'ordre est ce qu'on garde."""
    return re.findall(r'href="[^"]*/library/([a-z0-9-]+)"', html)


def _declare(uid, **kw):
    from app.database import SessionLocal
    from app.services.training_preferences import save_training_preferences

    with SessionLocal() as db:
        save_training_preferences(db, uid, **kw)


def _uid():
    from tests.helpers import get_test_user_id

    return get_test_user_id()


# ═════════ LE CORPUS RESTE COMMUN, ENTIER ET DANS SON ORDRE ═════════


def test_the_corpus_is_whole_and_identical_with_or_without_a_declaration(client):
    """LE CŒUR DE C8. Une déclaration contextualise, elle ne sélectionne pas.
    Si déclarer changeait la composition du catalogue, le produit choisirait à
    la place de l'utilisateur — c'est la définition du moteur interdit."""
    before = _slugs(client.get(LIBRARY_URL).text)
    _declare(_uid(), sessions_per_week=4, focus_priorities=[AXIS])
    after = _slugs(client.get(LIBRARY_URL).text)

    assert before, "aucun gabarit rendu — la garde ne mesurerait rien"
    assert after == before, (
        f"la déclaration a changé le corpus : {set(before) ^ set(after)} "
        f"— ordre avant {before} / après {after}"
    )


def test_the_order_is_the_catalogue_order_not_a_relevance_ranking(client):
    """Un tri par pertinence est un classement, donc un jugement. L'ordre rendu
    doit être celui du catalogue (`display_order`, `slug`), déclaration ou
    pas."""
    from app.database import SessionLocal
    from app.models.catalog import WorkoutTemplate

    _declare(_uid(), sessions_per_week=4, focus_priorities=[AXIS])
    with SessionLocal() as db:
        expected = [
            t.slug for t in db.query(WorkoutTemplate)
            .order_by(WorkoutTemplate.display_order, WorkoutTemplate.slug).all()
            if t.catalog_section not in ("archived", "user")
        ]
    assert _slugs(client.get(LIBRARY_URL).text) == expected


def test_no_score_no_rank_no_match_percentage_is_rendered(client):
    """Le vocabulaire d'un moteur laisse des traces. Aucune ne doit exister."""
    _declare(_uid(), sessions_per_week=4, focus_priorities=[AXIS])
    body = client.get(LIBRARY_URL).text.lower()
    for banned in ("recommandé pour toi", "score", "pertinence",
                   "correspondance", "match", "% adapté", "meilleur choix"):
        assert banned not in body, f"vocabulaire de moteur rendu : « {banned} »"


def test_the_service_produces_no_ordering_and_no_score():
    """Garde STRUCTURELLE sur le producteur : une surface honnête devant un
    service qui classe resterait un service qui classe."""
    body = _executable(SERVICE.read_text(encoding="utf-8"))
    for banned in ("sort(", "sorted(", "score", "rank", "reverse=True"):
        assert banned not in body, f"le service classe ou note : « {banned} »"


# ═════════ L'ANNOTATION EST UN FAIT, PAS UNE PARAPHRASE ═════════


def test_the_zones_come_from_the_canonical_resolver():
    """Le champ `focus` est du texte libre (« Adducteurs », « Grand dorsal ») :
    il ne partage pas le vocabulaire des zones et ne peut pas en tenir lieu.
    L'autorité est `resolve_zone`."""
    src = SERVICE.read_text(encoding="utf-8")
    assert "from app.services.exercise_zone_resolver import resolve_zone" in src
    assert ".focus" not in _executable(src), (
        "le service lit le texte libre `focus`"
    )


def test_every_rendered_zone_label_is_canonical(client):
    """Une étiquette hors `ZONE_LABELS` serait une zone inventée."""
    from app.services.muscle_mapping import ZONE_LABELS

    body = client.get(LIBRARY_URL).text
    rendered = re.findall(
        r'<li class="template-card__zone[^"]*">\s*([^<]+?)\s*(?:<|$)', body)
    assert rendered, "aucune zone rendue — la garde ne mesurerait rien"
    unknown = sorted(set(rendered) - set(ZONE_LABELS.values()))
    assert not unknown, f"zones hors vocabulaire canonique : {unknown}"


def test_a_template_without_resolvable_zones_renders_no_empty_list(client):
    """Le LISS pur n'a aucun exercice. Doctrine A4 : pas de module vide, pas de
    « aucune zone ». Il garde son texte libre, qui est tout ce qu'il a."""
    body = client.get(LIBRARY_URL).text
    assert '<ul class="template-card__zones">\n              </ul>' not in body
    liss = [c for c in _cards(body) if "liss-only" in c]
    assert len(liss) == 1, "le gabarit témoin a disparu du catalogue"
    assert "template-card__zones" not in liss[0]
    assert "Cardio faible intensite" in liss[0], (
        "sans zones ET sans texte libre, la carte ne dit plus rien"
    )


def test_the_free_text_line_is_replaced_not_duplicated(client):
    """La substitution décidée AU RENDU : les deux lignes disaient deux fois la
    même chose en deux vocabulaires. Une carte qui a des zones ne rend plus son
    texte libre — et le détail, lui, le garde."""
    body = client.get(LIBRARY_URL).text
    push = [c for c in _cards(body) if "push-a" in c]
    assert len(push) == 1
    assert "template-card__zones" in push[0]
    assert "template-card__focus" not in push[0], "doublon de vocabulaire rendu"
    assert "Pectoraux, Deltoïdes, Triceps" in client.get("/library/push-a").text


# ═════════ LA PRIORITÉ EST RAPPELÉE, JAMAIS DEVINÉE ═════════


def test_nothing_is_marked_as_declared_without_a_declaration(client):
    body = client.get(LIBRARY_URL).text
    assert "is-declared" not in body
    assert "priorités déclarées" not in body


def test_the_declared_axis_is_marked_on_the_zones_it_covers(client):
    """Le pendant : une garde qui ne teste que l'absence laisserait passer une
    surface qui ne marque jamais rien."""
    _declare(_uid(), sessions_per_week=4, focus_priorities=[AXIS])
    body = client.get(LIBRARY_URL).text
    assert "is-declared" in body
    marked = re.findall(
        r'<li class="template-card__zone is-declared">\s*([^<]+?)\s*<', body)
    assert marked, "aucune zone marquée alors qu'une priorité est déclarée"
    assert set(marked) == {ZONE_LABEL}, (
        f"marques hors de l'axe déclaré : {sorted(set(marked))}"
    )


def test_the_legend_names_the_axis_the_user_declared_not_the_zone(client):
    """L'utilisateur a déclaré « Bras », pas « Biceps ». Lui renvoyer le mot de
    la zone lui prêterait une déclaration qu'il n'a pas faite."""
    _declare(_uid(), sessions_per_week=4, focus_priorities=["arms"])
    body = client.get(LIBRARY_URL).text
    legend = body.split('class="zone-filter__legend"', 1)[1].split("</p>", 1)[0]
    assert "Bras" in legend
    assert "Biceps" not in legend


def test_the_zone_mark_carries_the_axis_word_for_assistive_tech(client):
    """La marque visuelle est une teinte et un soulignement : elle ne dit rien
    à une synthèse vocale. Le texte de rechange doit donc porter l'information,
    et porter le mot que l'utilisateur a employé — l'AXE, pas la zone."""
    _declare(_uid(), sessions_per_week=4, focus_priorities=["arms"])
    body = client.get(LIBRARY_URL).text
    hidden = re.findall(r'<span class="sr-only">\s*([^<]*priorité[^<]*)</span>',
                        body)
    assert hidden, "la marque n'est perceptible que visuellement"
    assert all("Bras" in h for h in hidden), hidden
    assert not any("Biceps" in h or "Triceps" in h for h in hidden), hidden


def test_core_carries_no_declared_mark_because_it_has_no_axis(client):
    """`core` est une des 11 zones et n'a délibérément PAS d'axe radar. Aucune
    déclaration ne peut donc le marquer — ce n'est pas un trou, c'est la
    taxonomie."""
    from app.services.muscle_mapping import RADAR_AXES

    every_axis = list(RADAR_AXES)
    _declare(_uid(), sessions_per_week=4, focus_priorities=every_axis[:3])
    body = client.get(LIBRARY_URL).text
    marked = re.findall(
        r'<li class="template-card__zone is-declared">\s*([^<]+?)\s*<', body)
    assert "Core / Abdos" not in marked


# ═════════ LE FILTRE EST DEMANDÉ, ET ON EN SORT ═════════


def test_no_filter_is_applied_unless_asked(client):
    _declare(_uid(), sessions_per_week=4, focus_priorities=[AXIS])
    assert len(_slugs(client.get(LIBRARY_URL).text)) == 13


def test_an_asked_filter_restricts_and_says_so(client):
    body = client.get(f"{LIBRARY_URL}?zone={ZONE}").text
    slugs = _slugs(body)
    assert 0 < len(slugs) < 13
    assert f"{len(slugs)} séance" in body
    assert "sur 13" in body, "le total disparu, l'utilisateur ne sait plus"
    assert ZONE_LABEL in body


def test_every_template_kept_by_the_filter_really_works_that_zone(client):
    """Un filtre qui garde un gabarit sans la zone demandée ment deux fois."""
    body = client.get(f"{LIBRARY_URL}?zone={ZONE}").text
    for card in _cards(body):
        assert ZONE_LABEL in card, f"gabarit sans {ZONE_LABEL} retenu : {card[:80]}"


def test_the_way_back_to_the_whole_corpus_is_always_there(client):
    """⚠ C'est la DESTINATION qui compte, pas l'étiquette. Ma première écriture
    cherchait la chaîne « Toutes » : en pointant cette puce vers une zone, elle
    restait verte tout en enfermant l'utilisateur dans un filtre. Trouvé en
    plantant le défaut."""
    body = client.get(f"{LIBRARY_URL}?zone={ZONE}").text
    chips = re.findall(r'<a class="zone-filter__chip[^"]*"\s*\n?\s*href="([^"]+)"'
                       r'[\s\S]*?>([^<]+)</a>', body)
    assert chips, "aucune puce rendue — la garde ne mesurerait rien"
    back = [href for href, label in chips if label.strip() == "Toutes"]
    assert len(back) == 1, "la puce de retour a disparu ou s'est dupliquée"
    assert "zone=" not in back[0], (
        f"« Toutes » mène encore à un filtre : {back[0]}"
    )


def test_the_filter_panel_opens_itself_when_a_filter_is_active(client):
    """Replier l'état courant laisserait un catalogue amputé sans dire
    pourquoi."""
    assert "<details class=\"zone-filter\" open>" in client.get(
        f"{LIBRARY_URL}?zone={ZONE}").text
    assert "<details class=\"zone-filter\">" in client.get(LIBRARY_URL).text


def test_an_unknown_zone_is_ignored_rather_than_rendered(client):
    """Une valeur hors vocabulaire ne peut venir que d'une URL bricolée.
    Afficher « 0 résultat pour <valeur> » lui donnerait l'apparence d'une zone
    qui existe."""
    body = client.get(f"{LIBRARY_URL}?zone=pas_une_zone").text
    assert len(_slugs(body)) == 13
    assert "pas_une_zone" not in body


def test_only_zones_some_template_works_are_offered(client):
    """Offrir un filtre qui ne peut rien rendre est une impasse construite
    exprès."""
    body = client.get(LIBRARY_URL).text
    codes = re.findall(r'href="[^"]*/library\?zone=([a-z_]+)"', body)
    assert codes
    for code in codes:
        assert _slugs(client.get(f"{LIBRARY_URL}?zone={code}").text), (
            f"le filtre « {code} » ne rend aucun gabarit"
        )


def test_the_filter_chips_are_reachable_targets():
    """44 px = standard produit AUREN, pas WCAG 2.2. Une puce plus petite
    ferait retomber cette surface sous le plancher que `TRAIN1-E` vient de
    remonter ailleurs."""
    css = (ROOT / "app/static/css/app.css").read_text(encoding="utf-8")
    for selector in (".zone-filter__summary", ".zone-filter__chip"):
        rule = css.split(selector + " {", 1)[1].split("}", 1)[0]
        assert "min-height: 44px" in rule, f"{selector} sous le standard"
