"""`REC-CP0a` — `HISTORY_IS_CAUSAL` : une décision ne lit que son passé.

CE QUE CETTE GARDE TIENT, ET POURQUOI ELLE N'EXISTAIT PAS
----------------------------------------------------------
`recommend_next_session(db, user_id, now=…)` accepte un horodatage de décision,
et `scripts/reco_calibration_report.py` s'en sert pour **rejouer** le moteur à
des dates passées afin d'estimer la phrase qui avait été servie.

Audit du 2026-09-23 : **aucune** des douze requêtes du chemin ne portait de
borne supérieure sur `started_at`. Une décision évaluée au 1er mars lisait donc
les séances du 15 mars. Les chiffres de calibration produits jusqu'ici décrivent
un moteur qui lisait le futur — ils ne sont pas une base de comparaison.

Le défaut était **invisible** pour deux raisons, et les deux comptent :

  · `max(0, (now - started).days)` écrasait les deltas négatifs à zéro, si bien
    qu'une séance future se lisait « aujourd'hui » au lieu de se signaler ;
  · le court-circuit « séance ouverte » n'avait aucune borne **et** s'exécutait
    avant que `now` soit résolu : une séance ouverte aujourd'hui faisait rendre
    `None` à tous les horodatages rejoués, donc l'échantillon se vidait en
    silence plutôt que de rendre un résultat faux visible.

MÉTHODE. L'invariant est énoncé sans condition et vérifié par **différence** :
on calcule une recommandation à T0, on ajoute une séance à T1 > T0, on
recalcule à T0. Les deux doivent être identiques. C'est une propriété, pas un
échantillon : elle ne dépend d'aucun contenu particulier.
"""
from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta

from app.services.recommendation import (
    recommend_next_session,
    reset_template_zones_cache,
)
from tests.helpers import get_test_user_id

#: Horodatage de décision. Fixe, pour que la garde ne dépende pas du jour où
#: elle tourne — une garde dont le résultat bouge avec l'horloge n'en est pas
#: une.
T0 = datetime(2026, 6, 15, 18, 0, tzinfo=UTC)


def _mk(slug: str, quand: datetime, **kw):
    """Sème une séance terminée. Délègue au constructeur canonique du dépôt.

    On réutilise `_mk_session` plutôt que d'écrire un semeur : c'est lui qui
    connaît les instantanés de gabarit, les séries de travail complétées et la
    durée, et une seconde version dériverait.
    """
    from tests.test_recommendation_service import _mk_session

    return _mk_session(template_slug=slug, started_at=quand, **kw)


def _decision(quand: datetime):
    """La recommandation évaluée à `quand`, cache de zones réinitialisé."""
    from app.database import SessionLocal

    reset_template_zones_cache()
    with SessionLocal() as db:
        return recommend_next_session(db, get_test_user_id(), now=quand)


def _empreinte(reco) -> tuple:
    """Ce qui doit rester identique : le gagnant, son score, sa phrase, et
    l'ordre exact des alternatives.

    On ne compare pas l'objet entier : il porte des instances SQLAlchemy dont
    l'identité change d'une session à l'autre sans que la décision change.
    """
    if reco is None:
        return ("aucune",)
    return (
        reco["top"]["template"].slug,
        reco["top"]["score"],
        reco["top"]["phrase"],
        tuple(a["template"].slug for a in reco["alternatives"]),
    )


def _signaux(quand):
    """Ce que le moteur LIT à `quand` — c'est là que vit la causalité.

    ⚠ MA PREMIÈRE ÉCRITURE N'ASSERTAIT QUE SUR LA DÉCISION FINALE, ET ELLE NE
    MORDAIT PAS.

    Vérifiée par mutation : en retirant les six bornes, seules deux des six
    faisaient échouer la garde. Diagnostic — pas supposition — en instrumentant
    `_compute_signals` : les signaux, eux, changeaient énormément.

        days_since_last_strength    2 → -3
        availability_by_zone[pecs]  1.0 → 0.0
        hard_sets_by_zone_24h       {} → {pecs: 12, triceps: 4}
        last_strength_session_zones ['quads'] → ['pecs']

    …et le gagnant ne bougeait pas. **C'est une seconde information, et elle
    vaut d'être écrite** : le moteur est à ce point épinglé qu'un bouleversement
    complet de ses entrées ne déplace pas sa sortie. C'est la preuve directe du
    défaut P1 que `REC-CP1` doit quantifier.

    La causalité est donc assertée sur les ENTRÉES. Une garde qui n'observe que
    la sortie d'un moteur épinglé n'observe rien.
    """
    from app.database import SessionLocal
    from app.services.recommendation import _compute_signals

    reset_template_zones_cache()
    with SessionLocal() as db:
        s = _compute_signals(db, get_test_user_id(), quand)
    return {
        champ: getattr(s, champ)
        for champ in (
            "cold_start", "kinds_recent", "days_since_last_cardio",
            "days_since_last_strength", "soft_restart", "fatigue_score",
            "hard_sets_by_zone_recent", "hard_sets_by_zone_24h",
            "hard_sets_14d_by_zone", "median_hard_sets_14d",
            "last_strength_session_zones", "recent_strength_zones_by_session",
            "availability_by_zone", "hours_since_last_by_zone",
        )
    }


# ═════════════════ L'INVARIANT ═════════════════


def test_une_seance_posterieure_ne_change_pas_une_decision_passee(client):
    """⚠ `HISTORY_IS_CAUSAL` — L'INVARIANT CENTRAL DE `REC-CP0a`.

    Une décision évaluée à T0 ne peut lire que des faits existant à T0. On le
    vérifie par différence plutôt que par inspection : la même décision, avant
    et après l'ajout d'une séance postérieure, doit rendre exactement la même
    chose.

    Vérifiée par mutation : retirer n'importe laquelle des bornes
    `started_at < now` du chemin fait diverger les deux empreintes.
    """
    # Un passé réel, pour que la décision à T0 ait de quoi se fonder.
    _mk("push-a", T0 - timedelta(days=6))
    _mk("pull-a", T0 - timedelta(days=4))
    _mk("legs-a", T0 - timedelta(days=2))

    signaux_avant = _signaux(T0)
    decision_avant = _empreinte(_decision(T0))
    assert decision_avant != ("aucune",), (
        "prémisse : la décision à T0 doit exister, sinon la garde compare "
        "deux absences et passe à vide"
    )

    # Le futur, du point de vue de T0. Volontairement massif — même zone que
    # le passé récent, à 24 h de la décision : si une borne manque, tous les
    # signaux de fenêtre le voient.
    #
    # ⚠ LE RESSENTI EST DIFFÉRENT, ET C'EST NÉCESSAIRE. `_mk_session` pose
    # `good`/`high` par défaut ; avec un passé et un futur identiques sur cet
    # axe, `fatigue_score` vaut la même chose quelles que soient les trois
    # séances lues, et la borne de fatigue pouvait tomber sans que la garde
    # s'en aperçoive. Trouvé par mutation : 5 bornes sur 6 mordaient, la
    # sixième non. Le corpus doit produire l'état qu'il prétend observer.
    _mk("push-a", T0 + timedelta(days=1),
        global_state="fatigued", concentration="low")
    _mk("push-a", T0 + timedelta(days=3),
        global_state="fatigued", concentration="low")

    signaux_apres = _signaux(T0)

    # ── L'ASSERTION QUI PORTE : les ENTRÉES du moteur sont inchangées.
    divergents = {
        champ: (signaux_avant[champ], signaux_apres[champ])
        for champ in signaux_avant
        if signaux_avant[champ] != signaux_apres[champ]
    }
    assert not divergents, (
        "des séances POSTÉRIEURES à la décision ont changé ce que le moteur "
        "lit à T0 — il voit le futur.\n"
        + "\n".join(f"  {c}: {a}  →  {b}" for c, (a, b) in divergents.items())
    )

    # ── Et le pendant : la décision elle-même ne bouge pas non plus.
    assert _empreinte(_decision(T0)) == decision_avant


def test_une_seance_ouverte_posterieure_ne_fait_pas_taire_le_rejeu(client):
    """Le court-circuit « séance ouverte » est borné lui aussi.

    Il s'exécutait **avant** que `now` soit résolu et sans aucune borne : une
    séance ouverte aujourd'hui faisait rendre `None` à tous les horodatages
    passés. Le rejeu ne rendait pas une mauvaise réponse — il n'en rendait
    aucune, ce qui est plus difficile à remarquer.
    """
    _mk("push-a", T0 - timedelta(days=3))
    assert _decision(T0) is not None, "prémisse : la décision à T0 existe"

    # Une séance ouverte APRÈS T0.
    reponse = client.post(
        "/sessions", data={"template_slug": "pull-a"}, follow_redirects=False
    )
    sid = int(re.match(r"/sessions/(\d+)", reponse.headers["location"]).group(1))

    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    with SessionLocal() as db:
        ouverte = db.get(WorkoutSession, sid)
        ouverte.started_at = T0 + timedelta(days=2)
        db.commit()

    assert _decision(T0) is not None, (
        "une séance ouverte APRÈS la décision fait taire le rejeu à T0"
    )


def test_la_fatigue_est_celle_de_la_decision_pas_celle_d_aujourd_hui(client):
    """`compute_behavioral_state` lisait l'horloge murale, sans paramètre.

    C'était la fuite la plus silencieuse du chemin : `fatigue_score` porte le
    filtre `_passes_fatigue_filter` et trois branches de phrase, et il décrivait
    toujours aujourd'hui.

    On le prouve directement sur le service, pas à travers le moteur : c'est là
    que vit la propriété.
    """
    from app.database import SessionLocal
    from app.services.behavioral import compute_behavioral_state

    _mk("push-a", T0 - timedelta(days=2), global_state="good", concentration="high")

    with SessionLocal() as db:
        uid = get_test_user_id()
        avant = compute_behavioral_state(db, uid, now=T0).fatigue_score

    # Une séance éreintante, APRÈS la décision.
    _mk("legs-a", T0 + timedelta(days=1), global_state="fatigued", concentration="low")

    with SessionLocal() as db:
        apres = compute_behavioral_state(db, get_test_user_id(), now=T0).fatigue_score

    assert apres == avant, (
        f"la fatigue à T0 a changé parce qu'une séance postérieure a été "
        f"ajoutée : {avant} → {apres}"
    )


def test_le_delta_de_jours_ne_peut_plus_etre_ecrase_a_zero():
    """Le `max(0, …)` est retiré de la source, et cette garde le tient.

    Ce n'est pas du zèle : c'est précisément ce clamp qui a caché la fuite
    pendant toute la vie du moteur. Une séance du futur se lisait
    « aujourd'hui » au lieu de rendre un delta négatif visible.

    On lit la source plutôt que le comportement parce que le comportement est
    désormais *impossible* à produire — les requêtes sont bornées. Ce que la
    garde empêche, c'est qu'on remette le clamp « par prudence » et qu'on
    reperde le signal.
    """
    import pathlib

    src = (
        pathlib.Path(__file__).resolve().parent.parent
        / "app/services/recommendation.py"
    ).read_text(encoding="utf-8")
    code = re.sub(r'"""[\s\S]*?"""', " ", src)
    code = "\n".join(ligne.split("#", 1)[0] for ligne in code.splitlines())

    assert "max(0, (now - started).days)" not in code, (
        "le clamp qui masquait les séances futures est revenu"
    )


def test_le_demarrage_a_froid_respecte_les_seances_exclues(client):
    """`EXCLUDED_FROM_STATS_IS_RESPECTED` sur le compte de démarrage à froid.

    C'était la seule requête du moteur à ne pas filtrer `excluded_from_stats`.
    Un utilisateur dont les trois seules séances sont exclues des KPI sortait
    donc du démarrage à froid, alors que **tous** les autres signaux voyaient un
    historique vide — le moteur se croyait chevronné sur un compte vierge.
    """
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    ids = [
        _mk("push-a", T0 - timedelta(days=d)) for d in (9, 6, 3)
    ]
    with SessionLocal() as db:
        for sid in ids:
            db.get(WorkoutSession, sid).excluded_from_stats = True
        db.commit()

    reco = _decision(T0)
    assert reco is not None
    assert reco["context"]["cold_start"] is True, (
        "trois séances EXCLUES des KPI ont fait sortir le moteur du démarrage "
        "à froid — elles comptaient là où elles ne comptent nulle part ailleurs"
    )
