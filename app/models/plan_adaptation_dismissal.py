"""`UI-CP3.5` — l'écartement d'une adaptation. Et rien d'autre.

POURQUOI CETTE TABLE EST SI PETITE
----------------------------------
Tout ce qui fait une décision — identité d'exécution, identité de contenu,
cause, conséquence, empreinte de plan, justification, horodatage — vit déjà
dans `decision_traces`, dont l'**immuabilité est imposée** par un écouteur
`before_update` qui lève plutôt que de laisser réécrire une preuve.

C'est exactement pour cela qu'on ne peut pas y poser un `dismissed_at` : une
trace immuable ne porte pas de cycle de vie. Le cycle de vie a donc son propre
support, et il ne contient que ce que la trace refuse.

CE QU'ELLE N'EST PAS
--------------------
Ce n'est ni un journal d'événements, ni une machine à états. Les trois états du
contrat de tranche se lisent ainsi :

    ACTIVE      une trace `REPLAN_DELTA` sans ligne ici,
                dont l'empreinte de plan vaut encore
    DISMISSED   une ligne ici
    SUPERSEDED  **dérivé** — l'empreinte de plan ne correspond plus au
                contexte courant, ou une décision plus récente porte sur le
                même sujet

`SUPERSEDED` n'est pas stocké, et c'est délibéré : le marquer exigerait
d'écrire à la LECTURE, ce que le contrat interdit. Le dériver le rend
automatique — un changement de cadence ou de matériel périme les anciennes
décisions sans qu'aucun code ne s'en occupe.

L'ÉCARTEMENT NE SUPPRIME RIEN
-----------------------------
La trace historique survit intacte. Ce qui cesse, c'est l'EFFET : l'adaptation
ne compose plus le plan effectif. *« L'historique survit ; le comportement,
non. »*
"""
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PlanAdaptationDismissal(Base):
    """Une adaptation que l'utilisateur a écartée."""

    __tablename__ = "plan_adaptation_dismissals"
    __table_args__ = (
        Index("ix_plan_adapt_dismissal_user", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    #: L'identité d'EXÉCUTION de la trace écartée — `decision_traces.decision_id`.
    #: Pas une clé étrangère SQL : `decision_traces` a sa propre politique de
    #: rétention (`OWNER_LIFETIME`) et l'y attacher ferait de cette table une
    #: contrainte sur elle. Unique, parce qu'écarter deux fois la même décision
    #: est le même fait.
    decision_id: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    #: Quand. Le seul autre fait de cette table.
    dismissed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(UTC), server_default=func.now())


__all__ = ["PlanAdaptationDismissal"]
