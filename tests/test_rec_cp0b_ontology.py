"""`REC-CP0b` — une seule ontologie, et l'ignorance cesse de se lire « frais ».

CE QUE CES GARDES FERMENT
--------------------------
Le moteur de recommandation était coupé en deux, à l'intérieur de la même
fonction :

  · ses signaux de tonnage passaient par `resolve_exercise_zones` — corrections
    relues, puis base, puis sous-chaîne ;
  · ses zones de gabarit, sa carte du dernier travail et sa disponibilité
    passaient par `classify_exercise(name)`, **sous-chaîne pure**.

Trois exercices du catalogue divergent de façon prouvée entre les deux.
`Calf press leg press` comptait en `calves` pour la mesure de l'exposition et
en `quads` pour la recommandation : le produit mesurait l'entraînement avec une
ontologie et décidait la séance suivante avec une autre.

ET LE SECOND DÉFAUT EST PIRE, PARCE QU'IL ÉPINGLE
--------------------------------------------------
Une zone sans trace recevait `availability = 1.0` — fraîcheur maximale — que la
zone n'ait jamais été travaillée **ou** qu'elle l'ait été par un exercice que le
moteur n'a pas su classer. `WEIGHT_AVAILABILITY = 35` en fait la plus grosse
composante du score : un gabarit dont les zones échouent au classement marquait
donc le maximum à **chaque** décision.

Ce n'est pas une imprécision. C'est un mécanisme d'épinglage, et la
substitution en texte libre en est la source vivante — `sessions.py` accepte un
nom arbitraire que le matcher ignore.

MÉTHODE. Chaque garde structurante est vérifiée en **plantant son défaut**.
"""
from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta

from app.services.recommendation import (
    AVAILABILITY_INCONNUE,
    _compute_signals,
    reset_template_zones_cache,
)
from tests.helpers import get_test_user_id

T0 = datetime(2026, 6, 15, 18, 0, tzinfo=UTC)

#: Les trois exercices dont les deux ontologies divergeaient, avec la zone que
#: le contrat formel (corrections relues) leur attribue. Mesuré par
#: `build_parity_report` le 2026-09-23 : ce sont EXACTEMENT les trois
#: `intentional_divergences` du catalogue, ni plus ni moins.
DIVERGENCES_CONNUES = {
    "Calf press leg press": "calves",
    "Rear delt fly machine (pec deck inversé)": "delt_post",
    "Relevé de jambes suspendu": "core",
}


def _signaux(quand):
    from app.database import SessionLocal

    reset_template_zones_cache()
    with SessionLocal() as db:
        return _compute_signals(db, get_test_user_id(), quand)


# ═══════════ 1. UNE SEULE AUTORITÉ ═══════════


def test_le_moteur_n_appelle_plus_le_classifieur_par_sous_chaine():
    """Le moteur consomme le contrat formel, plus le matcher nu.

    On lit le code exécutable, commentaires et docstrings retirés : la prose de
    ce fichier et celle du moteur EXPLIQUENT le défaut, et une garde qui lit la
    prose accuse le texte qui documente la correction. Défaut déjà commis
    plusieurs fois sur ce dépôt.
    """
    import pathlib

    src = (
        pathlib.Path(__file__).resolve().parent.parent
        / "app/services/recommendation.py"
    ).read_text(encoding="utf-8")
    code = re.sub(r'"""[\s\S]*?"""', " ", src)
    code = "\n".join(ligne.split("#", 1)[0] for ligne in code.splitlines())

    assert "classify_exercise" not in code, (
        "le moteur rappelle le classifieur par sous-chaîne — la seconde "
        "ontologie est revenue"
    )
    assert "resolve_exercise_zones" in code, (
        "le moteur n'appelle plus le contrat formel"
    )


def test_les_deux_autorites_ne_divergent_pas(client):
    """⚠ CETTE GARDE TRANSFORME UNE MESURE DATÉE EN INVARIANT.

    Le moteur résout ses zones **sans base** (`db=None`), parce que son cache
    est indexé par tuple de noms et qu'une `Session` n'y a pas sa place.

    Ce choix n'est légitime que si les deux chemins rendent la même chose.
    Mesuré le 2026-09-23 sur les 102 exercices du catalogue : **0 divergent**.
    Mais c'est un fait daté, pas une propriété — l'audit précédent affirmait
    « 68 mappés, zéro conflit » et était devenu faux sans que personne le voie.

    On le vérifie donc à chaque exécution, sur le catalogue réel.
    """
    from app.database import SessionLocal
    from app.models.exercise import Exercise
    from app.services.body_zone_source import resolve_exercise_zones

    with SessionLocal() as db:
        noms = [e.name for e in db.query(Exercise).all()]
        assert noms, "catalogue vide — la garde ne mesure rien"

        divergents = []
        for nom in noms:
            avec = resolve_exercise_zones(db, nom)
            sans = resolve_exercise_zones(None, nom)
            if (avec.primary, tuple(avec.secondary)) != (
                sans.primary, tuple(sans.secondary)
            ):
                divergents.append((nom, avec.primary, sans.primary))

    assert not divergents, (
        "le chemin SANS base diverge du chemin AVEC base — le moteur ne peut "
        f"plus se passer de la base : {divergents[:5]}"
    )


def test_les_trois_divergences_connues_rendent_la_zone_du_contrat():
    """Le cas concret, nommé, plutôt qu'une propriété abstraite.

    `Calf press leg press` comptait en `quads` pour la recommandation parce que
    le motif « leg press » précède « calves » dans la liste ordonnée du matcher.
    Une garde qui ne vérifierait que « une seule autorité » passerait si les
    deux chemins devenaient également faux.
    """
    from app.services.body_zone_source import resolve_exercise_zones

    for nom, attendue in DIVERGENCES_CONNUES.items():
        resolu = resolve_exercise_zones(None, nom)
        assert resolu.primary == attendue, (
            f"« {nom} » rend « {resolu.primary} » au lieu de « {attendue} » — "
            "le moteur est retombé sur la sous-chaîne"
        )


# ═══════════ 2. `UNKNOWN_DOES_NOT_MEAN_AVAILABLE` ═══════════


def test_une_zone_jamais_vue_reste_fraiche_quand_tout_a_ete_lu(client):
    """LE PENDANT, ET IL COMPTE AUTANT.

    Sans lui, on pourrait « corriger » le défaut en déclarant tout inconnu, et
    la garde suivante passerait. Quand la fenêtre est **entièrement** lisible,
    « jamais travaillée » est une vraie mesure et la zone est vraiment fraîche.
    """
    from tests.test_recommendation_service import _mk_session

    _mk_session(template_slug="push-a", started_at=T0 - timedelta(days=3))

    s = _signaux(T0)
    assert s.observation_partielle is False, (
        "aucun exercice n'était illisible — l'observation n'est pas partielle"
    )
    # `quads` n'est pas travaillée par push-a : jamais vue, et on a tout lu.
    assert s.availability_by_zone["quads"] == 1.0


def test_un_exercice_illisible_interdit_de_declarer_une_zone_fraiche(client):
    """⚠ LE DÉFAUT D'ÉPINGLAGE QUE CETTE TRANCHE FERME.

    Une substitution en texte libre que le matcher ignore rendait la séance
    invisible pour la carte du dernier travail. Toutes les zones non vues
    passaient alors à `availability = 1.0`, la valeur la plus recommandable,
    sur la composante la plus lourde du score (35 points).

    Le moteur connaissait pourtant déjà la bonne réponse : `_score_template`
    écrit `availability = 0.5  # inconnu → neutre` pour un gabarit sans zones.
    La décision existait, le moyen de l'appliquer des deux côtés n'existait pas.
    """
    from app.database import SessionLocal
    from app.models.session import SessionExercise
    from tests.test_recommendation_service import _mk_session

    sid = _mk_session(template_slug="push-a", started_at=T0 - timedelta(days=3))

    # Une substitution que le matcher ne peut pas classer.
    with SessionLocal() as db:
        se = (
            db.query(SessionExercise)
            .filter(SessionExercise.session_id == sid)
            .first()
        )
        se.substituted_name = "Zorglub press oblique 47°"
        db.commit()

    s = _signaux(T0)

    assert s.observation_partielle is True, (
        "un exercice illisible n'a pas été retenu comme tel — l'ignorance a "
        "été effacée au lieu d'être déclarée"
    )
    jamais_vues = [
        z for z, h in s.hours_since_last_by_zone.items() if h >= 24 * 365
    ]
    assert jamais_vues, "prémisse : au moins une zone sans trace"
    for zone in jamais_vues:
        assert s.availability_by_zone[zone] == AVAILABILITY_INCONNUE, (
            f"« {zone} » est déclarée fraîche à "
            f"{s.availability_by_zone[zone]} alors qu'un exercice de la "
            "fenêtre n'a pas pu être lu — l'ignorance est rendue comme une "
            "mesure"
        )


def test_l_inconnu_est_neutre_pas_penalisant():
    """Ne pas savoir n'est pas une raison d'écarter une zone.

    La valeur est celle que le moteur emploie déjà pour l'inconnu, pas une
    valeur inventée pour l'occasion — et elle est strictement entre les deux
    extrêmes, donc ni fraîche ni fatiguée.
    """
    assert AVAILABILITY_INCONNUE == 0.5
    assert 0.0 < AVAILABILITY_INCONNUE < 1.0
