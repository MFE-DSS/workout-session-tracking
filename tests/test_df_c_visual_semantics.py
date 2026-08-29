"""`DF-C` — le type de série se voit, il ne se déchiffre pas.

CE QUE CETTE TRANCHE FERME
---------------------------
`É1` / `S1` étaient des **codes techniques** : il fallait les lire, puis les
traduire. Sur un téléphone, entre deux séries, la distinction préparation /
travail doit être perceptible **avant** la lecture.

Deux dimensions, deux porteurs, et c'est ce qui rend la chose lisible :

  * le TYPE (échauffement vs travail) → un **microglyphe** ;
  * l'ÉTAT (passé · courant · futur) → les marqueurs `✓ / ● / ○`, inchangés.

Le NUMÉRO reste typographique — il est utile, et n'a aucune raison de devenir
un dessin.

LE GATE, tel que l'opérateur l'a posé : à 390 px, **sans lire le texte
adjacent et même en niveaux de gris**, distinguer en moins d'une seconde
préparation / série de travail / passé-courant-futur. C'est un jugement
humain ; ces gardes en verrouillent les CONDITIONS MATÉRIELLES — que la
distinction tienne par la forme et non par la teinte, et qu'elle ne repose
jamais sur le seul dessin pour qui ne le voit pas.

Y SONT REPLIÉES, SUR ORDRE, les cinq cibles `<summary>` mesurées sous 44 px de
l'écran de séance — « do not create a separate target-size tranche ».
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
CARD = ROOT / "app/templates/_partials/exercise_card.html"
CSS = ROOT / "app/static/css/session_focus.css"

# Un sélecteur CSS et son corps. Hoisté : écrit trois fois, il déclenchait
# `S1192`, et le pré-scan AST l'a vu avant Sonar.
CSS_RULE = r"([^{}]+)\{([^}]*)\}"

WARMUP_GLYPH = "setline__glyph--warmup"
WORK_GLYPH = "setline__glyph--work"


def _card() -> str:
    return re.sub(r"\{#.*?#\}", " ", CARD.read_text(encoding="utf-8"), flags=re.S)


def _css() -> str:
    return re.sub(r"/\*[\s\S]*?\*/", " ", CSS.read_text(encoding="utf-8"))


def _glyph(name: str) -> str:
    """Le fragment `<svg>` d'un glyphe, isolé du reste du gabarit."""
    return _card().split(name, 1)[1].split("</svg>", 1)[0]


def _page(client, sid: int) -> str:
    return client.get(f"/sessions/{sid}").text


def _rule(selector: str) -> str:
    css = _css()
    return next(
        (body for sel, body in re.findall(CSS_RULE, css)
         if selector in sel),
        "",
    )


# ═════════ 1. LES CODES ALPHABÉTIQUES ONT DISPARU DES LIGNES ═════════


def test_no_set_line_still_renders_a_letter_code(client):
    """LA GARDE DE FOND, sur le RENDU et non sur le gabarit : plus aucune
    ligne ne porte `É1` ni `S1`.

    Les DEUX états, parce qu'ils ne rendent pas les mêmes branches : la séance
    neuve n'a ni ligne passée ni série de travail courante, et la séance
    avancée replie les échauffements en récapitulatif. Une seule des deux
    laissait passer la moitié des gabarits.
    """
    for sid in (_session(client), _advanced_session(client)):
        body = _page(client, sid)
        codes = re.findall(r'<span class="setline__code">([\s\S]*?)</span>', body)
        assert codes, "aucun code de ligne rendu — la garde ne mesure rien"
        for code in codes:
            text = re.sub(r"<[^>]+>", "", code).strip()
            assert not re.match(r"^[ÉS]\d", text), (
                f"code alphabétique rendu : {text!r}"
            )


def test_the_ordinal_survives(client):
    """Le numéro reste utile — le retirer aurait été une soustraction, pas une
    substitution."""
    sid = _session(client)
    body = _page(client, sid)
    codes = [re.sub(r"<[^>]+>", "", c).strip()
             for c in re.findall(r'<span class="setline__code">([\s\S]*?)</span>', body)]
    numbered = [c for c in codes if re.fullmatch(r"\d+", c)]
    assert len(numbered) >= 3, f"ordinaux rendus : {codes}"


# ═════════ 2. LE TYPE EST PORTÉ PAR UNE FORME ═════════


def test_both_types_have_their_own_glyph(client):
    sid = _session(client)
    body = _page(client, sid)
    assert WARMUP_GLYPH in body, "aucun glyphe d'échauffement rendu"
    assert WORK_GLYPH in body, "aucun glyphe de série de travail rendu"


def test_the_two_glyphs_differ_by_shape_not_by_colour():
    """LE CŒUR DU GATE. Le niveau de gris ne pardonne pas une distinction de
    teinte : il faut que la GÉOMÉTRIE diffère. L'échauffement est une diagonale
    OUVERTE (trait), le travail une horizontale PLEINE (rectangle)."""
    warm, work = _glyph(WARMUP_GLYPH), _glyph(WORK_GLYPH)

    assert "<path" in warm, "l'échauffement n'est pas un tracé"
    assert 'fill="none"' in warm, "l'échauffement devrait être ouvert, pas plein"
    assert "<rect" in work, "le travail n'est pas une forme pleine"
    assert 'fill="currentColor"' in work, "le travail devrait être plein"
    assert warm != work, "les deux glyphes sont identiques"


def test_neither_glyph_carries_a_colour_of_its_own():
    """`CLAUDE.md §5.4` — aucune couleur neuve. Les glyphes héritent de la
    couleur de leur ligne, donc ils suivent l'état sans qu'aucune règle ne le
    répète."""
    for name in (WARMUP_GLYPH, WORK_GLYPH):
        svg = _glyph(name)
        assert "currentColor" in svg, f"{name} ne suit pas la couleur de sa ligne"
        assert not re.search(r"#[0-9a-fA-F]{3,6}", svg), f"couleur en dur dans {name}"


def test_the_glyph_is_never_dimmed_below_the_line_it_lives_on():
    """Le glyphe REMPLACE un caractère : il doit être aussi visible que lui.

    ⚠ J'avais posé `opacity: .85` sur l'échauffement pour « le rendre plus
    discret ». Mesuré au pixel, ça rendait le porteur du TYPE plus faible que
    l'ordinal qu'il accompagne — **9,10:1 contre 12,02:1** sur la ligne
    courante, **2,25:1 contre 2,66:1** sur les futures. Retiré, les deux sont
    identiques.

    L'atténuation des lignes futures est déjà portée par la couleur de la
    ligne : c'est la dimension ÉTAT, et `currentColor` la suit seule. En
    ajouter une par-dessus affaiblissait la seule chose que la tranche pose.
    """
    for name in (WARMUP_GLYPH, WORK_GLYPH):
        for selector in (f".{name}", ".setline__glyph"):
            body = _rule(selector)
            assert "opacity" not in body, (
                f"`{selector}` atténue le glyphe sous la ligne qui le porte"
            )


def test_no_emoji_or_pictogram_was_introduced(client):
    """L'ordre l'interdit explicitement : pas de flamme, pas d'emoji.

    ⚠ La garde lit le RENDU, pas la source. Ma première écriture balayait le
    gabarit et attrapait le `⚠` de mes propres commentaires d'avertissement —
    une garde qui accuse sa propre prose. Ce qui compte est ce que
    l'utilisateur voit.

    Les marqueurs d'état `✓ ● ○` sont EXCLUS : ce sont les signes historiques
    de l'état, pas des pictogrammes décoratifs, et ils sont gardés par
    `test_the_state_is_still_carried_by_its_own_marker`.
    """
    sid = _session(client)
    rendered = _page(client, sid)
    # On vise les EMOJI, pas les symboles typographiques : `←`, `☰`, `✓`, `→`
    # appartiennent à la coque depuis longtemps et ne sont pas des
    # pictogrammes décoratifs. Une plage trop large accusait ces signes-là —
    # elle mesurait autre chose que ce qu'elle prétendait.
    emoji = {ch for ch in rendered
             if ord(ch) >= 0x1F000 or ch == "\ufe0f"}
    assert not emoji, f"emoji rendus : {sorted(emoji)}"


# ═════════ 3. LE DESSIN N'EST JAMAIS LA SEULE VÉRITÉ ═════════


def test_every_glyph_is_hidden_from_assistive_technology():
    """Un `<svg>` lu à voix haute produirait du bruit : c'est le texte de
    rechange qui porte l'information."""
    for name in (WARMUP_GLYPH, WORK_GLYPH):
        assert 'aria-hidden="true"' in _glyph(name), f"{name} n'est pas masqué"


def test_the_accessible_name_says_the_type_in_words(client):
    """Le contrat : `Échauffement 1` / `Série de travail 1`. Un lecteur
    d'écran ne voit pas une rampe.

    ⚠ Une garde de PRÉSENCE ne gardait rien : les deux mots figuraient déjà
    sur la ligne courante, donc réintroduire un code sur les lignes PASSÉES
    la laissait verte. On exige donc en plus qu'AUCUN nom accessible ne soit
    un code — c'est la propriété réelle, la présence n'en était qu'un reflet.
    """
    bodies = [_page(client, _session(client)),
              _page(client, _advanced_session(client))]
    for body in bodies:
        hidden = re.findall(r'<span class="sr-only">([^<]+)</span>', body)
        assert hidden, "aucun nom accessible rendu — la garde ne mesure rien"
        for name in hidden:
            assert not re.match(r"^[ÉS]\d", name.strip()), (
                f"nom accessible redevenu un code : {name!r}"
            )
    joined = " · ".join(re.findall(r'<span class="sr-only">([^<]+)</span>',
                                   " ".join(bodies)))
    assert "Échauffement" in joined, joined
    assert "Série de travail" in joined, joined


def test_every_line_whose_type_is_a_glyph_names_it_in_words(client):
    """LA PROPRIÉTÉ, et non un cas particulier : dès qu'une ligne confie son
    TYPE à un glyphe `aria-hidden`, elle doit le dire en toutes lettres.

    ⚠ Trouvé en relisant le diff, pas en lisant un test. La ligne du
    récapitulatif d'échauffement n'avait AUCUN `sr-only` : elle disait « É1 »
    avant, elle n'aurait plus annoncé que « 1 ». Retirer le code sans rendre
    le mot aurait appauvri cette ligne au lieu de la traduire — une
    soustraction seule (`CLAUDE.md §5.3`), sur le seul canal qui ne voit pas
    le dessin.

    La ligne de récapitulatif porte le mot « Échauffement » en clair : elle
    n'a rien à confier à un glyphe, donc elle n'entre pas dans la règle.
    """
    for sid in (_session(client), _advanced_session(client)):
        lines = re.findall(r'<li class="setline[^"]*"[^>]*>([\s\S]*?)</li>',
                           _page(client, sid))
        assert lines, "aucune ligne de série rendue — la garde ne mesure rien"
        glyphed = [ln for ln in lines if "setline__glyph" in ln]
        assert glyphed, "aucune ligne ne porte de glyphe — la garde ne mesure rien"
        for line in glyphed:
            # L'aplatissement est hoisté HORS de la f-string : l'antislash y
            # est refusé jusqu'à Python 3.11, cible de la CI — l'interpréteur
            # local (3.14) l'accepte, donc le test passait ici et aurait cassé
            # là-bas.
            flat = re.sub(r"\s+", " ", line)[:120]
            assert 'class="sr-only"' in line, (
                f"une ligne confie son type à un glyphe masqué sans le nommer : {flat!r}"
            )


def test_the_state_is_still_carried_by_its_own_marker(client):
    """Deux dimensions, deux porteurs. Le glyphe ne doit pas absorber l'état,
    sinon on retombe sur un signe qui dit deux choses à la fois."""
    sid = _session(client)
    body = _page(client, sid)
    markers = re.findall(r'<span class="setline__marker[^"]*"[^>]*>([^<]+)</span>', body)
    assert markers, "les marqueurs d'état ont disparu"
    assert set(markers) <= {"✓", "●", "○"}, set(markers)


# ═════════ 4. LES CIBLES SOUS 44 PX, REPLIÉES DANS CETTE TRANCHE ═════════


def test_the_session_disclosures_reach_the_product_touch_floor():
    """Mesurées à 390 px : 28, 39, 20 et 20 px. 44 px = standard produit
    AUREN, **pas** WCAG 2.2 (24×24 avec exception d'espacement) — aucune
    non-conformité réglementaire n'est corrigée ici."""
    rule = _rule(".session-feedback__note, .rule) > summary")
    assert "min-height: 44px" in rule, (
        "les replis de l'écran de séance n'ont pas de plancher tactile"
    )


def test_the_overload_disclosure_reaches_the_product_floor():
    """« Pourquoi ? » de l'indice de surcharge : **29 px, visible**, avec un
    `min-height: 24px` posé exprès.

    Le commentaire d'origine (`Sb_30.5`) justifiait ce 24 par « pas obligatoire
    44x44 » — c'est le raisonnement de WCAG 2.2, pas le standard PRODUIT
    d'AUREN, qui est 44. Le contrôle a été trouvé en mesurant la PAGE entière ;
    mon relevé précédent ne balayait que la carte de séance et le déclarait
    conforme. Une mesure trop étroite conclut faux.
    """
    rule = _rule(".overload-hint__why-toggle")
    assert "min-height: 44px" in rule, (
        "le repli « Pourquoi ? » est retombé sous le plancher produit"
    )
    # ⚠ Viser l'état FERMÉ nommément. Chercher `::before` « quelque part
    # autour » laissait la règle `[open]` satisfaire la garde à la place de
    # celle qu'on veut protéger : elle restait verte alors que le marqueur de
    # l'état fermé avait disparu.
    closed = [body for sel, body in re.findall(CSS_RULE, _css())
              if ".overload-hint__why-toggle::before" in sel and "[open]" not in sel]
    assert closed, "la règle du marqueur de l'état fermé a disparu"
    assert "content:" in closed[0], "le marqueur du repli fermé ne dessine rien"


def test_the_floor_rule_stays_at_zero_specificity():
    """`:where()` — n'importe quel composant doit pouvoir redéfinir sans
    lutte de cascade."""
    css = _css()
    assert ":where(.session-feedback__note, .rule) > summary" in css, (
        "le plancher n'est pas posé en `:where()`"
    )


def test_those_disclosures_still_look_like_disclosures():
    """⚠ `display: flex` sur un `<summary>` SUPPRIME son marqueur natif —
    défaut mesuré en `UX4_02C`. Le plancher emploie `flex` : il doit donc
    redessiner le chevron, sinon on échange une cible trop petite contre une
    affordance invisible."""
    css = _css()
    drawing = [
        body for sel, body in re.findall(CSS_RULE, css)
        if ".session-feedback__note, .rule) > summary::before" in sel
        and "border-left" in body
    ]
    assert drawing, "le plancher masque le marqueur natif sans le remplacer"


def _session(client) -> int:
    r = client.post("/sessions", data={"template_slug": "push-a"},
                    follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def _advanced_session(client) -> int:
    """Une séance où les TROIS états coexistent : au moins une série passée,
    une série de travail courante, et des séries futures.

    ⚠ NÉCESSAIRE. Deux gardes n'exerçaient que l'état INITIAL — où le courant
    est un échauffement et où aucune série passée n'existe. Elles restaient
    donc vertes quand on réintroduisait un code alphabétique sur la série de
    travail ou sur une ligne passée. Trouvé en plantant le défaut.

    ⚠ ET LE POST EST CUMULATIF, comme la vraie carte. Ma première écriture
    n'envoyait que la série visée : chaque envoi EFFAÇAIT les précédentes —
    précisément le défaut que `DF-B` documente et interdit. L'état atteint
    était alors « courant = échauffement 1 », et les deux gardes restaient
    vertes pour cette raison-là, pas parce qu'elles gardaient quelque chose.
    """
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog

    sid = _session(client)
    with SessionLocal() as db:
        se = db.execute(
            select(SessionExercise)
            .where(SessionExercise.session_id == sid)
            .order_by(SessionExercise.position.asc()).limit(1)).scalar_one()
        sets = db.execute(
            select(SetLog).where(SetLog.session_exercise_id == se.id)
            .order_by(SetLog.kind.asc(), SetLog.set_index.asc())).scalars().all()
        se_id = se.id
        order = [x.id for x in sets if x.kind != "work"]
        order += [x.id for x in sets if x.kind == "work"][:1]

    # Deux échauffements puis la PREMIÈRE série de travail : restent alors des
    # lignes passées des DEUX types, une série de travail COURANTE, et des
    # futures. Le formulaire sérialise toutes les valeurs — on fait pareil.
    data: dict[str, str] = {"nav": "stay_norest"}
    for set_id in order:
        data[f"set_{set_id}_weight_kg"] = "40"
        data[f"set_{set_id}_reps"] = "10"
        client.post(f"/sessions/{sid}/exercises/{se_id}", data=dict(data),
                    follow_redirects=False)
    return sid

