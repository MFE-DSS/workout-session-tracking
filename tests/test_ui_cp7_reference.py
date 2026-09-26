"""`UI-CP7 REFERENCE` — un document se présente comme un document.

LA RÈGLE QUI GOUVERNE LA TRANCHE
----------------------------------
`AUREN_INSTRUMENTS §2bis`, mot pour mot :

    « Un document ne doit jamais avoir l'air d'un instrument en panne. »
    « La frontière doit être PERCEPTIBLE. »

⚠ CE QU'AUCUNE GARDE DE CE FICHIER NE PEUT VOIR
-------------------------------------------------
**Aucune garde du dépôt ne regarde un pixel.** Ce module lit du HTML servi et
des déclarations CSS ; il ne mesure ni une hauteur rendue, ni un contraste, ni
une densité à l'écran.

C'est précisément le trou par lequel `UI-CP5` a livré une cible tactile de
18 px avec toutes les gardes au vert, et par lequel cette tranche a d'abord
livré un facteur d'explication sans capitale. Les chiffres de rendu du rapport
viennent donc d'une mesure au navigateur, pas d'ici — et `CLAUDE.md §5.1`
impose au surplus l'exposition à l'opérateur.

Ce que ces gardes tiennent est le CONTRAT : quelles classes, quels rangs,
quelles déclarations. Pas le rendu.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
APP_CSS = ROOT / "app/static/css/app.css"

#: Le marqueur d'ouverture du bloc de grammaire de document.
MARQUEUR = "UI-CP7 REFERENCE` — LA GRAMMAIRE DE DOCUMENT"


def _grammaire_de_document() -> str:
    """Le bloc CSS de la tranche, **commentaires retirés**.

    ⚠ DEUX PIÈGES, TOUS DEUX RENCONTRÉS EN ÉCRIVANT CE FICHIER.

    Le premier : chercher une couleur en dur sur le texte brut trouvait le
    `#999` cité dans un COMMENTAIRE — celui qui raconte précisément qu'une
    couleur en dur avait été refusée. Une garde qui lit la prose comme du code
    accuse le récit de l'incident au lieu du code.

    Le second : `re.search` sur toute la feuille trouvait `.doc-head__title`
    du bloc d'IMPRESSION, déclaré plus haut. La garde mesurait la mauvaise
    règle et se croyait rouge à bon droit. On borne donc la lecture au bloc de
    la tranche.
    """
    css = APP_CSS.read_text(encoding="utf-8")
    bloc = css[css.index(MARQUEUR):]
    return re.sub(r"/\*.*?\*/", "", bloc, flags=re.S)

#: Les quatre surfaces que `§2bis` nomme et que `UI-CP6` a classées `DOCUMENT`.
DOCUMENTS = ("/science", "/science/atlas", "/coach-report", "/export")


def _servi(client, chemin: str) -> str:
    r = client.get(chemin, follow_redirects=True)
    assert r.status_code == 200, f"{chemin} → {r.status_code}"
    return r.text


# ═══════════ 1. `Q1` — LA FRONTIÈRE EST PERCEPTIBLE ═══════════


def test_chaque_document_porte_une_tete_et_une_colonne_de_lecture(client):
    """`Q1 = C` — la tête d'abord, la colonne ensuite.

    La tête est ce qui distingue un document d'un instrument **sans défiler** :
    un instrument réserve le rang DISPLAY à un relevé MESURÉ, un document y met
    son titre. C'est la moitié de `Q6` que rien n'utilisait.
    """
    for chemin in DOCUMENTS:
        corps = _servi(client, chemin)
        assert 'class="doc' in corps, f"{chemin} n'ouvre pas de colonne de lecture"
        assert "doc-head__title" in corps, f"{chemin} n'a pas de tête de document"


def test_le_titre_du_document_n_est_plus_domine_par_ses_sections(client):
    """⚠ LE DÉFAUT QUE SEULE LA MESURE A RENDU VISIBLE.

    Mesuré au navigateur avant la tranche, sur les deux surfaces `/science` :
    le titre du document faisait **18 px, centré**, et ses propres titres de
    section **22 px**. Un document dont le titre chuchote pendant que ses
    sections crient n'a pas de hiérarchie de lecture — et il ressemble à un
    instrument, qui lui aussi ouvre sur des intitulés de bloc.

    Le rendu n'est pas vérifiable ici. Ce qui l'est : le rang déclaré. On
    épingle donc que `.doc-head__title` porte bien le rang DISPLAY (32) et
    qu'il est aligné au début, pas centré.
    """
    bloc = re.search(r"\.doc-head__title\s*\{([^}]*)\}",
                     _grammaire_de_document())
    assert bloc, "`.doc-head__title` n'est plus déclaré"
    corps = bloc.group(1)
    assert "font-size: 32px" in corps, (
        f"le titre de document a quitté le rang DISPLAY : {corps.strip()}"
    )
    assert "text-align: start" in corps, (
        "le titre de document est centré — c'est une grammaire d'écran "
        "d'accueil, pas de document"
    )


def test_un_seul_display_par_document(client):
    """`Q6` — « un seul DISPLAY par écran ».

    Un document n'a pas de relevé souverain : son titre est donc ce seul
    DISPLAY. En poser un second reviendrait à réintroduire la compétition de
    rangs que la tranche vient de supprimer.
    """
    for chemin in DOCUMENTS:
        corps = _servi(client, chemin)
        assert corps.count("doc-head__title") == 1, (
            f"{chemin} porte {corps.count('doc-head__title')} titres au rang "
            "DISPLAY"
        )


def test_la_colonne_de_lecture_est_bornee_en_ch(client):
    """La borne est en `ch`, pas en pixels.

    `ch` suit la police : la colonne reste à ~68 caractères quelle que soit la
    taille choisie, là où un `max-width` en px dériverait au premier changement
    d'échelle. Mesuré au navigateur : 134 → 68 caractères par ligne sur
    `/science` en desktop.
    """
    bloc = re.search(r"^\.doc\s*\{([^}]*)\}", _grammaire_de_document(), re.M)
    assert bloc, "`.doc` n'est plus déclaré"
    assert re.search(r"max-width:\s*\d+ch", bloc.group(1)), (
        f"la colonne n'est plus bornée en `ch` : {bloc.group(1).strip()}"
    )


# ═══════════ 2. `Q2` — LA GRAMMAIRE DE DOCUMENT ═══════════


def test_les_surfaces_de_reference_n_empruntent_plus_la_carte(client):
    """`Q2 = B` — remplacer, pas retirer.

    `.card` est le conteneur de **rang 1** du socle (`Q5` : « séance
    recommandée, exercice actif, formulaire ouvert »). Mesurées avant la
    tranche : 18 cartes sur `/science`, 32 sur l'atlas — toutes autour de
    PROSE. Un document fait de cinquante cartes se lit comme un tableau de
    bord : c'est « avoir l'air d'un instrument », pas en panne mais emprunté.
    """
    for chemin in ("/science", "/science/atlas"):
        corps = _servi(client, chemin)
        # ⚠ `\bcard\b` attrapait `rule-card` : en regex le tiret est une
        # frontière de mot, donc une SOUS-CHAÎNE passait pour l'objet. On
        # extrait les listes de classes et on cherche le JETON exact.
        cartes = sum(
            1 for attr in re.findall(r'class="([^"]*)"', corps)
            if "card" in attr.split()
        )
        assert cartes == 0, f"{chemin} porte encore {cartes} cartes"


def test_export_garde_ses_cartes_et_c_est_une_decision(client):
    """⚠ LA RÈGLE N'EST PAS APPLIQUÉE LÀ OÙ ELLE NE DIT RIEN.

    Les trois cartes de `/export` ne contiennent pas de prose : ce sont des
    blocs FONCTIONNELS — un menu d'actions, un relevé chiffré, deux boutons de
    téléchargement. `Q5` réserve la carte à ce rang, et `Q2` visait les
    surfaces `/science`.

    Cette garde existe pour que l'écart soit une DÉCISION consignée, et non un
    oubli qu'une passe de cohérence viendrait « corriger » un jour.
    """
    corps = _servi(client, "/export")
    assert any("card" in attr.split()
               for attr in re.findall(r'class="([^"]*)"', corps)), (
        "les cartes fonctionnelles de `/export` ont été retirées — `Q2` ne "
        "visait pas cette surface, et la prose n'y remplacerait pas un bouton"
    )


# ═══════════ 3. `Q3` — LE REPLI, ET SES CIBLES ═══════════


def test_l_atlas_replie_ses_familles_et_en_laisse_une_ouverte(client):
    """`Q3 = A`, et une décision de rendu qui relève de `§2bis`.

    ⚠ Le sommaire ancré EXISTAIT DÉJÀ (`Sb_07`) : mon brief d'arbitrage
    affirmait le contraire. La tranche ajoute le REPLI, pas le sommaire.

    La première famille reste ouverte. Neuf lignes repliées et rien d'autre
    donneraient exactement ce que `§2bis` interdit : un document qui a l'air
    d'un instrument vide.
    """
    corps = _servi(client, "/science/atlas")
    replis = re.findall(r"<details[^>]*class=\"[^\"]*disclosure", corps)
    assert len(replis) >= 8, f"l'atlas ne replie que {len(replis)} familles"
    ouverts = re.findall(r"<details[^>]*\sopen", corps)
    assert len(ouverts) == 1, (
        f"{len(ouverts)} familles ouvertes — il en faut exactement une : zéro "
        "donnerait un document d'apparence vide, plusieurs annuleraient le repli"
    )


def test_l_atlas_adopte_le_composant_au_lieu_de_reecrire_un_repli(client):
    """`.disclosure` porte déjà la géométrie 44 px, le chevron et le focus.

    Son propre commentaire dit qu'il s'adopte « pour UNE classe sur le
    `<details>` », et qu'« un composant qu'on n'adopte pas parce qu'il coûte
    trop cher à adopter n'est pas un composant : c'est une intention ».
    """
    corps = _servi(client, "/science/atlas")
    assert "disclosure__panel" in corps
    assert "atlas-family__repli" not in corps, (
        "un repli maison a été écrit à côté du composant existant"
    )


def test_les_ancres_publiques_de_l_atlas_survivent_au_repli(client):
    """Les ancres `#family-<slug>` sont publiques depuis `Sb_07`.

    ⚠ ELLES RESTENT SUR L'ÉLÉMENT REPLIABLE LUI-MÊME. Placées à l'intérieur du
    repli, un navigateur qui n'ouvre pas automatiquement un `<details>` ciblé
    par un fragment ferait atterrir le lecteur sur du contenu masqué.
    """
    corps = _servi(client, "/science/atlas")
    for slug in ("pecs-press", "back-vertical", "legs-quad-dominant"):
        assert re.search(
            rf'<details[^>]*id="family-{slug}"', corps), (
            f"l'ancre publique #family-{slug} n'est plus portée par le repli"
        )


def test_les_cibles_du_sommaire_declarent_le_plancher_tactile():
    """⚠ UNE GARDE DE DÉCLARATION, ET ELLE DIT CE QU'ELLE NE PROUVE PAS.

    Mesurées au navigateur avant la tranche : **28 px**. Ce sont des contrôles
    de navigation AUTONOMES — la catégorie que le plancher produit de 44 px
    vise — et non des liens en ligne dans la prose, qui relèvent d'une autre
    catégorie et ne sont pas touchés ici.

    Cette garde lit la DÉCLARATION. Elle ne prouve pas la géométrie rendue :
    une règle plus spécifique ailleurs pourrait l'écraser sans qu'elle bronche.
    Seule la mesure au navigateur le prouve, et elle est au rapport (9 cibles
    sous 44 px → 0).
    """
    css = APP_CSS.read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    bloc = re.search(r"\.atlas-toc__item\s*\{([^}]*)\}", css)
    assert bloc, "`.atlas-toc__item` n'est plus déclaré"
    assert "min-height: 44px" in bloc.group(1), (
        f"le sommaire est repassé sous le plancher : {bloc.group(1).strip()}"
    )


# ═══════════ 4. `Q4` — LA SIGNATURE, ET L'IMPRESSION ═══════════


def test_chaque_document_signe_sa_provenance(client):
    """`Q4 = A` — le pied générique devient une signature.

    Il coûtait 135 px pour un mot-marque et un lien que la navigation
    secondaire porte déjà. Il porte désormais ce qu'un document doit dire et
    qu'aucune des quatre surfaces ne disait : d'où vient ce texte.
    """
    for chemin in DOCUMENTS:
        corps = _servi(client, chemin)
        assert 'class="doc-sig"' in corps, f"{chemin} ne signe pas sa provenance"
        assert 'class="foot"' not in corps, (
            f"{chemin} porte encore le pied générique"
        )


def test_la_signature_nomme_le_produit_meme_sur_papier(client):
    """En impression la topbar est masquée. Sans la signature, une feuille
    remise à un coach externe ne dirait plus d'où elle vient."""
    for chemin in DOCUMENTS:
        corps = _servi(client, chemin)
        assert re.search(
            r'<span class="doc-sig__source">\s*Auren\s*</span>', corps), (
            f"{chemin} ne nomme pas le produit dans sa signature"
        )


def test_l_affordance_d_impression_reste_sur_le_seul_document_qui_la_justifie(client):
    """`Q4`, réponse SCINDÉE — et la scission est le cœur de la réponse.

    Les règles `@media print` valent pour les quatre documents. Le BOUTON, non.
    `coach-report` est décrit dans le dépôt comme « un document à présenter à
    un coach externe » : son intention d'impression est établie. Celle d'un
    atlas de machines ne l'est pas, et la supposer serait inventer un besoin.
    """
    corps = _servi(client, "/coach-report")
    assert "window.print()" in corps, (
        "`coach-report` a perdu son affordance d'impression"
    )
    for chemin in ("/science", "/science/atlas", "/export"):
        autre = _servi(client, chemin)
        assert "window.print()" not in autre, (
            f"{chemin} propose d'imprimer — rien n'établit cette intention"
        )


def test_un_seul_bloc_d_impression_dans_la_feuille():
    """⚠ J'EN AVAIS ÉCRIT UN SECOND, ET DEUX GARDES L'ONT REFUSÉ.

    Elles le refusaient pour une couleur en dur (`#999`), et elles avaient
    raison sur un point que je n'avais pas vu : la feuille a déjà un bloc
    d'impression. Deux blocs `@media print` dans le même fichier sont deux
    implémentations du même sujet, vouées à diverger — le dépôt en porte assez
    d'exemples.
    """
    css = APP_CSS.read_text(encoding="utf-8")
    blocs = len(re.findall(r"@media\s+print\s*\{", css))
    assert blocs == 1, (
        f"{blocs} blocs `@media print` dans `app.css` — ils divergeront"
    )


def test_aucune_couleur_en_dur_dans_la_grammaire_de_document():
    """`CLAUDE.md §5.4` — toute couleur est un token de la palette.

    La grammaire de document n'introduit AUCUNE couleur : c'est ce qui la rend
    compatible avec `AUREN_INSTRUMENTS`, qui accepte deux dialectes visuels et
    pas un troisième. La frontière se lit à la forme du texte et au rang du
    titre, jamais à un ornement propre aux documents.
    """
    fautes = re.findall(r"#[0-9a-fA-F]{3,8}\b", _grammaire_de_document())
    assert not fautes, (
        f"couleur en dur dans la grammaire de document : {fautes}"
    )
