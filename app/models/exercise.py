"""`Sb_EXERCISE_IDENTITY_01` — l'entité qui n'existait pas.

POURQUOI
--------
Jusqu'ici, **aucune table ne représentait un exercice.** Il n'existait que des
*lignes* qui en mentionnaient un, chacune dans son vocabulaire :

* ``template_exercises`` — une ligne de gabarit : ``code`` vaut ``E1…E8``,
  c'est-à-dire une **position**. Mesuré : **7 codes sur 8 portent plusieurs
  noms** (``E3`` en porte 15). Le code n'identifie rien.
* ``template_exercises.id`` — identifie la ligne, pas l'exercice. Mesuré :
  **28 noms sur 68 apparaissent dans au moins deux gabarits**, donc autant de
  lignes distinctes pour un même mouvement.
* ``session_exercises.exercise_name_snapshot`` / ``substituted_name`` — du
  texte, figé au moment de la séance.
* ``exercise_muscle_mappings.exercise_code`` — un **nom**, malgré son intitulé.

La recherche ne pouvait donc se faire que par le nom. Elle marche aujourd'hui
— 68/68 du catalogue sont attribués — et elle ne survivra pas au premier
renommage produit.

CE QUE CETTE TABLE EST, ET N'EST PAS
------------------------------------
``slug`` est l'**identité** : engendré une fois, jamais régénéré, jamais
réutilisé. ``name`` est un **libellé**, libre de changer sans rien casser.
C'est toute la séparation que le dépôt n'avait pas.

Mesuré avant d'écrire : une slugification déterministe des 68 noms du
catalogue produit **68 slugs distincts, zéro collision**. Le backfill est donc
déterministe — c'est ce qui autorise cette migration à être purement additive.

CE QU'ELLE NE TRANCHE PAS
-------------------------
**Une identité par nom distinct existant. Aucune fusion.** L'audit a relevé
**17 paires de quasi-doublons dans le seul catalogue** — de
``Hip thrust Smith`` ~ ``Hip thrust Smith machine`` (manifestement le même
mouvement) à ``Rowing câble assis prise large`` ~ ``prise neutre``
(manifestement deux variantes). Décider lesquelles fusionner est un **jugement
produit**, pas une dérivation.

D'où ``ExerciseAlias`` : fusionner plus tard devient **additif** — on ajoute
une ligne d'alias et on repointe, on ne détruit rien. La convention existe
déjà en données (``exercise_knowledge_base._aliases``) ; elle monte ici au
rang de schéma.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

#: Provenance d'un nom. Sert à mesurer la migration, pas à décider.
SOURCE_CATALOG = "catalog"
SOURCE_EKB = "ekb"
SOURCE_MANUAL = "manual"


class Exercise(Base):
    """Un mouvement, une fois. Le reste du dépôt le désigne par son ``slug``."""

    __tablename__ = "exercises"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_exercises_slug"),
        Index("ix_exercises_name", "name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    #: **Immuable.** Engendré à la création depuis le nom d'alors, puis figé.
    #: Un renommage produit change ``name`` et laisse ``slug`` intact — c'est
    #: précisément ce que le nom-comme-clé ne pouvait pas offrir.
    slug: Mapped[str] = mapped_column(String(length=96), nullable=False)

    #: Libellé courant. Mutable, et sans conséquence sur l'identité.
    name: Mapped[str] = mapped_column(String(length=255), nullable=False)

    #: D'où le nom est venu la première fois. Instrument de mesure.
    source: Mapped[str] = mapped_column(
        String(length=16), nullable=False, default=SOURCE_CATALOG
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    aliases: Mapped[list[ExerciseAlias]] = relationship(
        back_populates="exercise", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - confort de debug
        return f"<Exercise {self.slug!r}>"


class ExerciseAlias(Base):
    """Un autre nom pour le même mouvement.

    Deux usages, et un seul mécanisme : absorber les vocabulaires divergents
    déjà en base (le catalogue écrit ``Curl marteau câble (corde)`` là où l'EKB
    écrit ``Curl marteau câble corde`` — **même chaîne une fois normalisée**),
    et rendre une fusion future **additive**.
    """

    __tablename__ = "exercise_aliases"
    __table_args__ = (
        UniqueConstraint("normalized", name="uq_exercise_aliases_normalized"),
        Index("ix_exercise_aliases_exercise", "exercise_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    exercise_id: Mapped[int] = mapped_column(
        ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False
    )

    #: Le nom tel qu'il est écrit quelque part dans le produit.
    alias: Mapped[str] = mapped_column(String(length=255), nullable=False)

    #: Le même, normalisé — c'est **lui** qui est unique. Chercher sur la forme
    #: brute laisserait « Curl marteau câble (corde) » et « Curl marteau câble
    #: corde » cohabiter comme deux exercices.
    normalized: Mapped[str] = mapped_column(String(length=255), nullable=False)

    source: Mapped[str] = mapped_column(
        String(length=16), nullable=False, default=SOURCE_CATALOG
    )

    exercise: Mapped[Exercise] = relationship(back_populates="aliases")

    def __repr__(self) -> str:  # pragma: no cover - confort de debug
        return f"<ExerciseAlias {self.alias!r}>"


__all__ = [
    "SOURCE_CATALOG",
    "SOURCE_EKB",
    "SOURCE_MANUAL",
    "Exercise",
    "ExerciseAlias",
]
