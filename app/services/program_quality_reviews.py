"""Quality review persistence (Sb_CUSTOM_PROGRAM_SCORING_03).

Écrit une trace FIGÉE de scoring dans `user_program_quality_reviews`, à
partir du moteur pur de `SCORING_01`. C'est la seule couche du lot scoring
qui touche la DB — le moteur et la couche feedback restent purs.

Frontières dures :
- **INSERT-ONLY** : une trace n'est jamais réécrite. L'immutabilité est
  gardée deux fois — par la contrainte UNIQUE `(user_program_id, version)`
  et par le listener applicatif `before_update` (`PERSISTENCE_05`). Ce
  service n'émet aucun UPDATE.
- **APPEL EXPLICITE UNIQUEMENT** : aucun branchement automatique dans
  `validate_draft` (Option B, arbitrage opérateur). Valider un brouillon
  reste un geste métier pur et idempotent ; y greffer une écriture DB
  créerait un effet de bord caché.
- **OWNER-SCOPED, sans fuite d'existence** : un programme inexistant et un
  programme d'autrui produisent la MÊME erreur (patron `user_program_drafts`).
- **Statuts scorables** : `draft` et `validated` (les ères d'édition).
  `archived` et `published` sont refusés — la trace d'une version publiée
  relève de l'ère publication, non ouverte.
- Le feedback de `SCORING_02` n'est **pas** persisté : fonction pure du
  résultat, reconstructible à tout moment.

Idempotence douce : re-scorer une version déjà tracée retourne la trace
existante (`created=False`) sans rien écrire — re-scorer est légitime,
pas fautif. Une nouvelle trace n'apparaît qu'avec une nouvelle version.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.user_program import (
    UserProgram,
    UserProgramExercise,
    UserProgramQualityReview,
    UserProgramSession,
)
from app.services.program_quality_engine import (
    ExerciseKnowledgeBase,
    ExerciseSlot,
    ProgramDefinition,
    SessionPlan,
    UserProfile,
    score_program,
)

_NOT_FOUND = "Programme introuvable"

# Ères d'édition : le scoring éclaire le brouillon (spec 03 §10).
SCORABLE_STATUSES = ("draft", "validated")


class QualityReviewError(Exception):
    """Erreur de domaine lisible pour la persistance des traces."""


@dataclass(frozen=True)
class StoredQualityReview:
    """Résultat de l'écriture — la trace, et si elle vient d'être créée."""

    review: UserProgramQualityReview
    created: bool


# ───────────────────── adaptateur ORM → payload pur ─────────────────────


def _working_sets(exercise: UserProgramExercise) -> int:
    """Séries de travail = plages de reps hors échauffement.

    On COMPTE les `rep_targets` non-warmup ; on ne parse JAMAIS la chaîne
    `set_scheme` (texte libre, non contractuel).
    """
    return sum(1 for rt in exercise.rep_targets if not rt.is_warmup)


def program_to_quality_definition(program: UserProgram) -> ProgramDefinition:
    """Projette l'arbre ORM en payload pur consommable par le moteur.

    Le moteur ne connaît ni Session ni ORM : cette fonction est le seul
    point de contact entre les deux mondes.
    """
    sessions = tuple(
        SessionPlan(
            name=session.name,
            position=session.position,
            kind=session.kind,
            exercises=tuple(
                ExerciseSlot(
                    exercise_name=exercise.exercise_name,
                    position=exercise.position,
                    working_sets=_working_sets(exercise),
                )
                for exercise in session.exercises
            ),
        )
        for session in program.sessions
    )
    return ProgramDefinition(title=program.title, sessions=sessions)


# ─────────────────────────── lecture owner-scoped ───────────────────────────


def _owned_program(db: Session, user_id: int, program_id: int) -> UserProgram:
    """Charge un programme possédé, arbre complet. Inexistant et non-possédé
    sont indistinguables (zéro fuite d'existence)."""
    program = db.execute(
        select(UserProgram)
        .where(UserProgram.user_id == user_id, UserProgram.id == program_id)
        .options(
            selectinload(UserProgram.sessions)
            .selectinload(UserProgramSession.exercises)
            .selectinload(UserProgramExercise.rep_targets)
        )
    ).scalar_one_or_none()
    if program is None:
        raise QualityReviewError(_NOT_FOUND)
    if program.archived_at is not None:
        raise QualityReviewError("Programme archivé — désarchiver d'abord")
    if program.status not in SCORABLE_STATUSES:
        raise QualityReviewError(
            "Une version publiée ne se re-score pas — sa trace appartient à "
            "la publication (fonctionnalité à venir)"
        )
    return program


def get_quality_review(
    db: Session, user_id: int, program_id: int, version: int
) -> UserProgramQualityReview | None:
    """Trace d'une version précise, owner-scopée. None si absente/non possédée."""
    return db.execute(
        select(UserProgramQualityReview)
        .join(UserProgram, UserProgram.id == UserProgramQualityReview.user_program_id)
        .where(
            UserProgram.user_id == user_id,
            UserProgramQualityReview.user_program_id == program_id,
            UserProgramQualityReview.version == version,
        )
    ).scalar_one_or_none()


# ─────────────────────────────── écriture ───────────────────────────────


def _dump(payload) -> str:
    """Sérialise un payload du moteur en JSON textuel stable."""
    return json.dumps(payload, ensure_ascii=False, default=lambda o: o.__dict__)


def compute_and_store_quality_review(
    db: Session,
    user_id: int,
    program_id: int,
    *,
    ekb: ExerciseKnowledgeBase | None = None,
    profile: UserProfile | None = None,
    computed_at: datetime | None = None,
) -> StoredQualityReview:
    """Score un programme possédé et écrit sa trace figée.

    INSERT-ONLY : si `(programme, version)` est déjà tracé, retourne la trace
    existante avec `created=False` — aucune écriture, aucun UPDATE.
    """
    program = _owned_program(db, user_id, program_id)
    version = program.current_version

    existing = get_quality_review(db, user_id, program_id, version)
    if existing is not None:
        # Idempotence douce : le passé n'est jamais recalculé ni réécrit.
        return StoredQualityReview(review=existing, created=False)

    definition = program_to_quality_definition(program)
    result = score_program(definition, ekb, profile)

    review = UserProgramQualityReview(
        user_program_id=program.id,
        version=version,
        grade=result.grade,
        global_score=result.global_score,
        subscores_json=_dump([s.__dict__ for s in result.subscores]),
        alerts_json=_dump(list(result.alerts)),
        suggestions_json=_dump(list(result.suggestions)),
        assumptions_json=_dump(list(result.assumptions)),
        missing_data_json=_dump(list(result.missing_data)),
        scoring_version=result.scoring_version,
        ekb_version=result.ekb_version,
        confidence=result.confidence,
        coverage_ratio=result.coverage_ratio,
        grade_cap_reason=result.grade_cap_reason,
        computed_at=computed_at or datetime.now(UTC),
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return StoredQualityReview(review=review, created=True)
