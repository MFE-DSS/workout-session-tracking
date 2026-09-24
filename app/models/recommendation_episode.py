"""`REC-CP4` — l'épisode de recommandation : ce qui a été proposé, et ce que
l'utilisateur en a fait.

CE QUE CETTE TABLE EXISTE POUR CORRIGER
------------------------------------------
La passe `REC-CP1..CP3` a établi que le moteur n'est pas « bloqué » :

    conseil SUIVI    → il tourne, six gabarits sur dix décisions
    conseil DÉCLINÉ  → il répète le même conseil indéfiniment

Le défaut n'est donc pas un poids de score. C'est que **AUREN ne se souvient
pas d'avoir déjà donné un conseil que l'utilisateur a explicitement écarté**.

CE QU'ELLE N'EST PAS
----------------------
Ce n'est **pas** une préférence utilisateur. On n'y écrit jamais « cet
utilisateur n'aime pas le LISS » ni une pénalité de score. On y écrit qu'à un
instant donné, dans un contexte donné, un conseil précis a été écarté — et
rien de plus. Une préférence durable exigerait des preuves répétées, et elle
est hors périmètre.

Ce n'est **pas** un journal d'événements générique. Une seule table, bornée,
sans EAV, sans projection, sans rejeu d'agrégats.

TROIS ÉTATS, UN SEUL PERSISTÉ
--------------------------------
On reprend mot pour mot la doctrine déjà établie par
`plan_adaptation_dismissals` (`UI-CP3.5`), plutôt que d'en inventer une
seconde :

* `UNRESOLVED` est l'**absence de ligne**. Un utilisateur qui voit une
  recommandation et ferme l'application n'a rien dit — et
  `NO ACTION != NEGATIVE FEEDBACK`.
* `RESOLVED` est **la ligne**, avec son issue.
* `SUPERSEDED` est **dérivé** à la lecture, en comparant l'empreinte de
  contexte stockée à l'empreinte courante. Le marquer exigerait d'écrire
  pendant un `GET`, ce que le contrat interdit — et une colonne de cycle de vie
  pourrait rester périmée, là où une dérivation ne le peut pas.

C'est pourquoi il n'y a **pas** de colonne `lifecycle` : elle serait la seule
source possible d'un état faux.

AUCUN BACKFILL
----------------
Aucun épisode n'a jamais été enregistré, donc aucun ne peut être reconstitué.
`creation_source` dit d'où vient une séance créée ; il ne dit pas **quelle**
recommandation était affichée à ce moment-là. Fabriquer des épisodes
historiques affirmerait une présentation que personne n'a observée.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

#: L'utilisateur a démarré la séance recommandée.
ACCEPTED_TOP = "ACCEPTED_TOP"
#: L'utilisateur a démarré une des alternatives proposées.
ACCEPTED_ALTERNATIVE = "ACCEPTED_ALTERNATIVE"
#: L'utilisateur a démarré autre chose, alors qu'un conseil était affiché.
CHOSE_OTHER = "CHOSE_OTHER"
#: L'utilisateur a écarté le conseil sans rien démarrer.
#:
#: ⚠ AUCUNE SURFACE NE PRODUIT CETTE ISSUE AUJOURD'HUI, et c'est une décision.
#: L'ajouter supposerait un bouton « écarter » — donc une affordance de
#: rétroaction permanente, que le périmètre exclut tant qu'aucune preuve ne
#: l'exige. L'issue existe dans le contrat parce que `CHOSE_OTHER` et
#: « écarté sans rien faire » ne sont pas le même geste, et les confondre
#: rendrait la télémétrie inintelligible le jour où l'affordance existera.
EXPLICITLY_DISMISSED = "EXPLICITLY_DISMISSED"

#: Les issues qui valent REFUS, et elles seules.
#:
#: Accepter le conseil ou une de ses alternatives ne crée aucune mémoire
#: négative : il n'y a rien à ne pas reproposer.
ISSUES_DE_REFUS = frozenset({CHOSE_OTHER, EXPLICITLY_DISMISSED})

ISSUES = frozenset({
    ACCEPTED_TOP, ACCEPTED_ALTERNATIVE, CHOSE_OTHER, EXPLICITLY_DISMISSED,
})


class RecommendationEpisode(Base):
    """Un conseil donné, et son issue. Une ligne par contexte de décision."""

    __tablename__ = "recommendation_episodes"
    __table_args__ = (
        # ⚠ `§11-G` — DEUX RENDUS DE LA MÊME DÉCISION NE FONT PAS DEUX
        # MÉMOIRES. L'unicité est portée par la base, pas par la politesse des
        # appelants : un double envoi de formulaire est le même fait.
        UniqueConstraint(
            "user_id", "context_fingerprint",
            name="uq_reco_episode_user_context"),
        Index("ix_reco_episode_user_context", "user_id", "context_fingerprint"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    #: L'empreinte du CONTEXTE MATÉRIEL de la décision — déterministe, sans
    #: horodatage, dérivée des seules entrées que le moteur consomme.
    #: C'est elle qui rend la supersession dérivable.
    context_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)

    #: `v2` ou `v3`. Une décision ancienne reste intelligible quand la
    #: politique change (`§11-H`) : on sait qui l'a produite.
    policy_version: Mapped[str] = mapped_column(String(16), nullable=False)

    #: Quand le conseil a été PRÉSENTÉ (transmis par le formulaire), distinct
    #: de quand il a été résolu.
    decided_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    resolved_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp())

    #: Le conseil : le gabarit en tête, et les alternatives offertes.
    proposed_top_slug: Mapped[str] = mapped_column(String(64), nullable=False)
    #: Joint par virgules, borné. Pas une table de liaison : deux alternatives
    #: au plus, et rien ne les interroge individuellement.
    proposed_alt_slugs: Mapped[str] = mapped_column(
        String(255), nullable=False, default="")

    outcome: Mapped[str] = mapped_column(String(32), nullable=False)
    #: Ce qui a effectivement été démarré. `NULL` si rien ne l'a été.
    chosen_slug: Mapped[str | None] = mapped_column(String(64), nullable=True)

    #: La séance créée par ce geste, quand il y en a une. Pas une clé
    #: étrangère : une séance supprimée ne doit pas effacer la mémoire du
    #: conseil, qui reste un fait observé.
    session_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    @property
    def est_un_refus(self) -> bool:
        return self.outcome in ISSUES_DE_REFUS

    @property
    def alternatives(self) -> tuple[str, ...]:
        return tuple(s for s in self.proposed_alt_slugs.split(",") if s)
