"""Sb_ORCHESTRATOR_EXPLAINER_01 — expliquer sans jamais décider ni promettre.

Le test qui compte le plus ici est négatif : **la morphologie ne doit jamais
apparaître comme raison de plan**, parce que le planificateur ne la consomme
pas. L'afficher affirmerait une causalité qui n'existe pas.
"""
from __future__ import annotations

import re

import pytest

PROGRAMS_URL = "/programs"
MATERIALIZE_URL = "/programs/from-weekly-plan"
WHY_TITLE = "Pourquoi ce plan ?"


@pytest.fixture(autouse=True)
def _app_db(client):
    return client


def _session():
    from app.database import SessionLocal

    return SessionLocal()


def _uid():
    from tests.helpers import get_test_user_id

    return get_test_user_id()


def _save_prefs(db, uid, cadence=4, focus=("arms",), equipment=None):
    from app.services.training_preferences import save_training_preferences

    save_training_preferences(
        db, uid, sessions_per_week=cadence,
        focus_priorities=list(focus),
        available_equipment=list(equipment) if equipment else None,
    )


def _observe(db, uid, cadence=4, focus=("arms",), equipment=None):
    """Write a real trace group the way the product does."""
    from app.services.decision_analytics import observe_plan_generation
    from app.services.training_preferences import TrainingPreferencesData
    from app.services.weekly_planner import build_weekly_plan
    from app.services.weekly_volume_budget import build_weekly_volume_budget

    prefs = TrainingPreferencesData(
        sessions_per_week=cadence,
        focus_priorities=tuple(focus),
        available_equipment=tuple(equipment) if equipment else None,
    )
    budget = build_weekly_volume_budget(prefs)
    plan = build_weekly_plan(prefs, budget=budget)
    return observe_plan_generation(db, uid, budget, plan, prefs)


def _explain(uid=None):
    from app.services.orchestrator_explainer import build_plan_explanation

    with _session() as db:
        return build_plan_explanation(db, uid if uid is not None else _uid())


def _section(client) -> str:
    page = client.get(PROGRAMS_URL).text
    if WHY_TITLE not in page:
        return ""
    start = page.index(WHY_TITLE)
    return page[start:page.index("</section>", start)]


def _visible(client) -> str:
    return re.sub(r"<[^>]+>", " ", _section(client))


# ── Raisons réellement causales ──────────────────────────────────────────────


def test_the_declared_cadence_appears_accurately():
    with _session() as db:
        _observe(db, _uid(), cadence=4)
    texts = " ".join(i.text for i in _explain().items)
    assert "4 séances" in texts


@pytest.mark.parametrize("cadence", [2, 3, 5])
def test_the_cadence_shown_is_the_one_declared(cadence):
    with _session() as db:
        _observe(db, _uid(), cadence=cadence)
    texts = " ".join(i.text for i in _explain().items)
    assert f"{cadence} séances" in texts


def test_the_declared_priorities_appear_accurately():
    with _session() as db:
        _observe(db, _uid(), focus=("arms",))
    exp = _explain()
    priority_items = [i for i in exp.items if "priorités" in i.text]
    assert priority_items
    assert all(i.source_label == "Selon tes préférences" for i in priority_items)


def test_product_policy_is_labelled_as_a_convention_not_physiology():
    with _session() as db:
        _observe(db, _uid())
    policy = [i for i in _explain().items
              if i.source_label == "Convention de planification"]
    assert policy
    blob = " ".join((i.text + " " + (i.detail or "")) for i in policy).lower()
    assert "convention" in blob
    for banned in ("besoin biologique", "ton corps a besoin", "physiolog",
                   "optimal", "scientifiquement"):
        assert banned not in blob


def test_a_real_equipment_constraint_is_explained():
    """Only when a zone was genuinely unmet."""
    with _session() as db:
        _observe(db, _uid(), focus=("arms",), equipment=["bodyweight"])
    items = _explain().items
    constraints = [i for i in items if i.source_label == "Contrainte du catalogue"]
    if constraints:
        assert all("matériel" in i.text for i in constraints)


def test_recovery_appears_only_when_it_was_actually_consumed():
    """No replan ran, so no recovery source exists — and none is invented."""
    with _session() as db:
        _observe(db, _uid())
    assert not [i for i in _explain().items
                if i.source_label == "Estimation de récupération"]


# ── La morphologie n'est PAS une raison de plan ──────────────────────────────


def test_morphology_never_appears_as_a_plan_reason():
    """The planner does not consume morphology; claiming it would be false."""
    from datetime import UTC, datetime

    from sqlalchemy import select

    from app.models.measurement import BodyMeasurement
    from app.models.user import User

    with _session() as db:
        uid = _uid()
        db.execute(select(User).where(User.id == uid)).scalar_one().height_cm = 180
        db.add(BodyMeasurement(
            user_id=uid, measured_at=datetime.now(UTC),
            wingspan_cm=190.0, waist_cm=78.0, chest_cm=104.0))
        db.commit()
        _observe(db, uid)

    blob = " ".join(
        (i.text + " " + (i.detail or "") + " " + i.source_label)
        for i in _explain().items
    ).lower()
    for banned in ("envergure", "ape index", "morpholog", "proportion",
                   "wingspan", "longiligne"):
        assert banned not in blob


def test_the_rendered_section_never_mentions_morphology(client):
    from datetime import UTC, datetime

    from sqlalchemy import select

    from app.models.measurement import BodyMeasurement
    from app.models.user import User

    with _session() as db:
        uid = _uid()
        _save_prefs(db, uid)
        db.execute(select(User).where(User.id == uid)).scalar_one().height_cm = 180
        db.add(BodyMeasurement(
            user_id=uid, measured_at=datetime.now(UTC), wingspan_cm=190.0))
        db.commit()
    client.post(MATERIALIZE_URL, follow_redirects=False)

    blob = _visible(client).lower()
    for banned in ("envergure", "ape index", "morpholog", "proportion"):
        assert banned not in blob


def test_an_excluded_source_is_filtered_by_nature_not_by_position():
    """The exclusion must not depend on the 5-item cap to hide a reason.

    Planting a morphology item appended at the END left all 26 tests green:
    the filter compared `source_label` (a French string) to a raw token, so it
    matched nothing, and truncation quietly dropped the planted item past the
    cap. The reason was invisible for the wrong reason.

    The filter now runs on `source_kind` and **before** truncation, so this
    holds even when the excluded item is first.
    """
    from app.services.decision_analytics import MORPHOLOGY_INFERENCE
    from app.services.orchestrator_explainer import (
        EXCLUDED_FROM_PLAN_REASONS,
        ExplanationItem,
    )

    assert MORPHOLOGY_INFERENCE in EXCLUDED_FROM_PLAN_REASONS
    # The excluded token is a NATURE, never a display label.
    from app.services.orchestrator_explainer import SOURCE_LABELS

    assert MORPHOLOGY_INFERENCE not in SOURCE_LABELS
    for kind in EXCLUDED_FROM_PLAN_REASONS:
        assert kind not in SOURCE_LABELS.values()

    item = ExplanationItem(
        source_kind=MORPHOLOGY_INFERENCE, source_label="peu importe",
        text="x",
    )
    assert item.source_kind in EXCLUDED_FROM_PLAN_REASONS


def test_every_rendered_item_carries_an_allowed_nature():
    with _session() as db:
        _observe(db, _uid(), focus=("arms", "chest"))
    from app.services.orchestrator_explainer import EXCLUDED_FROM_PLAN_REASONS

    items = _explain().items
    assert items
    for item in items:
        assert item.source_kind not in EXCLUDED_FROM_PLAN_REASONS


def test_the_morphology_guard_states_the_reason():
    from app.services.orchestrator_explainer import MORPHOLOGY_GUARD

    low = MORPHOLOGY_GUARD.lower()
    assert "aucune decision de planification" in low


# ── Alternatives rejetées : invisibles en V1 ─────────────────────────────────


def test_rejected_alternatives_are_never_user_facing(client):
    with _session() as db:
        _save_prefs(db, _uid())
    client.post(MATERIALIZE_URL, follow_redirects=False)
    blob = _visible(client).lower()
    for banned in ("rejeté", "rejete", "écarté", "ecarte", "au lieu de",
                   "nous avons choisi plutôt"):
        assert banned not in blob


# ── Confiance ────────────────────────────────────────────────────────────────


def test_no_confidence_is_invented_for_declared_or_policy_sources():
    with _session() as db:
        _observe(db, _uid())
    for item in _explain().items:
        if item.source_label in ("Selon tes préférences",
                                 "Convention de planification"):
            assert item.confidence_label is None


def test_no_percentage_is_ever_rendered(client):
    with _session() as db:
        _save_prefs(db, _uid())
    client.post(MATERIALIZE_URL, follow_redirects=False)
    assert not re.search(r"\d+\s*%", _visible(client))


# ── Absence de trace ─────────────────────────────────────────────────────────


def test_without_traces_the_surface_says_so_instead_of_inventing():
    exp = _explain()
    assert exp.available is False
    assert exp.items == ()
    assert "Aucune trace" in exp.unavailable_notice


def test_the_page_invents_no_reason_when_there_is_no_trace(client):
    """`TRAIN1-E` / C7 — GARDE RÉORIENTÉE, PAS AFFAIBLIE.

    Elle exigeait la phrase « Aucune trace de décision » DANS une carte
    « Pourquoi ce plan ? » rendue à vide. Mesuré : une boîte de plus de 80 px
    dont tout le corps était cette phrase — le module vide pleine taille que
    l'arbitrage C7 retire.

    L'invariant qui compte n'était jamais la phrase : c'était **qu'aucune
    raison ne soit inventée**. La carte n'apparaît plus faute de trace ; la
    garde vérifie donc que le vocabulaire des raisons est absent, ce qui est
    strictement plus fort — il couvre les huit étiquettes de source, pas une
    formule d'absence.
    """
    blob = _visible(client)
    assert "Pourquoi ce plan" not in blob
    for invented in ("Tu as demandé", "Le produit planifie", "déduit de"):
        assert invented not in blob


# ── Déterminisme et absence de prose générée ─────────────────────────────────


def test_the_same_traces_produce_byte_identical_output():
    with _session() as db:
        _observe(db, _uid())
    first = _explain()
    second = _explain()
    assert [(i.source_label, i.text, i.detail) for i in first.items] == \
        [(i.source_label, i.text, i.detail) for i in second.items]


def test_the_copy_is_a_closed_mapping_with_no_llm():
    import inspect

    import app.services.orchestrator_explainer as mod

    src = inspect.getsource(mod)
    for banned in ("openai", "anthropic", "llm", "completion", "prompt",
                   "generate_text"):
        assert banned not in src.lower()


def test_no_enum_token_is_ever_rendered(client):
    with _session() as db:
        _save_prefs(db, _uid())
    client.post(MATERIALIZE_URL, follow_redirects=False)
    blob = _section(client)
    for token in ("USER_DECLARED", "PRODUCT_POLICY", "CATALOG_CONSTRAINT",
                  "RECOVERY_ESTIMATE", "MORPHOLOGY_INFERENCE", "VOLUME_BAND"):
        assert token not in blob


def test_the_surface_never_speaks_as_an_ai(client):
    with _session() as db:
        _save_prefs(db, _uid())
    client.post(MATERIALIZE_URL, follow_redirects=False)
    blob = _visible(client).lower()
    for banned in ("l'ia", "l’ia", "intelligence artificielle", "l'algorithme pense",
                   "je pense que"):
        assert banned not in blob


def test_at_most_five_explanations_are_shown():
    from app.services.orchestrator_explainer import MAX_EXPLANATIONS

    with _session() as db:
        _observe(db, _uid(), focus=("arms", "chest", "back"))
    assert len(_explain().items) <= MAX_EXPLANATIONS


# ── Isolation ────────────────────────────────────────────────────────────────


def test_another_users_traces_never_explain_my_plan():
    from app.models.user import User

    with _session() as db:
        other = User(username="explainer_other", password_hash="x")
        db.add(other)
        db.commit()
        db.refresh(other)
        _observe(db, other.id, cadence=6)

    assert _explain(_uid()).available is False


def test_an_explainer_failure_does_not_break_the_programs_page(client, monkeypatch):
    import app.services.orchestrator_explainer as mod

    monkeypatch.setattr(
        mod, "build_plan_explanation",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("boom")))
    assert client.get(PROGRAMS_URL).status_code == 200


def test_the_explainer_writes_nothing():
    import inspect

    import app.services.orchestrator_explainer as mod

    src = inspect.getsource(mod)
    for banned in ("db.add(", "db.commit(", "db.delete(", "db.merge("):
        assert banned not in src


def test_no_frozen_planner_module_imports_the_explainer():
    import pathlib

    import app.services as services_pkg

    root = pathlib.Path(services_pkg.__file__).parent
    for name in ("weekly_volume_budget", "weekly_planner",
                 "weekly_capacity_allocator", "weekly_set_allocation",
                 "weekly_plan_materialization", "set_contribution",
                 "adaptive_replan", "recommendation"):
        assert "orchestrator_explainer" not in \
            (root / f"{name}.py").read_text(encoding="utf-8"), name


def test_rendering_the_explanation_does_not_move_the_plan(client):
    from app.services.training_preferences import TrainingPreferencesData
    from app.services.weekly_planner import build_weekly_plan

    prefs = TrainingPreferencesData(sessions_per_week=4,
                                    focus_priorities=("arms",))
    before = build_weekly_plan(prefs)
    with _session() as db:
        _save_prefs(db, _uid())
    client.post(MATERIALIZE_URL, follow_redirects=False)
    client.get(PROGRAMS_URL)
    assert build_weekly_plan(prefs).fingerprint == before.fingerprint
