"""Valide le catalogue scientifique d'exercices et régénère son rapport (`Sb_SCI_V2_01`).

Applique le schéma versionné (`data/sci/exercise_catalogue.schema.json`), puis les contrôles
qu'un schéma ne peut pas exprimer :

* références de preuve résolues dans E0, essais longitudinaux nommés un à un ;
* capacités d'équipement connues de TRAIN A (registre servi + delta **proposé**) et accordées
  par un objet physique ; aucun accessoire déduit sur une station ;
* une exigence `UNKNOWN` ne se déguise jamais en « aucun matériel » ;
* une identité = une fiche canonique ; un alias porte la science et les faits opérationnels de
  sa fiche canonique ;
* fixtures de régression des erreurs historiques (ruling 11).

Le rapport (`data/sci/exercise_catalogue.validation_report.json`) est **régénéré**, jamais
écrit à la main, et épingle le condensat du catalogue qu'il a validé.

**Pourquoi un moteur de schéma interne.** `jsonschema` n'est pas une dépendance du dépôt (la
CI installe le lock). Ce module applique le sous-ensemble de JSON Schema 2020-12 que le schéma
emploie, et **refuse** tout mot-clé qu'il ne sait pas appliquer au lieu de l'ignorer. Sa
concordance avec `jsonschema` est vérifiée par les tests là où la bibliothèque est installée.

Usage :
    python scripts/validate_sci_catalogue.py            # affiche les métriques
    python scripts/validate_sci_catalogue.py --write    # régénère le rapport
    python scripts/validate_sci_catalogue.py --check    # échoue si le rapport versionné diffère
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = "data/sci/exercise_catalogue.json"
SCHEMA = "data/sci/exercise_catalogue.schema.json"
REPORT = "data/sci/exercise_catalogue.validation_report.json"
EVIDENCE = "data/sci/evidence_registry.json"
POLICY = "data/sci/exposure_credit_policy.json"
DELTA = "data/sci/train_a_delta_proposal.json"
FIXTURES = "data/sci/sources/regression_fixtures.json"
REGISTRY = "data/equipment_registry.json"
EKB = "data/exercise_knowledge_base.json"

#: f.8 — les essais longitudinaux d'hypertrophie du registre, lus un par un (un modèle EMG n'en est pas un)
LONGITUDINAL_HYPERTROPHY_TRIALS = frozenset({"EV-60", "EV-62", "EV-63", "EV-64", "EV-65", "EV-66"})
HEADER_KEYS = ("catalogue_version", "schema_id", "zone_model_version", "credit_policy_version",
               "evidence_registry_version", "equipment_registry_base", "equipment_registry_delta",
               "source_exercise_ids", "sources_digest")
SCHEMA_PREFIX = "schema:"


# ---------------------------------------------------------------------------
# Moteur de schéma (sous-ensemble 2020-12 effectivement employé)
# ---------------------------------------------------------------------------

class UnsupportedSchemaKeyword(ValueError):
    """Le schéma emploie un mot-clé que ce moteur n'applique pas : échouer, ne pas ignorer."""


ANNOTATIONS = frozenset({"$id", "$schema", "$defs", "title", "description", "format"})
ASSERTIONS = frozenset({"type", "enum", "const", "required", "properties", "additionalProperties", "items",
                        "minItems", "maxItems", "uniqueItems", "minLength", "pattern", "minimum", "maximum",
                        "contains", "allOf", "oneOf", "not", "if", "then", "else", "$ref"})
_SUBSCHEMA = ("items", "contains", "not", "if", "then", "else")
_SUBSCHEMA_MAPS = ("properties", "$defs")
_SUBSCHEMA_LISTS = ("allOf", "oneOf")


def _keyword_supported(key: str) -> bool:
    return key in ANNOTATIONS or key in ASSERTIONS or key.startswith("x-")


def unsupported_keywords(schema) -> set[str]:
    """Tout mot-clé du schéma (récursivement) que ce moteur ne sait pas appliquer."""
    if not isinstance(schema, dict):
        return set()
    found = {k for k in schema if not _keyword_supported(k)}
    children = [schema[k] for k in _SUBSCHEMA if k in schema]
    children += [v for k in _SUBSCHEMA_MAPS for v in schema.get(k, {}).values()]
    children += [v for k in _SUBSCHEMA_LISTS for v in schema.get(k, [])]
    if isinstance(schema.get("additionalProperties"), dict):
        children.append(schema["additionalProperties"])
    for child in children:
        found |= unsupported_keywords(child)
    return found


def _json_equal(a, b) -> bool:
    """Égalité JSON : `true` n'égale pas `1`, `1` égale `1.0`."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if _is_number(a) and _is_number(b):
        return a == b
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_json_equal(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_json_equal(x, y) for x, y in zip(a, b, strict=True))
    return type(a) is type(b) and a == b


def _is_number(x) -> bool:
    return isinstance(x, int | float) and not isinstance(x, bool)


_TYPES = {
    "object": lambda x: isinstance(x, dict),
    "array": lambda x: isinstance(x, list),
    "string": lambda x: isinstance(x, str),
    "boolean": lambda x: isinstance(x, bool),
    "null": lambda x: x is None,
    "number": _is_number,
    "integer": lambda x: _is_number(x) and float(x).is_integer(),
}


@dataclass
class _Ctx:
    root: dict
    errors: list = field(default_factory=list)


def _fail(ctx: _Ctx, path: tuple, message: str) -> None:
    ctx.errors.append((path, message))


def _valid(instance, schema, ctx: _Ctx) -> bool:
    probe = _Ctx(ctx.root)
    _check(instance, schema, probe, ())
    return not probe.errors


def _check_generic(instance, schema: dict, ctx: _Ctx, path: tuple) -> None:
    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_TYPES[t](instance) for t in types):
            _fail(ctx, path, f"{instance!r:.60} is not of type {schema['type']}")
    if "enum" in schema and not any(_json_equal(instance, e) for e in schema["enum"]):
        _fail(ctx, path, f"{instance!r:.60} is not one of the allowed values")
    if "const" in schema and not _json_equal(instance, schema["const"]):
        _fail(ctx, path, f"{instance!r:.60} is not {schema['const']!r}")


def _check_object(instance: dict, schema: dict, ctx: _Ctx, path: tuple) -> None:
    for key in schema.get("required", []):
        if key not in instance:
            _fail(ctx, path, f"{key!r} is a required property")
    props = schema.get("properties", {})
    for key, value in instance.items():
        if key in props:
            _check(value, props[key], ctx, (*path, key))
        elif schema.get("additionalProperties") is False:
            _fail(ctx, path, f"additional property {key!r} is not allowed")
        elif isinstance(schema.get("additionalProperties"), dict):
            _check(value, schema["additionalProperties"], ctx, (*path, key))


def _check_array(instance: list, schema: dict, ctx: _Ctx, path: tuple) -> None:
    if "minItems" in schema and len(instance) < schema["minItems"]:
        _fail(ctx, path, f"expected at least {schema['minItems']} items")
    if "maxItems" in schema and len(instance) > schema["maxItems"]:
        _fail(ctx, path, f"expected at most {schema['maxItems']} items")
    if schema.get("uniqueItems") and any(_json_equal(a, b) for i, a in enumerate(instance)
                                         for b in instance[i + 1:]):
        _fail(ctx, path, "items are not unique")
    if "items" in schema:
        for i, item in enumerate(instance):
            _check(item, schema["items"], ctx, (*path, i))
    if "contains" in schema and not any(_valid(item, schema["contains"], ctx) for item in instance):
        _fail(ctx, path, "no item matches 'contains'")


def _check_scalar(instance, schema: dict, ctx: _Ctx, path: tuple) -> None:
    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            _fail(ctx, path, f"shorter than {schema['minLength']} characters")
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            _fail(ctx, path, f"{instance!r:.60} does not match {schema['pattern']!r}")
    if _is_number(instance):
        if "minimum" in schema and instance < schema["minimum"]:
            _fail(ctx, path, f"{instance} is less than {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            _fail(ctx, path, f"{instance} is greater than {schema['maximum']}")


def _check_combinators(instance, schema: dict, ctx: _Ctx, path: tuple) -> None:
    for sub in schema.get("allOf", []):
        _check(instance, sub, ctx, path)
    if "oneOf" in schema:
        matches = sum(_valid(instance, sub, ctx) for sub in schema["oneOf"])
        if matches != 1:
            _fail(ctx, path, f"matches {matches} of the oneOf alternatives (exactly 1 required)")
    if "not" in schema and _valid(instance, schema["not"], ctx):
        _fail(ctx, path, "matches a 'not' schema")
    if "if" in schema:
        branch = "then" if _valid(instance, schema["if"], ctx) else "else"
        if branch in schema:
            _check(instance, schema[branch], ctx, path)


def _resolve(ref: str, root: dict) -> dict:
    if not ref.startswith("#/"):
        raise UnsupportedSchemaKeyword(f"$ref non local : {ref}")
    node = root
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def _check(instance, schema, ctx: _Ctx, path: tuple) -> None:
    if schema is True or schema == {}:
        return
    if schema is False:
        _fail(ctx, path, "no value is allowed here")
        return
    unknown = {k for k in schema if not _keyword_supported(k)}
    if unknown:
        raise UnsupportedSchemaKeyword(f"mots-clés non appliqués : {sorted(unknown)}")
    if "$ref" in schema:
        _check(instance, _resolve(schema["$ref"], ctx.root), ctx, path)
    _check_generic(instance, schema, ctx, path)
    if isinstance(instance, dict):
        _check_object(instance, schema, ctx, path)
    elif isinstance(instance, list):
        _check_array(instance, schema, ctx, path)
    else:
        _check_scalar(instance, schema, ctx, path)
    _check_combinators(instance, schema, ctx, path)


def schema_errors(instance, schema: dict) -> list[tuple[tuple, str]]:
    """Erreurs de `instance` contre `schema` : liste de (chemin, message), vide si valide."""
    ctx = _Ctx(schema)
    _check(instance, schema, ctx, ())
    return ctx.errors


# ---------------------------------------------------------------------------
# Entrées
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Inputs:
    schema: dict
    evidence: dict
    source_ids: tuple[str, ...]
    registry: dict
    delta: dict
    fixtures: list
    credit_policy_id: str


def _read(root: Path, rel: str):
    return json.loads((root / rel).read_text(encoding="utf-8"))


def parse(raw: bytes) -> dict:
    return json.loads(raw)


def load_catalogue_doc(root: Path = ROOT) -> dict:
    return parse((root / CATALOGUE).read_bytes())


def load_inputs(root: Path = ROOT) -> Inputs:
    ekb = _read(root, EKB)["exercises"]
    return Inputs(schema=_read(root, SCHEMA), evidence=_read(root, EVIDENCE),
                  source_ids=tuple(sorted(e["variant_key"] for e in ekb.values())),
                  registry=_read(root, REGISTRY), delta=_read(root, DELTA),
                  fixtures=_read(root, FIXTURES)["fixtures"], credit_policy_id=_read(root, POLICY)["policy_id"])


# ---------------------------------------------------------------------------
# Contrôles
# ---------------------------------------------------------------------------


def _roles(r: dict) -> dict[str, str]:
    return {c["zone"]: c["role"] for c in r["exercise_science"]["contributions"]}


def _caps_of(r: dict) -> list[str]:
    out: list[str] = []
    for member in r["exercise_operational"].get("equipment_requirements", []):
        out += member["any_of"] if isinstance(member, dict) else [member]
    return out


def _vocabulary(inputs: Inputs) -> tuple[set[str], set[str], list[str]]:
    """Capacités connues, capacités accordées par un objet, et erreurs du delta (accessoire déduit)."""
    known = set(inputs.registry["capabilities"]) | set(inputs.delta.get("new_capabilities", {}))
    granted = {c for item in inputs.registry["items"] for c in item.get("capabilities", [])}
    granted |= {c for item in inputs.delta.get("new_items", []) for c in item.get("capabilities", [])}
    errors = []
    for add in inputs.delta.get("item_capability_additions", []):
        granted |= set(add.get("add_capabilities", []))
        errors += [f"delta: inferred accessory — {add['item_id']} granted {cap}"
                   for cap in add.get("add_capabilities", []) if cap.startswith("cable_attachment_")]
    return known, granted, errors


def _header_errors(doc: dict, inputs: Inputs) -> list[str]:
    header = doc.get("catalogue_header", {})
    errors = [f"header: {k} missing" for k in HEADER_KEYS if k not in header]
    expected = {"schema_id": inputs.schema.get("$id"), "credit_policy_version": inputs.credit_policy_id,
                "equipment_registry_base": inputs.registry.get("version"),
                "equipment_registry_delta": inputs.delta.get("delta_version"),
                "source_exercise_ids": list(inputs.source_ids)}
    errors += [f"header: {k} must be {v!r:.80}" for k, v in expected.items() if k in header and header[k] != v]
    return errors


def _coverage_errors(doc: dict, inputs: Inputs) -> list[str]:
    ids = [r.get("exercise_id") for r in doc.get("records", [])]
    errors = []
    for label, bad in (("missing records", sorted(set(inputs.source_ids) - set(ids))),
                       ("unknown exercise_id", sorted(set(ids) - set(inputs.source_ids))),
                       ("duplicate exercise_id", sorted({i for i in ids if ids.count(i) > 1}))):
        if bad:
            errors.append(f"{label}: {bad}")
    if ids != sorted(ids):
        errors.append("records are not sorted by exercise_id")
    return errors


def _contribution_reasons(r: dict, inputs: Inputs) -> list[str]:
    contribs = r["exercise_science"]["contributions"]
    zones = [c["zone"] for c in contribs]
    reasons = [f"zone listed twice: {z}" for z in sorted({z for z in zones if zones.count(z) > 1})]
    for c in contribs:
        reasons += [f"evidence_ref not in E0: {ev}" for ev in c["evidence_refs"] if ev not in inputs.evidence]
        if c["role_basis"] == "longitudinal_trial" and not set(c["evidence_refs"]) & LONGITUDINAL_HYPERTROPHY_TRIALS:
            reasons.append(f"longitudinal_trial without a longitudinal hypertrophy trial: {c['zone']}")
        reasons += [f"sub_region prefix ≠ zone: {sr['id']}" for sr in c.get("sub_regions", []) or []
                    if not sr["id"].startswith(c["zone"] + ".")]
    return reasons


def _equipment_reasons(r: dict, known: set[str], granted: set[str]) -> list[str]:
    op = r["exercise_operational"]
    reasons = []
    if op["equipment_requirement_status"] == "RESOLVED" and not op["equipment_requirements"] \
            and op["equipment_mode"] != "bodyweight":
        reasons.append(f"RESOLVED [] (no equipment) on a {op['equipment_mode']} exercise — an unknown requirement "
                       "must stay UNKNOWN, never become no-equipment")
    for cap in _caps_of(r):
        if cap not in known:
            reasons.append(f"capability not in TRAIN A (registry + proposed delta): {cap}")
        elif cap not in granted:
            reasons.append(f"capability granted by no physical object: {cap}")
    return reasons


def _record_reasons(r: dict, inputs: Inputs, known: set[str], granted: set[str]) -> list[str]:
    reasons = [f"{SCHEMA_PREFIX} {'/'.join(map(str, p)) or '<root>'}: {m[:160]}"
               for p, m in sorted(schema_errors(r, inputs.schema), key=lambda e: [str(x) for x in e[0]])]
    if reasons:  # les contrôles suivants supposent une fiche valide au schéma
        return reasons
    return _contribution_reasons(r, inputs) + _equipment_reasons(r, known, granted)


def _strip_curation(op: dict) -> dict:
    return {k: v for k, v in op.items() if k != "curation"}


def _alias_reasons(alias: dict, canon: dict) -> list[str]:
    """Un alias EST son mouvement canonique : il y pointe, et en porte la science et les faits opérationnels."""
    reasons = []
    if alias["identity"]["alias_of"] != canon["exercise_id"]:
        reasons.append(f"alias_of must be {canon['exercise_id']}")
    if alias["exercise_science"] != canon["exercise_science"]:
        reasons.append("legacy alias science differs from its canonical record")
    if _strip_curation(alias["exercise_operational"]) != _strip_curation(canon["exercise_operational"]):
        reasons.append("legacy alias operational facts differ from its canonical record")
    return reasons


def _identity_errors(records: list[dict], per_record: dict[str, list[str]]) -> list[str]:
    identities: dict[str, list[dict]] = {}
    for r in records:
        if "identity" in r and not _schema_failed(per_record, r["exercise_id"]):
            identities.setdefault(r["identity"]["scientific_identity_id"], []).append(r)
    errors = []
    for ident, members in sorted(identities.items()):
        canon = [m for m in members if m["identity"]["identity_relation"] == "CANONICAL"]
        if len(canon) != 1:
            errors.append(f"identity {ident}: {len(canon)} CANONICAL records (exactly 1 required)")
            continue
        for alias in (m for m in members if m is not canon[0]):
            per_record[alias["exercise_id"]] += _alias_reasons(alias, canon[0])
    return errors


def _schema_failed(per_record: dict[str, list[str]], rid: str) -> bool:
    reasons = per_record.get(rid, [])
    return bool(reasons) and reasons[0].startswith(SCHEMA_PREFIX)


def _fixture_reasons(r: dict, a: dict) -> list[str]:
    rr = _roles(r)
    prim = {z for z, v in rr.items() if v == "PRIMARY"}
    caps = _caps_of(r)
    bad = [f"zone {z} present" for z in a.get("zone_absent", []) if z in rr]
    bad += [f"{z} not PRIMARY" for z in a.get("primary_includes", []) if z not in prim]
    if "pattern_is" in a and r["exercise_science"]["movement_pattern"] != a["pattern_is"]:
        bad.append(f"pattern ≠ {a['pattern_is']}")
    if "equipment_mode_is" in a and r["exercise_operational"]["equipment_mode"] != a["equipment_mode_is"]:
        bad.append(f"equipment_mode ≠ {a['equipment_mode_is']}")
    bad += [f"capability {c} present" for c in a.get("capability_absent", []) if c in caps]
    if a.get("capability_any_prefix") and not any(c.startswith(p) for c in caps for p in a["capability_any_prefix"]):
        bad.append(f"no capability with prefix {a['capability_any_prefix']}")
    return bad


def _apply_fixtures(by_id: dict, fixtures: list, per_record: dict[str, list[str]]) -> None:
    for fx in fixtures:
        for rid in fx["exercise_ids"]:
            if rid in by_id and not _schema_failed(per_record, rid):
                per_record[rid] += [f"{fx['id']}: {b}" for b in _fixture_reasons(by_id[rid], fx["assert"])]


# ---------------------------------------------------------------------------
# Vue dérivée et métriques
# ---------------------------------------------------------------------------


def _report_row(r: dict, reasons: list[str]) -> dict:
    rid = r["exercise_id"]
    if reasons and reasons[0].startswith(SCHEMA_PREFIX):
        return {"exercise_id": rid, "publishable": False, "compiler_candidate": False, "resolved_primary_zones": [],
                "primary_blocked_zones": [], "coverage_zones": [], "exposure_vector_complete": False,
                "blocking_reasons": reasons}
    c = r["exercise_science"]["contributions"]
    resolved = sorted(x["zone"] for x in c if x["role"] == "PRIMARY" and x["role_basis"] != "unresolved")
    blocked = sorted(x["zone"] for x in c if x["role"] == "UNKNOWN")
    blocking = list(reasons)
    if r["exercise_operational"]["curation"]["status"] != "reviewed":
        blocking.append(f"curation.status = {r['exercise_operational']['curation']['status']}")
    if not resolved:
        blocking.append("no resolved PRIMARY contribution")
    publishable = not blocking
    return {"exercise_id": rid, "publishable": publishable,
            "compiler_candidate": publishable and r["identity"]["identity_relation"] == "CANONICAL",
            "resolved_primary_zones": resolved, "primary_blocked_zones": blocked,
            "coverage_zones": sorted(x["zone"] for x in c if x["role"] in ("PRIMARY", "SECONDARY")),
            "exposure_vector_complete": not blocked, "blocking_reasons": blocking}


def _count(records: list[dict], pred) -> int:
    return sum(1 for r in records if pred(r))


def _metrics(records: list[dict], rows: list[dict], inputs: Inputs, format_errors: list[str]) -> dict:
    canonical = [r for r in records if r.get("identity", {}).get("identity_relation") == "CANONICAL"]
    status: dict[str, int] = {}
    for r in records:
        s = r["exercise_operational"]["curation"]["status"]
        status[s] = status.get(s, 0) + 1
    return {
        "source_records": f"{len(records)}/{len(inputs.source_ids)}",
        "format_errors": len(format_errors),
        "status": dict(sorted(status.items())),
        "publishable": _count(rows, lambda x: x["publishable"]),
        "compiler_candidates": _count(rows, lambda x: x["compiler_candidate"]),
        "canonical_identities": len({r["identity"]["scientific_identity_id"] for r in canonical}),
        "legacy_aliases": _count(records, lambda r: r.get("identity", {}).get("identity_relation") == "LEGACY_ALIAS"),
        "canonical_by_classification": {c: _count(canonical, lambda r, c=c: r["identity"]["group_classification"] == c)
                                        for c in ("UNIQUE", "EXACT_CANONICAL_DUPLICATE", "LEGITIMATE_VARIANT",
                                                  "UNRESOLVED")},
        "aliases_by_merge_basis": {b: _count(records, lambda r, b=b: r.get("identity", {}).get("merge_basis") == b)
                                   for b in ("source_facts", "operator_definition")},
        "incomplete_exposure_vectors": _count(rows, lambda x: not x["exposure_vector_complete"]),
        "equipment_requirements_unknown": _count(
            records, lambda r: r["exercise_operational"].get("equipment_requirement_status") == "UNKNOWN"),
        "machine_unspecified": _count(records, lambda r: r["exercise_operational"].get("equipment_mode")
                                      == "machine_unspecified"),
        "true_any_of_requirements": _count(canonical, lambda r: any(
            isinstance(m, dict) for m in r["exercise_operational"].get("equipment_requirements", []))),
        "content_execution_mismatches": _count(records, lambda r: "content_alignment" in r),
        "regression_fixtures": len(inputs.fixtures),
    }


@dataclass(frozen=True)
class Result:
    format_errors: list[str]
    records: list[dict]
    metrics: dict


def validate(doc: dict, inputs: Inputs) -> Result:
    records = doc.get("records", [])
    by_id = {r.get("exercise_id"): r for r in records}
    known, granted, delta_errors = _vocabulary(inputs)
    format_errors = _header_errors(doc, inputs) + _coverage_errors(doc, inputs) + delta_errors
    per_record = {r["exercise_id"]: _record_reasons(r, inputs, known, granted) for r in records}
    format_errors += _identity_errors(records, per_record)
    _apply_fixtures(by_id, inputs.fixtures, per_record)
    rows = [_report_row(r, per_record[r["exercise_id"]]) for r in records]
    format_errors += [f"{r['exercise_id']}: {x}" for r in records for x in per_record[r["exercise_id"]]]
    return Result(format_errors=format_errors, records=rows, metrics=_metrics(records, rows, inputs, format_errors))


def render_report(result: Result, catalogue_raw: bytes) -> bytes:
    header = parse(catalogue_raw).get("catalogue_header", {})
    report = {"catalogue_version": header.get("catalogue_version"),
              "catalogue_digest": hashlib.sha256(catalogue_raw).hexdigest(),
              "metrics": result.metrics, "format_errors": result.format_errors, "records": result.records}
    return (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main(argv: list[str]) -> int:
    raw = (ROOT / CATALOGUE).read_bytes()
    result = validate(parse(raw), load_inputs(ROOT))
    report = render_report(result, raw)
    print(json.dumps(result.metrics, ensure_ascii=False, indent=1))
    for e in result.format_errors[:80]:
        print("  -", e)
    if "--write" in argv:
        (ROOT / REPORT).write_bytes(report)
    if "--check" in argv and (ROOT / REPORT).read_bytes() != report:
        print(f"DRIFT {REPORT} — régénérer avec scripts/validate_sci_catalogue.py --write")
        return 1
    return 1 if result.format_errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
