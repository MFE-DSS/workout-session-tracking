#!/usr/bin/env python3
"""Sb_OPS.scope-guard — garde-fou anti-overcheck (classification du diff).

Classe le diff courant (staged + unstaged vs HEAD) en un TIER de risque
déterministe et imprime le niveau de vérification LOCAL minimal suffisant,
d'après `.check-policy.json`. But : éviter de lancer un full sweep local de
10-15 min sur un changement isolé (service pur, docs) qui ne peut pas
régresser le reste de la suite.

Ce garde-fou ne réduit JAMAIS la CI réelle (3 jobs au push, source de
vérité). Il ne réduit que les checks LOCAUX redondants. Il est versionné
(repo), donc non aliénable par un prompt.

Usage :
    python scripts/check_scope.py            # classe le diff vs HEAD, imprime le tier
    python scripts/check_scope.py --files a.py b.py   # classe une liste explicite
    python scripts/check_scope.py --json     # sortie machine

Tiers (voir .check-policy.json) :
    docs        → spec_protocol seul (aucun sweep)
    isolated    → ruff + targeted + broad ciblé (PAS de full sweep local)
    shared_code → + full sweep local (fichier partagé modifié)
    migration   → + tous les migration checks
    ci_infra    → full + validation CI réelle impérative

Précédence : migration > ci_infra > shared_code > isolated > docs.
En cas de doute, on remonte d'un cran (jamais descendre).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POLICY_FILE = ROOT / ".check-policy.json"


def _load_policy() -> dict:
    if not POLICY_FILE.exists():
        print(f"FATAL: {POLICY_FILE} missing.", file=sys.stderr)
        sys.exit(2)
    return json.loads(POLICY_FILE.read_text(encoding="utf-8"))


def _changed_files() -> list[str]:
    """Union of staged + unstaged + untracked paths vs HEAD."""
    files: set[str] = set()
    for cmd in (
        ["git", "diff", "--name-only", "HEAD"],
        ["git", "diff", "--name-only", "--cached"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ):
        out = subprocess.run(
            cmd, cwd=ROOT, capture_output=True, text=True, check=False
        ).stdout
        files.update(p.strip() for p in out.splitlines() if p.strip())
    return sorted(files)


def _is_docs_only(files: list[str]) -> bool:
    return bool(files) and all(
        f.startswith("docs/") or f.endswith(".md") for f in files
    )


def _touches(files: list[str], *prefixes: str) -> list[str]:
    return [f for f in files if any(f.startswith(p) for p in prefixes)]


def _touches_regex(files: list[str], *patterns: str) -> list[str]:
    return [f for f in files if any(re.search(p, f) for p in patterns)]


def _module_name(path: str) -> str | None:
    """app/services/foo.py -> app.services.foo (None if not an importable py)."""
    if not path.endswith(".py") or not path.startswith("app/"):
        return None
    return path[:-3].replace("/", ".")


def _is_imported_elsewhere(path: str, all_changed: list[str]) -> bool:
    """True if the given app/ python file is imported by ANY other module in
    app/ — i.e. it is 'shared code', not a brand-new isolated leaf.

    A file that is only referenced by tests/ (or by nothing) is NOT shared:
    changing it cannot regress a lardon of the suite outside its surface.
    """
    mod = _module_name(path)
    if mod is None:
        return False
    # Build the two import spellings we look for.
    # e.g. app.services.foo  →  "import app.services.foo" or "from app.services.foo"
    #                            and "from app.services import foo"
    parent = ".".join(mod.split(".")[:-1])
    leaf = mod.split(".")[-1]
    needles = [
        f"import {mod}",
        f"from {mod} ",
        f"from {mod}\t",
        f"from {mod}\n",
        f"from {parent} import {leaf}",
    ]
    app_dir = ROOT / "app"
    for py in app_dir.rglob("*.py"):
        rel = py.relative_to(ROOT).as_posix()
        if rel == path:
            continue  # don't count the file importing itself
        try:
            text = py.read_text(encoding="utf-8")
        except OSError:
            continue
        if any(n in text for n in needles):
            return True
    return False


def classify(files: list[str], policy: dict) -> dict:
    """Return {tier, reasons[], triggering_files{}} for the given diff."""
    reasons: list[str] = []
    triggers: dict[str, list[str]] = {}

    if not files:
        return {"tier": "isolated", "reasons": ["no changes detected"], "triggers": {}}

    # migration tier
    mig = _touches(files, "migrations/", "app/models/") + _touches_regex(
        files, r"^data/schema_snapshot\.sql$"
    )
    if mig:
        triggers["migration"] = sorted(set(mig))
        reasons.append("touches migrations/models/schema")
        return {"tier": "migration", "reasons": reasons, "triggers": triggers}

    # ci_infra tier
    ci = _touches(files, ".github/", "scripts/") + _touches_regex(
        files, r"^requirements.*\.txt$", r"^pyproject\.toml$", r"^package\.json$"
    )
    if ci:
        triggers["ci_infra"] = sorted(set(ci))
        reasons.append("touches CI / scripts / dependencies")
        return {"tier": "ci_infra", "reasons": reasons, "triggers": triggers}

    # docs tier (only if EVERYTHING is docs)
    if _is_docs_only(files):
        return {
            "tier": "docs",
            "reasons": ["docs-only diff"],
            "triggers": {"docs": files},
        }

    # shared_code vs isolated: any modified app/ py imported elsewhere?
    #
    # ⚠ LA DÉTECTION PAR IMPORTS NE VOIT QUE LE PYTHON, ET C'EST UN TROU.
    #
    # Une feuille de style et un gabarit ne s'`import`ent pas : ils étaient donc
    # INDÉTECTABLES comme partagés, et `check_scope` les classait `isolated` —
    # c'est-à-dire au niveau de vérification le PLUS BAS. Mesuré le 2026-09-03
    # par observation dynamique de 1391 tests :
    #
    #     app/static/css/app.css            lu par 54,8 % de la suite
    #     app/static/css/interaction.css               52,0 %
    #     app/static/css/target_closure.css            51,7 %
    #     app/templates/base.html          rendu par  50,7 %
    #
    # `AUREN_UI_BLUEPRINT §8` l'avait signalé sans le chiffrer. À la veille
    # d'une phase de refonte UI, c'est exactement le mauvais sens d'erreur :
    # toucher la feuille globale autorisait le minimum de contrôles.
    #
    # La liste vit dans `.check-policy.json` (versionné) : la faire évoluer
    # demande un commit, jamais un prompt.
    global_assets = _touches(files, *policy.get("global_surfaces", {}).get("paths", []))
    app_py = [f for f in files if f.startswith("app/") and f.endswith(".py")]
    shared_hits = [f for f in app_py if _is_imported_elsewhere(f, files)] + global_assets
    if global_assets:
        reasons.append("touches a globally-observed stylesheet/template")
    if shared_hits:
        triggers["shared_code"] = sorted(shared_hits)
        reasons.append("modifies app/ code imported elsewhere (shared)")
        return {"tier": "shared_code", "reasons": reasons, "triggers": triggers}

    # anything else that isn't pure docs but touches only new/leaf files → isolated
    reasons.append("new/leaf files only, nothing shared imported elsewhere")
    triggers["isolated"] = files
    return {"tier": "isolated", "reasons": reasons, "triggers": triggers}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--files", nargs="*", help="Classify an explicit file list.")
    parser.add_argument("--json", action="store_true", help="Machine-readable output.")
    args = parser.parse_args()

    policy = _load_policy()
    files = args.files if args.files else _changed_files()
    result = classify(files, policy)
    tier = result["tier"]
    tier_spec = policy["tiers"][tier]

    payload = {
        "tier": tier,
        "reasons": result["reasons"],
        "triggering_files": result["triggers"],
        "changed_files": files,
        "required_local_checks": tier_spec["required_local_checks"],
        "skip": tier_spec.get("skip", []),
        "ci_note": tier_spec.get("ci_note", "CI réelle au push = source de vérité."),
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print("=== scope guard (anti-overcheck) ===")
    print(f"  changed files : {len(files)}")
    print(f"  TIER          : {tier.upper()}")
    for r in result["reasons"]:
        print(f"    · {r}")
    print()
    print("  Required LOCAL checks (minimum suffisant) :")
    for c in tier_spec["required_local_checks"]:
        print(f"    ✓ {c}")
    if tier_spec.get("skip"):
        print()
        print("  Skippable EN LOCAL (redondant à ce tier) :")
        for s in tier_spec["skip"]:
            print(f"    ⤫ {s}")
    print()
    print(f"  CI note : {payload['ci_note']}")
    print()
    print(
        "  Rappel : la CI réelle (3 jobs) au push reste la source de vérité de "
        "non-régression globale. Ce garde-fou ne réduit QUE les checks locaux."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
