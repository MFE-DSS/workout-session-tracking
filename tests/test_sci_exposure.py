"""Sb_SCI_V2_02 — le registre d'exposition dérivé (spec §7).

Une ligne par série de travail réalisée et par zone contributrice, avec le RÔLE BRUT ;
l'agrégat applique la politique de crédit à la lecture et ne fait jamais d'un UNKNOWN un zéro.
Dérivé, recalculable, jamais persisté ; aucun consommateur servi.
"""

from __future__ import annotations

import ast
import dataclasses
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

import app.models  # noqa: F401 — peuple Base.metadata
from app.database import Base
from app.models.session import SessionExercise, SetLog, WorkoutSession
from app.models.user import User
from app.services import sci_exposure as sx
from app.services import sci_identity as si
from app.services import zone_exposure
from app.services.sci_catalogue import load_catalogue
from app.services.substitution import actual_exercise_name

ROOT = Path(__file__).resolve().parents[1]
T0 = datetime(2026, 9, 1, 18, 0, tzinfo=UTC)
#: les valeurs du CONTRAT (spec §7.3), écrites en clair : comparer aux constantes du module
#: rendrait la garde aveugle à un échange de ces constantes (contre-preuve du 2026-10-24)
EXACT, MINIMUM = "EXACT", "MINIMUM"


@pytest.fixture
def db():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as s:
        s.add(User(id=1, username="u1", password_hash="x"))
        s.add(User(id=2, username="u2", password_hash="x"))
        s.commit()
        yield s


def _session(db: Session, *, user_id=1, days=0, status="completed", excluded=False, exercises=()):
    """exercises : (nom prescrit, nom substitué ou None, [(kind, completed), …])"""
    s = WorkoutSession(user_id=user_id, template_slug_snapshot="t", template_name_snapshot="T", status=status,
                       excluded_from_stats=excluded, started_at=T0 + timedelta(days=days))
    for pos, (name, substituted, sets) in enumerate(exercises, start=1):
        se = SessionExercise(exercise_code_snapshot=f"E{pos}", exercise_name_snapshot=name,
                             substituted_name=substituted, position=pos)
        counters: dict[str, int] = {}
        for kind, completed in sets:
            counters[kind] = counters.get(kind, 0) + 1
            se.set_logs.append(SetLog(kind=kind, set_index=counters[kind], completed=completed))
        s.session_exercises.append(se)
    db.add(s)
    db.commit()
    return s


WORK, WARM = ("work", True), ("warmup", True)
UNDONE = ("work", False)


def _ledger(db, **kw):
    kw.setdefault("window_start", T0 - timedelta(days=30))
    kw.setdefault("until", T0 + timedelta(days=30))
    return sx.load_ledger(db, 1, **kw)


# ── éligibilité : la seule notion de « série faite » du dépôt


def test_done_work_set_rule_is_the_one_zone_exposure_uses(db):
    s = _session(db, exercises=[("Pompes", None, [WARM, WARM, WORK, UNDONE, WORK, WORK])])
    se = s.session_exercises[0]
    assert sum(sx.is_done_work_set(sl) for sl in se.set_logs) == zone_exposure._work_sets(se) == 3


def test_only_completed_eligible_sessions_in_the_window_count(db):
    _session(db, days=0, exercises=[("Pompes", None, [WORK])])
    _session(db, days=1, status="in_progress", exercises=[("Pompes", None, [WORK])])
    _session(db, days=2, status="abandoned", exercises=[("Pompes", None, [WORK])])
    _session(db, days=3, excluded=True, exercises=[("Pompes", None, [WORK])])
    _session(db, days=4, user_id=2, exercises=[("Pompes", None, [WORK])])
    _session(db, days=10, exercises=[("Pompes", None, [WORK])])  # = until : borne exclusive
    lines = _ledger(db, until=T0 + timedelta(days=10))
    assert {ln.set_log_id for ln in lines} == {_set_ids(db, days=0)}


def _set_ids(db, *, days):
    s = db.execute(select(WorkoutSession).where(WorkoutSession.started_at == T0 + timedelta(days=days))).scalar_one()
    (sl,) = s.session_exercises[0].set_logs
    return sl.id


def test_window_start_is_inclusive(db):
    _session(db, days=0, exercises=[("Pompes", None, [WORK])])
    assert _ledger(db, window_start=T0)


# ── lignes : rôle brut, nom exécuté, provenance


def test_one_line_per_done_set_and_contributing_zone_with_raw_roles(db):
    _session(db, exercises=[("Roulette abdominale", None, [WORK, WORK])])
    lines = _ledger(db)
    record = load_catalogue().record("roulette-abdominale")
    zones = [c["zone"] for c in record["exercise_science"]["contributions"]]
    assert len(lines) == 2 * len(zones)
    assert {(ln.zone, ln.raw_role) for ln in lines} == {(c["zone"], c["role"])
                                                        for c in record["exercise_science"]["contributions"]}


def test_a_line_never_stores_a_credit():
    names = {f.name for f in dataclasses.fields(sx.LedgerLine)}
    assert "raw_role" in names
    assert not {n for n in names if "credit" in n}


def test_executed_name_rule_is_actual_exercise_name(db):
    s = _session(db, exercises=[("Pompes", "Pushdown corde", [WORK]), ("Pompes", None, [WORK])])
    for se in s.session_exercises:
        assert sx.executed_name(se) == actual_exercise_name(se)


def test_the_executed_name_is_the_substituted_one(db):
    _session(db, exercises=[("Pompes", "Pushdown corde", [WORK])])
    lines = _ledger(db)
    assert {ln.prescribed_name for ln in lines} == {"Pompes"}
    assert {ln.executed_name for ln in lines} == {"Pushdown corde"}
    assert {ln.scientific_identity_id for ln in lines} == {"cable_rope_triceps_pushdown"}


def test_lines_carry_their_provenance(db):
    _session(db, exercises=[("Pompes", None, [WORK])])
    version = load_catalogue().header["catalogue_version"]
    for ln in _ledger(db):
        assert ln.catalogue_version == version
        assert ln.role_basis
        assert ln.evidence_refs


def test_an_unknown_exercise_is_one_explicit_line_without_zone(db):
    _session(db, exercises=[("Mon exercice perso", None, [WORK, WORK])])
    lines = _ledger(db)
    assert len(lines) == 2
    assert all(ln.resolution.status == "UNKNOWN_IDENTITY" and ln.zone is None and ln.raw_role is None
               for ln in lines)


def test_the_ledger_is_deterministic(db):
    _session(db, days=1, exercises=[("Pompes", None, [WORK]), ("Roulette abdominale", None, [WORK])])
    _session(db, days=0, exercises=[("Face pull câble", None, [WORK, WORK])])
    first, second = _ledger(db), _ledger(db)
    assert first == second
    started = [ln.session_started_at for ln in first]
    assert started == sorted(started)


def test_building_the_ledger_writes_nothing(db):
    _session(db, exercises=[("Pompes", None, [WORK]), ("Mon exercice perso", None, [WORK])])
    counts = [db.scalar(select(func.count()).select_from(m)) for m in (WorkoutSession, SessionExercise, SetLog)]
    _ledger(db)
    assert not db.new
    assert not db.dirty
    assert not db.deleted
    assert counts == [db.scalar(select(func.count()).select_from(m)) for m in (WorkoutSession, SessionExercise, SetLog)]


# ── agrégat : crédit à la lecture, UNKNOWN jamais zéro, bornes


def _line(zone, role, *, set_id=1, status="RESOLVED", uncertain=False):
    res = si.IdentityResolution(status=status, query="x", step=None, variant_key=None,
                                scientific_identity_id=None, canonical_exercise_id=None,
                                catalogue_version="v", reason=None)
    return sx.LedgerLine(session_id=1, session_exercise_id=1, set_log_id=set_id, session_started_at=T0,
                         prescribed_name="x", executed_name="x", resolution=res, catalogue_version="v",
                         scientific_identity_id=None if zone is None else "i", zone=zone, raw_role=role,
                         role_basis=None if zone is None else "joint_action_anatomy",
                         evidence_refs=() if zone is None else ("EV-71",), execution_uncertain=uncertain)


def test_policy_v1_credits_are_applied_at_read_time():
    agg = sx.aggregate([_line("pecs", "PRIMARY", set_id=1), _line("pecs", "SECONDARY", set_id=2),
                        _line("pecs", "MINOR", set_id=3)])
    assert agg["pecs"].resolved_credit == 1.5
    assert (agg["pecs"].primary_sets, agg["pecs"].secondary_sets, agg["pecs"].minor_sets) == (1, 1, 1)
    assert agg["pecs"].bound == EXACT


def test_unknown_role_is_counted_apart_never_as_zero():
    agg = sx.aggregate([_line("triceps", "PRIMARY", set_id=1), _line("triceps", "UNKNOWN", set_id=2)])
    assert agg["triceps"].resolved_credit == 1.0
    assert agg["triceps"].unknown_sets == 1
    assert agg["triceps"].bound == MINIMUM
    assert agg["pecs"].bound == EXACT


def test_a_zone_known_only_as_unknown_is_not_declared_untrained():
    agg = sx.aggregate([_line("rear_delts", "UNKNOWN")])
    assert agg["rear_delts"].resolved_credit == 0.0
    assert agg["rear_delts"].bound == MINIMUM
    assert agg["rear_delts"].unknown_sets == 1


def test_an_unknown_identity_set_makes_every_zone_a_minimum():
    agg = sx.aggregate([_line("pecs", "PRIMARY", set_id=1), _line(None, None, set_id=2, status="UNKNOWN_IDENTITY")])
    assert set(agg) == set(sx.ZONES)
    assert all(z.bound == MINIMUM and z.unknown_identity_sets == 1 for z in agg.values())


def test_no_history_at_all_is_exact_zero_everywhere():
    agg = sx.aggregate([])
    assert len(sx.ZONES) == 15
    assert set(agg) == set(sx.ZONES)
    assert all(z.resolved_credit == 0.0 and z.bound == EXACT for z in agg.values())


def test_execution_uncertain_sets_block_exact_evidence():
    agg = sx.aggregate([_line("hip_flexors", "PRIMARY", uncertain=True)])
    assert agg["hip_flexors"].bound == EXACT
    assert agg["hip_flexors"].execution_uncertain_sets == 1
    assert agg["hip_flexors"].exact_evidence is False
    assert sx.aggregate([_line("hip_flexors", "PRIMARY")])["hip_flexors"].exact_evidence is True


def test_content_mismatch_records_produce_uncertain_lines(db):
    _session(db, exercises=[("Relevé de jambes suspendu", None, [WORK]), ("Pompes", None, [WORK])])
    lines = _ledger(db)
    assert {ln.execution_uncertain for ln in lines if ln.executed_name.startswith("Relevé")} == {True}
    assert {ln.execution_uncertain for ln in lines if ln.executed_name == "Pompes"} == {False}


def test_end_to_end_unknown_contribution_is_minimum_not_zero(db):
    """« Roulette abdominale » : triceps est UNKNOWN dans la fiche (vecteur incomplet)."""
    _session(db, exercises=[("Roulette abdominale", None, [WORK, WORK, WORK])])
    agg = sx.aggregate(_ledger(db))
    assert agg["abs"].resolved_credit == 3.0
    assert agg["abs"].primary_sets == 3
    assert agg["lats"].resolved_credit == 1.5
    assert agg["triceps"].resolved_credit == 0.0
    assert agg["triceps"].bound == MINIMUM


def test_an_unknown_policy_role_is_refused():
    lines = [_line("pecs", "HALF")]
    with pytest.raises(ValueError):
        sx.aggregate(lines)


# ── aucune consommation servie, aucun accès aux moteurs


SCI_RUNTIME = ("sci_catalogue", "sci_identity", "sci_exposure")


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    mods = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    mods |= {n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    mods |= {f"{n.module}.{a.name}" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) for a in n.names}
    return mods


def test_no_product_module_consumes_the_scientific_layer():
    offenders = []
    for path in sorted((ROOT / "app").rglob("*.py")):
        if path.stem in SCI_RUNTIME:
            continue
        if any(m.startswith(f"app.services.{s}") for m in _imports(path) for s in SCI_RUNTIME):
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


@pytest.mark.parametrize("stem", ["sci_identity", "sci_exposure"])
def test_the_scientific_layer_reaches_no_engine(stem):
    forbidden = ("app.services.recommendation", "app.services.advice_memory", "app.services.equipment_model",
                 "app.services.environment_", "app.services.muscle_scoring", "app.services.set_contribution",
                 "app.services.zone_exposure", "app.services.substitution", "app.routers", "app.templates")
    imported = _imports(ROOT / "app" / "services" / f"{stem}.py")
    assert not {m for m in imported for f in forbidden if m.startswith(f)}
