"""MOB-00 — the native feature migration map stays exhaustive (spec `mobile/feature-migration-map`).

Every route the web app mounts belongs to exactly one user feature of the inventory, and
the inventory names no route the app no longer mounts. A route added without being
classified fails here, in the same commit — that is the point: the migration backlog
cannot silently lose a capability.

The mounted routes are read from the app built by the `client` fixture, never from a
direct `from app.main import app`: the fixture purges every `app.*` module, so a direct
import can yield an app with no business router mounted, and the verdict would depend on
the test order (see `test_no_internal_link_traverses_a_redirect.py`).
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest
import yaml
from starlette.routing import Mount

ROOT = Path(__file__).resolve().parent.parent
#: the change folder while it is open; the living spec once the change is archived
CANDIDATES = (
    ROOT / "openspec" / "changes" / "native-feature-migration-map" / "inventory.yaml",
    ROOT / "openspec" / "specs" / "mobile" / "feature-migration-map" / "inventory.yaml",
)
FIELDS = (
    "feature", "legacy_location", "domain_owner", "api", "data", "user_actions",
    "native_destination", "status", "dependencies", "visual_assets", "migration_risk",
)
STATUSES = {"KEEP_DOMAIN", "REWRITE_NATIVE", "WEB_ONLY", "DEPRECATE", "BLOCKED"}
PROPOSABLE = {"WEB_ONLY", "DEPRECATE"}


def _inventory() -> dict:
    path = next((p for p in CANDIDATES if p.exists()), None)
    assert path is not None, f"inventory not found in {[str(p) for p in CANDIDATES]}"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def route_key(route) -> str:
    """`METHOD /path` for a route, `MOUNT /path` for a mount — HEAD is implied by GET."""
    if isinstance(route, Mount):
        return f"MOUNT {route.path}"
    methods = sorted((getattr(route, "methods", None) or set()) - {"HEAD"})
    return f"{' '.join(methods)} {route.path}"


def shape_errors(feature: dict) -> list[str]:
    """What is wrong with one inventory entry (empty = well formed)."""
    errors = [f"missing field {f!r}" for f in FIELDS if f not in feature]
    status = feature.get("status")
    if status not in STATUSES:
        errors.append(f"unknown status {status!r}")
    if status == "BLOCKED" and not feature.get("dependencies"):
        errors.append("BLOCKED without a named dependency")
    if feature.get("proposed") and status not in PROPOSABLE:
        errors.append(f"only {sorted(PROPOSABLE)} can be a proposal, not {status!r}")
    return errors


def coverage_gaps(mounted: set[str], inventory: dict) -> dict[str, list[str]]:
    """Routes mounted but not inventoried, inventoried but not mounted, inventoried twice, stale exclusions."""
    listed = Counter(r for f in inventory["features"] for r in f.get("routes", []))
    excluded = set(inventory.get("excluded_routes", []))
    return {
        "unclassified": sorted(mounted - set(listed) - excluded),
        "ghosts": sorted(set(listed) - mounted),
        "twice": sorted(r for r, n in listed.items() if n > 1),
        "stale_exclusions": sorted(excluded - mounted),
    }


def test_every_entry_is_well_formed():
    offenders = {f.get("id", "?"): shape_errors(f) for f in _inventory()["features"] if shape_errors(f)}
    assert not offenders, offenders


def test_entry_ids_are_unique():
    ids = Counter(f["id"] for f in _inventory()["features"])
    assert not [i for i, n in ids.items() if n > 1], ids


def test_every_mounted_route_is_inventoried_exactly_once(client):
    gaps = coverage_gaps({route_key(r) for r in client.app.routes}, _inventory())
    assert not any(gaps.values()), gaps


# ── the guard bites ─────────────────────────────────────────────────────────

GOOD = {f: [] for f in FIELDS} | {"feature": "x", "status": "REWRITE_NATIVE"}


def test_a_missing_field_is_named():
    bad = {k: v for k, v in GOOD.items() if k != "api"}
    assert shape_errors(bad) == ["missing field 'api'"]


def test_an_unknown_status_is_refused():
    assert shape_errors(GOOD | {"status": "LATER"}) == ["unknown status 'LATER'"]


def test_a_block_without_a_cause_is_refused():
    assert shape_errors(GOOD | {"status": "BLOCKED"}) == ["BLOCKED without a named dependency"]


def test_only_a_retirement_or_web_only_can_be_a_proposal():
    assert shape_errors(GOOD | {"proposed": True}), "a REWRITE_NATIVE proposal must be refused"
    assert not shape_errors(GOOD | {"status": "WEB_ONLY", "proposed": True})


def test_an_unclassified_route_is_caught():
    inv = {"features": [{"routes": ["GET /a"]}], "excluded_routes": []}
    assert coverage_gaps({"GET /a", "POST /b"}, inv)["unclassified"] == ["POST /b"]


def test_a_ghost_route_is_caught():
    inv = {"features": [{"routes": ["GET /a", "GET /gone"]}], "excluded_routes": []}
    assert coverage_gaps({"GET /a"}, inv)["ghosts"] == ["GET /gone"]


def test_a_route_listed_twice_is_caught():
    inv = {"features": [{"routes": ["GET /a"]}, {"routes": ["GET /a"]}], "excluded_routes": []}
    assert coverage_gaps({"GET /a"}, inv)["twice"] == ["GET /a"]


def test_a_stale_exclusion_is_caught():
    inv = {"features": [{"routes": ["GET /a"]}], "excluded_routes": ["GET /docs-gone"]}
    assert coverage_gaps({"GET /a"}, inv)["stale_exclusions"] == ["GET /docs-gone"]


@pytest.mark.parametrize("path", ["/openapi.json", "/api/docs"])
def test_route_key_drops_the_implied_head(path):
    class _R:
        methods = {"GET", "HEAD"}

    r = _R()
    r.path = path
    assert route_key(r) == f"GET {path}"
