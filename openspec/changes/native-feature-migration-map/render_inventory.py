"""Render inventory.yaml as inventory.md — one table per family, never edited by hand.

Usage: python3 render_inventory.py   (writes inventory.md next to this file)
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
FAMILIES = {
    "mission": "Mission",
    "seance": "Séance",
    "compte": "Compte",
    "profil": "Profil",
    "progres": "Progrès",
    "recuperation": "Récupération",
    "programmes": "Programmes",
    "reference": "Référence",
    "social": "Social",
    "exploitation": "Exploitation",
}


def _cell(value) -> str:
    if isinstance(value, list):
        value = " · ".join(str(v) for v in value) if value else "—"
    return str(value).replace("|", "/").replace("\n", " ")


def render(inv: dict) -> str:
    features = inv["features"]
    routes = sum(len(f["routes"]) for f in features)
    statuses = Counter(f["status"] for f in features)
    lines = [
        "# Inventaire des fonctions web → destination native (MOB-00)",
        "",
        f"Généré depuis `inventory.yaml` (base `{inv['base_sha']}`) — ne pas éditer à la main.",
        f"**{len(features)} fonctions**, **{routes} routes** rattachées, "
        + ", ".join(f"{s} {n}" for s, n in sorted(statuses.items())) + ".",
        "« (proposé) » = proposition de l'agent, à trancher par l'opérateur.",
        "",
    ]
    for key, title in FAMILIES.items():
        rows = [f for f in features if f["family"] == key]
        if not rows:
            continue
        lines += [
            f"## {title}",
            "",
            "| Fonction | Statut | Destination native | Routes | Propriétaire du domaine | Dépendances | Risque |",
            "|---|---|---|---|---|---|---|",
        ]
        for f in rows:
            status = f["status"] + (" (proposé)" if f.get("proposed") else "")
            lines.append(
                f"| {_cell(f['feature'])} | {status} | {_cell(f['native_destination'])} | {len(f['routes'])} "
                f"| {_cell(f['domain_owner'])} | {_cell(f['dependencies'])} | {_cell(f['migration_risk'])} |"
            )
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    inventory = yaml.safe_load((HERE / "inventory.yaml").read_text(encoding="utf-8"))
    (HERE / "inventory.md").write_text(render(inventory), encoding="utf-8")
    print("inventory.md written")
