"""Zones agnostiques (opérateur, 2026-10-29) — l'app reçoit les zones d'un exercice par le contrat canonique.

« De manière agnostique, tu associes les images à des zones de travail. Ces zones de travail sont après
exploitées par des exercices comme muscles principaux ou secondaires […] Et après, les exercices sont ajoutés
dans les programmes. »

Avant : le plan mobile et le relevé classaient par l'ancien classifieur à sous-chaîne, sans les corrections
revues — « Rear delt fly machine (pec deck inversé) » sortait en `pecs`, « Relevé de jambes suspendu » en `calves`.
"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from tests.test_d9_mobile_sessions import _start, _token

ROOT = Path(__file__).resolve().parent.parent
REAR_DELT = "Rear delt fly machine (pec deck inversé)"
HANGING_LEG_RAISE = "Relevé de jambes suspendu"


def _by_name(plan: dict, name: str) -> dict:
    return next(e for e in plan["exercises"] if e["executed_name"] == name)


def test_every_plan_zone_is_the_canonical_resolution(client):
    from app.database import SessionLocal
    from app.services.body_zone_source import resolve_exercise_zones

    plan = _start(client, _token(), slug="pull-a").json()
    assert plan["exercises"], "prémisse : un plan servi"
    with SessionLocal() as db:
        for e in plan["exercises"]:
            z = resolve_exercise_zones(db, e["executed_name"])
            assert (e["zone"] or {}).get("zone", "unknown") == z.primary, e["executed_name"]
            assert [s["zone"] for s in e["secondary_zones"]] == list(z.secondary), e["executed_name"]


def test_the_rear_delt_fly_is_a_posterior_deltoid_on_the_phone(client):
    plan = _start(client, _token(), slug="pull-a").json()
    assert _by_name(plan, REAR_DELT)["zone"]["zone"] == "delt_post"


def test_a_press_carries_its_secondary_zone(client):
    plan = _start(client, _token(), slug="push-a").json()
    chest = _by_name(plan, "Chest Press machine")
    assert chest["zone"]["zone"] == "pecs"
    assert [s["zone"] for s in chest["secondary_zones"]] == ["triceps"]
    assert all(s["label"] for s in chest["secondary_zones"])


def _done_session(*names: str):
    def se(name):
        return SimpleNamespace(substituted_name=None, exercise_name_snapshot=name,
                               set_logs=[SimpleNamespace(kind="work", completed=True)])
    return SimpleNamespace(session_exercises=[se(n) for n in names])


def test_the_recap_names_the_same_zone_as_the_plan():
    from app.services.session_recap import _zones_touched

    zones = {z["zone"]: z["sets"] for z in _zones_touched(_done_session(REAR_DELT, HANGING_LEG_RAISE))}
    assert zones == {"delt_post": 1, "core": 1}


def test_no_mobile_payload_module_falls_back_to_the_old_classifier():
    """Une classe, pas un fichier : tout ce qui construit le plan ou le relevé servis à l'app."""
    for module in ("app/services/mobile_read_models.py", "app/services/session_recap.py"):
        src = (ROOT / module).read_text(encoding="utf-8")
        assert "classify_exercise" not in src, module
        assert "resolve_exercise_zones" in src, module
