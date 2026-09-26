"""`UI-CP8R` — le repos a une origine de temps durable, et elle est juste.

LE DÉFAUT QUE CETTE TRANCHE FERME
---------------------------------
Reproduit au navigateur avant d'écrire une ligne :

    série validée   → REPOS 1:30
    attendre 3 s
    recharger       → REPOS 1:30      ← identique

`?rest=1` ne peut affirmer qu'une chose : « un repos vient de démarrer sur
CETTE requête ». Il ne porte **aucune origine de temps**. Le gabarit posait
donc `data-rest-started`, un drapeau booléen, et le décompte repartait de sa
durée pleine à chaque rendu.

Deux colonnes additives et nullables le remplacent — `SetLog.completed_at`
(un FAIT : quand la série a été faite) et `SetLog.rest_dismissed_at` (une
DÉCISION : l'utilisateur a choisi de dépasser ce repos). L'état `REST` est
**dérivé** d'elles à chaque rendu, donc il ne peut pas se désynchroniser.

CE QUE CE MODULE PROUVE
-----------------------
Les neuf preuves `A`–`I` du paquet de conception, plus les cinq amendements
`J`–`N` de l'arbitrage opérateur.

⚠ AUCUNE GARDE ICI N'ATTEINT L'ÉTAT `REST` PAR UNE URL. C'est le fond même
de la tranche : si un paramètre pouvait encore fabriquer ou supprimer un
repos, il subsisterait deux systèmes de vérité concurrents. Les gardes `M`
et `N` vérifient explicitement qu'il n'en reste qu'un.
"""
from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta

FENETRE = 90  # `REST_FALLBACK_SECONDS` — politique inchangée par la tranche.


# ───────────────────────── montage ─────────────────────────


def _seance(db, user_id, *, n_series=3):
    """Un exercice, `n_series` séries de travail, aucune faite."""
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    s = WorkoutSession(
        user_id=user_id,
        template_slug_snapshot="cp8r",
        template_name_snapshot="CP8R",
        started_at=datetime.now(UTC),
        status="in_progress",
    )
    se = SessionExercise(
        exercise_code_snapshot="E1",
        exercise_name_snapshot="Développé couché",
        position=1,
    )
    for i in range(n_series):
        se.set_logs.append(SetLog(
            kind="work", set_index=i + 1,
            weight_kg=None, reps=None, completed=False,
        ))
    s.session_exercises.append(se)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def _ids(db, session_id):
    from app.models.session import SessionExercise, SetLog

    se = db.query(SessionExercise).filter_by(session_id=session_id).one()
    series = (db.query(SetLog)
              .filter_by(session_exercise_id=se.id, kind="work")
              .order_by(SetLog.set_index).all())
    return se.id, [sl.id for sl in series]


def _faire(db, set_id, *, il_y_a=0, poids=80.0, reps=8):
    """Marque une série faite, à `il_y_a` secondes dans le passé."""
    from app.models.session import SetLog

    sl = db.query(SetLog).filter_by(id=set_id).one()
    sl.weight_kg, sl.reps, sl.completed = poids, reps, True
    sl.completed_at = datetime.now(UTC) - timedelta(seconds=il_y_a)
    db.commit()


def _restant(client, session_id, se_id):
    """Le restant RENDU, ou `None` s'il n'y a pas de repos."""
    body = client.get(f"/sessions/{session_id}?active={se_id}").text
    m = re.search(r'data-rest-remaining="(\d+)"', body)
    return int(m.group(1)) if m else None


def _monter(client, **kw):
    """Séance + identifiants, dans une session DB refermée."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        s = _seance(db, user.id, **kw)
        se_id, sets = _ids(db, s.id)
        return s.id, se_id, sets


# ═══════════════════════════════════════════════════════════════════════
#  A–C — LE TEMPS S'ÉCOULE VRAIMENT
# ═══════════════════════════════════════════════════════════════════════


def test_A_le_rendu_soustrait_le_temps_ecoule(client):
    """`A` — rendu à T0+3 s ⇒ ~87 s, jamais 90.

    C'est le défaut d'origine, réduit à son noyau. Avant la tranche, cette
    valeur était `90` quel que soit le temps passé.
    """
    from app.database import SessionLocal

    sid, se_id, sets = _monter(client)
    with SessionLocal() as db:
        _faire(db, sets[0], il_y_a=3)

    restant = _restant(client, sid, se_id)
    assert restant is not None, "aucun repos rendu après une série faite"
    assert 85 <= restant <= 88, (
        f"le rendu n'a pas soustrait le temps écoulé : {restant}"
    )


def test_B_un_rechargement_ne_relance_pas_le_decompte(client):
    """`B` — LE SYMPTÔME EXACT DU DOGFOOD.

    Deux rendus successifs de la MÊME URL doivent décroître. Avant la
    tranche, les deux rendaient `90`.
    """
    from app.database import SessionLocal

    sid, se_id, sets = _monter(client)
    with SessionLocal() as db:
        _faire(db, sets[0], il_y_a=30)

    premier = _restant(client, sid, se_id)
    with SessionLocal() as db:
        _faire(db, sets[0], il_y_a=50)  # 20 s de plus se sont écoulées
    second = _restant(client, sid, se_id)

    assert premier is not None
    assert second is not None
    assert second < premier, (
        f"le décompte est reparti en arrière : {premier} → {second}"
    )
    assert 18 <= premier - second <= 22, (premier, second)


def test_C_un_repos_expire_n_est_plus_un_repos(client):
    """`C` — au-delà de la fenêtre, l'état sort tout seul.

    Personne n'a besoin d'annoncer la fin : elle se déduit. C'est ce qui
    rend la sortie correcte même si l'onglet a dormi, si le JavaScript n'a
    jamais tourné, ou si l'utilisateur revient le lendemain.
    """
    from app.database import SessionLocal

    sid, se_id, sets = _monter(client)
    with SessionLocal() as db:
        _faire(db, sets[0], il_y_a=FENETRE + 30)

    assert _restant(client, sid, se_id) is None


# ═══════════════════════════════════════════════════════════════════════
#  D — LE DÉCOMPTE CLIENT NE COMPTE PAS LES RAPPELS
# ═══════════════════════════════════════════════════════════════════════


def test_D_le_client_raisonne_sur_une_echeance_pas_sur_des_rappels():
    """`D` — un onglet bridé ne doit pas allonger le repos.

    Un `setInterval` n'est pas une horloge : le navigateur espace ses
    rappels en arrière-plan. Décrémenter à chaque tick transformerait
    chaque rappel manqué en une seconde de repos qui n'a pas existé.

    La garde lit le CODE, parce que c'est une propriété structurelle : le
    restant se calcule depuis une échéance, et le retour au premier plan
    repeint immédiatement.
    """
    import pathlib

    js = (pathlib.Path(__file__).resolve().parent.parent
          / "app/static/js/session_focus.js").read_text(encoding="utf-8")
    code = re.sub(r"/\*.*?\*/", "", js, flags=re.DOTALL)
    code = re.sub(r"(?m)^\s*//.*$", "", code)

    assert "deadline - Date.now()" in code, (
        "le restant n'est pas calculé depuis une échéance"
    )
    assert not re.search(r"remaining\s*-=|\bsecondes?\s*--", code), (
        "un décrément par tick est revenu : la dérive avec lui"
    )
    assert "visibilitychange" in code, (
        "le retour au premier plan ne repeint pas"
    )
    # ⚠ `§6` — surtout PAS `performance.now()` comme horloge locale : sur
    # WebKit elle n'avance pas de façon fiable au travers d'une veille de
    # l'OS, donc un téléphone verrouillé figerait le décompte.
    assert "performance.now()" not in code, (
        "`performance.now()` ne survit pas à une mise en veille WebKit"
    )


# ═══════════════════════════════════════════════════════════════════════
#  E–F — CE QUI NE DOIT PAS FABRIQUER DE REPOS
# ═══════════════════════════════════════════════════════════════════════


def test_E_corriger_une_vieille_serie_ne_relance_rien(client):
    """`E` — la correction préserve `completed_at`, donc ne relance pas.

    Sans la préservation, rectifier une faute de frappe sur la série 1
    pendant la série 3 imposerait 90 secondes d'arrêt.
    """
    from app.database import SessionLocal
    from app.models.session import SetLog

    sid, se_id, sets = _monter(client)
    with SessionLocal() as db:
        _faire(db, sets[0], il_y_a=FENETRE + 600)  # il y a dix minutes
    assert _restant(client, sid, se_id) is None

    client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={f"set_{sets[0]}_weight_kg": "82.5",
              f"set_{sets[0]}_reps": "8", "nav": "stay_norest"},
        follow_redirects=False,
    )

    with SessionLocal() as db:
        sl = db.query(SetLog).filter_by(id=sets[0]).one()
        assert sl.weight_kg == 82.5, "la correction n'a pas été enregistrée"
        age = (datetime.now(UTC) - sl.completed_at.replace(tzinfo=UTC))
    assert age.total_seconds() > FENETRE, (
        "`completed_at` a été réécrit : la correction a fabriqué un instant"
    )
    assert _restant(client, sid, se_id) is None


def test_F_une_ligne_historique_ne_fabrique_aucun_repos(client):
    """`F` — `completed = True` + `completed_at = NULL` ⇒ jamais de repos.

    C'est la forme EXACTE de toute série d'avant la migration. Fabriquer
    un horodatage au backfill aurait mis d'anciennes séances en repos
    actif ; ne rien fabriquer les laisse muettes, ce qui est la vérité.
    """
    from app.database import SessionLocal
    from app.models.session import SetLog

    sid, se_id, sets = _monter(client)
    with SessionLocal() as db:
        sl = db.query(SetLog).filter_by(id=sets[0]).one()
        sl.weight_kg, sl.reps, sl.completed = 80.0, 8, True
        sl.completed_at = None  # ← la ligne d'avant la migration
        db.commit()

    assert _restant(client, sid, se_id) is None, (
        "une série sans heure connue a produit un repos"
    )


# ═══════════════════════════════════════════════════════════════════════
#  G — LE SAUT SURVIT
# ═══════════════════════════════════════════════════════════════════════


def test_G_le_saut_de_repos_survit_au_rechargement(client):
    """`G` — LA RAISON D'ÊTRE DE LA SECONDE COLONNE.

    Avant la tranche, passer le repos était un GET vers la même page sans
    `rest=1` : ça ne survivait au rechargement que parce que l'URL
    rechargée perdait le paramètre. En retirant au paramètre son autorité,
    on retirait au saut son unique mécanisme — sans écriture, le rendu
    suivant aurait re-dérivé le repos et annulé la décision.
    """
    from app.database import SessionLocal
    from app.models.session import SetLog

    sid, se_id, sets = _monter(client)
    with SessionLocal() as db:
        _faire(db, sets[0], il_y_a=5)
    assert _restant(client, sid, se_id) is not None

    r = client.post(f"/sessions/{sid}/exercises/{se_id}/rest/skip",
                    follow_redirects=False)
    assert r.status_code == 303

    assert _restant(client, sid, se_id) is None, "le repos est revenu"
    # …et il reste absent au rechargement suivant, puis au suivant.
    assert _restant(client, sid, se_id) is None

    with SessionLocal() as db:
        sl = db.query(SetLog).filter_by(id=sets[0]).one()
        assert sl.rest_dismissed_at is not None, (
            "le saut n'a rien écrit : il ne tient que par l'URL"
        )


def test_G_bis_le_saut_est_une_soumission_native_sans_javascript(client):
    """`G` — et il fonctionne sans JavaScript.

    Le geste écrit désormais, donc ce ne peut plus être un lien. Il ne peut
    pas non plus être un `<form>` imbriqué dans celui de la carte : ce
    serait du HTML invalide. `formaction` dévie un bouton de soumission du
    formulaire existant — natif, sans script.
    """
    import pathlib

    card = (pathlib.Path(__file__).resolve().parent.parent
            / "app/templates/_partials/exercise_card.html").read_text(
                encoding="utf-8")
    balisage = re.sub(r"\{#.*?#\}", "", card, flags=re.DOTALL)

    assert balisage.count("dismiss_rest") == 2, (
        "les deux sorties de repos — la ligne de série et la commande du "
        "dock — doivent viser la même route, et elle seule"
    )
    assert "formaction=" in balisage
    # Un `<form>` dans un `<form>` est invalide : le navigateur le supprime
    # silencieusement, et la sortie de repos cesserait d'exister.
    assert balisage.count("<form") == 1, (
        "un second formulaire est apparu dans la carte"
    )


# ═══════════════════════════════════════════════════════════════════════
#  H–I — COMPATIBILITÉ
# ═══════════════════════════════════════════════════════════════════════


def test_H_une_seance_d_avant_la_migration_se_rend_sans_erreur(client):
    """`H` — les lignes anciennes restent lisibles.

    Séance terminée, séries complétées, aucune heure. Le rendu ne doit ni
    échouer ni inventer un repos.
    """
    from app.database import SessionLocal
    from app.models.session import SetLog, WorkoutSession

    sid, se_id, sets = _monter(client)
    with SessionLocal() as db:
        for set_id in sets:
            sl = db.query(SetLog).filter_by(id=set_id).one()
            sl.weight_kg, sl.reps, sl.completed = 80.0, 8, True
            sl.completed_at = None
        s = db.query(WorkoutSession).filter_by(id=sid).one()
        s.status, s.ended_at = "completed", datetime.now(UTC)
        db.commit()

    r = client.get(f"/sessions/{sid}?active={se_id}", follow_redirects=False)
    assert r.status_code in (200, 303), r.text[:300]
    if r.status_code == 200:
        assert "data-rest-remaining" not in r.text


def test_I_l_export_et_la_restauration_portent_la_chronologie(client):
    """`I` — aller-retour, avec et sans les clés neuves.

    Option A de l'arbitrage : les deux champs partent dans l'export et
    reviennent à la restauration. Un export ANCIEN, dépourvu de ces clés,
    doit se restaurer sans erreur — l'absence et `null` disent la même
    chose, « heure inconnue », donc aucun numéro de version n'est requis.
    """
    from app.database import SessionLocal
    from app.services.export_builder import CSV_HEADERS, build_json_payload
    from app.services.restore import restore_from_json_payload

    sid, se_id, sets = _monter(client)
    with SessionLocal() as db:
        _faire(db, sets[0], il_y_a=5)
    client.post(f"/sessions/{sid}/exercises/{se_id}/rest/skip",
                follow_redirects=False)

    with SessionLocal() as db:
        charge = build_json_payload(db)

    series = charge["sessions"][0]["exercises"][0]["sets"]
    assert "completed_at" in series[0]
    assert "rest_dismissed_at" in series[0]
    assert series[0]["completed_at"] is not None
    assert series[0]["rest_dismissed_at"] is not None
    assert series[1]["completed_at"] is None, (
        "une série jamais faite ne doit porter aucune heure"
    )
    assert CSV_HEADERS[-2:] == ["completed_at", "rest_dismissed_at"], (
        "les colonnes CSV doivent être APPENDUES : un consommateur qui lit "
        "par index ne doit pas être décalé"
    )

    # ⚠ `SCHEMA_VERSION` N'EST PAS INCRÉMENTÉ, ET C'EST UN CHOIX MOTIVÉ.
    #
    # `backup_verifier` refuse toute charge dont la version DIFFÈRE de la
    # courante. L'incrémenter invaliderait donc, d'un coup, toutes les
    # sauvegardes déjà écrites sur disque — pour signaler deux clés
    # OPTIONNELLES dont l'absence a exactement le même sens que `null`.
    # Le remède serait plus destructeur que l'absence de remède.
    #
    # Un export d'AVANT la migration : les clés n'existent pas du tout.
    ancien = dict(charge)
    ancien["sessions"] = [
        {k: v for k, v in charge["sessions"][0].items() if k != "exercises"}
        | {"exercises": [
            dict(charge["sessions"][0]["exercises"][0],
                 sets=[{k: v for k, v in sl.items()
                        if k not in ("completed_at", "rest_dismissed_at")}
                       for sl in series])
        ]}
    ]
    from app.database import SessionLocal as _SL
    from app.models.session import SetLog, WorkoutSession

    with _SL() as db:
        db.query(SetLog).delete()
        db.query(WorkoutSession).delete()
        db.commit()
        res = restore_from_json_payload(db, ancien)
        assert not res.errors, res.errors
        db.commit()
        for sl in db.query(SetLog).all():
            assert sl.completed_at is None
            assert sl.rest_dismissed_at is None


# ═══════════════════════════════════════════════════════════════════════
#  J–L — L'ÉPISODE DE COMPLÉTION (amendements opérateur)
# ═══════════════════════════════════════════════════════════════════════


def test_J_un_saut_ne_survit_pas_a_une_nouvelle_execution(client):
    """`J` — L'INVARIANT D'ÉPISODE.

        compléter → passer le repos → retirer la série → refaire

    Le saut appartenait à l'exécution PRÉCÉDENTE. S'il survivait, la série
    refaite n'aurait pas de repos, et l'utilisateur ne pourrait ni le voir
    venir ni l'expliquer : rien à l'écran ne rappelle un geste fait avant
    un effacement.
    """
    from app.database import SessionLocal
    from app.models.session import SetLog

    sid, se_id, sets = _monter(client)

    client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={f"set_{sets[0]}_weight_kg": "80", f"set_{sets[0]}_reps": "8",
              "nav": "stay"},
        follow_redirects=False,
    )
    client.post(f"/sessions/{sid}/exercises/{se_id}/rest/skip",
                follow_redirects=False)
    with SessionLocal() as db:
        assert db.query(SetLog).filter_by(id=sets[0]).one().rest_dismissed_at

    # RETIRER CETTE SÉRIE — dé-complétion explicite.
    client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={"clear_set": str(sets[0]), "nav": "stay_norest"},
        follow_redirects=False,
    )
    with SessionLocal() as db:
        sl = db.query(SetLog).filter_by(id=sets[0]).one()
        assert sl.completed is False
        assert sl.completed_at is None, "l'heure d'une série effacée subsiste"
        assert sl.rest_dismissed_at is None, (
            "la décision de saut a survécu à l'effacement de la série"
        )

    # Refaite : nouvel épisode, nouveau repos.
    client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={f"set_{sets[0]}_weight_kg": "85", f"set_{sets[0]}_reps": "6",
              "nav": "stay"},
        follow_redirects=False,
    )
    with SessionLocal() as db:
        sl = db.query(SetLog).filter_by(id=sets[0]).one()
        assert sl.completed_at is not None
        assert sl.rest_dismissed_at is None
    assert _restant(client, sid, se_id) is not None, (
        "la série refaite n'a produit aucun repos"
    )


def test_J_bis_une_serie_incomplete_portant_un_saut_le_perd_en_se_completant(client):
    """`J` — le versant que le chemin nominal ne peut pas atteindre.

    ⚠ CETTE GARDE EXISTE PARCE QUE LA MUTATION A SURVÉCU.

    `test_J` passe par « retirer la série », qui efface déjà les deux
    horodatages. Quand on arrive ensuite à INCOMPLÈTE → COMPLÈTE, le
    dismissal est donc DÉJÀ nul : retirer l'effacement de cette branche ne
    faisait rougir aucun test. Une ligne qu'aucune garde ne peut tuer n'est
    protégée par personne.

    L'état existe pourtant vraiment. `restore` lit `completed`,
    `completed_at` et `rest_dismissed_at` de façon INDÉPENDANTE depuis le
    JSON : une charge restaurée peut parfaitement porter une série
    incomplète avec un saut enregistré. Sans l'effacement à l'entrée, la
    première exécution de cette série n'aurait aucun repos, et rien à
    l'écran ne pourrait l'expliquer.

    On sème donc exactement cet état, comme une restauration le produirait.
    """
    from app.database import SessionLocal
    from app.models.session import SetLog

    sid, se_id, sets = _monter(client)
    with SessionLocal() as db:
        sl = db.query(SetLog).filter_by(id=sets[0]).one()
        sl.completed, sl.completed_at = False, None
        sl.rest_dismissed_at = datetime.now(UTC) - timedelta(days=3)
        db.commit()

    client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={f"set_{sets[0]}_weight_kg": "80", f"set_{sets[0]}_reps": "8",
              "nav": "stay"},
        follow_redirects=False,
    )

    with SessionLocal() as db:
        sl = db.query(SetLog).filter_by(id=sets[0]).one()
        assert sl.completed_at is not None
        assert sl.rest_dismissed_at is None, (
            "un saut vieux de trois jours a survécu dans une exécution neuve"
        )
    assert _restant(client, sid, se_id) is not None, (
        "la série exécutée n'a produit aucun repos : un saut périmé l'a mangé"
    )


def test_K_complete_vers_complete_preserve_les_deux_horodatages(client):
    """`K` — une correction ne touche NI l'heure NI la décision.

    Le versant complémentaire de `J` : ce qui doit être effacé l'est
    (`J`), ce qui doit être préservé l'est (`K`). Les deux ensemble
    définissent l'épisode.
    """
    from app.database import SessionLocal
    from app.models.session import SetLog

    sid, se_id, sets = _monter(client)
    client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={f"set_{sets[0]}_weight_kg": "80", f"set_{sets[0]}_reps": "8",
              "nav": "stay"},
        follow_redirects=False,
    )
    client.post(f"/sessions/{sid}/exercises/{se_id}/rest/skip",
                follow_redirects=False)
    with SessionLocal() as db:
        sl = db.query(SetLog).filter_by(id=sets[0]).one()
        fait_a, saute_a = sl.completed_at, sl.rest_dismissed_at

    client.post(
        f"/sessions/{sid}/exercises/{se_id}",
        data={f"set_{sets[0]}_weight_kg": "82.5", f"set_{sets[0]}_reps": "8",
              "nav": "stay_norest"},
        follow_redirects=False,
    )
    with SessionLocal() as db:
        sl = db.query(SetLog).filter_by(id=sets[0]).one()
        assert sl.weight_kg == 82.5
        assert sl.completed_at == fait_a, "`completed_at` réécrit"
        assert sl.rest_dismissed_at == saute_a, "`rest_dismissed_at` réécrit"


def test_L_un_saut_repete_ne_reecrit_pas_l_histoire(client):
    """`L` — idempotence applicative du POST de saut.

    Un double tap, un renvoi de formulaire, un re-POST après un réseau
    capricieux : le second passage préserve l'horodatage du premier.
    Déplacer un instant déjà vécu serait réécrire l'histoire.
    """
    from app.database import SessionLocal
    from app.models.session import SetLog

    sid, se_id, sets = _monter(client)
    with SessionLocal() as db:
        _faire(db, sets[0], il_y_a=5)

    client.post(f"/sessions/{sid}/exercises/{se_id}/rest/skip",
                follow_redirects=False)
    with SessionLocal() as db:
        premier = db.query(SetLog).filter_by(id=sets[0]).one().rest_dismissed_at
    assert premier is not None

    for _ in range(3):
        r = client.post(f"/sessions/{sid}/exercises/{se_id}/rest/skip",
                        follow_redirects=False)
        assert r.status_code == 303
    with SessionLocal() as db:
        apres = db.query(SetLog).filter_by(id=sets[0]).one().rest_dismissed_at
    assert apres == premier, f"le saut a été réécrit : {premier} → {apres}"


# ═══════════════════════════════════════════════════════════════════════
#  M–N — L'EXTINCTION DU PARAMÈTRE DE REQUÊTE
# ═══════════════════════════════════════════════════════════════════════


def test_M_un_rest_1_entrant_ne_fabrique_aucun_repos(client):
    """`M` — une URL ancienne ne peut pas contredire les faits.

    Un signet, un historique de navigateur, un retour arrière : `?rest=1`
    reste syntaxiquement possible. Il doit être INERTE. S'il pouvait encore
    imposer l'état, deux systèmes de vérité coexisteraient — précisément ce
    que l'arbitrage interdit.
    """
    sid, se_id, _sets = _monter(client)

    body = client.get(f"/sessions/{sid}?active={se_id}&rest=1").text
    assert "data-rest-remaining" not in body, (
        "un paramètre d'URL a fabriqué un repos qu'aucun fait ne soutient"
    )


def test_N_une_url_sans_parametre_ne_supprime_aucun_repos(client):
    """`N` — le versant symétrique, et le plus facile à oublier.

    Il ne suffit pas que `?rest=1` n'invente rien : une URL SANS paramètre
    ne doit pas davantage étouffer un repos que les faits affirment. C'est
    l'ancien mécanisme du saut — « recharger sans le paramètre » — et il
    doit être mort lui aussi, sinon le saut resterait une propriété de
    l'URL au lieu d'être une décision enregistrée.
    """
    from app.database import SessionLocal

    sid, se_id, sets = _monter(client)
    with SessionLocal() as db:
        _faire(db, sets[0], il_y_a=10)

    nu = client.get(f"/sessions/{sid}?active={se_id}").text
    assert "data-rest-remaining" in nu, (
        "une URL sans `rest=1` a supprimé un repos que les faits affirment"
    )


def test_le_parametre_rest_n_est_plus_lu_nulle_part():
    """L'extinction, vérifiée sur le CODE et non sur un comportement.

    Une lecture résiduelle pourrait dormir dans une branche qu'aucune
    garde n'emprunte. On lit donc le routeur, commentaires retirés — il
    EXPLIQUE longuement le paramètre qu'il a cessé de lire, et confondre
    les deux est l'erreur que ce dépôt a déjà commise.
    """
    import pathlib

    src = (pathlib.Path(__file__).resolve().parent.parent
           / "app/routers/sessions.py").read_text(encoding="utf-8")
    code = "\n".join(
        ligne for ligne in src.splitlines()
        if not ligne.lstrip().startswith("#")
    )
    code = re.sub(r'"""».*?"""', "", code, flags=re.DOTALL)
    code = re.sub(r'(?s)""".*?"""', "", code)

    assert 'query_params.get("rest")' not in code, (
        "le paramètre `rest` est encore lu par le routeur"
    )
    assert "rest_signal" not in code, "`rest_signal` survit dans le code"
    assert "rest=1" not in code, "`rest=1` est encore émis quelque part"
