"""`Sb_EXERCISE_IDENTITY_01` — peupler `exercises` depuis les sources existantes.

Idempotent et rejouable, comme le reste de la graine. **N'invente aucun nom** :
tout ce qui est écrit ici vient déjà d'un fichier de données du dépôt.

ORDRE DES SOURCES, ET POURQUOI IL COMPTE
----------------------------------------
1. **Catalogue** (`reference_split.json`) — 68 noms distincts. Ce sont les
   exercices que le produit propose vraiment ; ils créent les identités.
2. **EKB** (`exercise_knowledge_base.json`) — 103 entrées, **surensemble strict
   du catalogue** (mesuré : les 68 y sont tous). Les 35 restants créent aussi
   une identité : ils décrivent des mouvements réels, simplement non
   programmés.
3. **Alias déclarés** (`exercise_knowledge_base._aliases`) — la convention
   existait déjà en données ; elle devient des lignes.

Le catalogue passe en premier pour que le nom porté par `Exercise.name` soit
celui que l'utilisateur voit, et non une variante d'enrichissement.

CE QUE LA GRAINE NE FAIT PAS
----------------------------
**Elle ne fusionne aucun quasi-doublon.** L'audit en a relevé 17 paires dans le
seul catalogue, de « Hip thrust Smith » ~ « Hip thrust Smith machine »
(manifestement le même mouvement) à « Rowing câble assis prise large » ~
« prise neutre » (manifestement deux variantes). Trancher est un jugement
produit ; la table d'alias existe pour que ce jugement, quand il tombera, soit
**additif**.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import BASE_DIR
from app.models.exercise import SOURCE_CATALOG, SOURCE_EKB, Exercise
from app.services.exercise_identity import add_alias, ensure_exercise, resolve_exercise

CATALOG_PATH = BASE_DIR / "data" / "reference_split.json"
EKB_PATH = BASE_DIR / "data" / "exercise_knowledge_base.json"


@dataclass
class SeedReport:
    """Ce que la graine a réellement fait — pas ce qu'elle a tenté."""

    created_catalog: int = 0
    created_ekb: int = 0
    aliases_declared: int = 0
    #: Alias déclaré pointant vers un nom qui désigne déjà un AUTRE exercice.
    #: Rendu, jamais résolu en silence : ce serait une fusion.
    alias_conflicts: list[str] = field(default_factory=list)
    total: int = 0


def _catalog_names(path: Path = CATALOG_PATH) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    seen: dict[str, None] = {}
    for tpl in payload["templates"]:
        for ex in tpl.get("exercises", []):
            seen.setdefault(ex["name"], None)
    return list(seen)


def _ekb(path: Path = EKB_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _create_missing(db: Session, names, source: str) -> int:
    """Crée ce qui manque, compte ce qui a été créé. Rien d'autre."""
    created = 0
    for name in names:
        if resolve_exercise(db, name) is None:
            created += 1
        ensure_exercise(db, name, source=source)
    return created


def _apply_declared_aliases(db: Session, declared: dict, report: SeedReport) -> None:
    """Applique `_aliases`, ou **dit pourquoi il ne l'a pas fait**.

    Extrait de `seed_exercise_identity` : la création d'identités et
    l'arbitrage des alias sont deux lectures, et les tenir ensemble coûtait 16
    de complexité cognitive pour 15 permis (`python:S3776`).
    """
    for alias, canonical in declared.items():
        target = resolve_exercise(db, canonical)
        if target is None:
            # Un alias vers un nom inconnu : on le dit, on ne l'invente pas.
            report.alias_conflicts.append(f"{alias!r} → cible inconnue {canonical!r}")
            continue
        held_by = resolve_exercise(db, alias)
        if held_by is None:
            if add_alias(db, target, alias, source=SOURCE_EKB) is not None:
                report.aliases_declared += 1
        elif held_by.id != target.id:
            report.alias_conflicts.append(
                f"{alias!r} déjà porté par {held_by.slug!r}, "
                f"déclaré pour {target.slug!r}"
            )


def seed_exercise_identity(
    db: Session,
    *,
    catalog_path: Path = CATALOG_PATH,
    ekb_path: Path = EKB_PATH,
) -> SeedReport:
    report = SeedReport()
    payload = _ekb(ekb_path)

    # Le catalogue d'abord : c'est lui qui fixe le `name` que l'utilisateur voit.
    report.created_catalog = _create_missing(
        db, _catalog_names(catalog_path), SOURCE_CATALOG
    )
    report.created_ekb = _create_missing(db, payload["exercises"], SOURCE_EKB)
    _apply_declared_aliases(db, payload.get("_aliases", {}), report)

    report.total = db.execute(select(func.count()).select_from(Exercise)).scalar_one()
    return report


__all__ = ["CATALOG_PATH", "EKB_PATH", "SeedReport", "seed_exercise_identity"]
