"""Intelligent session launcher.

Exposes a small branch tree that maps (type, variant) pairs to
ordered lists of template slugs. The service resolves these
branches against the actual catalog in the database, so variants
whose templates don't yet exist are automatically filtered out.
This keeps the launcher page honest as the catalog evolves.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.catalog import TemplateExercise, WorkoutTemplate


BRANCH_TREE: dict[str, dict[str, dict]] = {
    "standard": {
        "upper-push": {
            "label": "Haut / Push (pecs, épaules, triceps)",
            "slugs": ["push-a", "push-b"],
        },
        "upper-pull": {
            "label": "Haut / Pull (dos, biceps)",
            "slugs": ["pull-a", "pull-b"],
        },
        "lower-quads": {
            "label": "Bas / Quads dominant",
            "slugs": ["legs-a"],
        },
        "lower-post": {
            "label": "Bas / Postérieur dominant",
            "slugs": ["legs-b"],
        },
        "catch-shoulders": {
            "label": "Rattrapage épaules",
            "slugs": ["catch-up-shoulders"],
        },
        "catch-arms": {
            "label": "Rattrapage bras",
            "slugs": ["catch-up-arms"],
        },
        "catch-back": {
            "label": "Rattrapage dos largeur",
            "slugs": ["catch-up-back-width"],
        },
    },
    "short": {
        "upper": {"label": "Full upper court", "slugs": ["short-upper"]},
        "full-lower": {"label": "Full lower court", "slugs": ["short-lower"]},
        "full-body": {"label": "Full body court", "slugs": ["short-full-body"]},
        "spec": {
            "label": "Spécialisation courte",
            "slugs": [
                "catch-up-shoulders",
                "catch-up-arms",
                "catch-up-back-width",
            ],
        },
    },
    "cardio": {
        "_direct": {
            "label": "Cardio",
            "slugs": ["liss-only", "liss-abs"],
        },
    },
}


TYPE_LABELS: dict[str, str] = {
    "standard": "Séance standard",
    "short": "Séance courte",
    "cardio": "Cardio",
}


def _existing_slugs(db: Session) -> set[str]:
    """Return the set of template slugs currently present in the DB."""
    rows = db.execute(select(WorkoutTemplate.slug)).all()
    return {r[0] for r in rows}


def resolve_branch(
    db: Session, type_: str, variant: str | None
) -> list[WorkoutTemplate]:
    """Return the ordered list of WorkoutTemplate objects for a
    (type, variant) pair, filtered to slugs that actually exist.

    If `variant` is None and the type has a "_direct" branch, that
    branch is used. If the type or variant is unknown, returns an
    empty list.
    """
    type_branches = BRANCH_TREE.get(type_)
    if type_branches is None:
        return []

    if variant is None:
        if "_direct" in type_branches:
            branch = type_branches["_direct"]
        else:
            return []
    else:
        branch = type_branches.get(variant)
        if branch is None:
            return []

    existing = _existing_slugs(db)
    ordered_slugs = [s for s in branch["slugs"] if s in existing]
    if not ordered_slugs:
        return []

    stmt = (
        select(WorkoutTemplate)
        .where(WorkoutTemplate.slug.in_(ordered_slugs))
        .options(
            selectinload(WorkoutTemplate.exercises).selectinload(
                TemplateExercise.rep_targets
            )
        )
    )
    by_slug = {t.slug: t for t in db.execute(stmt).scalars().all()}
    # Preserve BRANCH_TREE order, not DB order.
    return [by_slug[s] for s in ordered_slugs if s in by_slug]


def get_available_variants(db: Session, type_: str) -> list[dict]:
    """Return [{"key", "label"}, ...] for variants under `type_`
    that have at least one existing template. Skips "_direct"."""
    type_branches = BRANCH_TREE.get(type_)
    if type_branches is None:
        return []
    existing = _existing_slugs(db)
    out: list[dict] = []
    for key, branch in type_branches.items():
        if key == "_direct":
            continue
        if any(s in existing for s in branch["slugs"]):
            out.append({"key": key, "label": branch["label"]})
    return out


def get_available_types(db: Session) -> list[dict]:
    """Return [{"key", "label"}, ...] for types that resolve to at
    least one branch with existing templates."""
    existing = _existing_slugs(db)
    out: list[dict] = []
    for type_key, branches in BRANCH_TREE.items():
        has_content = any(
            any(s in existing for s in branch["slugs"])
            for branch in branches.values()
        )
        if has_content:
            out.append(
                {"key": type_key, "label": TYPE_LABELS.get(type_key, type_key)}
            )
    return out
