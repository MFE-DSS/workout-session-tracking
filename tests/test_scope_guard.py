"""Sb_OPS.scope-guard — tests du classifieur anti-overcheck.

Verrouille la logique de `scripts/check_scope.py` : la classification en
tiers doit rester déterministe et conservative (précédence
migration > ci_infra > shared_code > isolated > docs), et le tier `isolated`
doit bien autoriser à SKIPPER le full sweep local (le point de la feature).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def _load(name: str):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _classify(files: list[str]) -> str:
    mod = _load("check_scope")
    return mod.classify(files, mod._load_policy())["tier"]


# ───────── tier classification ─────────


def test_docs_only_is_docs_tier():
    assert _classify(["docs/SPRINT_X.md", "docs/strategy/SPEC_REGISTRY.md"]) == "docs"


def test_migration_files_are_migration_tier():
    assert _classify(["migrations/versions/foo.py"]) == "migration"
    assert _classify(["app/models/bar.py"]) == "migration"
    assert _classify(["data/schema_snapshot.sql"]) == "migration"


def test_ci_infra_files_are_ci_infra_tier():
    assert _classify([".github/workflows/ci.yml"]) == "ci_infra"
    assert _classify(["scripts/check_scope.py"]) == "ci_infra"
    assert _classify(["requirements.txt"]) == "ci_infra"


def test_shared_code_when_modified_file_imported_elsewhere():
    # muscle_mapping is imported by many consumers → shared.
    assert _classify(["app/services/muscle_mapping.py"]) == "shared_code"


def test_a_globally_observed_stylesheet_is_shared_not_isolated():
    """⚠ LE TROU QUE LA DÉTECTION PAR IMPORTS NE POUVAIT PAS VOIR.

    `shared_code_detection` cherche un `import` Python. Une feuille de style et
    un gabarit ne s'importent pas : ils étaient donc classés `isolated`, c'est-
    à-dire au niveau de vérification LE PLUS BAS — alors que l'observation
    dynamique de 1391 tests les montre lus ou rendus par plus de la moitié de
    la suite (`app.css` 54,8 %, `base.html` 50,7 %).

    `AUREN_UI_BLUEPRINT §8` l'avait signalé sans le chiffrer.
    """
    for path in (
        "app/static/css/app.css",
        "app/static/css/interaction.css",
        "app/static/css/target_closure.css",
        "app/templates/base.html",
        "app/templates/_macros.html",
    ):
        assert _classify([path]) == "shared_code", (
            f"{path} est une surface globale : la classer `isolated` autorise "
            "le minimum de vérification sur le fichier qui casse le plus loin"
        )


def test_a_scoped_stylesheet_stays_isolated():
    """L'INVERSE, sans quoi la correction deviendrait un sur-contrôle général.

    `home.css` n'est lu que par 16 % de la suite : il n'a rien à faire dans la
    liste, et l'y mettre reviendrait à traiter tout le CSS comme global.
    """
    assert _classify(["app/static/css/home.css"]) == "isolated"
    assert _classify(["app/templates/index.html"]) == "isolated"


def test_the_global_list_is_documented_with_its_measure():
    """Une liste sans mesure redevient une opinion au premier doute.

    La policy porte le pourcentage observé pour chaque entrée ; sans lui,
    personne ne saura si la liste est encore vraie dans six mois.
    """
    import json
    import pathlib as _p

    pol = json.loads(
        (_p.Path(__file__).resolve().parent.parent / ".check-policy.json")
        .read_text(encoding="utf-8")
    )
    gs = pol["global_surfaces"]
    assert gs["paths"], "liste vide"
    # `_macros.html` est inclus par `base.html` : sa portée est celle de son
    # hôte, elle ne se mesure pas séparément. Toute AUTRE entrée doit porter
    # son pourcentage observé.
    measured = set(gs["_evidence"]) | {"app/templates/_macros.html"}
    undocumented = sorted(set(gs["paths"]) - measured)
    assert not undocumented, (
        f"entrées sans mesure associée : {undocumented} — une liste sans "
        "mesure redevient une opinion au premier doute"
    )


def test_isolated_when_new_leaf_file_not_imported_anywhere():
    # A synthetic app/ service path that no module imports → isolated.
    # NB: we deliberately use a NON-EXISTENT fixture path rather than a real
    # file, so the test stays semantic: it asserts the classifier's logic for
    # an un-imported leaf, and never breaks when a later sprint wires a real
    # service into a router (which correctly reclassifies it as shared_code).
    assert (
        _classify(["app/services/__scope_guard_new_leaf_fixture.py"]) == "isolated"
    )


def test_isolated_tier_allows_skipping_full_sweep():
    """The whole point of the guard: an isolated diff must NOT require a
    local full sweep."""
    mod = _load("check_scope")
    policy = mod._load_policy()
    isolated = policy["tiers"]["isolated"]
    assert "full_sweep_local" in isolated.get("skip", [])
    assert "full_sweep_local" not in isolated["required_local_checks"]
    assert "broad_sweep_scoped" in isolated["required_local_checks"]


# ───────── precedence (conservative: never downgrade) ─────────


def test_precedence_migration_wins_over_isolated():
    # A diff with both a new leaf AND a migration must classify as migration.
    assert _classify(["app/services/new_leaf.py", "migrations/versions/x.py"]) == "migration"


def test_precedence_shared_wins_over_docs():
    assert _classify(["app/services/muscle_mapping.py", "docs/X.md"]) == "shared_code"


def test_docs_tier_requires_only_spec_protocol():
    mod = _load("check_scope")
    policy = mod._load_policy()
    docs = policy["tiers"]["docs"]
    assert docs["required_local_checks"] == ["check_spec_protocol"]
    assert "full_sweep" in docs.get("skip", [])
