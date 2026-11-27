"""Data-only provenance: no historical Python import, writer or engine execution."""

from __future__ import annotations

import hashlib
import json
import os
import stat
from copy import deepcopy
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path

from .contracts import iso
from .limits import ReadLimits
from .sqlite_source import bounded_json

BASE = "docs/science/sci-p02-initial-policy/"
V3_AUTHORITY_FIELDS = (
    "contract_version",
    "engine_version",
    "policy_version",
    "binding_ref",
    "binding_digest",
    "bundle_digest",
    "effective_science_digest",
    "request_fingerprint",
    "observation_fingerprint",
    "full_evaluation_fingerprint",
    "plan_time_fingerprint",
    "start_policy_ref",
)
ROOT_PINS = {
    BASE
    + "stage2-v3/authority/registry.v1.json": "602ff0d32ebc625b4c9474660b5b36ee9983c4c598f16ae9b1269e67e5cea50f",
    BASE
    + "stage2-v3/authority/sources.v1.json": "a90d4868eea9cc75106163bdb35de3512c817577740343a99b2ad5c85b3e8c24",
    BASE
    + "calibration-time-01/policy.v1.json": "08a4834113b01f1417a9f45a5c7195c9d6c24c4dd8d1dd72d982b0c51aa73462",
    BASE + "v1/policy.json": "8aef079da6a15298bfa2ec1bdec1b417588b6f535224c61afb2f50f98612dfb4",
    BASE
    + "curation-01/candidates.v1.json": "d1a3f26268bcb33d3614ce3b4841a2dc42562541b39134646caabf9f37f37803",
    BASE
    + "pull-exposure-01/overlay.v1.json": "7aa247871658d62a00f02836e768d1bdc3ff3aa248f236660ab99efa2dbc75a1",
}


def digest(value, *, pretty=False):
    options = {"indent": 2} if pretty else {"separators": (",", ":")}
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, **options)
    return hashlib.sha256((raw + ("\n" if pretty else "")).encode()).hexdigest()


@dataclass
class SourceBudget:
    files: int = 0
    total: int = 0


class CatalogueReadContext:
    """Private parsing templates for one owned read; never an authority verdict."""

    def __init__(self, owner_id, profile_digest):
        self._scope = (owner_id, profile_digest)
        self._valid = True
        self._authority = None
        self._templates = {}

    def invalidate(self):
        self._templates.clear()
        self._authority = None

    def check_scope(self, owner_id, profile_digest):
        if not self._valid or self._scope != (owner_id, profile_digest):
            self.invalidate()
            self._valid = False
            raise ValueError("catalogue_context_mismatch")

    def bind_authority(self, authority):
        identity = digest(authority)
        if self._authority is not None and self._authority != identity:
            self.invalidate()
        self._authority = identity

    def seed(self, admitted):
        path = "data/sci/exercise_catalogue.json"
        raw = admitted.read(path)
        projection = admitted.catalogue_view()
        expected = admitted.pins[path]
        if hashlib.sha256(raw).hexdigest() != expected or projection.source_sha256 != expected:
            self.invalidate()
            raise ValueError("source_digest_mismatch")
        if len(self._templates) < 2:
            self._templates[(expected, admitted.limits)] = deepcopy(projection)

    def catalogue(self, raw, expected, limits):
        from .catalogue_source import project_catalogue

        if not self._valid:
            raise ValueError("catalogue_context_mismatch")
        if hashlib.sha256(raw).hexdigest() != expected:
            self.invalidate()
            raise ValueError("source_digest_mismatch")
        key = (expected, limits)
        template = self._templates.get(key)
        if template is not None:
            if template.source_sha256 != expected:
                self.invalidate()
                raise ValueError("source_digest_mismatch")
            return replace(template, document=deepcopy(template.document))
        projection = project_catalogue(raw, expected, limits)
        if len(self._templates) < 2:
            self._templates[key] = deepcopy(projection)
        return projection


class SourceView:
    """Bounded immutable bytes. Bundle code is verified as bytes, never executed."""

    def __init__(
        self, root, limits=ReadLimits(), expected=None, budget=None, catalogue_context=None
    ):
        self.root = Path(root).resolve(strict=True)
        self.limits = limits
        self.expected = expected
        self.raw = {}
        self.pins = {}
        self.budget = budget or SourceBudget()
        self.v3 = None
        self.bundle_root = None
        self.catalogue_context = catalogue_context

    def read(self, relative, expected=None, *, cap=None):
        if relative in self.raw:
            if expected and self.pins[relative] != expected:
                raise ValueError("source_digest_mismatch")
            return self.raw[relative]
        path = Path(relative)
        if (
            path.is_absolute()
            or ".." in path.parts
            or not path.parts
            or path.suffix in {".pyc", ".pyo"}
        ):
            raise ValueError("invalid_source_path")
        current = self.root
        for part in path.parts:
            current = current / part
            if current.is_symlink():
                raise ValueError("source_symlink")
        cap = min(cap or self.limits.source_total, self.limits.source_total - self.budget.total)
        if self.budget.files >= self.limits.source_files:
            raise ValueError("source_file_limit")
        descriptor = os.open(current, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | os.O_NONBLOCK)
        try:
            before = os.fstat(descriptor)
            if not stat.S_ISREG(before.st_mode) or before.st_size > cap:
                raise ValueError("source_byte_limit")
            with os.fdopen(descriptor, "rb", closefd=False) as file:
                raw = file.read(cap + 1)
            after = os.fstat(descriptor)
            if len(raw) > cap or (before.st_size, before.st_mtime_ns, before.st_ino) != (
                after.st_size,
                after.st_mtime_ns,
                after.st_ino,
            ):
                raise ValueError("source_changed")
        finally:
            os.close(descriptor)
        actual = hashlib.sha256(raw).hexdigest()
        pinned = expected or (self.expected or {}).get(relative)
        if self.expected is not None and pinned is None or pinned is not None and actual != pinned:
            raise ValueError("source_digest_mismatch")
        self.budget.total += len(raw)
        self.budget.files += 1
        self.raw[relative] = raw
        self.pins[relative] = actual
        return raw

    def json(self, relative, expected=None, *, cap=None):
        return bounded_json(self.read(relative, expected, cap=cap), self.limits)

    def catalogue_view(self):
        from .catalogue_source import project_catalogue

        if not hasattr(self, "_catalogue_projection"):
            path = "data/sci/exercise_catalogue.json"
            raw = self.read(path)
            self._catalogue_projection = (
                self.catalogue_context.catalogue(raw, self.pins[path], self.limits)
                if self.catalogue_context is not None
                else project_catalogue(raw, self.pins[path], self.limits)
            )
        return self._catalogue_projection

    @classmethod
    def local(cls, root=None, *, limits=ReadLimits(), expected=None, catalogue_context=None):
        return cls(
            root or Path(__file__).resolve().parents[3],
            limits,
            expected,
            catalogue_context=catalogue_context,
        )

    @classmethod
    def bundle(
        cls,
        root,
        packaging_digest,
        *,
        limits=ReadLimits(),
        budget=None,
        catalogue_context=None,
        authority=None,
    ):
        if catalogue_context is not None:
            catalogue_context.bind_authority(authority or {"packaging_digest": packaging_digest})
        try:
            return cls._bundle(root, packaging_digest, limits, budget, catalogue_context)
        except (OSError, ValueError, TypeError, KeyError):
            if catalogue_context is not None:
                catalogue_context.invalidate()
            raise

    @classmethod
    def _bundle(cls, root, packaging_digest, limits, budget, catalogue_context):
        if (
            type(packaging_digest) is not str
            or len(packaging_digest) != 64
            or any(char not in "0123456789abcdef" for char in packaging_digest)
        ):
            raise ValueError("source_digest_invalid")
        view = cls(root, limits, budget=budget, catalogue_context=catalogue_context)
        manifest = view.json("packaging-manifest.v1.json", packaging_digest, cap=131072)
        if manifest["contract_version"] != "plan-v3-private-science-bundle/1.0.0" or manifest.get(
            "calibration_inventory_version"
        ) not in (None, "plan-calibration-inventory/2.0.0"):
            raise ValueError("unsupported_source_inventory")
        pins = manifest["sha256"]
        if type(pins) is not dict or len(pins) + 1 > limits.source_files:
            raise ValueError("source_file_limit")
        for relative, expected in pins.items():
            if type(expected) is not str or len(expected) != 64:
                raise ValueError("source_digest_invalid")
            view.read(relative, expected)
        # Transitive historical pin constraints refer to those historical bytes.
        for relative, expected in ROOT_PINS.items():
            if pins.get(relative) != expected:
                raise ValueError("root_authority_not_attested")
            view.read(relative, expected)
        authorities = [
            BASE + "stage2-v3/authority/sources.v1.json",
            BASE + "calibration-time-01/SOURCE_PINS.json",
        ]
        for relative in authorities:
            for path, expected in view.json(relative)["sha256"].items():
                if pins.get(path) != expected:
                    raise ValueError("historical_source_not_attested")
                view.read(path, expected)
        for relative, field in [
            (BASE + "v1/policy.json", "source_hashes"),
            (BASE + "curation-01/candidates.v1.json", "source_sha256"),
            (BASE + "pull-exposure-01/overlay.v1.json", "source_sha256"),
        ]:
            for path, expected in view.json(relative)[field].items():
                if pins.get(path) != expected:
                    raise ValueError("historical_source_not_attested")
                view.read(path, expected)
        p = view.json(BASE + "calibration-time-01/policy.v1.json")
        view.read(p["source_manifest"], p["source_manifest_sha256"])
        view.v3 = compose_effective(view)
        policy = view.json(BASE + "stage2-v3/authority/registry.v1.json")
        source_pins = view.json(BASE + "stage2-v3/authority/sources.v1.json")["sha256"]
        binding = digest(
            {
                "policy": policy,
                "sources": source_pins,
                "historical_bundle": view.v3["bundle_digest"],
            },
            pretty=True,
        )
        view.v3.update(
            binding_ref=policy["binding_ref"],
            binding_digest=binding,
            bundle_digest=digest(
                {"binding": binding, "historical_bundle": view.v3["bundle_digest"]}, pretty=True
            ),
            registry_digest=ROOT_PINS[BASE + "stage2-v3/authority/registry.v1.json"],
            engine_version=policy["engine_version"],
            policy_version=policy["policy_version"],
        )
        if manifest.get("calibration_inventory_version"):
            verify_extension(view, manifest)
        return view


def verify_extension(view, manifest):
    directory = BASE + "calibration-six-extensions/authority/"
    registry = view.json(
        directory + "registry.v1.json",
        "a0c9a20a48490bb47272c7b8e03edc3b06ef4369e0eaf671bdd45eff39acb6ff",
    )
    sources = view.json(
        directory + "sources.v1.json",
        "d89b9308891b7e7c98a5a750ba7acdcc53825d06824cd236d2aefa4c7e4cc95f",
    )["sha256"]
    for path, expected in sources.items():
        if view.pins.get(path) != expected:
            raise ValueError("extension_source_not_attested")
        view.read(path, expected)
    parent = view.v3["bundle_digest"]
    if registry["v3_bundle_digest"] != parent or manifest.get(
        "calibration_extension_bundle_digest"
    ) != digest(dict(policy=registry, sources=sources, v3_bundle=parent), pretty=True):
        raise ValueError("extension_authority_mismatch")
    # Exposure roles still come exclusively from the historical effective catalogue.


def compose_effective(view):
    """Byte-attested pure counterpart of v2_registry._candidate_records/_build_registry."""
    p = view.json(
        BASE + "calibration-time-01/policy.v1.json",
        ROOT_PINS[BASE + "calibration-time-01/policy.v1.json"],
    )
    pins = view.json(p["source_manifest"], p["source_manifest_sha256"])["sha256"]
    curation = view.json(
        BASE + "curation-01/candidates.v1.json", ROOT_PINS[BASE + "curation-01/candidates.v1.json"]
    )
    pull = view.json(
        BASE + "pull-exposure-01/overlay.v1.json",
        ROOT_PINS[BASE + "pull-exposure-01/overlay.v1.json"],
    )
    legacy = view.json(BASE + "v1/policy.json", ROOT_PINS[BASE + "v1/policy.json"])
    records = {r["exercise_id"]: r for r in view.catalogue_view().document["records"]}
    overlays = {r["candidate_id"]: r for r in pull["candidates"]}
    candidates = {}
    for row in curation["candidates"]:
        other = overlays.get(row["candidate_id"])
        definition = (
            other["canonical_execution"]
            if other
            else records[row["candidate_id"]]["exercise_science"].get("canonical_execution")
        )
        profile = dict(
            candidate_id=row["candidate_id"],
            loaded_joint_actions=row["loaded_joint_actions"],
            support_setup=row["support_setup"],
            canonical_execution=definition,
        )
        candidates[row["candidate_id"]] = dict(
            candidate_id=row["candidate_id"],
            intent_id=row["intent_id"],
            admission=other["initial_scope_admission"] if other else row["initial_scope_admission"],
            unilateral=row["unilateral"],
            joint_type=row["joint_type"],
            source_roles=row["roles"],
            effective_roles=other["effective_roles"] if other else row["roles"],
            requires_qualified_role_projection=other is not None,
            realization_ref="initial-candidate-realisation/1.0.0@" + digest(profile),
        )
    admission = view.json(p["dose_source"])
    rules = {r["rule_id"]: r["value"] for r in admission["rules"]}
    dose = dict(
        source_version=admission["policy_version"],
        cadences=rules["scope"]["cadences"],
        work_sets=rules["work_sets"],
        rep_range=rules["repetitions"],
        rir_target=rules["effort"]["rir_target"],
        rest_seconds=rules["rest"],
        intents=legacy["intents"],
    )
    science = digest(dict(candidate_records=candidates, dose=dose, source_hashes=pins))
    return dict(
        candidates=candidates,
        effective_science_digest=science,
        effective_catalogue_version="initial-plan-effective-catalogue/1.0.0@" + science,
        bundle_digest=digest(
            dict(policy_sha256=ROOT_PINS[BASE + "calibration-time-01/policy.v1.json"], sources=pins)
        ),
    )


def canonical_time(value):
    if value is None:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed.astimezone(UTC)


@dataclass(frozen=True)
class QualifiedFact:
    fact: dict
    outside: bool


def _operation(row):
    if row is None:
        return None
    return dict(
        op_id=row["op_id"],
        expected_revision=row["expected_revision"],
        applied_revision=row["applied_revision"],
        body_digest=row["body_digest"],
        recorded_at=iso(canonical_time(row["recorded_at"])),
    )


def _receipt_chain(capture, c, slot, provenance, at, as_of):
    rows = capture.operation_rows(c["set_log_id"])
    if not rows or capture.truncated or any(r["reasons"] for r in rows):
        raise ValueError("RECEIPT_CHAIN_TRUNCATED")
    for index, row in enumerate(rows):
        receipt, observation = row["receipt"], row["observation"]
        material = dict(
            session_id=c["session_id"],
            set_id=c["set_log_id"],
            expected_revision=row["expected_revision"],
            observation=observation,
        )
        if digest(material) != row["body_digest"]:
            # Raw pre-normalization input was not separately persisted. A mismatch
            # may be normalization, not corruption; either way parity is unproven.
            raise ValueError("SOURCE_DIGEST_MISMATCH")
        if (
            row["expected_revision"] != index
            or row["applied_revision"] != index + 1
            or receipt["applied_revision"] != index + 1
            or receipt["op_id"] != row["op_id"]
            or receipt["session_id"] != c["session_id"]
            or receipt["set_id"] != c["set_log_id"]
            or receipt["state"] != "APPLIED"
            or observation["context"] != slot["prescription"]["context"]
        ):
            raise ValueError("CONTRADICTORY_EPISODE")
        if canonical_time(row["recorded_at"]) is None or canonical_time(row["recorded_at"]) > as_of:
            raise ValueError("CONTRADICTORY_EPISODE")
    if (
        not rows[-1]["observation"]["completed"]
        or rows[-1]["observation"]["reps"] != c["reps"]
        or canonical_time(rows[-1]["receipt"]["performed_at"]) != at
    ):
        raise ValueError("CONTRADICTORY_EPISODE")
    origin = next(r for r in rows if r["observation"]["completed"])
    if any(not r["observation"]["completed"] for r in rows[origin["applied_revision"] :]):
        raise ValueError("CONTRADICTORY_EPISODE")
    if canonical_time(origin["receipt"]["performed_at"]) != at:
        raise ValueError("CONTRADICTORY_EPISODE")
    provenance.update(origin_operation=_operation(origin), effective_operation=_operation(rows[-1]))
    estimated = origin["observation"].get("performed_at_estimated")
    adjusted = origin["receipt"].get("performed_at_adjusted")
    context, setting = (
        rows[-1]["observation"]["context"],
        rows[-1]["observation"]["setting"],
    )
    _validate_context(context, setting)
    expected_mass = (
        setting["value"]
        if setting is not None and context["load_semantics"] == "TOTAL_EXTERNAL"
        else None
    )
    if c["weight_kg"] != expected_mass:
        raise ValueError("CONTRADICTORY_EPISODE")
    return context, setting, estimated, adjusted


def _validate_context(context, setting):
    if (
        context["side"] != "BILATERAL"
        or context["load_semantics"]
        not in {"TOTAL_EXTERNAL", "PER_IMPLEMENT", "MACHINE_DISPLAY_KG"}
        or (
            setting is not None
            and (
                setting["kind"] != "MASS_KG"
                or setting["unit"] != "kg"
                or type(setting["value"]) not in (int, float)
                or setting["value"] < 0
            )
        )
    ):
        raise ValueError("CONTRADICTORY_EPISODE")


def qualify_fact(capture, candidate, sources, *, as_of):
    c = candidate
    marker = c["template_slug_snapshot"]
    binding_evidence = capture.binding_for(c["session_id"])
    profile = (
        "V3"
        if marker == "science:v3:first-session"
        else (
            "UNKNOWN"
            if c["reasons"]
            or marker is None
            or marker.startswith("science:")
            or binding_evidence is not None
            else "LEGACY"
        )
    )
    reasons = list(c["reasons"])
    try:
        at = canonical_time(c["completed_at"])
        started = canonical_time(c["started_at"])
    except (ValueError, TypeError):
        at = started = None
        reasons.append("INVALID_EVENT_TIME")
    membership, status = "IN_WINDOW", "CANONICAL_DATE_PARTIAL_ORIGIN"
    if at is None:
        membership, status = "UNKNOWN", "UNKNOWN_MEMBERSHIP"
        reasons.append("NULL_EVENT_TIME")
    elif at > as_of:
        membership, status = "UNKNOWN", "FUTURE"
        reasons.append("FUTURE_EVENT_TIME")
    elif started is None or at < started:
        membership, status = "UNKNOWN", "CONTRADICTORY_EPISODE"
        reasons.append("CONTRADICTORY_EPISODE")
    outside = (
        at is not None
        and membership == "IN_WINDOW"
        and not capture.query.window_start <= at < capture.query.window_until
    )
    provenance = dict(
        profile=profile,
        execution_profile_version=None,
        evaluation_id=None,
        binding_digest=None,
        effective_science_digest=None,
        origin_operation=None,
        effective_operation=None,
        source_status="UNKNOWN",
        reasons=[],
    )
    resolution = dict(
        status="UNKNOWN_IDENTITY",
        query=None,
        step=None,
        variant_key=None,
        scientific_identity_id=None,
        canonical_exercise_id=None,
        catalogue_version=None,
        reason="UNKNOWN_IDENTITY",
    )
    context = setting = None
    contributions = []
    estimated = adjusted = None
    if outside and profile == "LEGACY":
        return QualifiedFact({}, True)
    if profile == "LEGACY":
        resolution, contributions = sources.legacy(capture, c)
        provenance["source_status"] = (
            "QUALIFIED" if resolution["status"] == "RESOLVED" else "UNKNOWN"
        )
        provenance["reasons"] = ["LEGACY_PROVENANCE_NOT_PERSISTED"]
        reasons.append("UNKNOWN_ACQUISITION_SOURCE")
    elif profile == "V3":
        try:
            binding, mapping, slot, effective = qualify_v3(capture, c, sources)
            provenance.update(
                execution_profile_version=binding["execution_profile_version"],
                evaluation_id=binding["evaluation_id"],
                binding_digest=binding["binding_digest"],
                effective_science_digest=effective["effective_science_digest"],
                source_status="QUALIFIED",
            )
            resolution, contributions = sources.v3_resolution(mapping, effective)
            context, setting, estimated, adjusted = _receipt_chain(
                capture, c, slot, provenance, at, as_of
            )
            # Keep the full stored context through receipt/digest verification.
            # The public DTO carries canonical identity only in resolution.
            public_fields = (
                "context_ref",
                "equipment_ref",
                "realization_ref",
                "side",
                "load_semantics",
            )
            if set(context) not in (
                set(public_fields),
                set(public_fields) | {"canonical_exercise_id"},
            ) or (
                "canonical_exercise_id" in context
                and context["canonical_exercise_id"] != mapping["canonical_exercise_id"]
            ):
                raise ValueError("CONTRADICTORY_EPISODE")
            context = {key: context[key] for key in public_fields}
            # Acquisition implementation version is not persisted: no physical-time assertion.
            reasons.append("UNKNOWN_ACQUISITION_SOURCE")
            if estimated:
                reasons.append("ESTIMATED_ORIGIN")
            if adjusted:
                reasons.append("ADJUSTED_ORIGIN")
        except (KeyError, TypeError, ValueError, StopIteration) as exc:
            reason = (
                str(exc)
                if str(exc)
                in {
                    "RECEIPT_CHAIN_TRUNCATED",
                    "CONTRADICTORY_EPISODE",
                    "GRAPH_TRUNCATED",
                    "PROFILE_MISMATCH",
                    "SOURCE_DIGEST_MISMATCH",
                }
                else "EFFECTIVE_CATALOGUE_UNAVAILABLE"
            )
            provenance["source_status"] = "UNKNOWN"
            provenance["reasons"] = [reason]
            context = setting = None
            if outside:
                membership, status, outside = "UNKNOWN", "UNKNOWN_MEMBERSHIP", False
            contributions = []
            resolution["reason"] = reason
            if reason == "CONTRADICTORY_EPISODE":
                membership, status, outside = "UNKNOWN", "CONTRADICTORY_EPISODE", False
                reasons.append(reason)
    else:
        provenance["reasons"] = ["PROFILE_MISMATCH"]
    return QualifiedFact(
        dict(
            key={k: c[k] for k in ("session_id", "session_exercise_id", "set_log_id")},
            kind="work",
            completed=True,
            completed_at=iso(at),
            reps=c["reps"] if type(c["reps"]) is int and 0 <= c["reps"] <= 2147483647 else None,
            weight_kg=c["weight_kg"]
            if (
                profile == "LEGACY"
                or (
                    provenance["source_status"] == "QUALIFIED"
                    and context is not None
                    and context["load_semantics"] == "TOTAL_EXTERNAL"
                )
            )
            and c["weight_kg"] is not None
            and c["weight_kg"] >= 0
            else None,
            prescribed_name=c["exercise_name_snapshot"],
            executed_name=c["substituted_name"] or c["exercise_name_snapshot"],
            resolution=resolution,
            contributions=contributions,
            context=context,
            setting=setting,
            set_index=c["set_index"],
            temporal=dict(
                membership=membership,
                status=status,
                performed_at=iso(at),
                performed_at_estimated=estimated,
                performed_at_adjusted=adjusted,
                reasons=sorted(set(reasons)),
            ),
            provenance=provenance,
        ),
        outside,
    )


def qualify_v3(capture, c, sources):
    binding = capture.binding_for(c["session_id"])
    if (
        not binding
        or binding["reasons"]
        or binding["execution_profile_version"] != "first-plan-execution/3.0.0"
    ):
        raise ValueError("PROFILE_MISMATCH")
    payload = binding["immutable_payload"]
    if digest(payload) != binding["binding_digest"]:
        raise ValueError("SOURCE_DIGEST_MISMATCH")
    evaluation = capture.evaluation_for(binding["evaluation_id"])
    authority = capture.runtime_authority()
    if (
        not evaluation
        or evaluation["reasons"]
        or not authority
        or authority["reasons"]
        or type(authority["generation"]) is not int
        or authority["generation"] <= 0
        or authority["generation"] != evaluation["authority_generation"]
        or authority["generation"] != payload["authority_generation"]
    ):
        raise ValueError("EFFECTIVE_CATALOGUE_UNAVAILABLE")
    captured = evaluation["result"]
    if (
        any(payload["authority"][key] != captured[key] for key in V3_AUTHORITY_FIELDS)
        or payload["scientific_session"] != captured["candidate_plan"]["sessions"][0]
        or payload["allocation_ref"] != captured["candidate_plan"]["allocation_ref"]
    ):
        raise ValueError("SOURCE_DIGEST_MISMATCH")
    view = sources.bundle_for(authority)
    effective = view.v3
    for key in (
        "binding_ref",
        "binding_digest",
        "bundle_digest",
        "effective_science_digest",
        "engine_version",
        "policy_version",
    ):
        if payload["authority"][key] != effective[key]:
            raise ValueError("SOURCE_DIGEST_MISMATCH")
    for key in ("registry_digest", "binding_digest", "bundle_digest", "effective_science_digest"):
        if authority["publication"][key] != effective[key]:
            raise ValueError("SOURCE_DIGEST_MISMATCH")
    graph = capture.graph_for(c["session_id"])
    if capture.truncated:
        raise ValueError("GRAPH_TRUNCATED")
    expected = []
    selected = None
    for position, (mapping, slot) in enumerate(
        zip(payload["mapping"], payload["scientific_session"]["slots"], strict=True)
    ):
        identity = slot["selected"]["canonical_exercise_id"]
        if (
            mapping["canonical_exercise_id"] != identity
            or mapping["slot_id"] != slot["slot_id"]
            or mapping["intent_id"] != slot["intent_id"]
            or mapping["intent_id"] != effective["candidates"][identity]["intent_id"]
            or slot["prescription"]["context"]["realization_ref"]
            != effective["candidates"][identity]["realization_ref"]
            or len(mapping["set_ids"]) != slot["prescription"]["dose"]["work_sets"]
        ):
            raise ValueError("SOURCE_DIGEST_MISMATCH")
        expected.extend(
            (mapping["se_id"], position, None, set_id, index, 1)
            for index, set_id in enumerate(mapping["set_ids"], 1)
        )
        if c["set_log_id"] in mapping["set_ids"]:
            if mapping["se_id"] != c["session_exercise_id"] or c["substituted_name"]:
                raise ValueError("SOURCE_DIGEST_MISMATCH")
            selected = (mapping, slot)
    if graph != expected or selected is None:
        raise ValueError("SOURCE_DIGEST_MISMATCH")
    return binding, *selected, effective
