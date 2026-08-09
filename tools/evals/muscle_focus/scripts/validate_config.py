#!/usr/bin/env python3
"""Structural validation of the versioned harness config + schemas — GO C2 §16.
Does not run the Promptfoo binary (a live run needs a provider credential + supported Node); it checks
the config/schema shape so the harness is known-good and reproducible. Stdlib + PyYAML."""
from __future__ import annotations

import json
import pathlib

HARNESS = pathlib.Path(__file__).resolve().parent.parent


def main() -> int:
    import yaml
    e = []
    cfg = yaml.safe_load((HARNESS / "promptfooconfig.yaml").read_text())
    for k in ("description", "providers", "prompts", "tests", "defaultTest"):
        if k not in cfg:
            e.append(f"config missing key: {k}")
    provs = cfg.get("providers", [])
    if not provs or provs[0].get("config", {}).get("apiKeyRequired") is not False:
        e.append("mandatory provider must set apiKeyRequired: false")
    if len(cfg.get("prompts", [])) != 5:
        e.append(f"expected 5 judge prompts, got {len(cfg.get('prompts', []))}")
    raw = (HARNESS / "promptfooconfig.yaml").read_text().lower()
    for tok in ("sk-ant-", "sk-proj-", "api_key:", "apikey:"):
        if tok in raw:
            e.append(f"possible credential token in config: {tok}")
    for sch in ("agent_review.schema.json", "aggregate_review.schema.json"):
        try:
            json.loads((HARNESS / "schemas" / sch).read_text())
        except Exception as ex:
            e.append(f"schema {sch} invalid JSON: {ex}")
    for reg in ("common", "chest", "shoulders", "posterior"):
        try:
            yaml.safe_load((HARNESS / "rubrics" / f"{reg}.yaml").read_text())
        except Exception as ex:
            e.append(f"rubric {reg} invalid YAML: {ex}")
    w = yaml.safe_load((HARNESS / "rubrics" / "common.yaml").read_text())["weights"]
    if sum(w.values()) != 100:
        e.append(f"weights total {sum(w.values())} != 100")
    print("PROMPTFOO CONFIG + SCHEMA VALIDATION:\n" + ("PASS" if not e else "FAIL"))
    for x in e:
        print(f"  - {x}")
    return 0 if not e else 1


if __name__ == "__main__":
    raise SystemExit(main())
