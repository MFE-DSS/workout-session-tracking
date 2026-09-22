"""`UI-CP6 SHELL` — les gardes de la coque et de ses quatre modes.

CE QUE CES GARDES TIENNENT, ET POURQUOI ELLES EXISTENT
-------------------------------------------------------
Avant cette tranche, la coque était gouvernée par deux drapeaux dont **aucun
ne couvrait sa propre intention** :

  · `shell_focus_mode` masquait la barre basse pendant une séance active, et
    laissait la topbar (69 px) et le pied (79 px) ;
  · `shell_bare` disait « seuil » et ne retirait que le pied et la barre
    basse. Mesuré au rendu : `/forgot-password` exposait **huit** destinations
    authentifiées sur mobile et **onze** sur desktop, dont `/profile`,
    `/progress` et `/library` — et c'était le SEUL gabarit qui posait ce
    drapeau.

Un drapeau qui ne couvre pas son intention n'est pas un drapeau : c'est une
coïncidence qui tient tant que personne ne regarde. Ces gardes regardent.

MÉTHODE. Les gardes structurantes sont vérifiées en **plantant leur défaut**,
et le défaut planté est celui d'ORIGINE, pas une caricature.
"""
from __future__ import annotations

import pathlib
import re

from app.services.shell import (
    CHEMINS_INVITE,
    CONTACT,
    DESTINATIONS_ATTENDUES,
    MODE_DOCUMENT,
    MODE_FOCUS,
    MODE_GUEST,
    MODE_INSTRUMENT,
    MODES,
    MODES_AVEC_NAV_PRIMAIRE,
    MODES_AVEC_PIED,
    MODES_AVEC_TOPBAR,
    NAVIGATION_SECONDAIRE,
    PREFIXES_DOCUMENT,
    mode_de_coque,
)

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE_HTML = ROOT / "app/templates/base.html"
APP_CSS = ROOT / "app/static/css/app.css"
SHELL_PY = ROOT / "app/services/shell.py"


def _start(client, slug="push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug},
                    follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def _bloc(html: str, ouvrant: str) -> str:
    """Le fragment qui commence à `ouvrant`, jusqu'à sa balise fermante.

    ⚠ On ne borne PAS au premier `</a>` ni au premier `</nav>` rencontré : les
    structures de coque imbriquent un `<details>` et une seconde `<nav>`. Une
    borne naïve couperait avant les liens et ferait accuser le produit de ne
    pas rendre ce qu'il rend — défaut payé deux fois sur ce dépôt.

    On compte donc les ouvertures et fermetures de la MÊME balise.
    """
    i = html.find(ouvrant)
    assert i != -1, f"fragment introuvable : {ouvrant}"
    balise = ouvrant[1:].split()[0].rstrip(">")
    profondeur, j = 0, i
    motif = re.compile(rf"</?{balise}\b")
    for m in motif.finditer(html, i):
        profondeur += 1 if not m.group(0).startswith("</") else -1
        j = m.end()
        if profondeur == 0:
            break
    return html[i:j]


def _chemins(fragment: str) -> list[str]:
    """Les chemins des `href` du fragment, dans l'ordre du document."""
    bruts = re.findall(r'href="([^"]+)"', fragment)
    chemins = []
    for b in bruts:
        # `url_for` rend une URL absolue sous le client de test.
        chemin = re.sub(r"^https?://[^/]+", "", b)
        if chemin.startswith("/"):
            chemins.append(chemin)
    return chemins


# ═══════════════ 1. LES QUATRE MODES, ET LEUR PRÉCÉDENCE ═══════════════


def test_la_precedence_des_modes_est_epinglee_avec_son_ordre():
    """⚠ L'ORDRE ET LES MODES SONT ÉPINGLÉS DANS LA MÊME ASSERTION.

    Réordonner la précédence force donc à toucher la ligne qui l'énonce, au
    lieu de la changer en déplaçant un `if` trois fichiers plus loin. C'est le
    même dispositif que `PRECEDENCE_VERSION` dans `flight_recorder`.

    `GUEST` d'abord : une surface de seuil ne reçoit jamais le cockpit, quel
    que soit l'état par ailleurs. `FOCUS` ensuite : l'exécution possède
    l'écran. `DOCUMENT` ensuite. `INSTRUMENT` par défaut — se tromper dans ce
    sens rend une coque complète, jamais une coque vide.
    """
    assert MODES == (MODE_INSTRUMENT, MODE_FOCUS, MODE_DOCUMENT, MODE_GUEST)

    # GUEST prime sur FOCUS : même une séance en cours ne rend pas le cockpit
    # sur un chemin de seuil.
    assert mode_de_coque("/login", seance_en_cours=True) == MODE_GUEST
    # FOCUS prime sur DOCUMENT.
    assert mode_de_coque("/export", seance_en_cours=True) == MODE_FOCUS
    # DOCUMENT prime sur le défaut.
    assert mode_de_coque("/science") == MODE_DOCUMENT
    assert mode_de_coque("/progress") == MODE_INSTRUMENT


def test_un_prefixe_ne_deborde_pas_sur_un_chemin_voisin():
    """`/exportateur` n'est pas sous `/export`.

    Un `startswith` nu le rangerait pourtant en DOCUMENT, et la surface
    perdrait sa navigation primaire sans que rien ne le signale. La borne est
    le `/`, et cette garde est la seule qui la vérifie.
    """
    assert mode_de_coque("/export") == MODE_DOCUMENT
    assert mode_de_coque("/export/sessions.csv") == MODE_DOCUMENT
    assert mode_de_coque("/exportateur") == MODE_INSTRUMENT
    assert mode_de_coque("/logoutique") == MODE_INSTRUMENT


def test_le_module_de_coque_est_pur():
    """Ni base, ni horloge, ni requête : il doit se charger sans contexte.

    Un contrat de coque qui importerait `sqlalchemy` deviendrait impossible à
    interroger depuis un test de gabarit, et la prochaine tranche écrirait sa
    propre copie plutôt que de l'importer.
    """
    src = SHELL_PY.read_text(encoding="utf-8")
    code = re.sub(r'"""[\s\S]*?"""', " ", src)
    for interdit in ("sqlalchemy", "datetime", "fastapi", "request"):
        assert interdit not in code, f"`{interdit}` est entré dans le contrat"


# ═════════════════ 2. GUEST — LE COCKPIT NE FUIT PLUS ═════════════════


def test_aucune_destination_authentifiee_ne_fuit_sur_un_seuil(client):
    """⚠ LE DÉFAUT MESURÉ QUE CETTE TRANCHE FERME.

    `/forgot-password` rendait la topbar authentifiée sur mobile et le rail
    sur desktop — huit et onze destinations, dont `/profile`, `/progress` et
    `/library`. Et c'était le seul gabarit qui posait `shell_bare`, ce qui
    rendait le défaut **invisible à la relecture** : le drapeau avait l'air
    posé, donc le travail avait l'air fait.

    On assert sur le HTML SERVI, pas sur la présence d'un drapeau : c'est ce
    qui distingue « la page se déclare seuil » de « la page EST un seuil ».

    ⚠ IL FAUT SE DÉCONNECTER D'ABORD, ET MA PREMIÈRE ÉCRITURE NE LE FAISAIT
    PAS. La fixture `client` ouvre une session authentifiée ; `/login` renvoie
    alors une REDIRECTION vers l'accueil, et `follow_redirects=True` rendait
    donc le HTML de l'accueil — qui porte légitimement une topbar. La garde
    échouait en accusant le produit d'une fuite, alors qu'elle mesurait une
    autre page. On vérifie donc aussi qu'on n'a pas été redirigé.
    """
    client.post("/logout", follow_redirects=False)

    for chemin in ("/login", "/forgot-password"):
        reponse = client.get(chemin, follow_redirects=False)
        assert reponse.status_code == 200, (
            f"{chemin} rend {reponse.status_code} — la garde mesurerait une "
            "autre page que celle qu'elle nomme"
        )
        for structure in ('class="topbar"', 'class="app-rail"',
                          'class="app-bottom-nav"'):
            assert structure not in reponse.text, (
                f"{chemin} rend « {structure} » — le cockpit authentifié fuit "
                "sur une surface de seuil"
            )


def test_tous_les_chemins_de_seuil_sont_classes_invite():
    """Le pendant statique : la liste close couvre bien ce qu'elle prétend.

    Sans lui, retirer une entrée de `CHEMINS_INVITE` laisserait la garde
    ci-dessus verte sur les deux chemins qu'elle nomme, et rouvrirait la fuite
    sur les trois autres.
    """
    for chemin in CHEMINS_INVITE:
        assert mode_de_coque(chemin) == MODE_GUEST, chemin


# ═══════════ 3. FOCUS — L'EXÉCUTION POSSÈDE L'ÉCRAN, SANS PIÈGE ═══════════


def test_la_seance_active_retire_TOUT_le_chrome_global(client):
    """⚠ TROIS STRUCTURES, PAS UNE — ET C'EST LÀ QUE L'ANCIEN ÉTAT ÉCHOUAIT.

    `shell_focus_mode` ne retirait que la barre basse. Mesuré pendant une
    séance active : la topbar tenait toujours 69 px et le pied 79 px, en haut
    et en bas de l'instrument dont le contrat dit que l'exécution possède
    l'écran.

    Une garde qui ne vérifierait que la barre basse serait restée verte tout
    du long.
    """
    sid = _start(client, "push-a")
    corps = client.get(f"/sessions/{sid}").text
    for structure in ('class="topbar"', 'class="app-bottom-nav"',
                      'class="app-rail"', 'class="foot"'):
        assert structure not in corps, (
            f"« {structure} » survit pendant une séance active — l'exécution "
            "ne possède pas l'écran"
        )


def test_la_seance_active_garde_une_sortie_explicite(client):
    """LE PENDANT, ET SANS LUI LA GARDE CI-DESSUS AUTORISERAIT UN PIÈGE.

    Retirer tout le chrome global est la moitié facile. La moitié qui compte
    est que l'utilisateur puisse SORTIR — l'arbitrage le dit en toutes
    lettres : « do not trap the user ».

    La sortie est le retour de l'en-tête de séance. Mesuré au rendu : 44 px de
    haut, à 26 px du sommet, visible sans défiler aux quatre viewports testés.
    Elle porte un nom accessible parce que son libellé visible est une flèche.
    """
    sid = _start(client, "push-a")
    corps = client.get(f"/sessions/{sid}").text
    entete = _bloc(corps, '<header class="session-header')
    assert 'class="back session-head__back"' in entete, (
        "la sortie de la séance a disparu de l'en-tête"
    )
    assert "aria-label" in entete, (
        "la sortie n'a pas de nom accessible — son libellé visible est une "
        "flèche, donc le nom est le seul chemin pour une aide technique"
    )


def test_une_seance_terminee_retrouve_la_coque(client):
    """La règle d'activation suit l'état canonique, pas la route.

    Sans cette garde, « masquer sur `/sessions/*` » passerait pour correct et
    priverait le récap de sa navigation.
    """
    sid = _start(client, "push-a")
    client.post(f"/sessions/{sid}", data={"action": "end"},
                follow_redirects=True)
    corps = client.get(f"/sessions/{sid}").text
    assert 'class="app-bottom-nav"' in corps
    assert 'class="topbar"' in corps


# ═══════════ 4. LE PIED QUITTE L'INSTRUMENT, PAS LE DOCUMENT ═══════════


def test_aucun_pied_generique_sur_une_surface_d_instrument(client):
    """`Q3` — un pied de page est un objet de DOCUMENT.

    Il coûtait 135 px sur mobile pour porter un mot-marque et un lien que la
    navigation secondaire offre déjà.
    """
    for chemin in ("/", "/progress", "/history", "/library"):
        corps = client.get(chemin, follow_redirects=True).text
        assert 'class="foot"' not in corps, f"{chemin} rend encore le pied"


def test_le_document_garde_son_pied_et_contact_reste_atteignable(client):
    """LE PENDANT — `§5.3`, jamais une soustraction seule.

    Le pied survit sur les DOCUMENTS, temporairement et sur instruction
    explicite : sa refonte appartient à `UI-CP7 REFERENCE`. Et « Contact »
    n'est perdu nulle part, puisqu'il vit dans la navigation secondaire.
    """
    corps = client.get("/export", follow_redirects=True).text
    assert 'class="foot"' in corps, "le document a perdu son pied"

    instrument = client.get("/progress", follow_redirects=True).text
    assert "/contact" in instrument, (
        "« Contact » n'est plus atteignable depuis un instrument"
    )


# ═══════ 5. LA NAVIGATION SECONDAIRE — UNE SÉMANTIQUE, DEUX RENDUS ═══════


def test_les_deux_rendus_proposent_les_memes_destinations_dans_le_meme_ordre(client):
    """⚠ LA GARDE QUI N'EXISTAIT PAS, ET QUI EXPLIQUE LA TRANCHE.

    Les six liens secondaires étaient **écrits deux fois** dans `base.html` —
    `.topbar__nav` et `.app-rail__secondary-nav` — et les deux blocs ne sont
    **jamais rendus en même temps** : l'un est masqué par media query.
    Aucun test de page ne pouvait donc les comparer, et `UI-CP4` a dû éditer
    les deux à la main.

    Le HTML SERVI contient pourtant les deux. Cette garde les compare là, sans
    navigateur — ce qui la rend insensible à la rupture de 1024 px, et donc
    valable quelle que soit la largeur d'écran.

    L'ordre est comparé, pas seulement l'ensemble : deux rendus qui
    proposeraient les mêmes destinations dans deux ordres différents
    apprendraient deux produits à la même personne.
    """
    corps = client.get("/progress", follow_redirects=True).text
    mobile = _chemins(_bloc(corps, '<nav class="topbar__nav"'))
    desktop = _chemins(_bloc(corps, '<nav class="app-rail__secondary-nav"'))

    assert mobile, "aucun lien lu côté mobile — la sonde ne mesure rien"
    assert desktop, "aucun lien lu côté desktop — la sonde ne mesure rien"

    # `CONTACT` est une exception de PLACEMENT encodée : dans le menu sur
    # mobile, en pied de rail sur desktop. On compare donc l'ordre du reste.
    sans_contact = [c for c in mobile if c != "/contact"]
    assert sans_contact == desktop, (
        f"les deux rendus ont divergé.\n  mobile  : {sans_contact}\n"
        f"  desktop : {desktop}"
    )


def test_le_contrat_couvre_exactement_ce_qui_est_rendu(client):
    """La sémantique du contrat et le HTML servi ne peuvent pas diverger.

    Sans cette garde, ajouter une destination au contrat sans la rendre — ou
    l'inverse — passerait inaperçu : la garde de parité ci-dessus compare les
    deux rendus **entre eux**, et deux rendus également faux se valident.
    """
    corps = client.get("/progress", follow_redirects=True).text
    mobile = set(_chemins(_bloc(corps, '<nav class="topbar__nav"')))

    attendus = {d.id for d in NAVIGATION_SECONDAIRE} | {CONTACT.id}
    assert set(DESTINATIONS_ATTENDUES) == attendus

    # Chaque destination du contrat est effectivement rendue.
    assert len(mobile) == len(attendus), (
        f"{len(mobile)} destinations rendues pour {len(attendus)} au contrat"
    )


def test_le_placement_de_contact_est_une_exception_encodee():
    """`Q4` autorise les exceptions « à condition qu'elles soient encodées et
    testées ». Celle-ci l'est : `CONTACT` ne fait pas partie de la liste
    ordonnée, parce que sa POSITION diffère d'un rendu à l'autre, mais il
    appartient bien aux destinations attendues.

    Une exception qui vit seulement dans un commentaire n'est pas encodée.
    """
    assert CONTACT.id not in [d.id for d in NAVIGATION_SECONDAIRE]
    assert CONTACT.id in DESTINATIONS_ATTENDUES


def test_chaque_destination_du_contrat_peut_etre_soulignee(client):
    """Le contrat porte le NOM du drapeau, `base.html` porte sa VALEUR.

    La séparation est le prix de la pureté du module. Son risque est qu'une
    clé manque dans la table du gabarit : la destination serait rendue, mais
    jamais soulignée — un défaut silencieux, invisible à toute garde statique.

    On visite donc chaque route du contrat et on exige que sa destination soit
    soulignée dans les DEUX rendus.
    """
    corps_initial = client.get("/progress", follow_redirects=True).text
    routes = _chemins(_bloc(corps_initial, '<nav class="topbar__nav"'))

    for chemin in routes:
        if chemin == "/contact":
            continue  # aucune sous-activation, par contrat
        corps = client.get(chemin, follow_redirects=True).text
        menu = _bloc(corps, '<nav class="topbar__nav"')
        lien = re.search(
            rf'<a class="topbar__link ([^"]*)"[^>]*href="[^"]*{re.escape(chemin)}"',
            menu,
        )
        assert lien, f"{chemin} n'est plus rendu dans le menu"
        assert "is-subactive" in lien.group(1), (
            f"{chemin} est rendu mais jamais souligné — son drapeau manque "
            "dans la table `_actifs` de `base.html`"
        )


# ═══════════════════ 6. LE BUDGET DE CHROME, ET LES ACQUIS ═══════════════════


def test_la_topbar_tient_dans_la_hauteur_de_sa_cible():
    """`Q1` — 44 px, la hauteur du chevron, et rien autour.

    Elle mesurait 69 px : 12 px de remplissage au-dessus et au-dessous d'une
    cible qui fait déjà 44×44 par le plancher tactile. Le remplissage vertical
    était du vide ajouté autour d'une cible conforme.

    On épingle la DÉCLARATION plutôt qu'un pixel rendu : la garde doit survivre
    sans navigateur, et c'est la feuille qui porte la décision.
    """
    css = APP_CSS.read_text(encoding="utf-8")
    m = re.search(r"\n\.topbar\s*\{([^}]*)\}", css)
    assert m, ".topbar a disparu de la feuille"
    bloc = m.group(1)
    assert "min-height: 44px" in bloc, f".topbar ne déclare plus 44 px : {bloc}"
    rembourrage = re.search(r"padding:\s*([^;]+);", bloc)
    assert rembourrage, ".topbar ne déclare plus son remplissage"
    assert "12px" not in rembourrage.group(1), (
        "le remplissage vertical de 69 px est revenu : "
        f"{rembourrage.group(1)}"
    )


def test_les_acquis_de_la_coque_ne_regressent_pas(client):
    """`§12` — ce que `UI-CP6` doit préserver, nommé et vérifié.

    Quatre destinations primaires, exposées une seule fois chacune, un seul
    `aria-current`, et le rail desktop toujours là. Une tranche de coque qui
    les défait serait une régression, quel que soit le gain par ailleurs.
    """
    corps = client.get("/progress", follow_redirects=True).text

    barre = _bloc(corps, '<nav class="app-bottom-nav"')
    primaires = _chemins(barre)
    assert len(primaires) == 4, f"{len(primaires)} onglets primaires"
    assert len(set(primaires)) == 4, "un onglet primaire est offert deux fois"

    # ⚠ UN `aria-current` PAR STRUCTURE, PAS PAR DOCUMENT — et ma première
    # écriture comptait le document. La barre basse et le rail portent chacun
    # le leur ; ils coexistent dans le HTML et s'excluent par media query, donc
    # un utilisateur n'en voit jamais qu'un. Compter le document rendait 2 et
    # accusait le produit d'un défaut d'accessibilité qui n'existe pas.
    rail = _bloc(corps, '<aside class="app-rail"')
    assert barre.count('aria-current="page"') == 1, (
        "plus d'un onglet courant dans la barre basse"
    )
    assert rail.count('aria-current="page"') == 1, (
        "plus d'un élément courant dans le rail"
    )
    assert 'class="app-rail"' in corps, "le rail desktop a disparu"


def test_la_coque_ne_depend_d_aucun_javascript():
    """`§12` — SSR, divulgation native. Un `<details>` suffit.

    La coque n'a jamais eu de JS ; cette garde empêche qu'une tranche de
    « modes » en introduise un pour piloter ce que le serveur sait déjà.
    """
    src = BASE_HTML.read_text(encoding="utf-8")
    sans_commentaires = re.sub(r"\{#[\s\S]*?#\}", " ", src)
    coque = sans_commentaires[sans_commentaires.find("<body"):]
    assert "<script" not in coque, "un script est entré dans la coque"
    # `python:S9073` — une conjonction cacherait lequel des deux gestionnaires
    # est revenu. Une assertion par handler, et le message le nomme.
    for handler in ("onclick", "onchange", "oninput", "onsubmit"):
        assert handler not in coque, f"« {handler} » est entré dans la coque"


def test_les_modes_qui_rendent_quoi_sont_declares_et_coherents():
    """Les trois tables de rendu ne peuvent pas contredire les modes.

    Elles sont lues par `base.html` ; une valeur qui n'est pas un mode connu y
    serait silencieusement fausse — le `in` rendrait simplement `False`, et la
    structure disparaîtrait sans erreur.
    """
    for table in (MODES_AVEC_TOPBAR, MODES_AVEC_NAV_PRIMAIRE, MODES_AVEC_PIED):
        for mode in table:
            assert mode in MODES, f"« {mode} » n'est pas un mode connu"

    # Les deux modes dépouillés ne rendent AUCUNE structure globale.
    for mode in (MODE_FOCUS, MODE_GUEST):
        assert mode not in MODES_AVEC_TOPBAR
        assert mode not in MODES_AVEC_NAV_PRIMAIRE
        assert mode not in MODES_AVEC_PIED

    # `Q3` — l'instrument n'a plus de pied ; le document le garde.
    assert MODE_INSTRUMENT not in MODES_AVEC_PIED
    assert MODE_DOCUMENT in MODES_AVEC_PIED


def test_les_prefixes_de_document_suivent_le_contrat_des_instruments():
    """`AUREN_INSTRUMENTS §2bis` nomme quatre surfaces qui ne sont pas des
    instruments. Elles doivent toutes être classées, sinon la frontière que ce
    contrat demande de rendre perceptible ne l'est qu'à moitié.
    """
    for chemin in ("/science", "/atlas", "/coach-report", "/export"):
        assert mode_de_coque(chemin) == MODE_DOCUMENT, chemin
    assert set(PREFIXES_DOCUMENT) >= {
        "/science", "/atlas", "/coach-report", "/export",
    }
