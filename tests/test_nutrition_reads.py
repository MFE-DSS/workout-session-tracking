"""Stable owned nutrition views distinguish declared facts, targets and coverage."""

import pytest
from nutrition_helpers import nutrition_db, nutrition_environment
from test_nutrition_transactions import apply, prepared


@pytest.fixture()
def db(tmp_path):
    with nutrition_db(tmp_path) as session:
        yield session


@pytest.fixture(autouse=True)
def controlled_environment(monkeypatch):
    with nutrition_environment(monkeypatch):
        yield


def test_days_show_zero_missing_and_partial_coverage_without_inferred_macros(db):
    from app.services.nutrition_reads import read_days

    apply(db, prepared(db, values={"kcal_milli": 0}))
    page = read_days(db, 1, "2026-11-06", "2026-11-12", limit=100)
    assert page["collection_state"] == "COMPLETE"
    assert page["coverage"]["kcal_milli"] == {
        "known_days": 1, "missing_days": 6, "partial_days": 1,
        "declared_complete_days": 0, "withdrawn_days": 0, "total_calendar_days": 7,
    }
    assert page["totals"]["kcal_milli"] == {"value": 0, "known_days": 1}
    assert page["totals"]["protein_milli"] == {"value": None, "known_days": 0}


def test_page_watermark_does_not_mix_a_correction_with_previous_heads(db):
    from app.services.nutrition_reads import read_days

    apply(db, prepared(db, key="2026-11-11", request="eleven", values={"kcal_milli": 1000000}), key="2026-11-11")
    apply(db, prepared(db, values={"kcal_milli": 2000000}))
    first = read_days(db, 1, "2026-11-11", "2026-11-12", limit=1)
    assert first["collection_state"] == "PARTIAL"
    apply(db, prepared(db, request="change", values={"kcal_milli": 2500000}))
    second = read_days(db, 1, "2026-11-11", "2026-11-12", limit=1, cursor=first["next_cursor"])
    assert second["read_id"] == first["read_id"]
    assert second["entries"][0]["values"]["kcal_milli"] == 2000000
    assert second["totals"]["kcal_milli"] == {"value": 3000000, "known_days": 2}
    assert second["collection_state"] == "COMPLETE"
    assert read_days(db, 1, "2026-11-11", "2026-11-12")["totals"]["kcal_milli"]["value"] == 3500000


def test_cursor_cannot_be_reused_by_another_owner_or_period(db):
    from app.services.nutrition_commands import NutritionError
    from app.services.nutrition_reads import read_days

    apply(db, prepared(db, key="2026-11-11", request="eleven"), key="2026-11-11")
    apply(db, prepared(db))
    cursor = read_days(db, 1, "2026-11-11", "2026-11-12", limit=1)["next_cursor"]
    with pytest.raises(NutritionError):
        read_days(db, 2, "2026-11-11", "2026-11-12", limit=1, cursor=cursor)
    with pytest.raises(NutritionError):
        read_days(db, 1, "2026-11-10", "2026-11-12", limit=1, cursor=cursor)


def test_export_is_a_stable_all_revision_traversal_across_concurrent_append(db):
    from app.services.nutrition_reads import read_export

    target_key = ("STANDARD", "2026-11-01")
    apply(db, prepared(db, "TARGET", target_key, request="preset"), "TARGET", target_key)
    apply(db, prepared(db))
    first = read_export(db, 1, limit=1)
    assert first["entries"][0]["namespace"] == "TARGET"
    apply(db, prepared(db, request="later", values={"kcal_milli": 1700000}))
    second = read_export(db, 1, limit=1, cursor=first["next_cursor"])
    assert second["read_id"] == first["read_id"]
    assert second["entries"][0]["entry"]["values"]["kcal_milli"] == 1800000
    assert second["collection_state"] == "COMPLETE"


def test_empty_day_has_a_real_creation_token_without_creating_a_row(db):
    from nutrition_helpers import proof

    from app.models.nutrition import NutritionDayRevision
    from app.services.nutrition_consent import read_consent, set_consent
    from app.services.nutrition_reads import read_head

    grant = read_consent(db, 1)
    set_consent(db, 1, grant["consent_token"], True, 1, auth_proof=proof(db))
    result = read_head(db, 1, "DAY", "2026-11-12")
    assert result["state"] == "ABSENT" and result["entry"] is None
    assert len(result["head_token"]) == 64
    assert db.query(NutritionDayRevision).count() == 0


def test_target_list_has_current_heads_and_versions_preserve_disabled_original(db):
    from app.services.nutrition_reads import read_targets, read_versions

    key = ("STANDARD", "2026-11-01")
    first = apply(db, prepared(db, "TARGET", key, request="preset"), "TARGET", key)
    disable = prepared(db, "TARGET", key, {}, "disable")
    disable["operation"] = "DISABLE"
    apply(db, disable, "TARGET", key)
    current = read_targets(db, 1)
    assert len(current["entries"]) == 1
    assert current["entries"][0]["enabled"] is False
    history = read_versions(db, 1, "TARGET", first["entity_ref"])
    assert [r["enabled"] for r in history["entries"]] == [True, False]
    assert all(r["head_token"] is None for r in history["entries"])
