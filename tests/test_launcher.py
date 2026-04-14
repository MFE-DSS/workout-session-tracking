"""Unit tests for the launcher service (Sb_launcher_v1 Task 1)."""
from __future__ import annotations


def test_branch_tree_structure(client):
    from app.services.launcher import BRANCH_TREE

    assert "standard" in BRANCH_TREE
    assert "short" in BRANCH_TREE
    assert "cardio" in BRANCH_TREE


def test_resolve_branch_standard_upper_push(client):
    from app.database import SessionLocal
    from app.services.launcher import resolve_branch

    with SessionLocal() as db:
        result = resolve_branch(db, "standard", "upper-push")
    slugs = [t.slug for t in result]
    assert slugs == ["push-a", "push-b"]


def test_resolve_branch_cardio(client):
    from app.database import SessionLocal
    from app.services.launcher import resolve_branch

    with SessionLocal() as db:
        result = resolve_branch(db, "cardio", None)
    slugs = [t.slug for t in result]
    assert slugs == ["liss-abs"]


def test_resolve_branch_empty_for_unknown_variant(client):
    from app.database import SessionLocal
    from app.services.launcher import resolve_branch

    with SessionLocal() as db:
        result = resolve_branch(db, "standard", "does-not-exist")
    assert result == []


def test_get_available_variants_standard(client):
    from app.database import SessionLocal
    from app.services.launcher import get_available_variants

    with SessionLocal() as db:
        variants = get_available_variants(db, "standard")
    keys = {v["key"] for v in variants}
    assert "upper-push" in keys
    assert "upper-pull" in keys
    assert "lower-quads" in keys


def test_get_available_variants_short_filters_empty_branches(client):
    from app.database import SessionLocal
    from app.services.launcher import get_available_variants

    with SessionLocal() as db:
        variants = get_available_variants(db, "short")
    keys = {v["key"] for v in variants}
    assert "upper" in keys
    assert "full-lower" not in keys
    assert "full-body" not in keys


def test_get_available_types_only_shows_types_with_content(client):
    from app.database import SessionLocal
    from app.services.launcher import get_available_types

    with SessionLocal() as db:
        types = get_available_types(db)
    keys = {t["key"] for t in types}
    assert "standard" in keys
    assert "short" in keys
    assert "cardio" in keys
