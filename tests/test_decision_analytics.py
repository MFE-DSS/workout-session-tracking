"""Sb_DECISION_ANALYTICS_RUNTIME_01 — observer sans jamais décider.

Le test central de ce fichier n'est pas qu'une trace soit écrite : c'est que
**retirer entièrement le collecteur ne change aucune sortie produit**. Tout le
reste — taxonomie, arêtes, immuabilité — protège la qualité de la preuve ; ce
test-là protège le produit.
"""
from __future__ import annotations

import json

import pytest

# Comme les tranches morpho : la fixture `client` purge `sys.modules`, donc
# aucun import `app.*` au niveau module.

PROGRAMS_URL = "/programs"
MATERIALIZE_URL = "/programs/from-weekly-plan"


@pytest.fixture(autouse=True)
def _app_db(client):
    return client


def _session():
    from app.database import SessionLocal

    return SessionLocal()


def _uid():
    from tests.helpers import get_test_user_id

    return get_test_user_id()


def _prefs(cadence=4, focus=("arms",), equipment=None):
    from app.services.training_preferences import TrainingPreferencesData

    return TrainingPreferencesData(
        sessions_per_week=cadence,
        focus_priorities=tuple(focus),
        available_equipment=tuple(equipment) if equipment else None,
    )


def _budget_and_plan(prefs=None):
    from app.services.weekly_planner import build_weekly_plan
    from app.services.weekly_volume_budget import build_weekly_volume_budget

    prefs = prefs or _prefs()
    budget = build_weekly_volume_budget(prefs)
    return budget, build_weekly_plan(prefs, budget=budget), prefs


def _save_prefs(db, uid, cadence=4, focus=("arms",), equipment=None):
    from app.services.training_preferences import save_training_preferences

    save_training_preferences(
        db, uid, sessions_per_week=cadence,
        focus_priorities=list(focus),
        available_equipment=list(equipment) if equipment else None,
    )


def _all_traces(db, uid):
    from sqlalchemy import select

    from app.models.decision_trace import DecisionTrace

    return list(db.execute(
        select(DecisionTrace).where(DecisionTrace.user_id == uid)
        .order_by(DecisionTrace.id)
    ).scalars().all())


# ── Un groupe pour une génération ────────────────────────────────────────────


def test_one_plan_generation_yields_one_trace_group():
    from app.services.decision_analytics import observe_plan_generation

    budget, plan, prefs = _budget_and_plan()
    with _session() as db:
        uid = _uid()
        group = observe_plan_generation(db, uid, budget, plan, prefs)
        rows = _all_traces(db, uid)

    assert group
    assert rows
    assert {r.trace_group_id for r in rows} == {group}


def test_the_expected_decision_types_are_present():
    from app.services.decision_analytics import (
        CONTRIBUTION_CREDIT,
        SET_PRESCRIPTION,
        SLOT_SELECTION,
        VOLUME_BAND,
        ZONE_ALLOCATION,
        observe_plan_generation,
    )

    budget, plan, prefs = _budget_and_plan()
    with _session() as db:
        uid = _uid()
        observe_plan_generation(db, uid, budget, plan, prefs)
        kinds = {r.decision_type for r in _all_traces(db, uid)}

    assert {VOLUME_BAND, ZONE_ALLOCATION, SLOT_SELECTION,
            SET_PRESCRIPTION, CONTRIBUTION_CREDIT} <= kinds


def test_morphology_descriptors_are_not_persisted_in_v1():
    """The planner does not consume them; a trace would prove nothing."""
    from app.services.decision_analytics import observe_plan_generation

    budget, plan, prefs = _budget_and_plan()
    with _session() as db:
        uid = _uid()
        observe_plan_generation(db, uid, budget, plan, prefs)
        kinds = {r.decision_type for r in _all_traces(db, uid)}
    assert "MORPHOLOGY_DESCRIPTOR" not in kinds


def test_contribution_credit_is_aggregated_per_zone_not_per_set():
    from app.services.decision_analytics import (
        CONTRIBUTION_CREDIT,
        observe_plan_generation,
    )

    budget, plan, prefs = _budget_and_plan()
    with _session() as db:
        uid = _uid()
        observe_plan_generation(db, uid, budget, plan, prefs)
        credits = [r for r in _all_traces(db, uid)
                   if r.decision_type == CONTRIBUTION_CREDIT]

    zones = [json.loads(r.selected_output)["zone_code"] for r in credits]
    assert len(zones) == len(set(zones))          # one per zone
    physical_sets = sum(p.planned_sets for p in plan.prescriptions)
    assert len(credits) < physical_sets           # never one per set


# ── Identité vs empreinte ────────────────────────────────────────────────────


def test_the_fingerprint_is_deterministic_across_executions():
    from app.services.decision_analytics import observe_plan_generation

    budget, plan, prefs = _budget_and_plan()
    with _session() as db:
        uid = _uid()
        g1 = observe_plan_generation(db, uid, budget, plan, prefs)
        g2 = observe_plan_generation(db, uid, budget, plan, prefs)
        rows = _all_traces(db, uid)

    first = [r for r in rows if r.trace_group_id == g1]
    second = [r for r in rows if r.trace_group_id == g2]

    assert [r.decision_fingerprint for r in first] == \
        [r.decision_fingerprint for r in second]
    # Same content, different historical events.
    assert not ({r.decision_id for r in first} & {r.decision_id for r in second})


def test_the_fingerprint_ignores_creation_time():
    import inspect

    from app.services.decision_analytics import (
        PRODUCT_POLICY,
        VOLUME_BAND,
        DraftTrace,
        SourceRef,
        decision_fingerprint,
    )

    def _make():
        return DraftTrace(
            decision_type=VOLUME_BAND, policy_version="weekly-volume-v1",
            selected_output={"zone_code": "pecs"}, basis=("x",),
            sources=(SourceRef(PRODUCT_POLICY, "p", None),),
        )

    # Two independently built drafts with identical content.
    first = decision_fingerprint(_make(), ())
    second = decision_fingerprint(_make(), ())
    assert first == second

    # Structural: a timestamp is not even reachable from this function — it
    # takes no clock argument and its body never reads one.
    params = set(inspect.signature(decision_fingerprint).parameters)
    assert params == {"draft", "upstream_fingerprints"}
    body = inspect.getsource(decision_fingerprint).split('"""')[2]
    for banned in ("created_at", "datetime", "now(", "time."):
        assert banned not in body


def test_a_different_output_changes_the_fingerprint():
    from app.services.decision_analytics import (
        VOLUME_BAND,
        DraftTrace,
        decision_fingerprint,
    )

    a = DraftTrace(decision_type=VOLUME_BAND, policy_version="v1",
                   selected_output={"planning_low_sets": 10})
    b = DraftTrace(decision_type=VOLUME_BAND, policy_version="v1",
                   selected_output={"planning_low_sets": 12})
    assert decision_fingerprint(a, ()) != decision_fingerprint(b, ())


# ── Taxonomie des sources ────────────────────────────────────────────────────


def test_source_classes_stay_separate_in_storage():
    from app.services.decision_analytics import VOLUME_BAND, observe_plan_generation

    budget, plan, prefs = _budget_and_plan()
    with _session() as db:
        uid = _uid()
        observe_plan_generation(db, uid, budget, plan, prefs)
        bands = [r for r in _all_traces(db, uid) if r.decision_type == VOLUME_BAND]

    row = bands[0]
    prefs_payload = json.loads(row.preference_sources)
    constraints = json.loads(row.constraint_sources)
    # A declared priority must never be filed as a product policy.
    assert all(s["kind"] == "USER_DECLARED" for s in prefs_payload)
    assert all(s["kind"] != "USER_DECLARED" for s in constraints)


def test_no_single_flattened_reason_column_exists():
    from app.models.decision_trace import DecisionTrace

    cols = set(DecisionTrace.__table__.columns.keys())
    for banned in ("reason", "ai_reason", "context", "explanation"):
        assert banned not in cols
    assert {"constraint_sources", "preference_sources",
            "morphology_sources", "recovery_sources"} <= cols


def test_the_basis_is_cited_verbatim_never_reworded():
    """The trace quotes the engine; it does not paraphrase it."""
    from app.services.decision_analytics import (
        VOLUME_BAND,
        ZONE_ALLOCATION,
        observe_plan_generation,
    )

    budget, plan, prefs = _budget_and_plan()
    with _session() as db:
        uid = _uid()
        observe_plan_generation(db, uid, budget, plan, prefs)
        rows = _all_traces(db, uid)

    engine_band_basis = {z.zone_code: list(z.basis) for z in budget.zones}
    engine_alloc_basis = {c.zone_code: list(c.allocation_basis)
                          for c in plan.zone_coverage}

    checked = 0
    for r in rows:
        zone = json.loads(r.selected_output).get("zone_code")
        if r.decision_type == VOLUME_BAND and zone in engine_band_basis:
            assert json.loads(r.basis) == engine_band_basis[zone]
            checked += 1
        if r.decision_type == ZONE_ALLOCATION and zone in engine_alloc_basis:
            assert json.loads(r.basis) == engine_alloc_basis[zone]
            checked += 1
    assert checked, "no basis compared — the guard would be vacuous"


def test_the_taxonomy_guard_names_the_rule():
    from app.services.decision_analytics import SOURCE_TAXONOMY_GUARD

    low = SOURCE_TAXONOMY_GUARD.lower()
    assert "unclassified" in low
    assert "distinctes" in low


# ── Arêtes amont ─────────────────────────────────────────────────────────────


def test_the_upstream_graph_follows_real_dataflow():
    from app.services.decision_analytics import (
        SET_PRESCRIPTION,
        SLOT_SELECTION,
        VOLUME_BAND,
        ZONE_ALLOCATION,
        observe_plan_generation,
    )

    budget, plan, prefs = _budget_and_plan()
    with _session() as db:
        uid = _uid()
        observe_plan_generation(db, uid, budget, plan, prefs)
        rows = _all_traces(db, uid)

    by_id = {r.decision_id: r for r in rows}

    def parents(row):
        return [by_id[i] for i in json.loads(row.upstream_decision_ids)]

    for r in rows:
        if r.decision_type == ZONE_ALLOCATION:
            assert all(p.decision_type == VOLUME_BAND for p in parents(r))
        if r.decision_type == SLOT_SELECTION:
            assert all(p.decision_type == ZONE_ALLOCATION for p in parents(r))
        if r.decision_type == SET_PRESCRIPTION:
            assert all(p.decision_type == SLOT_SELECTION for p in parents(r))


def test_a_volume_band_has_no_upstream():
    from app.services.decision_analytics import VOLUME_BAND, observe_plan_generation

    budget, plan, prefs = _budget_and_plan()
    with _session() as db:
        uid = _uid()
        observe_plan_generation(db, uid, budget, plan, prefs)
        bands = [r for r in _all_traces(db, uid) if r.decision_type == VOLUME_BAND]
    assert all(json.loads(r.upstream_decision_ids) == [] for r in bands)


def test_edges_link_the_same_zone_not_merely_similar_decisions():
    from app.services.decision_analytics import (
        VOLUME_BAND,
        ZONE_ALLOCATION,
        observe_plan_generation,
    )

    budget, plan, prefs = _budget_and_plan()
    with _session() as db:
        uid = _uid()
        observe_plan_generation(db, uid, budget, plan, prefs)
        rows = _all_traces(db, uid)

    by_id = {r.decision_id: r for r in rows}
    for r in rows:
        if r.decision_type != ZONE_ALLOCATION:
            continue
        zone = json.loads(r.selected_output)["zone_code"]
        for pid in json.loads(r.upstream_decision_ids):
            parent = by_id[pid]
            assert parent.decision_type == VOLUME_BAND
            assert json.loads(parent.selected_output)["zone_code"] == zone


# ── Alternatives rejetées ────────────────────────────────────────────────────


def test_rejected_alternatives_are_empty_when_the_engine_never_ranked_any():
    from app.services.decision_analytics import observe_plan_generation

    budget, plan, prefs = _budget_and_plan()
    with _session() as db:
        uid = _uid()
        observe_plan_generation(db, uid, budget, plan, prefs)
        rows = _all_traces(db, uid)

    assert rows
    assert all(json.loads(r.rejected_alternatives) == [] for r in rows)


def test_the_collector_never_reconstructs_alternatives_from_the_catalog():
    """An empty list is the honest answer; a plausible list would be invented."""
    import inspect

    import app.services.decision_analytics as da

    src = inspect.getsource(da)
    for banned in ("planner_candidate_pool", "generate_program",
                   "substitution", "_rank_zone"):
        assert banned not in src


# ── Retirabilité — LA preuve centrale ────────────────────────────────────────


def test_disabling_the_collector_changes_no_business_output():
    """WITH collector vs collector entirely disabled → identical everything."""
    from app.services.adaptive_replan import replan
    from app.services.decision_analytics import observe_plan_generation
    from app.services.morphology_profile import (
        MorphologyFacts,
        build_morphology_profile,
    )
    from app.services.set_contribution import contributions_for
    from app.services.weekly_plan_materialization import assess_materialization
    from app.services.weekly_planner import build_weekly_plan
    from app.services.weekly_volume_budget import build_weekly_volume_budget

    prefs = _prefs()

    def snapshot():
        budget = build_weekly_volume_budget(prefs)
        plan = build_weekly_plan(prefs, budget=budget)
        facts = MorphologyFacts(height_cm=180.0, wingspan_cm=186.0,
                                waist_cm=78.0, chest_cm=104.0)
        return {
            "budget": [(z.zone_code, z.planning_low_sets, z.baseline_sets,
                        z.planning_high_sets) for z in budget.zones],
            "fingerprint": plan.fingerprint,
            "prescriptions": [(p.slot_id, p.exercise_name, p.planned_sets,
                               p.min_reps, p.max_reps) for p in plan.prescriptions],
            "contributions": sorted(
                (k, v.direct_sets, v.indirect_sets)
                for k, v in contributions_for(plan.prescriptions).items()),
            "replan": str(replan(plan, completed_sessions=1)),
            "materialization": str(assess_materialization(plan).status),
            "morphology": [d.descriptor_id for d in build_morphology_profile(facts)],
        }, budget, plan

    without, _, _ = snapshot()

    with_, budget, plan = snapshot()
    with _session() as db:
        uid = _uid()
        group = observe_plan_generation(db, uid, budget, plan, prefs)
        rows = _all_traces(db, uid)

    # The collector really ran — otherwise this proves nothing.
    assert group
    assert rows

    after, _, _ = snapshot()
    assert without == with_ == after


def test_observation_does_not_mutate_the_persisted_decision_inputs():
    """The DB-round-trip half of removability.

    The test above builds plans from in-memory preferences, so a collector that
    quietly rewrote *persisted* inputs — cadence, priorities, equipment — would
    slip through it entirely. This one plans through the database on both sides.
    """
    from app.services.decision_analytics import observe_plan_generation_for_user
    from app.services.training_preferences import get_training_preferences
    from app.services.weekly_planner import build_weekly_plan_for_user

    with _session() as db:
        uid = _uid()
        _save_prefs(db, uid, cadence=4, focus=("arms",))

        before_prefs = get_training_preferences(db, uid)
        before = build_weekly_plan_for_user(db, uid)

        group = observe_plan_generation_for_user(db, uid, before)

        after_prefs = get_training_preferences(db, uid)
        after = build_weekly_plan_for_user(db, uid)

    assert group, "collector did not run — the guard would be vacuous"
    assert after.fingerprint == before.fingerprint
    assert after_prefs.sessions_per_week == before_prefs.sessions_per_week
    assert after_prefs.focus_priorities == before_prefs.focus_priorities
    assert after_prefs.available_equipment == before_prefs.available_equipment


def test_recommendation_parity_is_untouched_by_the_collector():
    from app.services.decision_analytics import observe_plan_generation

    budget, plan, prefs = _budget_and_plan()
    import app.services.recommendation as reco

    before = sorted(n for n in dir(reco) if not n.startswith("_"))
    with _session() as db:
        observe_plan_generation(db, _uid(), budget, plan, prefs)
    assert sorted(n for n in dir(reco) if not n.startswith("_")) == before


def test_no_pure_engine_gained_a_db_or_user_dependency():
    import inspect

    from app.services.morphology_profile import build_morphology_profile
    from app.services.set_contribution import contributions_for
    from app.services.weekly_planner import build_weekly_plan
    from app.services.weekly_volume_budget import build_weekly_volume_budget

    for fn, expected in (
        (build_weekly_plan, {"preferences", "budget", "pool"}),
        (build_weekly_volume_budget, {"preferences"}),
        (build_morphology_profile, {"facts"}),
        (contributions_for, {"prescriptions"}),
    ):
        params = set(inspect.signature(fn).parameters)
        assert params == expected, fn.__name__
        assert "db" not in params
        assert "user_id" not in params


# ── Isolation des pannes ─────────────────────────────────────────────────────


def test_a_collector_failure_leaves_the_product_result_intact(monkeypatch):
    import app.services.decision_analytics as da

    def _boom(*_a, **_k):
        raise RuntimeError("trace storage exploded")

    monkeypatch.setattr(da, "persist_traces", _boom)

    budget, plan, prefs = _budget_and_plan()
    fingerprint_before = plan.fingerprint

    with _session() as db:
        group = da.observe_plan_generation(db, _uid(), budget, plan, prefs)

    # No fake success, and the plan is untouched.
    assert group is None
    assert plan.fingerprint == fingerprint_before


def test_a_collector_failure_does_not_break_materialization(client, monkeypatch):
    import app.services.decision_analytics as da

    monkeypatch.setattr(
        da, "observe_plan_generation_for_user",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    with _session() as db:
        _save_prefs(db, _uid())

    # The route must still create the draft even if observation explodes.
    r = client.post(MATERIALIZE_URL, follow_redirects=False)
    assert r.status_code in (303, 200)


def test_the_observer_never_substitutes_a_fake_success(monkeypatch):
    import app.services.decision_analytics as da

    monkeypatch.setattr(da, "persist_traces",
                        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("x")))
    budget, plan, prefs = _budget_and_plan()
    with _session() as db:
        assert da.observe_plan_generation(db, _uid(), budget, plan, prefs) is None


# ── Immuabilité ──────────────────────────────────────────────────────────────


def test_a_persisted_trace_cannot_be_updated():
    from app.models.decision_trace import DecisionTraceImmutableError
    from app.services.decision_analytics import observe_plan_generation

    budget, plan, prefs = _budget_and_plan()
    with _session() as db:
        uid = _uid()
        observe_plan_generation(db, uid, budget, plan, prefs)
        row = _all_traces(db, uid)[0]
        row.basis = json.dumps(["rewritten history"])
        with pytest.raises(DecisionTraceImmutableError):
            db.commit()
        db.rollback()


def test_no_public_update_or_recalculate_service_exists():
    import app.services.decision_analytics as da

    for banned in ("update_trace", "recalculate_traces", "rewrite_trace",
                   "refresh_traces"):
        assert not hasattr(da, banned)


def test_a_new_calculation_writes_new_rows_rather_than_editing_old_ones():
    from app.services.decision_analytics import observe_plan_generation

    budget, plan, prefs = _budget_and_plan()
    with _session() as db:
        uid = _uid()
        observe_plan_generation(db, uid, budget, plan, prefs)
        first = len(_all_traces(db, uid))
        observe_plan_generation(db, uid, budget, plan, prefs)
        second = len(_all_traces(db, uid))
    assert second == 2 * first


# ── Propriété et confidentialité ─────────────────────────────────────────────


def test_another_users_traces_are_invisible():
    from app.models.user import User
    from app.services.decision_analytics import (
        observe_plan_generation,
        traces_for_group,
    )

    budget, plan, prefs = _budget_and_plan()
    with _session() as db:
        uid = _uid()
        other = User(username="trace_other", password_hash="x")
        db.add(other)
        db.commit()
        db.refresh(other)

        group = observe_plan_generation(db, other.id, budget, plan, prefs)
        assert traces_for_group(db, other.id, group)
        # Same group id, wrong owner: not "denied", simply absent.
        assert traces_for_group(db, uid, group) == []


def test_no_credential_or_session_material_is_stored():
    from app.models.decision_trace import DecisionTrace

    cols = " ".join(DecisionTrace.__table__.columns.keys()).lower()
    for banned in ("password", "token", "cookie", "secret", "hash"):
        assert banned not in cols


# ── Pas de backfill ──────────────────────────────────────────────────────────


def test_the_migration_creates_no_historical_rows():
    import pathlib

    path = pathlib.Path("migrations/versions/20260816_add_decision_traces.py")
    src = path.read_text(encoding="utf-8")
    for banned in ("op.execute", "INSERT", "bulk_insert", "op.bulk_insert"):
        assert banned not in src


def test_a_user_with_history_but_no_observation_has_no_traces():
    """Past decisions were never traced; absence is a true statement."""
    with _session() as db:
        assert _all_traces(db, _uid()) == []
