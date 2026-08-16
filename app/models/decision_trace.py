"""Sb_DECISION_ANALYTICS_RUNTIME_01 — preuve historique d'une décision.

Une ligne = **une décision sémantique** déjà prise par un moteur. Ce modèle
n'entre dans aucune boucle de décision : il enregistre ce qui a été décidé,
avec quelles évidences, et **de quelle nature** était chacune.

Trois propriétés sont structurelles, pas conventionnelles :

**Immuabilité.** Une trace est une preuve historique. Elle n'est jamais
recalculée parce qu'une version de politique, une mesure ou une préférence a
changé : un nouveau calcul écrit de **nouvelles** lignes. Un écouteur SQLAlchemy
refuse tout `UPDATE` sur cette table, de sorte que la garantie ne dépend pas de
la discipline de l'appelant (`Sx_DECISION_ANALYTICS_01_SPEC`, OQ-3).

**Identité ≠ empreinte.** `decision_id` identifie un **événement** (deux
exécutions donnent deux identifiants) ; `decision_fingerprint` identifie un
**contenu** (deux exécutions aux mêmes évidences et au même résultat donnent la
même empreinte). C'est ce qui permet de dire « c'est la même décision, prise une
seconde fois » plutôt que de confondre les deux notions. `created_at` n'entre
donc **jamais** dans l'empreinte.

**Rétention = durée de vie du propriétaire.** `RETENTION_POLICY_V1 =
OWNER_LIFETIME` : aucun TTL, aucune purge, aucun archivage. La trace vit avec
l'historique de son propriétaire et disparaît avec lui via `ON DELETE CASCADE`.
Inventer une sémantique de rétention sans volume de production pour l'informer
produirait une règle arbitraire difficile à défaire (OQ-1).
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, event, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

# OQ-1 tranchée par l'opérateur : pas de TTL, pas de purge, pas d'archivage.
RETENTION_POLICY_V1 = "OWNER_LIFETIME"


class DecisionTrace(Base):
    __tablename__ = "decision_traces"
    __table_args__ = (
        Index("ix_decision_traces_user_created", "user_id", "created_at"),
        Index("ix_decision_traces_group", "trace_group_id"),
        Index("ix_decision_traces_fingerprint", "decision_fingerprint"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Identité d'ÉVÉNEMENT — unique par exécution.
    decision_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    # Une opération d'orchestration = un groupe (génération de plan, replan…).
    trace_group_id: Mapped[str] = mapped_column(String(64), nullable=False)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    decision_type: Mapped[str] = mapped_column(String(48), nullable=False)
    policy_version: Mapped[str] = mapped_column(String(48), nullable=False)

    # Identité de CONTENU — déterministe, sans horodatage.
    decision_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)

    # JSON sérialisé dans `Text` : convention native du dépôt (cf.
    # `training_preferences`), pas un système EAV générique.
    upstream_decision_ids: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    # Les quatre familles de sources restent SÉPARÉES en base. Les fondre en un
    # seul champ détruirait la distinction que la spec impose de préserver.
    constraint_sources: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    preference_sources: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    morphology_sources: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    recovery_sources: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    selected_output: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    # `[]` quand le moteur n'a jamais classé d'alternative. Jamais reconstruit.
    rejected_alternatives: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    # Repris TEL QUEL du moteur : la trace cite, elle ne reformule pas.
    basis: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    confidence: Mapped[str | None] = mapped_column(String(32), nullable=True)

    plan_fingerprint: Mapped[str | None] = mapped_column(String(64), nullable=True)
    program_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    program_version: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class DecisionTraceImmutableError(RuntimeError):
    """Levée quand du code tente de réécrire une preuve historique."""


@event.listens_for(DecisionTrace, "before_update", propagate=True)
def _forbid_update(_mapper, _connection, _target) -> None:  # pragma: no cover - garde
    """Interdit toute réécriture d'une trace persistée.

    Le garde vit ici plutôt que dans le service : une garantie d'immuabilité qui
    dépend de la politesse des appelants n'est pas une garantie. Un recalcul
    légitime écrit une nouvelle ligne ; seule la suppression par cycle de vie du
    propriétaire (CASCADE) est permise.
    """
    raise DecisionTraceImmutableError(
        "Une DecisionTrace est une preuve historique : elle ne se réécrit pas. "
        "Un nouveau calcul doit produire une nouvelle ligne."
    )
