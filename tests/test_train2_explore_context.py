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


def _keys(html: str) -> list[str]:
    """Clés de ligne du registre, dans l'ORDRE DE RENDU.

    ⚠ MIGRÉE PAR `UI-CP4 LOADOUT`. L'ancienne écriture relevait les `href` vers
    `/library/<slug>` — le lien de détail de la carte. Il n'y a plus de carte,
    et le lien de détail ne vit plus que dans le dépli : relever cela sur un
    registre fermé aurait rendu une liste vide, et trois gardes auraient
    constaté « rien n'a changé » en ne mesurant rien.

    L'identité d'une ligne est sa CLÉ DE DÉPLI. C'est la seule chose que la
    ligne porte toujours, ouverte comme fermée.
    """
    # ⚠ PAS `[?&]loadout=`. Sous filtre, l'URL porte `?zone=...&loadout=...`, et
    # Jinja échappe l'esperluette en `&amp;` — la classe de caractères voyait
    # alors « ; » et ne matchait plus rien. Le registre filtré paraissait vide
    # alors qu'il rendait ses lignes : la garde accusait le produit de son
    # propre défaut d'écriture.
    return re.findall(r"loadout=([a-z0-9-]+)\"", html)


def _slugs(html: str) -> list[str]:
    """Slugs de CATALOGUE dans l'ordre de rendu.

    Le registre contient deux types de ligne ; le préfixe les sépare
    (`app.services.loadout.session_key` / `program_key`).
    """
    return [k[2:] for k in _keys(html) if k.startswith("t-")]


def _disclosure(client, key: str) -> str:
    """Le DÉPLI d'une ligne — là où vivent désormais zones et commande.

    Une garde de contenu écrite sur le registre fermé serait verte par vacuité :
    elle observerait un écran qui, par conception, ne contient pas ce qu'elle
    prétend vérifier.

    ⚠ LA BORNE N'EST PAS `</li>`, et ce fichier avait déjà écrit pourquoi à
    propos des cartes : les zones sont rendues dans une liste IMBRIQUÉE, donc
    le premier `</li>` rencontré ferme une ZONE, pas le dépli. Borné ainsi, le
    fragment s'arrêtait après la première pastille et trois gardes accusaient
    le produit de ne pas marquer ce qu'il marquait. J'ai reproduit le défaut que
    ce fichier documentait.

    La borne est la POIGNÉE SUIVANTE : un dépli finit là où la ligne d'après
    commence. Vrai pour une ligne de catalogue ; un dépli de programme, lui,
    contient des poignées imbriquées et demanderait une autre borne.
    """
    body = client.get(f"{LIBRARY_URL}?loadout={key}").text
    assert 'class="loadout__open"' in body, f"la ligne « {key} » ne s'est pas dépliée"
    after = body.split('class="loadout__open"', 1)[1]
    assert 'class="loadout__handle"' in after, (
        f"« {key} » est la dernière ligne : la borne ne tiendrait pas"
    )
    return after.split('class="loadout__handle"', 1)[0]


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
    """Une étiquette hors `ZONE_LABELS` serait une zone inventée.

    ⚠ MIGRÉE PAR `Sb_UI_BIBLIO_01`. Cette garde interrogeait le catalogue NU, à
    l'époque où chaque carte rendait toutes ses zones. Depuis, une pastille
    n'apparaît que si elle DIT quelque chose — priorité déclarée ou zone
    filtrée — donc un catalogue nu n'en rend aucune, et l'assertion
    « aucune zone rendue » tombait.

    L'invariant, lui, n'a pas bougé d'un mot : ce qui est rendu appartient au
    vocabulaire canonique. On lui donne simplement un contexte où quelque chose
    est rendu, au lieu de le tester sur un écran qui n'affiche rien.
    """
    from app.services.muscle_mapping import ZONE_LABELS

    _declare(_uid(), sessions_per_week=4, focus_priorities=[AXIS])
    open_push = _disclosure(client, "t-push-a")
    rendered = re.findall(
        r'<li class="loadout__zone[^"]*">\s*([^<]+?)\s*(?:<|$)', open_push)
    assert rendered, "aucune zone rendue — la garde ne mesurerait rien"
    unknown = sorted(set(rendered) - set(ZONE_LABELS.values()))
    assert not unknown, f"zones hors vocabulaire canonique : {unknown}"


def test_a_template_without_resolvable_zones_says_so_rather_than_nothing(client):
    """LE LISS PUR N'A AUCUN EXERCICE — ET LE PRODUIT LE SAIT.

    ⚠ RETOURNÉE PAR `UI-CP4 LOADOUT §7`, et c'est un changement de doctrine
    assumé. L'ancienne garde exigeait qu'il ne soit **rien** rendu : pas de
    module vide, pas de « aucune zone » (A4). Mais rendre le même vide pour
    « aucun exercice » et pour « des exercices qu'on ne reconnaît pas »
    confondait une CONNAISSANCE avec un TROU.

    La doctrine A4 interdit le module vide et le reproche ; elle n'a jamais
    demandé de taire un fait. Ce que le produit sait, il le dit.
    """
    open_liss = _disclosure(client, "t-liss-only")
    assert 'class="loadout__zones"' not in open_liss, "liste de zones vide rendue"
    assert "Aucune zone prescrite" in open_liss
    # Et surtout : PAS le vocabulaire de l'inconnu, qui serait faux ici.
    assert "non cartographiées" not in open_liss


def test_the_free_text_line_is_replaced_not_duplicated(client):
    """La substitution : les deux lignes disaient deux fois la même chose en
    deux vocabulaires. Le texte libre `focus` ne remonte pas sur le registre —
    et le détail, lui, le garde.

    ⚠ MIGRÉE PAR `UI-CP4`. `focus` ne survit plus nulle part sur cette surface,
    pour aucun gabarit : la ligne porte le NOM et la CHARGE, le dépli porte les
    zones. La garde se durcit donc — elle ne vérifie plus une substitution
    conditionnelle mais une absence totale.
    """
    from app.services.template_zone_context import annotate_templates

    body = client.get(LIBRARY_URL).text
    assert "template-card__focus" not in body, "doublon de vocabulaire rendu"
    assert "Pectoraux, Deltoïdes, Triceps" not in body, "texte libre remonté"
    assert "Pectoraux, Deltoïdes, Triceps" in client.get("/library/push-a").text

    # La prémisse elle-même, mesurée : ce gabarit résout bien des zones.
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.catalog import WorkoutTemplate

    with SessionLocal() as db:
        tpl = db.execute(
            select(WorkoutTemplate).where(WorkoutTemplate.slug == "push-a")
        ).scalar_one()
        assert annotate_templates(db, [tpl])[tpl.id].zones, (
            "push-a ne résout plus aucune zone : la garde ne mesure plus la "
            "substitution qu'elle prétend garder"
        )


# ═════════ LA PRIORITÉ EST RAPPELÉE, JAMAIS DEVINÉE ═════════


def test_nothing_is_marked_as_declared_without_a_declaration(client):
    body = client.get(LIBRARY_URL).text
    assert "is-declared" not in body
    assert "priorités déclarées" not in body


def test_the_declared_axis_is_marked_on_the_zones_it_covers(client):
    """Le pendant : une garde qui ne teste que l'absence laisserait passer une
    surface qui ne marque jamais rien."""
    _declare(_uid(), sessions_per_week=4, focus_priorities=[AXIS])
    # `pull-a` travaille « Dos largeur » : c'est le témoin de l'axe déclaré.
    open_pull = _disclosure(client, "t-pull-a")
    assert "is-declared" in open_pull
    marked = re.findall(
        r'<li class="loadout__zone is-declared">\s*([^<]+?)\s*<', open_pull)
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
    # `pull-b` travaille les Biceps, couverts par l'axe déclaré « Bras ».
    open_pull_b = _disclosure(client, "t-pull-b")
    hidden = re.findall(r'<span class="sr-only">\s*([^<]*priorité[^<]*)</span>',
                        open_pull_b)
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
    # `legs-a` est le gabarit qui travaille le core : si une déclaration
    # pouvait le marquer, c'est là qu'on le verrait.
    open_legs = _disclosure(client, "t-legs-a")
    assert "Core / Abdos" in open_legs, (
        "le témoin ne travaille plus le core — la garde ne mesurerait rien"
    )
    marked = re.findall(
        r'<li class="loadout__zone is-declared">\s*([^<]+?)\s*<', open_legs)
    assert "Core / Abdos" not in marked


# ═════════ LE FILTRE EST DEMANDÉ, ET ON EN SORT ═════════


def test_no_filter_is_applied_unless_asked(client):
    _declare(_uid(), sessions_per_week=4, focus_priorities=[AXIS])
    assert len(_slugs(client.get(LIBRARY_URL).text)) == 13


def test_an_asked_filter_restricts_and_says_so(client):
    body = client.get(f"{LIBRARY_URL}?zone={ZONE}").text
    slugs = _slugs(body)
    assert 0 < len(slugs) < 13
    # « configuration » et non « séance » : le registre contient aussi des
    # programmes, et le décompte porte sur les deux.
    assert f"{len(_keys(body))} configuration" in body
    assert "sur 13" in body, "le total disparu, l'utilisateur ne sait plus"
    assert ZONE_LABEL in body


def test_every_row_kept_by_the_filter_says_why(client):
    """Un filtre qui garde une configuration sans la zone demandée ment deux fois.

    ⚠ CETTE GARDE A CHANGÉ LE PRODUIT, pour la seconde fois. `Sb_UI_BIBLIO_01`
    l'avait déjà arrêté une fois : la première écriture n'affichait que les
    zones déclarées, et huit cartes restaient sans dire pourquoi.

    `UI-CP4` a failli refaire la même chose en sens inverse — les zones passant
    au dépli, un registre filtré ne justifiait plus AUCUNE de ses lignes. La
    zone filtrée reste donc sur la ligne, seule de toutes les zones.
    """
    body = client.get(f"{LIBRARY_URL}?zone={ZONE}").text
    rows = re.findall(r'<a class="loadout__handle"[\s\S]*?</a>', body)
    assert rows, "aucune ligne rendue — la garde ne mesurerait rien"
    for row in rows:
        assert ZONE_LABEL in row, f"ligne sans {ZONE_LABEL} retenue : {row[:120]}"


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
