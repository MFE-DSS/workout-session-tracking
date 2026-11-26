"""The sole admitted descriptive SCI consumer. Never calls allocation or a writer."""

from __future__ import annotations

from dataclasses import asdict, replace
from datetime import UTC, datetime
from types import MappingProxyType
from uuid import uuid4

from app.services.exercise_identity import normalize
from app.services.sci_catalogue import (
    UNKNOWN_CREDIT,
    CreditPolicy,
    SciCatalogue,
    _check_identities,
    _freeze,
)
from app.services.sci_exposure import LedgerLine, aggregate
from app.services.sci_identity import IdentityResolution, SciIdentityResolver, build_name_index

from .contracts import BODYMAP, VERSION, ZONES, ObservedLoadResponse, iso
from .provenance import SourceView as ByteSourceView
from .provenance import canonical_time, digest, qualify_fact


class SourceView(ByteSourceView):
    def _legacy_resolver(self):
        if not hasattr(self, "_resolver"):
            doc = self.catalogue_view().document
            records = tuple(_freeze(row) for row in doc["records"])
            index = MappingProxyType({r["exercise_id"]: r for r in records})
            _check_identities(index)
            catalogue = SciCatalogue(
                _freeze(doc["catalogue_header"]),
                records,
                self.pins["data/sci/exercise_catalogue.json"],
                index,
            )
            self._resolver = SciIdentityResolver(
                catalogue,
                build_name_index(self.json("data/exercise_knowledge_base.json"), catalogue),
            )
        return self._resolver

    def legacy(self, capture, c):
        resolver = self._legacy_resolver()
        name = c["substituted_name"] or c["exercise_name_snapshot"]
        resolution = resolver.resolve_name(name)
        if not resolution.is_resolved:
            alias = capture.alias_name(normalize(name or ""))
            if alias:
                found = resolver.resolve_name(alias)
                if found.is_resolved:
                    resolution = replace(found, query=name, step=3)
        data = asdict(resolution)
        data["reason"] = None if resolution.is_resolved else "UNKNOWN_IDENTITY"
        roles = []
        if resolution.is_resolved:
            canonical = resolver.catalogue.record(resolution.canonical_exercise_id)
            uncertain = "content_alignment" in resolver.catalogue.record(resolution.variant_key)
            roles = [
                dict(
                    zone=r["zone"],
                    raw_role=r["role"],
                    role_basis=r["role_basis"],
                    evidence_refs=list(r["evidence_refs"]),
                    execution_uncertain=uncertain,
                )
                for r in canonical["exercise_science"]["contributions"]
            ]
        return data, roles

    def bundle_for(self, authority):
        if not self.bundle_root:
            raise ValueError("EFFECTIVE_CATALOGUE_UNAVAILABLE")
        if (
            self.v3 is None
            or self.v3.pins["packaging-manifest.v1.json"] != authority["packaging_digest"]
        ):
            self.v3 = ByteSourceView.bundle(
                self.bundle_root,
                authority["packaging_digest"],
                limits=self.limits,
                budget=self.budget,
            )
        return self.v3

    def v3_resolution(self, mapping, effective):
        identity = mapping["canonical_exercise_id"]
        # Historical roles and identities originate in the captured effective bundle.
        record = self.v3.catalogue_view().document
        row = next(r for r in record["records"] if r["exercise_id"] == identity)
        candidate = effective["candidates"][identity]
        resolution = dict(
            status="RESOLVED",
            query=identity,
            step=1,
            variant_key=identity,
            scientific_identity_id=row["identity"]["scientific_identity_id"],
            canonical_exercise_id=identity,
            catalogue_version=effective["effective_catalogue_version"],
            reason=None,
        )
        roles = [
            dict(
                zone=r["zone"],
                raw_role=r["role"],
                role_basis=r["role_basis"],
                evidence_refs=list(r["evidence_refs"]),
                execution_uncertain="content_alignment" in row,
            )
            for r in candidate["effective_roles"]
        ]
        return resolution, roles

    def verify_mapping(self):
        data = self.json("data/sci/readiness_bodymap_projection.v1.json")
        expected = {zone: target for target, zones in BODYMAP.items() for zone in zones}
        expected.update({zone: None for zone in ("anterior_delts", "adductors", "hip_flexors")})
        actual = {row["zone"]: row["bodymap_zone"] for row in data["entries"]}
        if (
            data["mapping_version"] != "sci-p07-bodymap-projection/0.1.0"
            or data["status"] != "ADMITTED_DESCRIPTIVE_ONLY"
            or actual != expected
            or len(data["entries"]) != 15
            or data["posterior"]["components"] != ["hamstrings", "glutes"]
            or data["posterior"]["resolved_credit"] is not None
            or data["posterior"]["documented_sets"] != "UNION_DISTINCT_EFFECTIVE_SET_KEYS"
        ):
            raise ValueError("p07_mapping_mismatch")

    def credit_policy(self):
        if hasattr(self, "_credit_policy"):
            return self._credit_policy
        self.verify_mapping()
        doc = self.json("data/sci/exposure_credit_policy.json")
        if doc["policy_id"] != "sci-exposure-credit-v1" or doc["credits"] != {
            "PRIMARY": 1.0,
            "SECONDARY": 0.5,
            "MINOR": 0.0,
            "UNKNOWN": "UNKNOWN",
        }:
            raise ValueError("credit_policy_mismatch")
        self._credit_policy = CreditPolicy(
            doc["policy_id"],
            MappingProxyType(
                {k: UNKNOWN_CREDIT if k == "UNKNOWN" else v for k, v in doc["credits"].items()}
            ),
        )
        return self._credit_policy


def _lines(facts):
    lines = []
    for fact in facts:
        data = fact["resolution"]
        resolution = IdentityResolution(**data)
        common = dict(
            **fact["key"],
            session_started_at=canonical_time(fact["completed_at"])
            or datetime.min.replace(tzinfo=UTC),
            prescribed_name=fact["prescribed_name"],
            executed_name=fact["executed_name"],
            resolution=resolution,
            catalogue_version=data["catalogue_version"],
            scientific_identity_id=data["scientific_identity_id"],
        )
        if not resolution.is_resolved:
            lines.append(
                LedgerLine(
                    **common,
                    zone=None,
                    raw_role=None,
                    role_basis=None,
                    evidence_refs=(),
                    execution_uncertain=False,
                )
            )
        else:
            for role in fact["contributions"]:
                lines.append(
                    LedgerLine(
                        **common,
                        zone=role["zone"],
                        raw_role=role["raw_role"],
                        role_basis=role["role_basis"],
                        evidence_refs=tuple(role["evidence_refs"]),
                        execution_uncertain=role["execution_uncertain"],
                    )
                )
    return lines


def project_capture(capture, query, sources, limits, *, as_of=None, runtime_profile_digest):
    as_of = as_of or datetime.now(UTC)
    facts = []
    outside_count = 0
    for c in capture.candidates():
        qualified = qualify_fact(capture, c, sources, as_of=as_of)
        if not qualified.outside:
            facts.append(qualified.fact)
        else:
            outside_count += 1
    truncated = capture.truncated
    reasons = set(capture.reasons)
    if truncated:
        reasons.add("SCAN_TRUNCATED")
    for fact in facts:
        reasons.update(fact["temporal"]["reasons"])
        reasons.update(fact["provenance"]["reasons"])
        if fact["resolution"]["status"] != "RESOLVED":
            reasons.add("UNKNOWN_IDENTITY")
    # Canonical role evidence is intentionally orthogonal to temporal coverage.
    evidence = aggregate(_lines(facts), sources.credit_policy()) if facts else None
    mapping_complete = not capture.reasons and all(
        f["resolution"]["status"] == "RESOLVED"
        and f["provenance"]["source_status"] == "QUALIFIED"
        and all(
            c["raw_role"] != "UNKNOWN" and not c["execution_uncertain"] for c in f["contributions"]
        )
        for f in facts
    )
    temporal_complete = (
        not facts
    )  # V1 never persisted a qualified acquisition implementation version.
    safe = [
        f
        for f in facts
        if f["temporal"]["membership"] == "IN_WINDOW"
        and f["provenance"]["source_status"] == "QUALIFIED"
        and f["resolution"]["status"] == "RESOLVED"
    ]
    certain_membership = all(f["temporal"]["membership"] == "IN_WINDOW" for f in facts)
    known = any(
        any(r["raw_role"] != "UNKNOWN" and not r["execution_uncertain"] for r in f["contributions"])
        for f in safe
    )
    state = "EMPTY" if not facts and not truncated and not reasons else "UNKNOWN"
    if known:
        state = "PARTIAL"

    def quantity(components, *, composite=False):
        selected = {
            f["key"]["set_log_id"]: f
            for f in safe
            if any(
                r["zone"] in components
                and r["raw_role"] != "UNKNOWN"
                and not r["execution_uncertain"]
                for r in f["contributions"]
            )
        }
        if not selected:
            return dict(
                state="EMPTY" if state == "EMPTY" else "UNKNOWN",
                documented_sets=None,
                resolved_credit=None,
                bound=None,
                reasons=["NO_DOCUMENTED_FACTS"]
                if state == "EMPTY"
                else sorted(reasons or {"UNKNOWN_ROLE"}),
            )
        credit = sum(
            sources.credit_policy().credit(r["raw_role"])
            for f in selected.values()
            for r in f["contributions"]
            if r["zone"] in components
            and r["raw_role"] != "UNKNOWN"
            and not r["execution_uncertain"]
        )
        return dict(
            state="PARTIAL",
            documented_sets=len(selected),
            resolved_credit=None if composite else credit,
            bound="EXACT"
            if not truncated and mapping_complete and certain_membership
            else "MINIMUM",
            reasons=sorted(reasons | ({"COMPOSITE_NO_CREDIT_AGGREGATION"} if composite else set())),
        )

    zones = []
    for zone in ZONES:
        relevant = any(any(r["zone"] == zone for r in f["contributions"]) for f in facts)
        ev = asdict(evidence[zone]) if evidence and relevant else None
        if ev:
            ev.pop("zone")
            ev.update(exact_evidence=evidence[zone].exact_evidence, scope="INSPECTED_ROLE_VECTOR")
        zones.append(
            dict(
                zone=zone,
                evidence=ev,
                window_result=quantity([zone]),
                last_qualified_observation=None,
            )
        )
    versions = {}
    for f in facts:
        version = f["resolution"]["catalogue_version"]
        if version:
            is_v3 = f["provenance"]["profile"] == "V3"
            key = "V3_CAPTURED_EFFECTIVE_BUNDLE" if is_v3 else "LEGACY_PINNED_READ_CLASSIFICATION"
            versions[key] = dict(
                catalogue_version=version,
                source_kind=key,
                digest=f["provenance"]["effective_science_digest"]
                if is_v3
                else sources.pins["data/sci/exercise_catalogue.json"],
            )
    pins = {"checkout:" + k: v for k, v in sources.pins.items()}
    if sources.v3:
        pins.update({"v3-bundle:" + k: v for k, v in sources.v3.pins.items()})
    used = capture.budget.used
    capture.budget.deadline()
    out = dict(
        contract_version=VERSION,
        availability="AVAILABLE",
        state=state,
        owner_id=capture.owner_id,
        read_id=str(uuid4()),
        as_of=iso(as_of),
        window={
            "from": iso(query.window_start),
            "until": iso(query.window_until),
            "time_zone": "UTC",
        },
        membership="LIVE_BOUNDED_MEMBERSHIP",
        policy_id="sci-exposure-credit-v1",
        catalogue_versions=list(versions.values()),
        mapping_version="sci-p07-bodymap-projection/0.1.0",
        coverage=dict(
            scan="TRUNCATED" if truncated else "COMPLETE",
            temporal="COMPLETE" if temporal_complete else "PARTIAL",
            mapping="COMPLETE" if mapping_complete else "PARTIAL",
            scope="CURRENT_DOCUMENTED_ELIGIBLE_SUBSET_NOT_REAL_TRAINING_COMPLETENESS",
            reasons=sorted(reasons),
        ),
        scan=dict(
            strategy="OWNER_ID_ASC_NESTED",
            truncated=truncated,
            reasons=["SCAN_TRUNCATED"] if truncated else [],
            limits={
                k: getattr(limits, k)
                for k in (
                    "sessions",
                    "exercises",
                    "work_sets",
                    "operations",
                    "graph_rows",
                    "statements",
                )
            },
            usage={
                **{
                    k: used.get(k, 0)
                    for k in (
                        "sessions",
                        "exercises",
                        "work_sets",
                        "operations",
                        "graph_rows",
                        "statements",
                        "db_input_bytes",
                    )
                },
                "sentinels": capture.sentinels,
                "unvisited_frontiers": capture.frontiers,
            },
        ),
        consistency=dict(
            kind="READ_TRANSACTION",
            runtime_profile_digest=runtime_profile_digest,
            result_digest="0" * 64,
            source_digests=[dict(source_ref=k, sha256=v) for k, v in sorted(pins.items())],
        ),
        zones=zones,
        bodymap_projection=dict(
            mapping_version="sci-p07-bodymap-projection/0.1.0",
            targets=[
                dict(
                    bodymap_zone=key,
                    components=components,
                    window_result=quantity(components, composite=key == "posterior"),
                    last_qualified_observation=None,
                )
                for key, components in BODYMAP.items()
            ],
            not_represented=["anterior_delts", "adductors", "hip_flexors"],
        ),
        facts=facts,
        exclusions=[
            dict(
                reason=r,
                inspected_count=None
                if r in {"SCAN_TRUNCATED", "GRAPH_TRUNCATED", "RECEIPT_CHAIN_TRUNCATED"}
                else capture.exclusions[r]
                + sum(
                    r
                    in (
                        f["temporal"]["reasons"]
                        + f["provenance"]["reasons"]
                        + (["UNKNOWN_IDENTITY"] if f["resolution"]["status"] != "RESOLVED" else [])
                    )
                    for f in facts
                ),
            )
            for r in sorted(reasons | set(capture.exclusions))
        ]
        + ([dict(reason="OUTSIDE_WINDOW", inspected_count=outside_count)] if outside_count else []),
    )
    out["consistency"]["result_digest"] = digest(out)
    return ObservedLoadResponse.model_validate(out)
