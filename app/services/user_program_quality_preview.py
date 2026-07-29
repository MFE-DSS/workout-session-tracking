"""Non-persisted draft quality preview (Sb_CUSTOM_PROGRAM_WIZARD_04).

Branche la qualité d'un brouillon custom DANS l'éditeur, sans jamais écrire
de trace. C'est le pendant LECTURE SEULE de `program_quality_reviews` :

    compute_and_store_quality_review  →  program_to_quality_definition
                                          → score_program → [INSERT]
    compute_quality_preview           →  program_to_quality_definition
                                          → score_program → build_program_quality_feedback

Ce module réutilise le MÊME adaptateur (`program_to_quality_definition`) et le
MÊME moteur (`score_program`) que le writer SCORING_03 — garantissant qu'une
preview et une future trace persistée de la même version **calculent à
l'identique**. La divergence serait un piège produit (une note en preview, une
autre en trace) : la réutilisation l'interdit par construction.

Frontières dures :
- **ZÉRO écriture** : aucune session DB, aucun `db.add`, aucun `db.commit`. Le
  programme est reçu déjà chargé (arbre eager) ; ce module ne requête rien.
- **NON bloquant, non normatif** : on assemble un affichage (chiffres bruts du
  moteur + langage produit de SCORING_02). Aucun état « non publiable ».
- **Pur vis-à-vis du scoring** : le seul contact avec l'ORM est l'adaptateur
  hérité, qui lit des attributs déjà chargés. Aucun LLM, déterministe.

Le writer `compute_and_store_quality_review` n'est **jamais** importé ici : une
preview n'écrit pas, point final.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.models.user_program import UserProgram
from app.services.program_quality_engine import (
    ExerciseKnowledgeBase,
    QualityReviewResult,
    UserProfile,
    score_program,
)
from app.services.program_quality_feedback import (
    ProgramQualityFeedback,
    build_program_quality_feedback,
)
from app.services.program_quality_reviews import program_to_quality_definition


@dataclass(frozen=True)
class QualityPreview:
    """Preview complète d'un brouillon — chiffres bruts + langage produit.

    Le template a besoin des deux mondes : `result` porte les nombres
    (`global_score`, `coverage_ratio`, `confidence`, `grade_cap_reason`) que la
    couche feedback ne ré-expose pas ; `feedback` porte le langage prêt à
    afficher (headline, items, notes, limitations, disclaimer).
    """

    result: QualityReviewResult
    feedback: ProgramQualityFeedback


def compute_quality_preview(
    program: UserProgram,
    *,
    ekb: ExerciseKnowledgeBase | None = None,
    profile: UserProfile | None = None,
) -> QualityPreview:
    """Score un brouillon possédé et renvoie sa preview — SANS rien écrire.

    Suppose l'arbre déjà chargé (via `get_draft`, eager). Réutilise l'adaptateur
    et le moteur du writer SCORING_03 pour garantir une note identique à une
    éventuelle trace persistée de la même version.
    """
    definition = program_to_quality_definition(program)
    result = score_program(definition, ekb, profile)
    feedback = build_program_quality_feedback(result)
    return QualityPreview(result=result, feedback=feedback)
