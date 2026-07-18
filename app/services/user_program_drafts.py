"""Draft CRUD for user-created programs (Sb_CUSTOM_PROGRAM_PERSISTENCE_04).

First SERVICE brick of the Custom Program track: minimal, owner-scoped
manipulation of a draft `UserProgram` and its tree — nothing else.

Hard boundaries (specs 03/04/05):
- OWNERSHIP: every function requires `user_id` and filters on it. A
  program that does not exist and a program owned by someone else are
  indistinguishable from the caller's perspective (no existence leak).
- "DELETE" IS SOFT: archiving sets `archived_at` (spec 04 §8). No hard
  delete is exposed (OQ-PERS-A reserved for a future explicit flow).
- EDITING RULES (spec 04 §6): only `draft` and `validated` programs are
  editable; editing a `validated` program flips it back to `draft`.
  `published` is immutable here — the post-publication new-cycle logic
  belongs to the publication era (spec 05), not to this service.
- NO publication, NO scoring, NO wizard, NO EKB.
- QUOTAS (PERSISTENCE_05, spec 04 §9): versioned application constants,
  enforced with gentle, actionable messages — never guilt-tripping.

Transaction convention: mutations validate, then commit themselves
(domain-CRUD pattern of squad/challenge/readiness); on integrity errors
the session is rolled back and a readable domain error is raised.
"""
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.user_program import (
    UserProgram,
    UserProgramExercise,
    UserProgramRepTarget,
    UserProgramSession,
)

_EDITABLE_STATUSES = ("draft", "validated")

_NOT_FOUND = "Programme introuvable"

# Quotas V1 (Sx_CUSTOM_PROGRAM_04 §9, PERSISTENCE_05) — versioned application
# constants, never DB config. The published-versions quota (5) only makes
# sense at publication time and is deferred to that era.
MAX_ACTIVE_PROGRAMS = 10
MAX_SESSIONS_PER_PROGRAM = 7
MAX_EXERCISES_PER_SESSION = 10


class UserProgramDraftError(Exception):
    """Readable domain error for draft CRUD misuse."""


# ──────────────────────────── reads ────────────────────────────


def _owned_query(user_id: int):
    return select(UserProgram).where(UserProgram.user_id == user_id)


def get_draft(db: Session, user_id: int, program_id: int) -> UserProgram | None:
    """Owner-scoped read with the full tree eagerly loaded. Returns None
    for a missing OR non-owned program (indistinguishable on purpose)."""
    return db.execute(
        _owned_query(user_id)
        .where(UserProgram.id == program_id)
        .options(
            selectinload(UserProgram.sessions)
            .selectinload(UserProgramSession.exercises)
            .selectinload(UserProgramExercise.rep_targets),
            selectinload(UserProgram.quality_reviews),
        )
    ).scalar_one_or_none()


def list_drafts(
    db: Session, user_id: int, *, include_archived: bool = False
) -> list[UserProgram]:
    """Owner's programs, most recently edited first."""
    stmt = _owned_query(user_id).order_by(UserProgram.updated_at.desc())
    if not include_archived:
        stmt = stmt.where(UserProgram.archived_at.is_(None))
    return list(db.execute(stmt).scalars().all())


# ─────────────────────────── mutations ───────────────────────────


def create_draft(
    db: Session, user_id: int, title: str, slug_base: str
) -> UserProgram:
    title = (title or "").strip()
    slug_base = (slug_base or "").strip()
    if not title:
        raise UserProgramDraftError("Le titre ne peut pas être vide")
    if not slug_base:
        raise UserProgramDraftError("Le slug ne peut pas être vide")

    active_count = db.execute(
        select(func.count())
        .select_from(UserProgram)
        .where(UserProgram.user_id == user_id, UserProgram.archived_at.is_(None))
    ).scalar_one()
    if active_count >= MAX_ACTIVE_PROGRAMS:
        raise UserProgramDraftError(
            f"Tu as déjà {MAX_ACTIVE_PROGRAMS} programmes actifs — en archiver "
            "un libère une place"
        )

    program = UserProgram(user_id=user_id, title=title, slug_base=slug_base)
    db.add(program)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise UserProgramDraftError(
            f"Un programme avec le slug « {slug_base} » existe déjà"
        ) from exc
    db.refresh(program)
    return program


def _owned_editable(db: Session, user_id: int, program_id: int) -> UserProgram:
    """Fetch an owned program and enforce the editing rules (spec 04 §6)."""
    program = db.execute(
        _owned_query(user_id).where(UserProgram.id == program_id)
    ).scalar_one_or_none()
    if program is None:
        raise UserProgramDraftError(_NOT_FOUND)
    if program.archived_at is not None:
        raise UserProgramDraftError("Programme archivé — désarchiver d'abord")
    if program.status not in _EDITABLE_STATUSES:
        raise UserProgramDraftError(
            "Une version publiée ne se modifie pas — l'édition ouvrira un "
            "nouveau cycle (fonctionnalité de publication à venir)"
        )
    if program.status == "validated":
        # Editing a validated program reopens the draft (spec 04 §6).
        program.status = "draft"
    return program


def rename_draft(
    db: Session, user_id: int, program_id: int, title: str
) -> UserProgram:
    title = (title or "").strip()
    if not title:
        raise UserProgramDraftError("Le titre ne peut pas être vide")
    program = _owned_editable(db, user_id, program_id)
    program.title = title
    db.commit()
    db.refresh(program)
    return program


def _validate_positions(values: list[int], label: str) -> None:
    if values != list(range(1, len(values) + 1)):
        raise UserProgramDraftError(
            f"Les positions de {label} doivent être séquentielles à partir de 1"
        )


def replace_draft_tree(
    db: Session, user_id: int, program_id: int, sessions_payload: list[dict]
) -> UserProgram:
    """Replace the WHOLE child tree of a draft (the V1 editing gesture:
    wizard and card editing rebuild server-side). Old children are purged
    by the delete-orphan cascade."""
    program = _owned_editable(db, user_id, program_id)

    if len(sessions_payload) > MAX_SESSIONS_PER_PROGRAM:
        raise UserProgramDraftError(
            f"Un programme compte au plus {MAX_SESSIONS_PER_PROGRAM} séances "
            "par semaine — regrouper ou alléger le plan"
        )
    _validate_positions(
        [s.get("position") for s in sessions_payload], "séances"
    )

    new_sessions: list[UserProgramSession] = []
    for s in sessions_payload:
        session = UserProgramSession(
            position=s["position"],
            name=(s.get("name") or "").strip() or f"Séance {s['position']}",
            kind=s.get("kind", "strength"),
            focus=s.get("focus", ""),
            duration_target_minutes=s.get("duration_target_minutes"),
            notes=s.get("notes"),
        )
        exercises_payload = s.get("exercises", [])
        if len(exercises_payload) > MAX_EXERCISES_PER_SESSION:
            raise UserProgramDraftError(
                f"Une séance compte au plus {MAX_EXERCISES_PER_SESSION} "
                "exercices — garder l'essentiel aide à tenir la durée"
            )
        _validate_positions(
            [e.get("position") for e in exercises_payload],
            f"exercices (séance {s['position']})",
        )
        for e in exercises_payload:
            exercise = UserProgramExercise(
                position=e["position"],
                exercise_name=e["exercise_name"],
                set_scheme=e["set_scheme"],
                variant_key=e.get("variant_key"),
                variant_group=e.get("variant_group"),
                equipment_family=e.get("equipment_family"),
                movement_pattern=e.get("movement_pattern"),
                notes=e.get("notes"),
                source_reason=e.get("source_reason", "manual"),
            )
            for i, rt in enumerate(e.get("rep_targets", []), start=1):
                exercise.rep_targets.append(
                    UserProgramRepTarget(
                        set_index=i,
                        min_reps=rt["min_reps"],
                        max_reps=rt["max_reps"],
                        technique=rt.get("technique"),
                        is_warmup=rt.get("is_warmup", False),
                    )
                )
            session.exercises.append(exercise)
        new_sessions.append(session)

    # Purge the old tree FIRST and flush, so the deletes reach the DB
    # before the new inserts — otherwise the unit of work may insert a
    # new session at a position still occupied by an old row and trip
    # the (program, position) unique constraint.
    program.sessions.clear()
    db.flush()
    program.sessions.extend(new_sessions)
    db.commit()
    db.refresh(program)
    return program


def validate_draft(db: Session, user_id: int, program_id: int) -> UserProgram:
    """Transition draft → validated (spec 04 §6) with a MINIMAL completeness
    check: at least one session, every session has at least one exercise,
    every exercise has at least one rep target. Publication stays a later,
    separately gated era — `validated` only marks the recap as accepted.
    Idempotent on an already-validated program."""
    program = db.execute(
        _owned_query(user_id)
        .where(UserProgram.id == program_id)
        .options(
            selectinload(UserProgram.sessions)
            .selectinload(UserProgramSession.exercises)
            .selectinload(UserProgramExercise.rep_targets)
        )
    ).scalar_one_or_none()
    if program is None:
        raise UserProgramDraftError(_NOT_FOUND)
    if program.archived_at is not None:
        raise UserProgramDraftError("Programme archivé — désarchiver d'abord")
    if program.status == "published":
        raise UserProgramDraftError("Une version publiée est déjà validée")
    if program.status == "validated":
        return program

    if not program.sessions:
        raise UserProgramDraftError("Ajoute au moins une séance avant de valider")
    for session in program.sessions:
        if not session.exercises:
            raise UserProgramDraftError(
                f"La séance « {session.name} » n'a pas encore d'exercice"
            )
        for exercise in session.exercises:
            if not exercise.rep_targets:
                raise UserProgramDraftError(
                    f"« {exercise.exercise_name} » n'a pas encore de plage "
                    "de répétitions"
                )

    program.status = "validated"
    db.commit()
    db.refresh(program)
    return program


def archive_draft(db: Session, user_id: int, program_id: int) -> UserProgram:
    """Soft delete (spec 04 §8): the program leaves the library, the data
    stays. Archiving an already-archived program is an explicit error."""
    program = db.execute(
        _owned_query(user_id).where(UserProgram.id == program_id)
    ).scalar_one_or_none()
    if program is None:
        raise UserProgramDraftError(_NOT_FOUND)
    if program.archived_at is not None:
        raise UserProgramDraftError("Programme déjà archivé")
    program.archived_at = datetime.now(UTC)
    db.commit()
    db.refresh(program)
    return program
