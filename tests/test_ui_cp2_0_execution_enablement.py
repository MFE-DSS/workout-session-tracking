"""`UI-CP2.0` — la tranche qui rend l'instrument d'exécution POSSIBLE.

Trois verrous, tous trouvés en **mesurant une séance réelle** au labo, aucun par
relecture. Ils ne sont pas des micro-défauts : ils interdisent le cockpit piloté
par l'état que `UI-CP2` doit construire.

    F1  l'exercice ne peut pas se terminer
    F2  le signal de repos est avalé
    F3  l'écriture de séance est tout-ou-rien

`F1` et `F2` sont **un seul défaut de sémantique d'état** : la branche
`WARMUP` était évaluée avant tout le reste, sans condition. `F3` est le contrat
d'écriture.

⚠ AUCUN GABARIT N'EST TOUCHÉ. Cette tranche ne change pas un pixel : elle rend
possible ce qui ne l'était pas.
"""
from __future__ import annotations

import re
from types import SimpleNamespace

import pytest

# Même contrainte que les autres suites : la fixture `client` purge
# `sys.modules`, donc aucun import `app.*` au niveau module.


# ═══════════════════════════════════════════════════════════════════════════
# PARTIE 1 — F1 + F2 : LA TABLE DE VÉRITÉ DES TRANSITIONS D'ÉTAT
# ═══════════════════════════════════════════════════════════════════════════


def _log(i, kind, done):
    """Une série minimale — le moteur d'état ne lit que ces trois champs."""
    return SimpleNamespace(id=i, kind=kind, set_index=i, completed=done)


def _exercice(warmups, works):
    """`warmups` / `works` : listes de booléens « déjà validée ? »."""
    logs = [_log(i + 1, "warmup", d) for i, d in enumerate(warmups)]
    logs += [_log(100 + i, "work", d) for i, d in enumerate(works)]
    return SimpleNamespace(set_logs=logs)


def _etat(warmups, works, *, rest=False, suivant="E2"):
    from app.services.console_state import build_console_state

    return build_console_state(
        _exercice(warmups, works),
        next_code=suivant,
        rest_signal=rest,
    )


#: LA TABLE DE VÉRITÉ, ligne à ligne.
#:
#: Colonnes : échauffements (validés ?) · travail (validé ?) · `?rest=1` ·
#: exercice suivant · ÉTAT ATTENDU
#:
#: ⚠ `UI-CP2.1` A CHANGÉ LA MACHINE, ET CETTE TABLE EN EST LA SPÉCIFICATION.
#: L'échauffement n'est plus une porte : il ne peut plus retenir un exercice
#: qui a du travail à faire. Les lignes marquées `CP2.1` sont celles dont
#: l'attendu a CHANGÉ — elles rendaient `warmup`, elles rendent désormais
#: l'état du travail.
#:
#: La colonne `skipwarm` a disparu avec le paramètre : il n'y a plus rien à
#: sauter.
TABLE = [
    # ── un exercice s'ouvre sur son TRAVAIL, quel que soit l'échauffement ──
    ("CP2.1 · neuf", [False, False], [False, False, False], False, "E2", "current_set"),
    ("CP2.1 · echauffement entame", [True, False], [False, False, False], False, "E2", "current_set"),
    ("CP2.1 · echauffement fait", [True, True], [False, False, False], False, "E2", "current_set"),
    # ── le travail et son repos ────────────────────────────────────────────
    ("travail commence + repos", [False, False], [True, False, False], True, "E2", "rest"),
    ("travail commence sans repos", [False, False], [True, False, False], False, "E2", "current_set"),
    ("repos au milieu du travail", [True, True], [True, False, False], True, "E2", "rest"),
    # ── le travail fini termine l'exercice ────────────────────────────────
    ("travail fini, echauffement en attente", [False, False], [True, True, True], False, "E2", "exercise_complete"),
    ("travail fini, sur le DERNIER exercice", [False, False], [True, True, True], False, None, "last_exercise_complete"),
    ("travail fini, tout fait", [True, True], [True, True, True], False, "E2", "exercise_complete"),
    ("travail fini + signal de repos", [False, False], [True, True, True], True, "E2", "exercise_complete"),
    # ── LE SEUL CAS OÙ L'ÉCHAUFFEMENT RESTE SOUVERAIN ─────────────────────
    #    Un exercice sans AUCUNE série de travail : ses échauffements SONT son
    #    travail. Sans cette branche il n'aurait pas d'état.
    ("sans travail, echauffement en attente", [False], [], False, "E2", "warmup"),
    ("sans travail, echauffement fait", [True], [], False, "E2", "exercise_complete"),
    ("sans travail ni echauffement", [], [], False, "E2", "exercise_complete"),
]


@pytest.mark.parametrize(
    ("nom", "warmups", "works", "rest", "suivant", "attendu"),
    TABLE,
    ids=[t[0] for t in TABLE],
)
def test_table_de_verite_des_transitions(nom, warmups, works, rest, suivant,
                                         attendu):
    """Chaque ligne de la table, vérifiée sur le moteur pur."""
    assert _etat(warmups, works, rest=rest, suivant=suivant).state == attendu


def test_l_echauffement_ne_retient_jamais_un_exercice_qui_a_du_travail():
    """L'INVARIANT DE `UI-CP2.1`, énoncé une fois plutôt qu'illustré.

    Constaté par l'opérateur en usage réel : le seul moyen DURABLE de sortir
    de l'échauffement était d'y saisir des valeurs, puisque « fait » se dérive
    de la présence d'un poids ou de répétitions. Le produit imposait donc de
    fabriquer des chiffres ou de rebondir.

    Cette garde balaie la table entière : dès qu'un exercice a la moindre
    série de travail, aucun chemin ne peut rendre `warmup`.
    """
    regressions = []
    for nom, warmups, works, rest, suivant, _ in TABLE:
        if not works:
            continue
        if _etat(warmups, works, rest=rest, suivant=suivant).state == "warmup":
            regressions.append(nom)
    assert not regressions, (
        f"l'échauffement retient encore un exercice qui a du travail : {regressions}"
    )


def test_aucune_valeur_d_echauffement_n_est_requise_pour_avancer():
    """LA PLAINTE DE L'OPÉRATEUR, prise au mot.

    « la redondance que les valeurs doivent être obligatoirement remplies sur
    les échauffements ». Un exercice dont AUCUN échauffement n'est renseigné
    doit pouvoir être exécuté et terminé de bout en bout.
    """
    from app.services.console_state import command_for

    # Rien n'est fait : on peut commencer à travailler.
    depart = _etat([False, False], [False, False, False])
    assert depart.state == "current_set"
    assert depart.warmup_done == 0

    # Tout le travail est fait, toujours aucun échauffement renseigné :
    # l'exercice se termine, et la commande mène ailleurs.
    fin = _etat([False, False], [True, True, True])
    assert fin.state == "exercise_complete"
    assert fin.warmup_done == 0
    assert command_for(fin)["label"] == "CONTINUER → E2"


def test_l_echauffement_reste_souverain_quand_il_EST_le_travail():
    """LA GARDE DE LA GARDE — l'inverse doit tenir aussi.

    Retirer purement la souveraineté de l'échauffement aurait laissé sans état
    un exercice qui n'a QUE des échauffements. La garde précédente serait alors
    satisfaite par un moteur qui n'affiche jamais `warmup`.
    """
    etat = _etat([False, False], [])
    assert etat.state == "warmup"
    assert etat.current_set is not None


def test_plus_aucune_sortie_ne_propose_de_sauter_l_echauffement():
    """`§5.3` — LA SOUSTRACTION PART AVEC SON REMPLAÇANT.

    « SAUTER L'ÉCHAUFFEMENT » existait parce que l'échauffement RETENAIT
    l'exercice, et elle ne tenait pas sa promesse : `?skipwarm=1` vivait dans
    l'URL, donc le saut ne survivait pas au rechargement — « le CTA ne va nulle
    part », constaté en usage.

    Ce qui la remplace n'est pas un autre bouton : il n'y a plus de porte. Une
    commande dont l'objet a disparu se retire, elle ne se remplace pas.
    """
    from app.services.console_state import secondary_for

    for warmups, works in (([False, False], [False, False, False]),
                           ([True, False], [False, False, False]),
                           ([False], [])):
        sorties = secondary_for(_etat(warmups, works))
        libelles = [s["label"] for s in sorties]
        assert not any("ÉCHAUFFEMENT" in lab.upper() for lab in libelles), (
            f"une sortie propose encore de sauter l'échauffement : {libelles}"
        )
        assert not any(s.get("kind") == "skip_warmup" for s in sorties)


# ⚠ TROIS GARDES DE `UI-CP2.0` SONT SUPERSÉDÉES PAR `UI-CP2.1`, PAS RETIRÉES.
#
#   `test_l_invariant_de_monotonie_tient_sur_toute_la_table`
#       tenait « une fois le travail commencé, plus jamais `warmup` ».
#       → remplacée par `test_l_echauffement_ne_retient_jamais_un_exercice_
#         qui_a_du_travail`, qui n'attend plus que le travail COMMENCE :
#         l'échauffement ne retient rien, dès la première seconde.
#
#   `test_l_echauffement_reste_souverain_tant_que_rien_n_a_commence`
#       tenait exactement la propriété que `UI-CP2.1` RETIRE. La garder aurait
#       interdit la décision de l'opérateur.
#       → remplacée par `test_l_echauffement_reste_souverain_quand_il_EST_le_
#         travail`, qui garde le seul cas où la souveraineté a encore un sens.
#
#   `test_skipwarm_n_ecrit_toujours_rien`
#       gardait qu'un paramètre n'écrivait rien. Le paramètre n'existe plus.
#       → remplacée par `test_aucune_valeur_d_echauffement_n_est_requise_pour_
#         avancer`, qui tient la propriété d'usage plutôt que le moyen.
#
# Chacune est donc remplacée par une garde plus forte, dans le même fichier et
# la même livraison.


def test_f1_la_commande_dominante_cesse_de_mentir():
    """LE DÉFAUT, DIT EN TERMES D'UTILISATEUR.

    Trois séries sur trois faites, un échauffement non coché : l'instrument
    rendait `WARMUP` et sa commande dominante disait **« PASSER AUX SÉRIES »**
    — vers des séries déjà faites. `EXERCICE_COMPLETE` n'était jamais atteint,
    donc « CONTINUER → E2 » n'apparaissait jamais.
    """
    from app.services.console_state import command_for

    etat = _etat([False, False], [True, True, True])
    assert etat.work_done == etat.work_total == 3
    assert etat.state == "exercise_complete"
    assert command_for(etat)["label"] == "CONTINUER → E2"


# ═══════════════════════════════════════════════════════════════════════════
# PARTIE 2 — F3 : L'ÉCRITURE DE SÉRIE DEVIENT UN PATCH PARTIEL
#
# Ces gardes exercent le PRODUIT — POST réels sur la route canonique. Une garde
# qui appellerait `_persist_set_values` à la main prouverait la fonction, pas
# le contrat que l'instrument utilisera.
# ═══════════════════════════════════════════════════════════════════════════


def _seance(client, slug="push-a"):
    r = client.post("/sessions", data={"template_slug": slug},
                    follow_redirects=False)
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def _premier_exercice(sid):
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SessionExercise

    with SessionLocal() as db:
        return db.execute(
            select(SessionExercise)
            .where(SessionExercise.session_id == sid)
            .order_by(SessionExercise.position)
        ).scalars().first().id


def _series(se_id, kind="work"):
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SetLog

    with SessionLocal() as db:
        logs = db.execute(
            select(SetLog).where(SetLog.session_exercise_id == se_id)
            .order_by(SetLog.set_index)
        ).scalars().all()
        return [(sl.id, sl.weight_kg, sl.reps, sl.completed)
                for sl in logs if sl.kind == kind]


def test_f3_trois_series_postees_une_a_une_survivent_toutes(client):
    """LE DÉFAUT MESURÉ, ET SA PREUVE.

    Au labo, sur une séance réelle, trois séries postées une à une laissaient
    **une seule** survivante : chaque envoi effaçait le précédent, parce que la
    boucle de persistance écrivait TOUTES les séries de l'exercice depuis le
    formulaire, et qu'une clé absente valait `None`.

    C'est le contrat que l'instrument d'exécution doit pouvoir utiliser : une
    série envoyée met à jour CETTE série, et laisse ses sœurs INCHANGÉES.
    """
    sid = _seance(client)
    se_id = _premier_exercice(sid)
    ids = [s[0] for s in _series(se_id)]
    assert len(ids) >= 3, "prémisse invalide : moins de trois séries de travail"

    for rang, sid_serie in enumerate(ids[:3]):
        client.post(
            f"/sessions/{sid}/exercises/{se_id}",
            data={f"set_{sid_serie}_weight_kg": "60",
                  f"set_{sid_serie}_reps": str(10 - rang),
                  "nav": "stay_norest"},
            follow_redirects=False,
        )

    apres = {s[0]: s for s in _series(se_id)}
    for rang, sid_serie in enumerate(ids[:3]):
        _, poids, reps, faite = apres[sid_serie]
        assert faite is True, f"la série {rang + 1} a été effacée par une autre"
        assert poids == 60.0
        assert reps == 10 - rang


def test_f3_une_serie_absente_du_formulaire_est_inchangee(client):
    """« ABSENT » veut dire INCHANGÉ, et rien d'autre."""
    sid = _seance(client)
    se_id = _premier_exercice(sid)
    ids = [s[0] for s in _series(se_id)]

    client.post(f"/sessions/{sid}/exercises/{se_id}",
                data={f"set_{ids[0]}_weight_kg": "80", f"set_{ids[0]}_reps": "8",
                      "nav": "stay_norest"}, follow_redirects=False)
    # Un second envoi qui ne cite QUE la deuxième série.
    client.post(f"/sessions/{sid}/exercises/{se_id}",
                data={f"set_{ids[1]}_weight_kg": "82", f"set_{ids[1]}_reps": "7",
                      "nav": "stay_norest"}, follow_redirects=False)

    apres = {s[0]: s for s in _series(se_id)}
    assert apres[ids[0]][1] == 80.0, "la première série a bougé sans être citée"
    assert apres[ids[0]][3] is True
    assert apres[ids[1]][1] == 82.0


def test_f3_un_champ_vide_reste_un_effacement_explicite(client):
    """⚠ « VIDE » N'EST PAS « ABSENT », et la distinction est le cœur du fix.

    `Sx_24 §E` : vide = non fait. Deux gardes existantes en dépendent, et elles
    postent des chaînes VIDES, pas des clés manquantes. Confondre les deux
    aurait rendu impossible d'effacer une série en la vidant — une capacité
    réelle, pas un effet de bord.
    """
    sid = _seance(client)
    se_id = _premier_exercice(sid)
    ids = [s[0] for s in _series(se_id)]

    client.post(f"/sessions/{sid}/exercises/{se_id}",
                data={f"set_{ids[0]}_weight_kg": "80", f"set_{ids[0]}_reps": "8",
                      "nav": "stay_norest"}, follow_redirects=False)
    assert {s[0]: s for s in _series(se_id)}[ids[0]][3] is True

    client.post(f"/sessions/{sid}/exercises/{se_id}",
                data={f"set_{ids[0]}_weight_kg": "", f"set_{ids[0]}_reps": "",
                      "nav": "stay_norest"}, follow_redirects=False)
    apres = {s[0]: s for s in _series(se_id)}[ids[0]]
    # Assertions séparées (`python:S9073`) : à l'échec, il faut savoir LEQUEL
    # des trois n'a pas été effacé, pas seulement que l'ensemble a échoué.
    assert apres[1] is None, "le poids n'est pas effacé"
    assert apres[2] is None, "les répétitions ne sont pas effacées"
    assert apres[3] is False, "un champ vidé n'efface plus la série"


def test_f3_la_correction_nommee_efface_toujours(client):
    """`RETIRER CETTE SÉRIE` — l'effacement EXPLICITE reste explicite."""
    sid = _seance(client)
    se_id = _premier_exercice(sid)
    ids = [s[0] for s in _series(se_id)]

    client.post(f"/sessions/{sid}/exercises/{se_id}",
                data={f"set_{ids[0]}_weight_kg": "80", f"set_{ids[0]}_reps": "8",
                      "nav": "stay_norest"}, follow_redirects=False)
    client.post(f"/sessions/{sid}/exercises/{se_id}",
                data={"clear_set": str(ids[0]), "nav": "stay_norest"},
                follow_redirects=False)

    apres = {s[0]: s for s in _series(se_id)}[ids[0]]
    assert apres[1] is None, "le poids survit à `clear_set`"
    assert apres[2] is None, "les répétitions survivent à `clear_set`"
    assert apres[3] is False, "la série reste marquée faite après `clear_set`"


def test_f3_le_formulaire_complet_se_comporte_exactement_comme_avant(client):
    """LA NON-RÉGRESSION QUI COMPTE LE PLUS.

    Le gabarit d'aujourd'hui poste TOUTES les séries de l'exercice à chaque
    envoi. Son comportement ne doit pas bouger d'un iota : les séries citées
    sont écrites, celles laissées vides sont non faites.
    """
    sid = _seance(client)
    se_id = _premier_exercice(sid)
    ids = [s[0] for s in _series(se_id)]

    donnees = {"nav": "stay_norest"}
    for i, sid_serie in enumerate(ids):
        rempli = i != 1                      # la deuxième reste vide
        donnees[f"set_{sid_serie}_weight_kg"] = "80" if rempli else ""
        donnees[f"set_{sid_serie}_reps"] = "10" if rempli else ""
    client.post(f"/sessions/{sid}/exercises/{se_id}", data=donnees,
                follow_redirects=False)

    apres = {s[0]: s for s in _series(se_id)}
    assert apres[ids[0]][3] is True
    assert apres[ids[1]][3] is False
    assert apres[ids[2]][3] is True


def test_f3_la_navigation_arriere_enregistre_toujours(client):
    """`nav=prev` — enregistrer PUIS revenir. Capacité préexistante.

    Un lien ne sauvegarde pas ; l'utilisateur qui vient de saisir une valeur la
    perdrait. `CLAUDE.md §5.3` interdit de la retirer, et un changement de
    contrat d'écriture est exactement le genre de tranche qui la casserait sans
    le voir.
    """
    sid = _seance(client)
    se_id = _premier_exercice(sid)
    ids = [s[0] for s in _series(se_id)]

    r = client.post(f"/sessions/{sid}/exercises/{se_id}",
                    data={f"set_{ids[0]}_weight_kg": "75",
                          f"set_{ids[0]}_reps": "9", "nav": "prev"},
                    follow_redirects=False)
    assert r.status_code in (302, 303)
    apres = {s[0]: s for s in _series(se_id)}[ids[0]]
    assert apres[1] == 75.0, "le poids n'a pas été enregistré avant de revenir"
    assert apres[2] == 9, "les répétitions n'ont pas été enregistrées"
    assert apres[3] is True, "la série n'est pas marquée faite"


def test_f3_les_echauffements_ne_sont_pas_emportes(client):
    """Une écriture de série de TRAVAIL ne touche pas les échauffements.

    Sous l'ancien contrat, poster une série de travail sans citer les
    échauffements les remettait à zéro — le même défaut, sur l'autre famille
    de séries. Personne ne le voyait parce que le formulaire citait tout.
    """
    sid = _seance(client)
    se_id = _premier_exercice(sid)
    warm = _series(se_id, kind="warmup")
    if not warm:
        pytest.skip("cet exercice n'a pas d'échauffement")
    travail = [s[0] for s in _series(se_id)]

    client.post(f"/sessions/{sid}/exercises/{se_id}",
                data={f"set_{warm[0][0]}_weight_kg": "20",
                      f"set_{warm[0][0]}_reps": "12", "nav": "stay_norest"},
                follow_redirects=False)
    client.post(f"/sessions/{sid}/exercises/{se_id}",
                data={f"set_{travail[0]}_weight_kg": "60",
                      f"set_{travail[0]}_reps": "10", "nav": "stay_norest"},
                follow_redirects=False)

    apres = {s[0]: s for s in _series(se_id, kind="warmup")}
    assert apres[warm[0][0]][3] is True, (
        "l'échauffement a été effacé par une écriture de série de travail"
    )


def test_f1_f2_et_f3_ensemble_sur_une_seance_reelle(client):
    """LE CHEMIN ORDINAIRE, DE BOUT EN BOUT.

    Enregistrer les trois séries de travail **une par une**, sans jamais
    renseigner un échauffement, et vérifier que l'exercice se termine
    réellement.

    ⚠ `UI-CP2.1` — il n'y a plus rien à sauter : l'exercice s'ouvre sur son
    travail. Ce chemin est donc devenu le chemin PAR DÉFAUT, plus un
    contournement.

    Aucun des trois défauts pris isolément ne rend ce chemin possible : F3
    conserve les séries, F1 laisse l'exercice se terminer, F2 autorise le repos
    entre-temps.
    """
    from app.services.console_state import build_console_state

    sid = _seance(client)
    se_id = _premier_exercice(sid)
    ids = [s[0] for s in _series(se_id)]

    for rang, sid_serie in enumerate(ids):
        client.post(f"/sessions/{sid}/exercises/{se_id}",
                    data={f"set_{sid_serie}_weight_kg": "60",
                          f"set_{sid_serie}_reps": str(10 - rang),
                          "nav": "stay"},
                    follow_redirects=False)

    assert all(s[3] for s in _series(se_id)), "des séries ont été perdues"

    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from app.database import SessionLocal
    from app.models.session import SessionExercise

    with SessionLocal() as db:
        se = db.execute(
            select(SessionExercise).where(SessionExercise.id == se_id)
            .options(selectinload(SessionExercise.set_logs))
        ).scalar_one()
        etat = build_console_state(se, next_code="E2")

    assert etat.state == "exercise_complete", (
        "l'exercice ne se termine pas alors que tout son travail est fait"
    )
