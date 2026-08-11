"""Sb_32.4 — formal BodyZone contract, reference seed, parity, one migration.

Three things are proven here.

1. **The seed is necessary and safe.** `init_db()` calls `create_all()`, which
   creates the reference tables EMPTY, after which the Alembic backfills — each
   guarded on "did I just create this table?" — can never fill them. Without an
   application-level seed the formal mapping would be an empty table and every
   lookup would silently degrade to substring matching.

2. **Parity is exhaustive and explained.** Legacy vs formal is compared over
   the complete canonical referential. Every divergence must be on the reviewed
   list, with its evidence; an unexplained one fails.

3. **Exactly one heavy consumer is migrated**, it genuinely reads the formal
   contract, and everything downstream of the untouched paths still behaves.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import func, select

from app.services.body_zone_source import (
    KNOWN_MAPPING_CORRECTIONS,
    PATH_CORRECTION,
    PATH_DB,
    PATH_SUBSTRING,
    PATH_UNKNOWN,
    ZoneResolution,
    build_parity_report,
    resolve_exercise_zones,
)
from app.services.muscle_mapping import (
    ZONE_LABELS,
    _classify_exercise_by_patterns,
)
from app.services.reference_data_seed import (
    SOURCE_MANUAL,
    canonical_exercise_referential,
    mapping_rows,
    seed_reference_data,
    zone_rows,
)
from tests.helpers import get_test_user_id

# ---------------------------------------------------------------------------
# Pure derivation — no DB
# ---------------------------------------------------------------------------


def test_zone_rows_derive_the_eleven_canonical_zones():
    rows = zone_rows()
    assert {r["code"] for r in rows} == set(ZONE_LABELS)
    by_code = {r["code"]: r for r in rows}
    assert by_code["pecs"]["radar_axis"] == "pecs"
    assert by_code["delt_post"]["radar_axis"] == "shoulders"
    assert by_code["calves"]["radar_axis"] == "lower"
    # `core` has no radar axis and must not be given a fabricated one.
    assert by_code["core"]["radar_axis"] is None


def test_referential_is_deterministic_and_sorted():
    first = canonical_exercise_referential()
    second = canonical_exercise_referential()
    assert first == second
    assert list(first) == sorted(first)
    assert len(first) == len(set(first))


def test_referential_excludes_metadata_keys():
    assert not any(name.startswith("_") for name in canonical_exercise_referential())


def test_mapping_rows_have_no_duplicate_unique_key():
    """(exercise_code, body_zone_code, role) is a UNIQUE constraint."""
    keys = [(r["exercise_code"], r["body_zone_code"], r["role"]) for r in mapping_rows()]
    assert len(keys) == len(set(keys))


def test_mapping_rows_never_invent_a_zone_for_an_unclassifiable_exercise():
    """Coverage is not padded: `unknown` is skipped, not guessed."""
    covered = {r["exercise_code"] for r in mapping_rows()}
    for name in canonical_exercise_referential():
        if _classify_exercise_by_patterns(name)[0] == "unknown":
            assert name not in covered, name


def test_mapping_rows_reference_only_real_body_zones():
    valid = set(ZONE_LABELS)
    for row in mapping_rows():
        assert row["body_zone_code"] in valid, row


def test_every_exercise_has_exactly_one_primary_row():
    primaries: dict[str, int] = {}
    for row in mapping_rows():
        if row["role"] == "primary":
            primaries[row["exercise_code"]] = primaries.get(row["exercise_code"], 0) + 1
    assert primaries
    assert set(primaries.values()) == {1}


# ---------------------------------------------------------------------------
# The reviewed correction list
# ---------------------------------------------------------------------------


def test_corrections_are_evidence_backed_and_actually_correct_something():
    assert KNOWN_MAPPING_CORRECTIONS
    for c in KNOWN_MAPPING_CORRECTIONS:
        assert c.primary != c.legacy_primary or c.secondary != c.legacy_secondary
        assert c.primary in ZONE_LABELS
        assert all(z in ZONE_LABELS for z in c.secondary)
        # Evidence must be substantive prose, not a placeholder.
        assert len(c.evidence) > 120, c.exercise_name


def test_each_correction_states_the_legacy_value_truthfully():
    """A correction that misquotes what it replaces is not reviewable."""
    for c in KNOWN_MAPPING_CORRECTIONS:
        legacy_primary, legacy_secondary = _classify_exercise_by_patterns(c.exercise_name)
        assert legacy_primary == c.legacy_primary, c.exercise_name
        assert tuple(legacy_secondary) == c.legacy_secondary, c.exercise_name


def test_the_two_known_wrong_mappings_are_the_ones_corrected():
    corrected = {c.exercise_name: c.primary for c in KNOWN_MAPPING_CORRECTIONS}
    assert corrected["Rear delt fly machine (pec deck inversé)"] == "delt_post"
    assert corrected["Relevé de jambes suspendu"] == "core"


def test_rear_delt_correction_matches_the_uncorrupted_sibling_name():
    """The bare name already classifies correctly — the parenthetical is the bug."""
    assert _classify_exercise_by_patterns("Rear delt fly machine")[0] == "delt_post"
    assert _classify_exercise_by_patterns(
        "Rear delt fly machine (pec deck inversé)")[0] == "pecs"


def test_hanging_leg_raise_siblings_are_all_core():
    """Its catalog session is 'Core / Abdos'; its siblings classify as core."""
    for sibling in ("Roulette abdominale (ab wheel rollout)",
                    "Crunch câble à genoux", "Pallof press câble"):
        assert _classify_exercise_by_patterns(sibling)[0] == "core", sibling


# ---------------------------------------------------------------------------
# The seed, against a real database
# ---------------------------------------------------------------------------


def _count(db, model):
    return db.execute(select(func.count()).select_from(model)).scalar()


def test_reference_tables_are_populated_after_a_normal_app_boot(client):
    """The whole reason this sprint needs a seed.

    Before Sb_32.4 these were 0/0 under the client fixture, because
    `create_all()` beats Alembic to the table creation.
    """
    from app.database import SessionLocal
    from app.models.body_zone import BodyZone
    from app.models.exercise_muscle_mapping import ExerciseMuscleMapping

    with SessionLocal() as db:
        assert _count(db, BodyZone) == len(ZONE_LABELS)
        assert _count(db, ExerciseMuscleMapping) == len(mapping_rows())


def test_seed_is_idempotent_on_an_already_populated_database(client):
    from app.database import SessionLocal
    from app.models.body_zone import BodyZone
    from app.models.exercise_muscle_mapping import ExerciseMuscleMapping

    with SessionLocal() as db:
        before = (_count(db, BodyZone), _count(db, ExerciseMuscleMapping))
        first = seed_reference_data(db)
        second = seed_reference_data(db)
        after = (_count(db, BodyZone), _count(db, ExerciseMuscleMapping))

    assert after == before
    assert first == {"zones_inserted": 0, "mappings_inserted": 0, "corrections_applied": 0}
    assert second == first


def test_seed_fills_empty_reference_tables(client):
    """Wipe the reference tables only, re-seed, and get the same state back."""
    from app.database import SessionLocal
    from app.models.body_zone import BodyZone
    from app.models.exercise_muscle_mapping import ExerciseMuscleMapping

    with SessionLocal() as db:
        db.query(ExerciseMuscleMapping).delete()
        db.query(BodyZone).delete()
        db.commit()
        assert _count(db, BodyZone) == 0

        stats = seed_reference_data(db)
        assert stats["zones_inserted"] == len(ZONE_LABELS)
        assert stats["mappings_inserted"] == len(mapping_rows())
        assert _count(db, ExerciseMuscleMapping) == len(mapping_rows())


def test_seed_repairs_a_known_wrong_row_left_by_the_alembic_backfill(client):
    """Production databases carry the migration's bug-for-bug rows.

    Insert-only would leave them wrong forever, so the reviewed corrections are
    reconciled. The stale attribution is deactivated, not deleted, so the table
    stays auditable.
    """
    from app.database import SessionLocal
    from app.models.exercise_muscle_mapping import ExerciseMuscleMapping

    name = "Rear delt fly machine (pec deck inversé)"
    with SessionLocal() as db:
        db.query(ExerciseMuscleMapping).filter(
            ExerciseMuscleMapping.exercise_code == name).delete()
        db.add(ExerciseMuscleMapping(
            exercise_code=name, body_zone_code="pecs", role="primary",
            source="baseline", position=0, is_active=True))
        db.add(ExerciseMuscleMapping(
            exercise_code=name, body_zone_code="triceps", role="secondary",
            source="baseline", position=1, is_active=True))
        db.commit()
        assert resolve_exercise_zones(db, name).primary == "delt_post"  # correction wins

        seed_reference_data(db)

        rows = db.query(ExerciseMuscleMapping).filter(
            ExerciseMuscleMapping.exercise_code == name).all()
        active = {(r.body_zone_code, r.role) for r in rows if r.is_active}
        assert active == {("delt_post", "primary")}
        # The wrong rows survive as deactivated history, not as deletions.
        assert {(r.body_zone_code, r.role) for r in rows if not r.is_active} == {
            ("pecs", "primary"), ("triceps", "secondary")}
        assert all(r.source == SOURCE_MANUAL for r in rows)


def test_seed_marks_corrections_with_manual_provenance(client):
    from app.database import SessionLocal
    from app.models.exercise_muscle_mapping import ExerciseMuscleMapping

    with SessionLocal() as db:
        for c in KNOWN_MAPPING_CORRECTIONS:
            rows = db.query(ExerciseMuscleMapping).filter(
                ExerciseMuscleMapping.exercise_code == c.exercise_name,
                ExerciseMuscleMapping.is_active.is_(True)).all()
            assert rows, c.exercise_name
            assert all(r.source == SOURCE_MANUAL for r in rows), c.exercise_name


# ---------------------------------------------------------------------------
# Wipe guards — the seed must be incapable of touching owned data
# ---------------------------------------------------------------------------


def _seed_user_data(db, uid):
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    s = WorkoutSession(
        user_id=uid, template_slug_snapshot="push-a",
        template_name_snapshot="Push A",
        started_at=datetime.now(UTC) - timedelta(days=1), status="completed")
    se = SessionExercise(exercise_code_snapshot="E1",
                         exercise_name_snapshot="Développé couché barre", position=1)
    se.set_logs.append(SetLog(kind="work", set_index=1, weight_kg=60.0,
                              reps=10, completed=True))
    s.session_exercises.append(se)
    db.add(s)
    db.commit()
    return s.id


def test_seed_never_touches_user_owned_rows(client):
    """Sessions, exercises, set logs and users survive a re-seed untouched."""
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession
    from app.models.user import User

    uid = get_test_user_id()
    with SessionLocal() as db:
        _seed_user_data(db, uid)
        before = {m.__name__: _count(db, m)
                  for m in (User, WorkoutSession, SessionExercise, SetLog)}
        assert before["WorkoutSession"] >= 1

        seed_reference_data(db)

        after = {m.__name__: _count(db, m)
                 for m in (User, WorkoutSession, SessionExercise, SetLog)}
    assert after == before


def test_seed_never_touches_custom_programs(client):
    from app.database import SessionLocal
    from app.models.user_program import UserProgram

    uid = get_test_user_id()
    with SessionLocal() as db:
        db.add(UserProgram(user_id=uid, title="Mon programme",
                           slug_base="mon-programme", status="draft"))
        db.commit()
        before = _count(db, UserProgram)
        seed_reference_data(db)
        after = _count(db, UserProgram)
        survivor = db.query(UserProgram).filter(
            UserProgram.slug_base == "mon-programme").one()

    assert after == before == 1
    assert survivor.status == "draft"


def test_seed_writes_only_the_two_reference_tables():
    """Source-level guard: no owned model is reachable from the seed."""
    from pathlib import Path

    import app.services.reference_data_seed as seed_mod

    source = Path(seed_mod.__file__).read_text(encoding="utf-8")
    for forbidden in ("WorkoutSession", "SessionExercise", "SetLog", "User",
                      "UserProgram", "WorkoutTemplate", "BodyMeasurement",
                      "delete(", "DELETE", "TRUNCATE", "drop"):
        assert forbidden not in source, forbidden


# ---------------------------------------------------------------------------
# The adapter contract
# ---------------------------------------------------------------------------


def test_a_referential_exercise_resolves_through_the_formal_mapping(client):
    from app.database import SessionLocal

    names = [n for n in canonical_exercise_referential()
             if _classify_exercise_by_patterns(n)[0] != "unknown"
             and n not in {c.exercise_name for c in KNOWN_MAPPING_CORRECTIONS}]
    assert names
    with SessionLocal() as db:
        resolved = resolve_exercise_zones(db, names[0])
    assert resolved.resolution_path == PATH_DB
    assert resolved.from_formal_mapping


def test_corrections_take_precedence_over_the_stored_row(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        for c in KNOWN_MAPPING_CORRECTIONS:
            resolved = resolve_exercise_zones(db, c.exercise_name)
            assert resolved.resolution_path == PATH_CORRECTION
            assert resolved.primary == c.primary
            assert resolved.secondary == c.secondary


def test_uncovered_name_falls_back_without_pretending_it_was_formal(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        resolved = resolve_exercise_zones(db, "Développé couché haltères maison")
    assert resolved.resolution_path == PATH_SUBSTRING
    assert resolved.from_formal_mapping is False
    assert resolved.primary == "pecs"


def test_unclassifiable_name_is_unknown_not_guessed(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        resolved = resolve_exercise_zones(db, "Zzz machine totalement inconnue")
    assert resolved.primary == "unknown"
    assert resolved.resolution_path == PATH_UNKNOWN
    assert resolved.is_known is False


@pytest.mark.parametrize("bad", ["", "   ", None])
def test_empty_name_is_unknown(bad):
    resolved = resolve_exercise_zones(None, bad)
    assert resolved.primary == "unknown"


def test_adapter_without_a_session_degrades_to_substring():
    """Pure callers must not crash; the path says how the answer was obtained."""
    resolved = resolve_exercise_zones(None, "Traction pronation")
    assert resolved.primary == "lats"
    assert resolved.resolution_path == PATH_SUBSTRING


def test_legacy_tuple_shape_is_drop_in_compatible():
    resolved = ZoneResolution(primary="pecs", secondary=("triceps",))
    primary, secondary = resolved.as_legacy_tuple()
    assert primary == "pecs"
    assert secondary == ["triceps"]
    assert isinstance(secondary, list)


def test_adapter_reuses_the_existing_lookup_rather_than_a_second_query(client, monkeypatch):
    """Sb_32.4: "Do NOT duplicate DB query logic across consumers".

    Proven behaviourally rather than by grepping for a string: the adapter must
    delegate to ``muscle_mapping._classify_exercise_by_lookup``. If someone
    writes a private second query here, this spy stops being called.
    """
    from app.database import SessionLocal
    from app.services import body_zone_source as mod

    calls: list[str] = []
    real = mod._classify_exercise_by_lookup

    def spy(db, exercise_code):
        calls.append(exercise_code)
        return real(db, exercise_code)

    monkeypatch.setattr(mod, "_classify_exercise_by_lookup", spy)

    corrected = {c.exercise_name for c in KNOWN_MAPPING_CORRECTIONS}
    name = next(n for n in canonical_exercise_referential()
                if n not in corrected
                and _classify_exercise_by_patterns(n)[0] != "unknown")
    with SessionLocal() as db:
        resolved = mod.resolve_exercise_zones(db, name)

    assert calls == [name]
    assert resolved.resolution_path == mod.PATH_DB


# ---------------------------------------------------------------------------
# Parity over the complete canonical referential
# ---------------------------------------------------------------------------


def test_parity_over_the_complete_referential_has_no_unexplained_divergence(client):
    from app.database import SessionLocal

    names = list(canonical_exercise_referential())
    with SessionLocal() as db:
        report = build_parity_report(db, names)

    print("\n".join(report.as_lines()))
    assert report.total == len(names)
    assert report.unexplained_divergences == []
    assert report.is_clean
    # Every divergence is a reviewed correction, and all of them are exercised.
    assert set(report.intentional_divergences) == {
        c.exercise_name for c in KNOWN_MAPPING_CORRECTIONS}
    assert report.exact_matches + len(report.intentional_divergences) == report.total


def test_parity_reports_the_only_uncovered_names(client):
    """Two English incline-press variants the French pattern list cannot place.

    They are reported as missing rather than mapped: inventing a zone to make
    coverage look complete is exactly what Sb_32.4 forbids.
    """
    from app.database import SessionLocal

    with SessionLocal() as db:
        report = build_parity_report(db, list(canonical_exercise_referential()))

    assert set(report.missing_formal_mapping) == {
        "Incline DB Press 30°", "Incline Dumbbell Press"}
    for name in report.missing_formal_mapping:
        assert _classify_exercise_by_patterns(name)[0] == "unknown"


def test_ambiguous_mapping_is_detected(client):
    """Two active primary rows for one exercise is a data fault, not a choice.

    The unique key is (exercise_code, body_zone_code, role), so two *different*
    zones can both sit as `primary`. The lookup would then pick whichever sorts
    first — stable, but arbitrary.
    """
    from app.database import SessionLocal
    from app.models.exercise_muscle_mapping import ExerciseMuscleMapping
    from app.services.body_zone_source import (
        build_parity_report as build,
    )
    from app.services.body_zone_source import (
        find_ambiguous_mappings as find,
    )

    name = "Traction assistée machine"  # really in the referential, so already seeded
    with SessionLocal() as db:
        assert find(db, [name]) == []
        db.add(ExerciseMuscleMapping(
            exercise_code=name, body_zone_code="upper_back", role="primary",
            source="manual", position=9, is_active=True))
        db.commit()
        assert find(db, [name]) == [name]
        report = build(db, [name])

    assert report.ambiguous_mappings == [name]
    assert report.is_clean is False


def test_a_correction_that_no_longer_matches_is_reported_unexplained(client, monkeypatch):
    """The parity harness must not rubber-stamp a stale correction entry.

    A correction whose `legacy_*` no longer describes what the classifier
    actually returns has silently stopped being reviewable — it must surface as
    unexplained, which is a HARD STOP, rather than pass as "intentional".
    """
    from app.database import SessionLocal
    from app.services import body_zone_source as mod

    name = "Traction assistée machine"
    stale = mod.ZoneCorrection(
        exercise_name=name, legacy_primary="quads", legacy_secondary=(),
        primary="calves", secondary=(),
        evidence="deliberately wrong entry used only to prove the harness bites",
    )
    monkeypatch.setitem(mod._CORRECTIONS_BY_NAME, name, stale)

    with SessionLocal() as db:
        report = mod.build_parity_report(db, [name])

    assert report.unexplained_divergences == [name]
    assert report.is_clean is False


# ---------------------------------------------------------------------------
# The migrated consumer
# ---------------------------------------------------------------------------


def test_migrated_consumer_reads_the_formal_contract(client, monkeypatch):
    """`muscle_scoring` must actually go through the adapter, not around it."""
    from app.database import SessionLocal
    from app.services import muscle_scoring

    seen: list[str] = []
    real = muscle_scoring.resolve_exercise_zones

    def spy(db, name):
        seen.append(name)
        return real(db, name)

    monkeypatch.setattr(muscle_scoring, "resolve_exercise_zones", spy)

    uid = get_test_user_id()
    with SessionLocal() as db:
        _seed_user_data(db, uid)
        muscle_scoring.compute_physique_dashboard(db, uid)

    assert "Développé couché barre" in seen


def test_migrated_consumer_resolves_each_distinct_name_once(client, monkeypatch):
    """No N+1: the formal path costs a query, the loop runs per set exercise.

    Six set exercises across three sessions, two distinct names. Before the
    per-invocation cache this issued six lookups in the root scoring primitive;
    it must issue two.
    """
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession
    from app.services import muscle_scoring

    calls: list[str] = []
    real = muscle_scoring.resolve_exercise_zones

    def spy(db, name):
        calls.append(name)
        return real(db, name)

    monkeypatch.setattr(muscle_scoring, "resolve_exercise_zones", spy)

    uid = get_test_user_id()
    with SessionLocal() as db:
        for day in (1, 2, 3):
            s = WorkoutSession(
                user_id=uid, template_slug_snapshot="push-a",
                template_name_snapshot="Push A",
                started_at=datetime.now(UTC) - timedelta(days=day),
                status="completed")
            for i, name in enumerate(("Hack squat", "Curl incliné haltères"), start=1):
                se = SessionExercise(exercise_code_snapshot=f"E{i}",
                                     exercise_name_snapshot=name, position=i)
                se.set_logs.append(SetLog(kind="work", set_index=1, weight_kg=40.0,
                                          reps=10, completed=True))
                s.session_exercises.append(se)
            db.add(s)
        db.commit()

        muscle_scoring.compute_physique_dashboard(db, uid)

    # 3 sessions × 2 exercises = 6 set exercises, but only 2 distinct names.
    assert len(calls) == 2, f"expected one resolution per distinct name, got {calls}"
    assert sorted(set(calls)) == ["Curl incliné haltères", "Hack squat"]


def test_migrated_consumer_applies_the_correction_end_to_end(client):
    """A rear-delt machine must now score shoulders, not chest."""
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession
    from app.services import muscle_scoring

    uid = get_test_user_id()
    with SessionLocal() as db:
        s = WorkoutSession(
            user_id=uid, template_slug_snapshot="pull-a",
            template_name_snapshot="Pull A",
            started_at=datetime.now(UTC) - timedelta(days=1), status="completed")
        se = SessionExercise(
            exercise_code_snapshot="E5",
            exercise_name_snapshot="Rear delt fly machine (pec deck inversé)",
            position=1)
        se.set_logs.append(SetLog(kind="work", set_index=1, weight_kg=30.0,
                                  reps=12, completed=True))
        s.session_exercises.append(se)
        db.add(s)
        db.commit()

        dash = muscle_scoring.compute_physique_dashboard(db, uid)

    by_zone = {z.zone: z for z in dash.zone_scores}
    assert by_zone["delt_post"].hard_sets == 1
    # The legacy attribution (pecs primary, triceps secondary) must be gone.
    assert by_zone["pecs"].hard_sets == 0
    assert by_zone["triceps"].hard_sets == 0


def test_migrated_consumer_still_honours_substituted_name(client):
    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog, WorkoutSession
    from app.services import muscle_scoring

    uid = get_test_user_id()
    with SessionLocal() as db:
        s = WorkoutSession(
            user_id=uid, template_slug_snapshot="push-a",
            template_name_snapshot="Push A",
            started_at=datetime.now(UTC) - timedelta(days=1), status="completed")
        se = SessionExercise(
            exercise_code_snapshot="E1",
            exercise_name_snapshot="Développé couché barre",
            substituted_name="Hack squat", position=1)
        se.set_logs.append(SetLog(kind="work", set_index=1, weight_kg=100.0,
                                  reps=8, completed=True))
        s.session_exercises.append(se)
        db.add(s)
        db.commit()

        dash = muscle_scoring.compute_physique_dashboard(db, uid)

    by_zone = {z.zone: z for z in dash.zone_scores}
    assert by_zone["quads"].hard_sets == 1
    assert by_zone["pecs"].hard_sets == 0


def test_body_map_descriptor_is_not_routed_through_the_adapter():
    """Sb_32.4 explicitly must not rebuild the existing narrow DB path."""
    from pathlib import Path

    import app.services.body_map_descriptor as mod

    assert "body_zone_source" not in Path(mod.__file__).read_text(encoding="utf-8")
