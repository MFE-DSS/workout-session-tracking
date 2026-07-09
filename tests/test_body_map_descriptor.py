"""Sb_32.3 — body_map_descriptor service contract + invariance.

Guards the pure descriptor service built over the Sx_32 mapping:

Contract & shape
  * known exercise → ``mapped`` descriptor (primary first, deduped, stable).
  * unknown exercise → ``unknown`` status + "À qualifier" + no invented zone.
  * output is JSON-serializable ; every field always present.

Invariance (contrainte #1)
  * descriptor zones (primary + secondary) match the Sb_32.1 baseline, on
    BOTH the name-only substring path and the DB-lookup path.

Honesty & isolation
  * ``resolution_path`` reflects the actual path (db_lookup / substring_fallback
    / unknown), never lies.
  * labels resolved from ``BodyZone`` when a DB is given, else ``ZONE_LABELS``.
  * no model / migration / schema / consumer / UI file touched by this sprint.
  * no medical claim in any descriptor string.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.services.body_map_descriptor import build_body_map_descriptor

ROOT = Path(__file__).resolve().parent.parent
BASELINE = ROOT / "tests" / "fixtures" / "classify_exercise_baseline.json"
SB_32_2_REVISION = "k2l7f3g4i65"

# Files this sprint must NOT touch (pure service sprint).
FORBIDDEN_FILES = [
    "app/services/muscle_mapping.py",
    "app/services/muscle_scoring.py",
    "app/services/body_intelligence_inputs.py",
    "app/services/coach_inference.py",
    "app/services/coach_report.py",
    "app/services/recommendation.py",
    "app/services/profile_metrics.py",
    "app/services/session_recap.py",
    "data/schema_snapshot.sql",
]
FORBIDDEN_DIRS = ["app/models", "migrations", "app/routers", "app/templates", "app/static"]

# Substrings that would signal a medical claim (must never appear).
MEDICAL_TERMS = ["diagnos", "médical", "medical", "patholog", "blessure", "traitement"]


def _baseline_entries() -> list[dict]:
    return json.loads(BASELINE.read_text(encoding="utf-8"))["entries"]


def _fresh_db() -> Path:
    tmp_dir = tempfile.mkdtemp(prefix="sb323-mig-")
    db_path = Path(tmp_dir) / "sb323.db"
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(cfg, SB_32_2_REVISION)
    return db_path


# ───────── 1-2. mapped / unknown ─────────


def test_known_exercise_returns_mapped_descriptor():
    d = build_body_map_descriptor("Chest Press machine")
    assert d["status"] == "mapped"
    assert d["primary_zone"] == "pecs"
    assert d["primary_label"] == "Pectoraux"
    assert d["is_qualified"] is True
    assert d["needs_qualification"] is False


def test_unknown_exercise_returns_unknown_a_qualifier():
    d = build_body_map_descriptor("Exercice inconnu xyz")
    assert d["status"] == "unknown"
    assert d["primary_zone"] == "unknown"
    assert d["primary_label"] == "À qualifier"
    assert d["secondary_zones"] == []
    assert d["zones"] == []
    assert d["is_qualified"] is False
    assert d["needs_qualification"] is True
    assert d["resolution_path"] == "unknown"


# ───────── 3-4. matches baseline (name-only) ─────────


def test_descriptor_primary_matches_baseline():
    for e in _baseline_entries():
        d = build_body_map_descriptor(e["name"])
        if e["primary"] == "unknown":
            assert d["status"] == "unknown"
        else:
            assert d["primary_zone"] == e["primary"], e["name"]


def test_descriptor_secondary_matches_baseline():
    for e in _baseline_entries():
        d = build_body_map_descriptor(e["name"])
        if e["primary"] != "unknown":
            assert d["secondary_zones"] == e["secondary"], e["name"]


# ───────── 5-6. db-lookup and fallback both == baseline ─────────


def test_db_lookup_path_matches_baseline():
    db_path = _fresh_db()
    engine = create_engine(f"sqlite:///{db_path}")
    mismatches = []
    paths = set()
    with Session(engine) as db:
        for e in _baseline_entries():
            d = build_body_map_descriptor(e["name"], exercise_code=e["name"], db=db)
            paths.add(d["resolution_path"])
            if e["primary"] == "unknown":
                if d["status"] != "unknown":
                    mismatches.append((e["name"], "status"))
            elif d["primary_zone"] != e["primary"] or d["secondary_zones"] != e["secondary"]:
                mismatches.append((e["name"], (e["primary"], e["secondary"]),
                                   (d["primary_zone"], d["secondary_zones"])))
    engine.dispose()
    assert not mismatches, mismatches[:5]
    # every backfilled catalog exercise resolved via the DB path
    assert paths == {"db_lookup"}


def test_fallback_path_without_db_matches_baseline():
    for e in _baseline_entries():
        d = build_body_map_descriptor(e["name"])  # no db
        if e["primary"] == "unknown":
            assert d["status"] == "unknown"
            assert d["resolution_path"] == "unknown"
        else:
            assert (d["primary_zone"], d["secondary_zones"]) == (e["primary"], e["secondary"])
            assert d["resolution_path"] == "substring_fallback"


# ───────── 7-8. label resolution ─────────


def test_labels_resolved_from_bodyzone_when_db_available():
    db_path = _fresh_db()
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as db:
        d = build_body_map_descriptor(
            "Chest Press machine", exercise_code="Chest Press machine", db=db
        )
    engine.dispose()
    # BodyZone-backed labels (identical values to ZONE_LABELS here, but
    # sourced from the DB row).
    assert d["primary_label"] == "Pectoraux"
    assert d["secondary_labels"] == ["Triceps"]


def test_labels_fallback_from_zone_labels_when_db_unavailable():
    from app.services.muscle_mapping import ZONE_LABELS

    d = build_body_map_descriptor("Chest Press machine")  # no db
    assert d["primary_label"] == ZONE_LABELS["pecs"]
    assert d["secondary_labels"] == [ZONE_LABELS["triceps"]]


# ───────── 9-10. dedup + stable order ─────────


def test_no_duplicate_zones():
    for e in _baseline_entries():
        d = build_body_map_descriptor(e["name"])
        codes = [z["code"] for z in d["zones"]]
        assert len(codes) == len(set(codes)), e["name"]
        # secondary never duplicates primary
        if d["status"] == "mapped":
            assert d["primary_zone"] not in d["secondary_zones"]


def test_stable_order_primary_then_secondary():
    d = build_body_map_descriptor("Chest Press machine")
    assert d["zones"][0]["role"] == "primary"
    assert all(z["role"] == "secondary" for z in d["zones"][1:])
    assert d["zones"][0]["code"] == d["primary_zone"]


# ───────── 11-13. isolation (no forbidden file touched) ─────────


def test_service_stays_pure_no_persistence():
    """Permanent invariant (independent of any later sprint's git diff): the
    descriptor service performs no DB write / no model mutation — it derives
    from the mapping and returns a dict. Guards the 'pure service' contract of
    Sb_32.3 regardless of which later sprint consumes it (e.g. the Worked Area
    UI wiring it into the session_detail route)."""
    src = (ROOT / "app" / "services" / "body_map_descriptor.py").read_text(
        encoding="utf-8"
    )
    for forbidden in ("db.add(", "db.commit(", "db.delete(", "session.add("):
        assert forbidden not in src, forbidden


def test_descriptor_service_signature_stable():
    """Permanent invariant (independent of any later sprint's git diff): the
    public service keeps its backward-compatible signature. Downstream sprints
    (e.g. the Worked Area UI) may wire it into routers/templates — that is
    allowed and no longer asserted here via git diff."""
    import inspect as pyinspect

    sig = pyinspect.signature(build_body_map_descriptor)
    params = sig.parameters
    assert list(params)[0] == "name"
    assert params["exercise_code"].kind == params["exercise_code"].KEYWORD_ONLY
    assert params["db"].kind == params["db"].KEYWORD_ONLY
    assert params["exercise_code"].default is None
    assert params["db"].default is None


# ───────── 14. no medical claim ─────────


def test_no_medical_claims_in_descriptor_strings():
    samples = ["Chest Press machine", "Exercice inconnu xyz", "Romanian Deadlift haltères"]
    for name in samples:
        d = build_body_map_descriptor(name)
        blob = json.dumps(d, ensure_ascii=False).lower()
        for term in MEDICAL_TERMS:
            assert term not in blob, f"medical term {term!r} in descriptor for {name!r}"


# ───────── 15-16. serializable + shape ─────────


def test_output_is_json_serializable():
    for name in ["Chest Press machine", "Exercice inconnu xyz"]:
        d = build_body_map_descriptor(name)
        # round-trips without error and stays a dict
        assert json.loads(json.dumps(d)) == d


def test_descriptor_shape_contract():
    expected_keys = {
        "status",
        "primary_zone",
        "primary_label",
        "secondary_zones",
        "secondary_labels",
        "zones",
        "source",
        "resolution_path",
        "is_qualified",
        "needs_qualification",
    }
    for name in ["Chest Press machine", "Exercice inconnu xyz"]:
        d = build_body_map_descriptor(name)
        assert set(d) == expected_keys, name
        assert isinstance(d["status"], str)
        assert isinstance(d["primary_zone"], str)
        assert isinstance(d["primary_label"], str)
        assert isinstance(d["secondary_zones"], list)
        assert isinstance(d["secondary_labels"], list)
        assert isinstance(d["zones"], list)
        assert isinstance(d["is_qualified"], bool)
        assert isinstance(d["needs_qualification"], bool)
        for z in d["zones"]:
            assert set(z) == {"code", "label", "role"}
