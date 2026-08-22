"""Résolution zone d'un exercice, **avec sa provenance** (`MUSCLE_MAPPING_TRUTH_01`).

POURQUOI CE MODULE EXISTE
--------------------------
`classify_exercise` rend une zone, ou la chaîne ``"unknown"``. Un consommateur
analytique ne peut pas distinguer « cet exercice est vraiment non attribuable »
de « le matcher a répondu par défaut » — et c'est exactement la distinction
dont dépend la vérité de l'instrument anatomique.

Ce résolveur rend donc **la zone ET sa source**. Rien d'autre : il ne décide de
rien, ne compte rien, n'agrège rien.

**RÉSERVÉ À L'ANALYTIQUE ANATOMIQUE.** `recommendation` et `substitution` sont
gelés et consomment `classify_exercise(name)` ; changer l'autorité sous eux
modifierait des décisions d'entraînement. Une garde interdit qu'ils importent
ce module.

CE QUE L'AUDIT A MESURÉ, ET CE QU'IL NE PROUVE PAS
---------------------------------------------------
Sur les **68 exercices actifs du catalogue** : 68 mappés en base, 68 reconnus
par le matcher hérité, **zéro conflit**. Les deux autorités s'accordent.

Cela ne prouve **rien** pour les substitutions en texte libre ni pour les
exercices futurs. La base est donc l'**autorité cible**, et la bascule globale
des consommateurs reste **différée** : ce module expose la provenance pour
qu'un appelant puisse la traiter, il ne bascule personne.

⚠ LA CLÉ DE RECHERCHE EST UN NOM, ET C'EST TRANSITOIRE
--------------------------------------------------------
Le vocabulaire du dépôt est trompeur :

    TemplateExercise.code                   E1 … E8  → une POSITION
    SessionExercise.exercise_code_snapshot  E1 … E8  → une POSITION
    ExerciseMuscleMapping.exercise_code     « Chest Press machine » → un NOM

Passer `exercise_code_snapshot` à la recherche en base ne matcherait **jamais**.
Le nom canonique sert donc de clé **de transition**, et **n'est pas déclaré
identité finale** : voir la tranche `EXERCISE_IDENTITY_NORMALIZATION`.
"""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.services.muscle_mapping import ZONE_LABELS, classify_exercise

#: Le mapping vient de la table `ExerciseMuscleMapping` — autorité cible.
SOURCE_DB = "DB_EXACT"
#: Le mapping vient du matcher par sous-chaînes — repli de migration.
SOURCE_LEGACY = "LEGACY_FALLBACK"
#: Aucune autorité ne reconnaît cet exercice. **Ce n'est pas zéro.**
SOURCE_UNMAPPED = "UNMAPPED"


@dataclass(frozen=True)
class ZoneResolution:
    """Une zone, et d'où elle vient. `zone is None` ⟺ `source is UNMAPPED`."""

    zone: str | None
    source: str

    @property
    def mapped(self) -> bool:
        return self.zone is not None


def resolve_zone(db: Session, name: str) -> ZoneResolution:
    """Zone primaire d'un exercice, avec sa provenance.

    La base est interrogée **en premier** — elle est l'autorité cible. Le
    matcher hérité ne sert que de repli, et le dire dans la valeur de retour
    est ce qui permettra un jour de mesurer combien de résolutions en
    dépendent encore.
    """
    clean = (name or "").strip()
    if not clean:
        return ZoneResolution(None, SOURCE_UNMAPPED)

    # ⚠ Le nom passe en `exercise_code` parce que c'est ce que la colonne
    # contient réellement. Le paramètre est mal nommé, pas mal utilisé.
    primary, _ = classify_exercise(clean, exercise_code=clean, db=db)
    if primary in ZONE_LABELS:
        from app.models.exercise_muscle_mapping import ExerciseMuscleMapping

        hit = (
            db.query(ExerciseMuscleMapping)
            .filter(
                ExerciseMuscleMapping.exercise_code == clean,
                ExerciseMuscleMapping.is_active.is_(True),
            )
            .first()
        )
        return ZoneResolution(primary, SOURCE_DB if hit else SOURCE_LEGACY)

    return ZoneResolution(None, SOURCE_UNMAPPED)


__all__ = [
    "SOURCE_DB",
    "SOURCE_LEGACY",
    "SOURCE_UNMAPPED",
    "ZoneResolution",
    "resolve_zone",
]
