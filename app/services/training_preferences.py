"""Contrat des préférences d'entraînement déclarées (Sb_TRAINING_PREFERENCES_01).

**Frontière canonique unique.** Tout accès aux préférences passe par
`get_training_preferences` / `save_training_preferences`. Les futurs
consommateurs — `WeeklyVolumeBudget`, `WeeklyPlanner` — lisent ce service et non
la table : disperser les requêtes de préférence dans les consommateurs
disperserait aussi la validation, et c'est la validation qui porte le contrat.

**Ce que ce module garantit :**

1. **Aucun défaut caché.** Une préférence non déclarée reste `None` de bout en
   bout. Rien ici ne convertit une absence en fait — pas de `sessions_per_week
   = 3`, pas de « tout le matériel », pas de priorité implicite. Un test balaie
   le module et échoue sur toute réapparition de ce motif.
2. **`NULL` ≠ `[]`.** Une liste absente et une liste explicitement vide sont
   deux déclarations différentes et le restent jusqu'au stockage.
3. **Vocabulaires fermés.** Une valeur hors vocabulaire lève ; elle n'est jamais
   silencieusement ignorée. Une valeur historique illisible **remonte** au lieu
   d'être remplacée par une valeur fabriquée.
4. **Rien n'est inféré.** Ni de l'historique de séances, ni de la morphologie,
   ni de la readiness. Ce sont des faits **déclarés**.

**Vocabulaire des priorités — décision opérateur de cette tranche.**
`morphology_profile.FOCUS_CANDIDATE_VOCAB` a été audité puis **écarté**, sur
preuve : son propre commentaire le définit comme « candidats d'orientation
admis (**jamais une priorité appliquée** — build suivant) », ses 4 jetons
(`upper_chest`, `lateral_delts`, `rear_delts_upper_back`, `calves`) ne sont
**pas** des codes `BodyZone`, et ils ne permettent pas de déclarer quadriceps,
biceps ou dos. Le vocabulaire retenu est celui des **axes radar**
(`muscle_mapping.RADAR_AXIS_ORDER`) : déjà canonique, déjà libellé en français,
déjà l'axe de lecture du profil, et projetable vers les zones par
`radar_axis_for_zone` — la projection canonique de P0.1 — donc consommable par
un futur budget de volume **sans nouvelle table de correspondance**.

Conséquence assumée : `core` n'appartient à aucun axe radar et ne peut donc pas
être priorisé. C'est la même limite que le roll-up macro de P0.4, pas une
nouvelle.

**Priorité déclarée ≠ candidat morphologique.** Les deux sources restent
distinctes et distinguables : rien ici ne lit la morphologie, et un test le
vérifie. Un futur consommateur pourra lire les deux, en sachant laquelle
l'utilisateur a énoncée.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.training_preferences import TrainingPreferences
from app.services.muscle_mapping import RADAR_AXES, RADAR_AXIS_ORDER

PREFERENCES_CONTRACT_VERSION = 1

# ---------------------------------------------------------------------------
# Vocabulaires fermés
# ---------------------------------------------------------------------------

#: Bornes structurelles de la cadence. **Ce ne sont pas des jugements** : 7
#: n'est pas « mieux » que 1, et 3 n'est pas un optimum. La borne haute existe
#: parce qu'une semaine compte sept jours, pas parce qu'au-delà ce serait
#: déconseillé.
SESSIONS_PER_WEEK_MIN = 1
SESSIONS_PER_WEEK_MAX = 7

#: Vocabulaire des priorités : les axes radar canoniques, dans l'ordre
#: d'affichage du profil. Aucun jeton nouveau n'est inventé.
FOCUS_PRIORITY_VOCAB: tuple[str, ...] = tuple(RADAR_AXIS_ORDER)

#: Familles d'équipement du référentiel (`data/exercise_properties.json` et
#: `data/exercise_knowledge_base.json`, identiques). Déclarées **en dur** et non
#: dérivées à l'exécution : ce vocabulaire est **persisté**, donc il doit être
#: stable même si la donnée bouge. Un test le compare au référentiel et échoue
#: sur toute divergence — l'alignement est prouvé, pas supposé, et une dérive
#: devient un échec bruyant au lieu d'invalider silencieusement des valeurs déjà
#: stockées.
EQUIPMENT_FAMILY_VOCAB: tuple[str, ...] = (
    "barbell",
    "bodyweight",
    "cable",
    "dumbbell",
    "machine",
    "smith",
)

#: Libellés de présentation. Aucun libellé français n'existait pour ces familles
#: dans le dépôt ; les codes machine restent la seule vérité, ceci n'est qu'une
#: couche d'affichage.
EQUIPMENT_FAMILY_LABELS: dict[str, str] = {
    "barbell": "Barre libre",
    "bodyweight": "Poids du corps",
    "cable": "Poulie",
    "dumbbell": "Haltères",
    "machine": "Machine guidée",
    "smith": "Smith machine",
}


def focus_priority_label(axis_key: str) -> str:
    """Libellé d'un axe — repris du vocabulaire canonique, jamais réécrit."""
    axis = RADAR_AXES.get(axis_key)
    return axis["label"] if axis else axis_key


def equipment_family_label(family: str) -> str:
    return EQUIPMENT_FAMILY_LABELS.get(family, family)


# ---------------------------------------------------------------------------
# Objet de domaine
# ---------------------------------------------------------------------------


class PreferenceValidationError(ValueError):
    """Valeur refusée — jamais corrigée en silence."""


@dataclass(frozen=True)
class TrainingPreferencesData:
    """Préférences déclarées, en mémoire. `None` = non déclaré, partout.

    Immuable : une préférence lue ne peut pas être modifiée par inadvertance
    par un consommateur, ce qui compte d'autant plus que plusieurs services
    liront le même objet.
    """

    sessions_per_week: int | None = None
    focus_priorities: tuple[str, ...] | None = None
    available_equipment: tuple[str, ...] | None = None

    @property
    def is_empty(self) -> bool:
        """Aucune des trois dimensions n'a été déclarée."""
        return (
            self.sessions_per_week is None
            and self.focus_priorities is None
            and self.available_equipment is None
        )


#: Ce que reçoit un utilisateur sans ligne : trois `None`, pas des valeurs par
#: défaut. Nommé pour qu'aucun appelant n'ait à fabriquer l'équivalent.
UNDECLARED = TrainingPreferencesData()


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_sessions_per_week(value: Any) -> int | None:
    """1–7, ou `None`. Un booléen est refusé — `True` n'est pas « 1 séance »."""
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise PreferenceValidationError(
            f"sessions_per_week doit être un entier ou None, reçu {value!r}"
        )
    if not SESSIONS_PER_WEEK_MIN <= value <= SESSIONS_PER_WEEK_MAX:
        raise PreferenceValidationError(
            f"sessions_per_week hors bornes {SESSIONS_PER_WEEK_MIN}–"
            f"{SESSIONS_PER_WEEK_MAX} : {value!r}"
        )
    return value


def validate_focus_priorities(value: Any) -> tuple[str, ...] | None:
    """Liste **ordonnée**, sans doublon, entièrement dans le vocabulaire.

    Un doublon est une **erreur** et non une déduplication silencieuse : dans
    une liste ordonnée il est ambigu (quel rang garder ?), et deviner
    trahirait l'intention déclarée. L'ordre est préservé tel quel.
    """
    if value is None:
        return None
    items = _as_string_list(value, "focus_priorities")
    seen: set[str] = set()
    for item in items:
        if item not in FOCUS_PRIORITY_VOCAB:
            raise PreferenceValidationError(
                f"priorité inconnue {item!r} — vocabulaire fermé : "
                f"{list(FOCUS_PRIORITY_VOCAB)}"
            )
        if item in seen:
            raise PreferenceValidationError(
                f"priorité en double {item!r} — l'ordre serait ambigu"
            )
        seen.add(item)
    return tuple(items)


def validate_available_equipment(value: Any) -> tuple[str, ...] | None:
    """Ensemble de familles. Sémantique d'ensemble, donc ordre canonique.

    Contrairement aux priorités, l'ordre ne porte **aucun** sens ici : deux
    déclarations des mêmes familles sont la même déclaration. Les doublons sont
    donc normalisés — pas ambigus — et la sortie suit l'ordre du vocabulaire
    pour que la comparaison et le stockage soient déterministes.
    """
    if value is None:
        return None
    items = _as_string_list(value, "available_equipment")
    unknown = [item for item in items if item not in EQUIPMENT_FAMILY_VOCAB]
    if unknown:
        raise PreferenceValidationError(
            f"famille d'équipement inconnue {unknown!r} — vocabulaire fermé : "
            f"{list(EQUIPMENT_FAMILY_VOCAB)}"
        )
    present = set(items)
    return tuple(f for f in EQUIPMENT_FAMILY_VOCAB if f in present)


def _as_string_list(value: Any, field: str) -> list[str]:
    if isinstance(value, str) or not isinstance(value, (list, tuple)):
        raise PreferenceValidationError(
            f"{field} doit être une liste ou None, reçu {type(value).__name__}"
        )
    for item in value:
        if not isinstance(item, str):
            raise PreferenceValidationError(
                f"{field} n'accepte que des chaînes, reçu {item!r}"
            )
    return list(value)


# ---------------------------------------------------------------------------
# Sérialisation
# ---------------------------------------------------------------------------


def _dump(value: tuple[str, ...] | None) -> str | None:
    """`None` reste `None` — il ne devient jamais `"[]"`."""
    if value is None:
        return None
    return json.dumps(list(value))


def _load(raw: str | None, field: str) -> tuple[str, ...] | None:
    """JSON → tuple. Une valeur illisible **remonte**, elle n'est pas remplacée.

    Fabriquer une liste vide sur du JSON corrompu convertirait une donnée
    perdue en déclaration explicite « aucune priorité » — une affirmation que
    l'utilisateur n'a jamais faite.
    """
    if raw is None:
        return None
    try:
        parsed = json.loads(raw)
    except (TypeError, ValueError) as exc:
        raise PreferenceValidationError(
            f"{field} illisible en base : {raw!r}"
        ) from exc
    if not isinstance(parsed, list):
        raise PreferenceValidationError(
            f"{field} attendu comme liste en base, reçu {type(parsed).__name__}"
        )
    return tuple(parsed)


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


def get_training_preferences(db: Session, user_id: int) -> TrainingPreferencesData:
    """Les préférences déclarées d'**un** utilisateur. Lecture seule.

    Aucune ligne ⇒ `UNDECLARED` : trois `None`, jamais des valeurs par défaut.
    La portée propriétaire est imposée par le filtre `user_id` — ce service ne
    lit jamais une autre ligne que celle demandée.
    """
    row = db.execute(
        select(TrainingPreferences).where(TrainingPreferences.user_id == user_id)
    ).scalar_one_or_none()
    if row is None:
        return UNDECLARED
    return TrainingPreferencesData(
        sessions_per_week=row.sessions_per_week,
        focus_priorities=_load(row.focus_priorities, "focus_priorities"),
        available_equipment=_load(row.available_equipment, "available_equipment"),
    )


def save_training_preferences(
    db: Session,
    user_id: int,
    *,
    sessions_per_week: Any = None,
    focus_priorities: Any = None,
    available_equipment: Any = None,
) -> TrainingPreferencesData:
    """Crée ou met à jour **la** ligne de cet utilisateur. Atomique.

    **Valider d'abord, persister ensuite** : les trois champs sont validés avant
    toute écriture, donc une valeur refusée ne laisse jamais la ligne à moitié
    mise à jour.

    L'appel remplace l'état déclaré dans son ensemble : passer `None` pour un
    champ signifie « non déclaré », pas « inchangé ». Un remplacement complet
    est le seul moyen pour l'utilisateur de **retirer** une déclaration, et un
    formulaire soumet de toute façon l'état entier.
    """
    validated_sessions = validate_sessions_per_week(sessions_per_week)
    validated_focus = validate_focus_priorities(focus_priorities)
    validated_equipment = validate_available_equipment(available_equipment)

    row = db.execute(
        select(TrainingPreferences).where(TrainingPreferences.user_id == user_id)
    ).scalar_one_or_none()

    if row is None:
        row = TrainingPreferences(user_id=user_id)
        db.add(row)

    row.sessions_per_week = validated_sessions
    row.focus_priorities = _dump(validated_focus)
    row.available_equipment = _dump(validated_equipment)
    row.updated_at = datetime.now(UTC)
    db.commit()

    return TrainingPreferencesData(
        sessions_per_week=validated_sessions,
        focus_priorities=validated_focus,
        available_equipment=validated_equipment,
    )


__all__ = [
    "EQUIPMENT_FAMILY_LABELS",
    "EQUIPMENT_FAMILY_VOCAB",
    "FOCUS_PRIORITY_VOCAB",
    "PREFERENCES_CONTRACT_VERSION",
    "PreferenceValidationError",
    "SESSIONS_PER_WEEK_MAX",
    "SESSIONS_PER_WEEK_MIN",
    "TrainingPreferencesData",
    "UNDECLARED",
    "equipment_family_label",
    "focus_priority_label",
    "get_training_preferences",
    "save_training_preferences",
    "validate_available_equipment",
    "validate_focus_priorities",
    "validate_sessions_per_week",
]
