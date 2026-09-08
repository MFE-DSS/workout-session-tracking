"""`UI-CP2` — A+ : la surface primaire se recompose avec l'état.

⚠ POURQUOI CE FICHIER EXISTE, dit sans enjoliver.

La refonte A+ a été écrite, rendue, mesurée — puis **aucune garde n'en tenait
la composition**. Les trente-deux gardes converties protègent des capacités
héritées : que rien ne devienne inatteignable, que le bilan reste joignable,
que la référence atteigne l'œil. Aucune ne disait ce que A+ APPORTE.

Le trou a été trouvé en replantant : retirer la bande de séries de l'état
`REST` — c'est-à-dire défaire le cœur de la recomposition — laissait la suite
entièrement verte. C'est l'oubli d'`UI-CP1` qui se répétait, sur la tranche
suivante.

CE QUE CES GARDES TIENNENT, et que rien d'autre ne tenait :

  * l'écran ne rend que l'exercice ACTIF ;
  * `REST` est TEMPS-SOUVERAIN — pas de bande de séries, pas de champ de
    saisie, une seule sortie ;
  * `EXERCISE_COMPLETE` est un état de TRANSITION, donc l'un des plus légers ;
  * le bilan et le rappel méthode ont QUITTÉ l'exécution ;
  * l'orientation reste atteignable et conforme à la cible tactile.
"""
from __future__ import annotations

import re

import pytest


def _seance(client, slug: str = "push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug},
                    follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def _exercices(session_id: int):
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SessionExercise

    with SessionLocal() as db:
        return list(db.execute(
            select(SessionExercise.id)
            .where(SessionExercise.session_id == session_id)
            .order_by(SessionExercise.position)
        ).scalars().all())


def _series(se_id: int, kind: str = "work"):
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SetLog

    with SessionLocal() as db:
        return [sl.id for sl in db.execute(
            select(SetLog).where(SetLog.session_exercise_id == se_id)
            .order_by(SetLog.set_index)
        ).scalars().all() if sl.kind == kind]


def _etat(body: str) -> str | None:
    m = re.search(r'data-console-state="([^"]+)"', body)
    return m.group(1) if m else None


# ═══════════════════════════════════════════════════════════════════════════
# LA RECOMPOSITION — un état, un écran
# ═══════════════════════════════════════════════════════════════════════════


def test_seul_l_exercice_actif_est_rendu(client):
    """Sept exercices dans la séance, UN seul instrument à l'écran.

    Mesuré avant la refonte : la page rendait les sept cartes dans les six
    états, et **seize des vingt-trois commandes visibles appartenaient à un
    autre état** — identiques quoi que l'utilisateur fût en train de faire.
    """
    sid = _seance(client)
    body = client.get(f"/sessions/{sid}").text
    consoles = re.findall(r'data-console-state="', body)
    assert len(consoles) == 1, f"{len(consoles)} consoles rendues au lieu d'une"
    cartes = re.findall(r'<details\b[^>]*\bclass="[^"]*\bcard\s+exercise-card\b',
                        body)
    assert len(cartes) == 1, f"{len(cartes)} cartes d'exercice au lieu d'une"


def test_les_autres_exercices_restent_atteignables_sans_javascript(client):
    """A+ retire les six cartes ; il ne retire pas les six exercices.

    `?active=` est une sélection SERVEUR — pas une ancre — donc l'accès
    survit à l'absence de script. C'est la contrepartie obligatoire du retrait
    (`CLAUDE.md §5.3`).
    """
    sid = _seance(client)
    body = client.get(f"/sessions/{sid}").text
    vises = {int(m) for m in re.findall(r'[?&]active=(\d+)', body)}
    assert vises >= set(_exercices(sid)), (
        f"exercices inatteignables : {set(_exercices(sid)) - vises}"
    )
    for lien in re.findall(r"<a\b[^>]*xc-strip__pip[^>]*>", body):
        assert "href=" in lien, "une pastille d'orientation n'est pas un lien"
        assert "onclick" not in lien, "activation confiée au JavaScript"


def test_le_bilan_et_le_rappel_methode_ont_quitte_l_execution(client):
    """Ils ne répondent pas à « que fais-je maintenant ».

    L'ambre plein le plus fort de l'ancienne page TERMINAIT LA SÉANCE, alors
    qu'on en était à la première série sur vingt et une. Deux propriétaires
    d'action se disputaient le même écran.
    """
    sid = _seance(client)
    execution = client.get(f"/sessions/{sid}").text
    assert "TERMINER LA SÉANCE" not in execution
    assert 'name="concentration"' not in execution
    assert "Rappel méthode" not in execution

    # ⚠ ET ILS EXISTENT AILLEURS. Sans cette moitié, la garde ci-dessus serait
    # satisfaite par une suppression pure.
    bilan = client.get(f"/sessions/{sid}?view=bilan").text
    assert "TERMINER LA SÉANCE" in bilan
    assert 'name="concentration"' in bilan
    assert "Rappel méthode" in bilan


# ═══════════════════════════════════════════════════════════════════════════
# REST — le temps devient souverain
# ═══════════════════════════════════════════════════════════════════════════


def _amener_au_repos(client, sid: int) -> str:
    """Une série de travail validée, par le produit, avec `nav=stay`."""
    se_id = _exercices(sid)[0]
    donnees = {"nav": "stay"}
    for w in _series(se_id, "warmup"):
        donnees[f"set_{w}_weight_kg"], donnees[f"set_{w}_reps"] = "20", "12"
    travail = _series(se_id)
    donnees[f"set_{travail[0]}_weight_kg"] = "60"
    donnees[f"set_{travail[0]}_reps"] = "10"
    r = client.post(f"/sessions/{sid}/exercises/{se_id}", data=donnees,
                    follow_redirects=False)
    body = client.get(r.headers["location"]).text
    assert _etat(body) == "rest", f"état {_etat(body)!r} au lieu de `rest`"
    return body


def test_le_repos_est_temps_souverain(client):
    """LA GARDE QUE LA REPLANTATION A RÉVÉLÉE MANQUANTE.

    Retirer la recomposition du repos — remettre la bande de séries — laissait
    la suite entièrement verte. Rien ne tenait ce que `§6` demande : *TIME
    becomes sovereign · do not render a separate TimerCard*.

    Trois propriétés, et elles se tiennent ensemble :

      1. AUCUNE bande de séries — la question du repos n'est pas « où en
         suis-je dans mes séries » ;
      2. AUCUN champ de saisie — il n'y a rien à taper pendant un repos ;
      3. UNE seule sortie — la ligne de série portait une seconde affordance
         ambre face à celle du dock ; c'était le défaut `DF-B`, et il ne peut
         plus se reproduire une fois la ligne retirée.
    """
    sid = _seance(client)
    body = _amener_au_repos(client, sid)

    assert "setline--current" not in body, (
        "la bande de séries est rendue pendant le repos"
    )
    assert "setline__resume" not in body, (
        "la ligne de série porte une seconde sortie — le défaut `DF-B` revient"
    )
    saisies = re.findall(r'<input\b[^>]*class="[^"]*setline__field', body)
    assert not saisies, f"{len(saisies)} champs de saisie pendant le repos"
    assert "rest-readout__value" in body, "le minuteur n'est pas rendu"


def test_le_repos_ne_recoit_pas_une_carte_de_minuteur(client):
    """`§5` l'interdit nommément : l'instrument DEVIENT temps-dominant, il ne
    reçoit pas un composant de plus.

    Mesuré au rendu à 390 px avant correction : le cadran vivait dans un
    encadré — fond, bordure, rayon — posé au milieu de l'écran.
    """
    sid = _seance(client)
    _amener_au_repos(client, sid)
    css = (pytest.importorskip("pathlib").Path(__file__).resolve().parent.parent
           / "app" / "static" / "css" / "session_focus.css").read_text(encoding="utf-8")
    bloc = css[css.find('.console[data-state="rest"] .session-focus__rest-timer'):]
    bloc = bloc[:bloc.find("}") + 1]
    assert bloc, "aucune règle ne retire le cadre du minuteur à l'état repos"
    for propriete in ("background: none", "border: none"):
        assert propriete in bloc, (
            f"le minuteur garde son cadre à l'état repos : `{propriete}` absent"
        )


def test_l_exercice_termine_est_un_etat_leger(client):
    """`§6` — c'est une TRANSITION, elle doit être l'un des états les plus
    légers, pas le plus lourd.

    Mesuré avant : `EXERCISE_COMPLETE` portait **26 commandes sur 3,50
    écrans** — le maximum des six états, au moment où l'on a le moins à faire.
    """
    sid = _seance(client)
    se_id = _exercices(sid)[0]
    donnees = {"nav": "stay"}
    for w in _series(se_id, "warmup"):
        donnees[f"set_{w}_weight_kg"], donnees[f"set_{w}_reps"] = "20", "12"
    for i, w in enumerate(_series(se_id)):
        donnees[f"set_{w}_weight_kg"] = "60"
        donnees[f"set_{w}_reps"] = str(10 - i)
    r = client.post(f"/sessions/{sid}/exercises/{se_id}", data=donnees,
                    follow_redirects=False)
    body = client.get(r.headers["location"]).text

    assert _etat(body) == "exercise_complete", f"état {_etat(body)!r}"
    assert "setline--current" not in body, (
        "la bande de séries survit à un exercice terminé — le récapitulatif "
        "dit déjà 3/3"
    )
    saisies = re.findall(r'<input\b[^>]*class="[^"]*setline__field', body)
    assert not saisies, "des champs de saisie subsistent sur un exercice fini"


# ═══════════════════════════════════════════════════════════════════════════
# ORIENTATION — permanente, discrète, et conforme
# ═══════════════════════════════════════════════════════════════════════════


def test_la_bande_d_orientation_respecte_la_cible_tactile(client):
    """⚠ MA PREMIÈRE ÉCRITURE INTRODUISAIT À ELLE SEULE SEPT CIBLES SOUS 44 px.

    `height: 5px` + `padding: 19px 0` + `margin: -19px 0` mesurait **38 px**
    au navigateur : les marges négatives se résorbaient dans le conteneur
    flex. Le commentaire de la règle affirmait le contraire.

    La pastille est désormais une boîte de 44 px qui centre une barre de 5 px
    en `::before`. Cette garde lit la FEUILLE DE STYLE, parce que c'est là que
    la faute était.
    """
    import pathlib

    css = (pathlib.Path(__file__).resolve().parent.parent / "app" / "static"
           / "css" / "session_focus.css").read_text(encoding="utf-8")
    bloc = css[css.find(".xc-strip__pip {"):]
    bloc = bloc[:bloc.find("}") + 1]
    assert "min-height: 44px" in bloc, (
        "la pastille d'orientation ne garantit pas la cible tactile du produit"
    )
    assert "margin: -" not in bloc, (
        "une marge négative porte la cible — elle se résorbe en flex, mesuré"
    )


def test_l_orientation_ne_devient_pas_une_carte_de_seance(client):
    """`§1` écarte explicitement la carte permanente du concept B.

    La bande oriente : une pastille par exercice, aucun texte, aucun chiffre.
    Si elle se mettait à porter des libellés, elle cesserait d'être une
    orientation pour devenir une seconde interface.
    """
    sid = _seance(client)
    body = client.get(f"/sessions/{sid}").text
    debut = body.find('class="xc-strip"')
    assert debut > 0, "la bande d'orientation n'est pas rendue"
    # ⚠ On découpe APRÈS la balise ouvrante. Découper depuis l'attribut laissait
    # `class="xc-strip" aria-label="…">` dans le fragment : le retrait des
    # balises le lisait alors comme du texte visible, et la garde accusait la
    # bande de porter ce qu'elle ne porte pas.
    bande = body[body.find(">", debut) + 1:]
    bande = bande[:bande.find("</nav>")]
    visible = re.sub(r"<[^>]+>", "", bande).strip()
    assert not visible, (
        f"la bande porte du texte visible et cesse d'orienter : {visible[:80]!r}"
    )
