"""Real logged sessions + normalized feedback.

Design rules enforced at the schema level:

1. A `WorkoutSession` is anchored to an absolute timestamp
   (`started_at`). The weekday is DERIVED from that timestamp,
   never stored structurally.

2. Every session snapshots enough of the catalog state
   (`template_slug_snapshot`, `exercise_code_snapshot`,
   `exercise_name_snapshot`) so that historical logs survive a
   template library rewrite. The FKs to the catalog are nullable
   with `ON DELETE SET NULL`: the catalog is free to evolve, the
   history stays intact.

3. Feedback is normalized via string / int enums defined in
   `app.enums`. Free-text notes exist but are optional and short
   (they do not feed analytics).
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Ensure catalog models are loaded so that string-based relationship
# references (e.g. "TemplateExercise") resolve correctly even when
# this module is imported in isolation after an app module purge.
import app.models.catalog  # noqa: F401


class WorkoutSession(Base):
    """One real workout, identified by its start timestamp."""

    __tablename__ = "workout_sessions"
    __table_args__ = (
        Index("ix_workout_sessions_started_at", "started_at"),
        # Covers: KPIs, leaderboard, behavioral engine, timeline,
        # progress — every query that filters eligible sessions for
        # a user and orders by date.
        Index(
            "ix_ws_user_status_excl_started",
            "user_id", "status", "excluded_from_stats", "started_at",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Owner. Nullable for backward compat with V1 single-user sessions.
    # V2 routes enforce that every new session has a user_id.
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # FK to the catalog. Nullable + SET NULL so the catalog can be
    # rewritten without orphaning history.
    template_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("workout_templates.id", ondelete="SET NULL"), nullable=True
    )
    # Denormalized snapshots captured at session creation time.
    template_slug_snapshot: Mapped[str] = mapped_column(String(64), nullable=False)
    template_name_snapshot: Mapped[str] = mapped_column(String(128), nullable=False)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="in_progress"
    )

    # Sprint 8: soft-exclude from KPI aggregation and timelines.
    # Lets the user hide test / empty / junk sessions from the
    # quality score, the timeline graphs, and the /progress page,
    # without deleting the raw data.
    excluded_from_stats: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    # Normalized session-level feedback (see app.enums)
    concentration: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    global_state: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)

    bodyweight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Cardio capture (Sb_cardio_capture) — relevant only for kind=cardio templates.
    # Machine calories is explicitly an indicative machine value, NEVER a
    # physiological truth. See SPIGNOS_SCIENCE_PAGE_SPEC.md section 3.
    cardio_duration_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cardio_bpm_avg: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cardio_machine_calories: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cardio_machine_type: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    free_note: Mapped[Optional[str]] = mapped_column(String(280), nullable=True)

    # Sb_13 — telemetry: where the session was created from.
    # Whitelisted values: 'reco_top' | 'reco_alt' | 'launcher' | 'library'
    # | 'replay'. NULL means unknown / pre-Sb_13.
    creation_source: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)

    # Sb_24.1 — scoring formula version gate (Sx_24 §H, §E.2).
    # 1 = pre-Sb_24 sessions, purely declarative formula (historic).
    # 2 = post-Sb_24 sessions, declarative + implicit signal contribution.
    # Existing rows are auto-set to 1 by the migration default — historic
    # stability is guaranteed by the gating in compute_session_quality.
    scoring_version: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="1", default=1
    )

    # Sb_30.3 — overload engine version pinned per session (Sx_30 OQ-B).
    # Reproducibility : a session computed with engine v=N can always be
    # rendered identically by the same engine version. Existing rows get
    # 1 via the column DEFAULT.
    overload_engine_version: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="1", default=1
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    session_exercises: Mapped[list["SessionExercise"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="SessionExercise.position",
    )

    # Read-only navigation to the template, used by the session detail
    # view to branch on `template.kind` (e.g. cardio vs strength).
    template = relationship(
        "WorkoutTemplate", lazy="select", foreign_keys=[template_id]
    )

    @property
    def weekday_iso(self) -> int:
        """ISO weekday (1=Mon..7=Sun) derived from `started_at`."""
        return self.started_at.isoweekday()


class SessionExercise(Base):
    """One exercise as it was actually performed inside a session."""

    __tablename__ = "session_exercises"
    __table_args__ = (
        UniqueConstraint("session_id", "position", name="uq_session_exercise_position"),
        # Covers join from WorkoutSession → SessionExercise in KPI
        # and quality score queries. The unique constraint already
        # indexes (session_id, position), but a bare session_id index
        # is more efficient for the join pattern.
        Index("ix_session_exercises_session_id", "session_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("workout_sessions.id", ondelete="CASCADE"), nullable=False
    )
    template_exercise_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("template_exercises.id", ondelete="SET NULL"), nullable=True
    )
    # Denormalized snapshots so analytics keep working after a reseed.
    exercise_code_snapshot: Mapped[str] = mapped_column(String(16), nullable=False)
    exercise_name_snapshot: Mapped[str] = mapped_column(String(255), nullable=False)

    position: Mapped[int] = mapped_column(Integer, nullable=False)

    # Normalized per-exercise feedback
    success_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 100|80|50
    muscle_sensation: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    free_note: Mapped[Optional[str]] = mapped_column(String(140), nullable=True)
    substituted_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Sb_24.1 — implicit signal label (Sx_24 §D.2).
    # Computed and persisted at the moment the parent session transitions
    # to status="completed". Never recomputed once set — guarantees
    # historic stability even if the detection rules evolve later
    # (Sb_24.next would bump scoring_version instead of recomputing).
    # Valid values are defined by services/implicit_signal.py::ImplicitLabel
    # (Sb_24.2). NULL means: not yet computed, or < 3 work sets, or
    # pattern not classifiable.
    implicit_label: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    implicit_label_computed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    session: Mapped[WorkoutSession] = relationship(back_populates="session_exercises")

    # Optional link back to the catalog. Nullable because a reseed may have
    # detached it (ON DELETE SET NULL). The session page uses this, when
    # present, to render the prescribed set scheme. Never relied on for
    # identity — snapshots above are the source of truth.
    template_exercise = relationship(
        "TemplateExercise",
        lazy="select",
    )

    set_logs: Mapped[list["SetLog"]] = relationship(
        back_populates="session_exercise",
        cascade="all, delete-orphan",
        order_by="SetLog.set_index",
    )


class SetLog(Base):
    """One logged set, warmup or work, actually attempted.

    V1 design choice: warmup and work sets live in the same table
    and are distinguished only by `kind`. Set indexes are scoped per
    (session_exercise, kind), so warmups number 1..N independently
    of work sets, matching how a coach writes a notebook.
    """

    __tablename__ = "set_logs"
    __table_args__ = (
        UniqueConstraint(
            "session_exercise_id", "kind", "set_index", name="uq_set_log_kind_index"
        ),
        # Covers: work set completion counts in KPIs and quality score.
        # Filters on (kind='work', completed=True) are the hottest
        # SetLog access pattern.
        Index(
            "ix_set_logs_exercise_kind_completed",
            "session_exercise_id", "kind", "completed",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    session_exercise_id: Mapped[int] = mapped_column(
        ForeignKey("session_exercises.id", ondelete="CASCADE"), nullable=False
    )
    kind: Mapped[str] = mapped_column(String(8), nullable=False, default="work")
    set_index: Mapped[int] = mapped_column(Integer, nullable=False)

    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    technique: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)

    # Normalized per-set feedback
    execution_quality: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    reps_target: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)

    # Distingue « pas encore tentée » (la ligne a été pré-rendue par le
    # constructeur de séance, l'utilisateur n'y a pas touché) de « exécutée ».
    #
    # ⚠ `UI-CP8R` — CE COMMENTAIRE DÉCRIVAIT UN PRODUIT QUI N'EXISTE PLUS.
    # Il parlait d'un drapeau « explicite » que l'utilisateur « cocherait ».
    # La case a été retirée par `Sb_24.4` : `completed` est DÉRIVÉ côté
    # serveur de la présence d'un poids OU de répétitions (`Sx_24 §E`), dans
    # `_persist_set_values`. Le comportement n'est pas touché ici — c'est la
    # prose qui est alignée sur lui, jamais l'inverse.
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # ── `UI-CP8R` · LA VÉRITÉ TEMPORELLE ────────────────────────────────
    #
    # QUAND la série a été exécutée. C'est la seule origine de temps durable
    # du repos : avant cette colonne, `?rest=1` disait « un repos vient de
    # démarrer sur CETTE requête » et ne pouvait rien dire de plus — un
    # rechargement trois secondes plus tard réaffichait 1:30.
    #
    # `NULL` sur une ligne `completed = True` signifie **heure inconnue**,
    # pas « jamais faite » : aucun backfill n'était honnête (voir la
    # migration `w4x9r5s6u17`). Une telle ligne ne produit jamais de repos.
    #
    # Contrat d'écriture (`_persist_set_values`) : posée à la transition
    # INCOMPLÈTE → COMPLÈTE, **préservée** quand une série déjà complète est
    # corrigée — sinon rectifier une faute de frappe ressusciterait un repos
    # vieux d'une heure — et effacée quand la série est dé-complétée.
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # QUAND l'utilisateur a décidé de dépasser le repos de CETTE série.
    #
    # Portée par SÉRIE, pas par séance : la décision appartient à la
    # transition qui l'a produite. Portée séance, corriger une vieille série
    # effacerait la décision prise sur la série courante.
    #
    # Elle appartient aussi à l'ÉPISODE de complétion courant : dé-compléter
    # puis refaire la série la remet à `NULL`. Un saut décidé sur une
    # exécution passée ne peut pas survivre dans une exécution neuve.
    #
    # Avant `UI-CP8R`, passer le repos n'écrivait RIEN : c'était un GET vers
    # la même URL sans `rest=1`, et ça ne survivait au rechargement que parce
    # que l'URL rechargée ne portait plus le paramètre. En retirant au
    # paramètre son autorité, on retirait au saut son unique mécanisme.
    rest_dismissed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    session_exercise: Mapped[SessionExercise] = relationship(back_populates="set_logs")
