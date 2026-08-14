"""Préférences d'entraînement **déclarées** par l'utilisateur (Sb_TRAINING_PREFERENCES_01).

Première source **persistée** de préférences du dépôt. Le préflight code-first a
établi qu'aucune n'existait : `User` ne porte que l'identité et des mesures
physiques, aucune migration ne mentionne ces concepts, et
`program_quality_engine.UserProfile` — qui déclare pourtant `sessions_per_week`
et `available_equipment` — est une **dataclass pure jamais construite nulle part
dans `app/`**. C'était un consommateur déclaré et jamais alimenté ; cette table
est ce qui l'alimentera.

**Ce que cette table est** : ce que l'utilisateur a **dit** vouloir ou pouvoir
faire. **Ce qu'elle n'est pas** : sa readiness, sa récupération, sa physiologie,
sa morphologie, une recommandation, une prescription optimale, un profil de
salle, ni un calendrier. Ces dimensions restent séparées, et rien ici ne modifie
une décision d'entraînement dans cette tranche.

**`NULL` n'est jamais `[]`.** La distinction est le cœur du contrat : un futur
planificateur doit pouvoir séparer « l'utilisateur l'a dit » de « le système l'a
supposé ». Aucune valeur non déclarée n'est convertie en fait stocké — pas de
`3 séances` par défaut, pas de « tout le matériel », pas de priorités implicites.

| État | Signification |
|---|---|
| aucune ligne | rien n'a été déclaré |
| `sessions_per_week = NULL` | cadence non déclarée |
| `focus_priorities = NULL` | priorités non déclarées |
| `focus_priorities = []` | **explicitement** aucune priorité particulière |
| `available_equipment = NULL` | disponibilité inconnue / non contrainte |
| `available_equipment = []` | **explicitement** aucun matériel externe |

**Stockage des listes** : JSON dans une colonne `Text`, la convention native du
dépôt (`user_program.subscores_json`, `alerts_json`, `suggestions_json`). Jamais
de chaîne séparée par des virgules. L'ordre des priorités est significatif et
préservé par le JSON ; la validation et la conversion vivent dans
`app.services.training_preferences`, jamais ici.
"""
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TrainingPreferences(Base):
    """Une ligne **au plus** par utilisateur. L'absence de ligne est valide."""

    __tablename__ = "training_preferences"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_training_preferences_user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    #: Cadence souhaitée, 1–7. `NULL` = non déclarée. Ce n'est **pas** un
    #: optimum : la logique de dose d'entraînement appartient au futur service
    #: de budget de volume, pas à une préférence déclarée.
    sessions_per_week: Mapped[int | None] = mapped_column(Integer, nullable=True)

    #: Liste **ordonnée** JSON de clés d'axe radar. `NULL` ≠ `[]`.
    focus_priorities: Mapped[str | None] = mapped_column(Text, nullable=True)

    #: Liste JSON de familles d'équipement, normalisée en ensemble ordonné.
    #: `NULL` ≠ `[]`.
    available_equipment: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
