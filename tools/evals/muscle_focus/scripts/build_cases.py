#!/usr/bin/env python3
"""Build promptfoo test cases (region x judge role) — GO C2 §5/§8. Deterministic.

Reads the region rubrics + AUREN_MUSCLE_FOCUS_REVIEW_ROOT and writes generated/cases.yaml consumed
by promptfooconfig.yaml. No absolute Martin-specific path is hardcoded; evidence is resolved relative
to the external review root at run time. Raw OBJ files are never referenced.
"""
from __future__ import annotations

import json
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent.parent
RUBRICS = HERE / "rubrics"
GEN = HERE / "generated"
PKG_SUBDIR = "07_external_review/sb-asset-03b-2r-qualified-anatomical-review"
ROLES = ["J1_anatomy_consistency", "J2_medical_illustration", "J3_fitness_semantics",
         "J4_adversarial_falsifier", "J5_provenance_governance"]


def _load_yaml(p):
    import yaml
    return yaml.safe_load(pathlib.Path(p).read_text())


def main() -> int:
    root = os.environ.get("AUREN_MUSCLE_FOCUS_REVIEW_ROOT", "${AUREN_MUSCLE_FOCUS_REVIEW_ROOT}")
    GEN.mkdir(parents=True, exist_ok=True)
    cases = []
    for region in ("chest", "shoulders", "posterior"):
        r = _load_yaml(RUBRICS / f"{region}.yaml")
        evidence = [f"{root}/{PKG_SUBDIR}/{e}" for e in r["evidence_files"]]
        constraints = {"special_rules": r.get("special_rules", []),
                       "constraints": r.get("constraints", {}),
                       "known_unresolved_warnings": r.get("known_unresolved_warnings", [])}
        for role in ROLES:
            cases.append({
                "description": f"{region}:{role}",
                "vars": {
                    "region": region,
                    "candidate_sha256": r["candidate_sha256"],
                    "judge_role": role,
                    "views": r["views"],
                    "evidence_files": evidence,
                    "constraints_json": json.dumps(constraints),
                    "run_id_prefix": f"{region}-{role}",
                },
            })
    # Emit as YAML without a PyYAML dependency at read-time for promptfoo (write plain YAML).
    lines = []
    for c in cases:
        lines.append(f"- description: \"{c['description']}\"")
        lines.append("  vars:")
        for k, v in c["vars"].items():
            if isinstance(v, list):
                lines.append(f"    {k}:")
                for it in v:
                    lines.append(f"      - {json.dumps(it)}")
            else:
                lines.append(f"    {k}: {json.dumps(v)}")
    (GEN / "cases.yaml").write_text("\n".join(lines) + "\n")
    (GEN / "cases.json").write_text(json.dumps(cases, indent=2) + "\n")
    print(f"generated {len(cases)} cases (3 regions x {len(ROLES)} roles) -> {GEN/'cases.yaml'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
