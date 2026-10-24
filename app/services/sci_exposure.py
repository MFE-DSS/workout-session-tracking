"""Registre d'exposition scientifique, dérivé de l'historique (`Sb_SCI_V2_02`, spec §7).

Une **ligne** par série de travail réalisée et par zone contributrice de la fiche canonique de
l'exercice exécuté. La ligne porte le **rôle brut** (`PRIMARY`, `SECONDARY`, `MINOR`, `UNKNOWN`),
jamais le crédit : l'**agrégat** applique la politique versionnée à la lecture.

**Éligibilité — une seule notion de « série faite » dans le dépôt** (spec §7.1, v3) :

* série : `kind == "work"` et `completed` — `zone_exposure._work_sets`, « même définition que
  `kpis.work_sets_done_30d` » ;
* séance : `status == "completed"`, `excluded_from_stats` faux, `started_at` dans
  `[window_start, until)` — les bornes de `muscle_scoring` ;
* nom exécuté : `substituted_name` sinon `exercise_name_snapshot` (`actual_exercise_name`).

Les deux règles sont recopiées, pas importées : ce module n'importe aucun module du chemin
servi. Des gardes de parité les épinglent contre leurs originaux.

**UNKNOWN n'est jamais zéro.** Une contribution `UNKNOWN` est décomptée à part et fait passer la
zone en borne `MINIMUM` (« au moins ce crédit »). Une série dont l'identité est inconnue fait
passer **toutes** les zones en `MINIMUM` : on ignore ce qu'elle a travaillé.

**Exécution incertaine** (§19.5). Une série faite sous un nom dont la fiche porte un écart
`CONTENT_EXECUTION_MISMATCH` est comptée, et décomptée en `execution_uncertain_sets`. Une zone
n'est une preuve exacte que si sa borne est `EXACT` et ce décompte nul.

Dérivé, recalculable, jamais persisté. Lecture seule. Aucun consommateur servi.
"""
from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import MappingProxyType

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.session import SessionExercise, WorkoutSession
from app.services.sci_catalogue import (
    UNKNOWN_CREDIT,
    CreditPolicy,
    SciCatalogue,
    load_credit_policy,
)
from app.services.sci_identity import IdentityResolution, SciIdentityResolver, load_resolver

_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "data" / "sci" / "exercise_catalogue.schema.json"
ZONES: tuple[str, ...] = tuple(
    json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))["$defs"]["zone"]["enum"])

BOUND_EXACT = "EXACT"
BOUND_MINIMUM = "MINIMUM"


def is_done_work_set(set_log) -> bool:
    """Série de travail validée — la définition de `zone_exposure._work_sets`."""
    return set_log.kind == "work" and bool(set_log.completed)


def executed_name(session_exercise) -> str:
    """Le nom réellement exécuté — la définition de `substitution.actual_exercise_name`."""
    return session_exercise.substituted_name or session_exercise.exercise_name_snapshot


@dataclass(frozen=True)
class LedgerLine:
    session_id: int
    session_exercise_id: int
    set_log_id: int
    session_started_at: datetime
    prescribed_name: str
    executed_name: str
    resolution: IdentityResolution
    catalogue_version: str
    scientific_identity_id: str | None
    zone: str | None
    raw_role: str | None
    role_basis: str | None
    evidence_refs: tuple[str, ...]
    execution_uncertain: bool


def _lines_for_exercise(session, se, resolution: IdentityResolution,
                        catalogue: SciCatalogue) -> list[LedgerLine]:
    done = sorted((sl for sl in se.set_logs if is_done_work_set(sl)), key=lambda sl: (sl.set_index, sl.id))
    common = {"session_id": session.id, "session_exercise_id": se.id, "session_started_at": session.started_at,
              "prescribed_name": se.exercise_name_snapshot, "executed_name": executed_name(se),
              "resolution": resolution, "catalogue_version": resolution.catalogue_version}
    if not resolution.is_resolved:
        return [LedgerLine(**common, set_log_id=sl.id, scientific_identity_id=None, zone=None, raw_role=None,
                           role_basis=None, evidence_refs=(), execution_uncertain=False) for sl in done]
    canonical = catalogue.record(resolution.canonical_exercise_id)
    uncertain = "content_alignment" in catalogue.record(resolution.variant_key)
    return [LedgerLine(**common, set_log_id=sl.id, scientific_identity_id=resolution.scientific_identity_id,
                       zone=c["zone"], raw_role=c["role"], role_basis=c["role_basis"],
                       evidence_refs=tuple(c["evidence_refs"]), execution_uncertain=uncertain)
            for sl in done for c in canonical["exercise_science"]["contributions"]]


def ledger_lines(sessions: Iterable, resolver: SciIdentityResolver, *,
                 db: Session | None = None) -> tuple[LedgerLine, ...]:
    """Lignes du registre pour des séances DÉJÀ éligibles, dans un ordre stable."""
    resolutions: dict[str, IdentityResolution] = {}
    lines: list[LedgerLine] = []
    for session in sorted(sessions, key=lambda s: (s.started_at, s.id)):
        for se in sorted(session.session_exercises, key=lambda x: (x.position, x.id)):
            name = executed_name(se)
            if name not in resolutions:
                resolutions[name] = resolver.resolve_name(name, db)
            lines += _lines_for_exercise(session, se, resolutions[name], resolver.catalogue)
    return tuple(lines)


def load_ledger(db: Session, user_id: int, *, window_start: datetime, until: datetime,
                resolver: SciIdentityResolver | None = None) -> tuple[LedgerLine, ...]:
    """Registre d'un utilisateur sur `[window_start, until)`. Une requête, lecture seule."""
    sessions = db.execute(
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user_id,
               WorkoutSession.status == "completed",
               WorkoutSession.excluded_from_stats.is_(False),
               WorkoutSession.started_at >= window_start,
               WorkoutSession.started_at < until)
        .options(selectinload(WorkoutSession.session_exercises).selectinload(SessionExercise.set_logs))
    ).scalars().all()
    return ledger_lines(sessions, resolver or load_resolver(), db=db)


# ---------------------------------------------------------------------------
# Agrégat par zone
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ZoneExposure:
    zone: str
    resolved_credit: float
    primary_sets: int
    secondary_sets: int
    minor_sets: int
    unknown_sets: int
    unknown_identity_sets: int
    execution_uncertain_sets: int
    bound: str
    policy_id: str

    @property
    def exact_evidence(self) -> bool:
        """Preuve exacte : rien d'inconnu, et aucune série d'exécution incertaine."""
        return self.bound == BOUND_EXACT and self.execution_uncertain_sets == 0


_ROLE_COUNTER = {"PRIMARY": "primary_sets", "SECONDARY": "secondary_sets", "MINOR": "minor_sets",
                 "UNKNOWN": "unknown_sets"}


def _tally(lines: Iterable[LedgerLine], policy: CreditPolicy) -> dict[str, dict]:
    counts = {z: {"resolved_credit": 0.0, "primary_sets": 0, "secondary_sets": 0, "minor_sets": 0,
                  "unknown_sets": 0, "execution_uncertain_sets": 0} for z in ZONES}
    for ln in lines:
        if not ln.resolution.is_resolved:
            continue
        if ln.zone not in counts:
            raise ValueError(f"zone hors vocabulaire : {ln.zone!r}")
        credit = policy.credit(ln.raw_role)
        bucket = counts[ln.zone]
        bucket[_ROLE_COUNTER[ln.raw_role]] += 1
        bucket["execution_uncertain_sets"] += ln.execution_uncertain
        if credit is not UNKNOWN_CREDIT:
            bucket["resolved_credit"] += credit
    return counts


def aggregate(lines: Iterable[LedgerLine], policy: CreditPolicy | None = None) -> Mapping[str, ZoneExposure]:
    """Exposition par zone, sur les 15 zones. Le crédit vient de la politique, à la lecture."""
    lines = tuple(lines)
    policy = policy or load_credit_policy()
    unknown_identity = len({ln.set_log_id for ln in lines if not ln.resolution.is_resolved})
    out = {}
    for zone, c in _tally(lines, policy).items():
        bound = BOUND_EXACT if c["unknown_sets"] == 0 and unknown_identity == 0 else BOUND_MINIMUM
        out[zone] = ZoneExposure(zone=zone, unknown_identity_sets=unknown_identity, bound=bound,
                                 policy_id=policy.policy_id, **c)
    return MappingProxyType(out)
