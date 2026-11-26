"""Strict wire DTO compiled from the admitted documentary shape using existing Pydantic core.

The schema is fixed package material, never supplied by a request. Coverage and
provenance invariants supplement structural validation; no metric is invented.
"""

from __future__ import annotations

import copy
import json
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from pydantic_core import SchemaValidator, core_schema

VERSION = "muscle-observed-load/1.0.0"
HEADER = "X-Auren-Muscle-Observed-Load-Contract"

_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "urn:auren:proposed:muscle-observed-load:1.0.0",
    "$comment": "DOCUMENTARY PROPOSED SCHEMA. NOT SERVED. Requires cross-field validation in WIRE_CONTRACT; byte/time/resource caps independent. No runtime code generated.",
    "oneOf": [{"$ref": "#/$defs/read_response"}, {"$ref": "#/$defs/error_response"}],
    "$defs": {
        "reasons": {
            "type": "array",
            "maxItems": 28,
            "items": {
                "type": "string",
                "enum": [
                    "SCAN_TRUNCATED",
                    "GRAPH_TRUNCATED",
                    "RECEIPT_CHAIN_TRUNCATED",
                    "NULL_EVENT_TIME",
                    "INVALID_EVENT_TIME",
                    "FUTURE_EVENT_TIME",
                    "CONTRADICTORY_EPISODE",
                    "ESTIMATED_ORIGIN",
                    "ADJUSTED_ORIGIN",
                    "UNKNOWN_ACQUISITION_SOURCE",
                    "UNKNOWN_IDENTITY",
                    "UNKNOWN_ROLE",
                    "EFFECTIVE_CATALOGUE_UNAVAILABLE",
                    "SOURCE_DIGEST_MISMATCH",
                    "PROFILE_MISMATCH",
                    "CONTENT_EXECUTION_MISMATCH",
                    "TEXT_LIMIT",
                    "JSON_LIMIT",
                    "SQL_LIMIT",
                    "TIME_LIMIT",
                    "MEMORY_LIMIT",
                    "OUTPUT_LIMIT",
                    "COMPOSITE_NO_CREDIT_AGGREGATION",
                    "NOT_REPRESENTED",
                    "OUTSIDE_WINDOW",
                    "SESSION_NOT_ELIGIBLE",
                    "LEGACY_PROVENANCE_NOT_PERSISTED",
                    "NO_DOCUMENTED_FACTS",
                ],
            },
            "uniqueItems": True,
        },
        "key": {
            "type": "object",
            "additionalProperties": False,
            "required": ["session_id", "session_exercise_id", "set_log_id"],
            "properties": {
                "session_id": {"type": "integer", "minimum": 1, "maximum": 9223372036854775807},
                "session_exercise_id": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 9223372036854775807,
                },
                "set_log_id": {"type": "integer", "minimum": 1, "maximum": 9223372036854775807},
            },
        },
        "window": {
            "type": "object",
            "additionalProperties": False,
            "required": ["from", "until", "time_zone"],
            "properties": {
                "from": {"type": "string", "format": "date-time", "pattern": "Z$", "maxLength": 40},
                "until": {
                    "type": "string",
                    "format": "date-time",
                    "pattern": "Z$",
                    "maxLength": 40,
                },
                "time_zone": {"const": "UTC"},
            },
        },
        "evidence": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "primary_sets",
                "secondary_sets",
                "minor_sets",
                "unknown_sets",
                "unknown_identity_sets",
                "execution_uncertain_sets",
                "resolved_credit",
                "bound",
                "policy_id",
                "exact_evidence",
                "scope",
            ],
            "properties": {
                "primary_sets": {"type": "integer", "minimum": 0, "maximum": 500},
                "secondary_sets": {"type": "integer", "minimum": 0, "maximum": 500},
                "minor_sets": {"type": "integer", "minimum": 0, "maximum": 500},
                "unknown_sets": {"type": "integer", "minimum": 0, "maximum": 500},
                "unknown_identity_sets": {"type": "integer", "minimum": 0, "maximum": 500},
                "execution_uncertain_sets": {"type": "integer", "minimum": 0, "maximum": 500},
                "resolved_credit": {"type": "number", "minimum": 0},
                "bound": {"type": "string", "enum": ["EXACT", "MINIMUM"]},
                "policy_id": {"const": "sci-exposure-credit-v1"},
                "exact_evidence": {"type": "boolean"},
                "scope": {"const": "INSPECTED_ROLE_VECTOR"},
            },
        },
        "quantity": {
            "type": "object",
            "additionalProperties": False,
            "required": ["state", "documented_sets", "resolved_credit", "bound", "reasons"],
            "properties": {
                "state": {"type": "string", "enum": ["OBSERVED", "PARTIAL", "UNKNOWN", "EMPTY"]},
                "documented_sets": {
                    "anyOf": [{"type": "integer", "minimum": 0, "maximum": 500}, {"type": "null"}]
                },
                "resolved_credit": {"anyOf": [{"type": "number", "minimum": 0}, {"type": "null"}]},
                "bound": {
                    "anyOf": [{"type": "string", "enum": ["EXACT", "MINIMUM"]}, {"type": "null"}]
                },
                "reasons": {"$ref": "#/$defs/reasons"},
            },
        },
        "last": {
            "type": "object",
            "additionalProperties": False,
            "required": ["key", "completed_at", "source_zone", "qualification"],
            "properties": {
                "key": {"$ref": "#/$defs/key"},
                "completed_at": {
                    "type": "string",
                    "format": "date-time",
                    "pattern": "Z$",
                    "maxLength": 40,
                },
                "source_zone": {
                    "type": "string",
                    "enum": [
                        "pecs",
                        "lats",
                        "upper_back",
                        "anterior_delts",
                        "lateral_delts",
                        "rear_delts",
                        "biceps",
                        "triceps",
                        "quads",
                        "hamstrings",
                        "glutes",
                        "adductors",
                        "calves",
                        "abs",
                        "hip_flexors",
                    ],
                },
                "qualification": {"const": "DOCUMENTARY_PROVENANCE_QUALIFIED"},
            },
        },
        "zone": {
            "type": "object",
            "additionalProperties": False,
            "required": ["zone", "evidence", "window_result", "last_qualified_observation"],
            "properties": {
                "zone": {
                    "type": "string",
                    "enum": [
                        "pecs",
                        "lats",
                        "upper_back",
                        "anterior_delts",
                        "lateral_delts",
                        "rear_delts",
                        "biceps",
                        "triceps",
                        "quads",
                        "hamstrings",
                        "glutes",
                        "adductors",
                        "calves",
                        "abs",
                        "hip_flexors",
                    ],
                },
                "evidence": {"anyOf": [{"$ref": "#/$defs/evidence"}, {"type": "null"}]},
                "window_result": {"$ref": "#/$defs/quantity"},
                "last_qualified_observation": {
                    "anyOf": [{"$ref": "#/$defs/last"}, {"type": "null"}]
                },
            },
        },
        "bodymap_target": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "bodymap_zone",
                "components",
                "window_result",
                "last_qualified_observation",
            ],
            "properties": {
                "bodymap_zone": {
                    "type": "string",
                    "enum": [
                        "pecs",
                        "lats",
                        "upper_back",
                        "delt_lat",
                        "delt_post",
                        "biceps",
                        "triceps",
                        "quads",
                        "posterior",
                        "calves",
                        "core",
                    ],
                },
                "components": {
                    "type": "array",
                    "maxItems": 2,
                    "items": {
                        "type": "string",
                        "enum": [
                            "pecs",
                            "lats",
                            "upper_back",
                            "anterior_delts",
                            "lateral_delts",
                            "rear_delts",
                            "biceps",
                            "triceps",
                            "quads",
                            "hamstrings",
                            "glutes",
                            "adductors",
                            "calves",
                            "abs",
                            "hip_flexors",
                        ],
                    },
                    "minItems": 1,
                    "uniqueItems": True,
                },
                "window_result": {"$ref": "#/$defs/quantity"},
                "last_qualified_observation": {
                    "anyOf": [{"$ref": "#/$defs/last"}, {"type": "null"}]
                },
            },
        },
        "bodymap": {
            "type": "object",
            "additionalProperties": False,
            "required": ["mapping_version", "targets", "not_represented"],
            "properties": {
                "mapping_version": {"const": "sci-p07-bodymap-projection/0.1.0"},
                "targets": {
                    "type": "array",
                    "maxItems": 11,
                    "items": {"$ref": "#/$defs/bodymap_target"},
                    "minItems": 11,
                },
                "not_represented": {
                    "type": "array",
                    "minItems": 3,
                    "maxItems": 3,
                    "uniqueItems": True,
                    "items": {
                        "type": "string",
                        "enum": ["anterior_delts", "adductors", "hip_flexors"],
                    },
                },
            },
        },
        "coverage": {
            "type": "object",
            "additionalProperties": False,
            "required": ["scan", "temporal", "mapping", "scope", "reasons"],
            "properties": {
                "scan": {"type": "string", "enum": ["COMPLETE", "TRUNCATED"]},
                "temporal": {"type": "string", "enum": ["COMPLETE", "PARTIAL"]},
                "mapping": {"type": "string", "enum": ["COMPLETE", "PARTIAL"]},
                "scope": {
                    "const": "CURRENT_DOCUMENTED_ELIGIBLE_SUBSET_NOT_REAL_TRAINING_COMPLETENESS"
                },
                "reasons": {"$ref": "#/$defs/reasons"},
            },
        },
        "budgets": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "sessions",
                "exercises",
                "work_sets",
                "operations",
                "graph_rows",
                "statements",
            ],
            "properties": {
                "sessions": {"const": 200},
                "exercises": {"const": 200},
                "work_sets": {"const": 500},
                "operations": {"const": 1000},
                "graph_rows": {"const": 500},
                "statements": {"const": 4096},
            },
        },
        "usage": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "sessions",
                "exercises",
                "work_sets",
                "operations",
                "graph_rows",
                "statements",
                "sentinels",
                "unvisited_frontiers",
                "db_input_bytes",
            ],
            "properties": {
                "sessions": {"type": "integer", "minimum": 0, "maximum": 200},
                "exercises": {"type": "integer", "minimum": 0, "maximum": 200},
                "work_sets": {"type": "integer", "minimum": 0, "maximum": 500},
                "operations": {"type": "integer", "minimum": 0, "maximum": 1000},
                "graph_rows": {"type": "integer", "minimum": 0, "maximum": 500},
                "statements": {"type": "integer", "minimum": 0, "maximum": 4096},
                "sentinels": {"type": "integer", "minimum": 0, "maximum": 1801},
                "db_input_bytes": {"type": "integer", "minimum": 0, "maximum": 2097152},
                "unvisited_frontiers": {"type": "integer", "minimum": 0, "maximum": 901},
            },
        },
        "scan": {
            "type": "object",
            "additionalProperties": False,
            "required": ["strategy", "limits", "usage", "truncated", "reasons"],
            "properties": {
                "strategy": {"const": "OWNER_ID_ASC_NESTED"},
                "limits": {"$ref": "#/$defs/budgets"},
                "usage": {"$ref": "#/$defs/usage"},
                "truncated": {"type": "boolean"},
                "reasons": {"$ref": "#/$defs/reasons"},
            },
        },
        "pin": {
            "type": "object",
            "additionalProperties": False,
            "required": ["source_ref", "sha256"],
            "properties": {
                "source_ref": {"type": "string", "minLength": 1, "maxLength": 256},
                "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            },
        },
        "catalogue": {
            "type": "object",
            "additionalProperties": False,
            "required": ["catalogue_version", "source_kind", "digest"],
            "properties": {
                "catalogue_version": {"type": "string", "minLength": 1, "maxLength": 256},
                "source_kind": {
                    "type": "string",
                    "enum": ["LEGACY_PINNED_READ_CLASSIFICATION", "V3_CAPTURED_EFFECTIVE_BUNDLE"],
                },
                "digest": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            },
        },
        "consistency": {
            "type": "object",
            "additionalProperties": False,
            "required": ["kind", "runtime_profile_digest", "result_digest", "source_digests"],
            "properties": {
                "kind": {"const": "READ_TRANSACTION"},
                "runtime_profile_digest": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "result_digest": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "source_digests": {
                    "type": "array",
                    "maxItems": 128,
                    "items": {"$ref": "#/$defs/pin"},
                },
            },
        },
        "resolution": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "status",
                "query",
                "step",
                "variant_key",
                "scientific_identity_id",
                "canonical_exercise_id",
                "catalogue_version",
                "reason",
            ],
            "properties": {
                "status": {"type": "string", "enum": ["RESOLVED", "UNKNOWN_IDENTITY"]},
                "query": {
                    "anyOf": [
                        {"type": "string", "minLength": 1, "maxLength": 512},
                        {"type": "null"},
                    ]
                },
                "step": {
                    "anyOf": [{"type": "integer", "minimum": 1, "maximum": 3}, {"type": "null"}]
                },
                "variant_key": {
                    "anyOf": [
                        {"type": "string", "minLength": 1, "maxLength": 256},
                        {"type": "null"},
                    ]
                },
                "scientific_identity_id": {
                    "anyOf": [
                        {"type": "string", "minLength": 1, "maxLength": 256},
                        {"type": "null"},
                    ]
                },
                "canonical_exercise_id": {
                    "anyOf": [
                        {"type": "string", "minLength": 1, "maxLength": 256},
                        {"type": "null"},
                    ]
                },
                "catalogue_version": {
                    "anyOf": [
                        {"type": "string", "minLength": 1, "maxLength": 256},
                        {"type": "null"},
                    ]
                },
                "reason": {
                    "anyOf": [
                        {
                            "type": "string",
                            "enum": [
                                "SCAN_TRUNCATED",
                                "GRAPH_TRUNCATED",
                                "RECEIPT_CHAIN_TRUNCATED",
                                "NULL_EVENT_TIME",
                                "INVALID_EVENT_TIME",
                                "FUTURE_EVENT_TIME",
                                "CONTRADICTORY_EPISODE",
                                "ESTIMATED_ORIGIN",
                                "ADJUSTED_ORIGIN",
                                "UNKNOWN_ACQUISITION_SOURCE",
                                "UNKNOWN_IDENTITY",
                                "UNKNOWN_ROLE",
                                "EFFECTIVE_CATALOGUE_UNAVAILABLE",
                                "SOURCE_DIGEST_MISMATCH",
                                "PROFILE_MISMATCH",
                                "CONTENT_EXECUTION_MISMATCH",
                                "TEXT_LIMIT",
                                "JSON_LIMIT",
                                "SQL_LIMIT",
                                "TIME_LIMIT",
                                "MEMORY_LIMIT",
                                "OUTPUT_LIMIT",
                                "COMPOSITE_NO_CREDIT_AGGREGATION",
                                "NOT_REPRESENTED",
                                "OUTSIDE_WINDOW",
                                "SESSION_NOT_ELIGIBLE",
                                "LEGACY_PROVENANCE_NOT_PERSISTED",
                                "NO_DOCUMENTED_FACTS",
                            ],
                        },
                        {"type": "null"},
                    ]
                },
            },
        },
        "contribution": {
            "type": "object",
            "additionalProperties": False,
            "required": ["zone", "raw_role", "role_basis", "evidence_refs", "execution_uncertain"],
            "properties": {
                "zone": {
                    "type": "string",
                    "enum": [
                        "pecs",
                        "lats",
                        "upper_back",
                        "anterior_delts",
                        "lateral_delts",
                        "rear_delts",
                        "biceps",
                        "triceps",
                        "quads",
                        "hamstrings",
                        "glutes",
                        "adductors",
                        "calves",
                        "abs",
                        "hip_flexors",
                    ],
                },
                "raw_role": {
                    "type": "string",
                    "enum": ["PRIMARY", "SECONDARY", "MINOR", "UNKNOWN"],
                },
                "role_basis": {
                    "anyOf": [
                        {"type": "string", "minLength": 1, "maxLength": 512},
                        {"type": "null"},
                    ]
                },
                "evidence_refs": {
                    "type": "array",
                    "maxItems": 64,
                    "items": {"type": "string", "minLength": 1, "maxLength": 512},
                },
                "execution_uncertain": {"type": "boolean"},
            },
        },
        "setting": {
            "type": "object",
            "additionalProperties": False,
            "required": ["kind", "value", "unit"],
            "properties": {
                "kind": {"type": "string", "minLength": 1, "maxLength": 64},
                "value": {"type": "number"},
                "unit": {"type": "string", "minLength": 1, "maxLength": 64},
            },
        },
        "context": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "context_ref",
                "equipment_ref",
                "realization_ref",
                "side",
                "load_semantics",
            ],
            "properties": {
                "context_ref": {
                    "anyOf": [
                        {"type": "string", "minLength": 1, "maxLength": 512},
                        {"type": "null"},
                    ]
                },
                "equipment_ref": {
                    "anyOf": [
                        {"type": "string", "minLength": 1, "maxLength": 512},
                        {"type": "null"},
                    ]
                },
                "realization_ref": {
                    "anyOf": [
                        {"type": "string", "minLength": 1, "maxLength": 512},
                        {"type": "null"},
                    ]
                },
                "side": {
                    "anyOf": [{"type": "string", "minLength": 1, "maxLength": 64}, {"type": "null"}]
                },
                "load_semantics": {
                    "anyOf": [{"type": "string", "minLength": 1, "maxLength": 64}, {"type": "null"}]
                },
            },
        },
        "operation": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "op_id",
                "expected_revision",
                "applied_revision",
                "body_digest",
                "recorded_at",
            ],
            "properties": {
                "op_id": {
                    "anyOf": [{"type": "string", "minLength": 1, "maxLength": 64}, {"type": "null"}]
                },
                "expected_revision": {
                    "anyOf": [
                        {"type": "integer", "minimum": 0, "maximum": 9223372036854775807},
                        {"type": "null"},
                    ]
                },
                "applied_revision": {
                    "anyOf": [
                        {"type": "integer", "minimum": 0, "maximum": 9223372036854775807},
                        {"type": "null"},
                    ]
                },
                "body_digest": {
                    "anyOf": [{"type": "string", "pattern": "^[0-9a-f]{64}$"}, {"type": "null"}]
                },
                "recorded_at": {
                    "anyOf": [
                        {"type": "string", "format": "date-time", "pattern": "Z$", "maxLength": 40},
                        {"type": "null"},
                    ]
                },
            },
        },
        "temporal": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "membership",
                "status",
                "performed_at",
                "performed_at_estimated",
                "performed_at_adjusted",
                "reasons",
            ],
            "properties": {
                "membership": {"type": "string", "enum": ["IN_WINDOW", "UNKNOWN"]},
                "status": {
                    "type": "string",
                    "enum": [
                        "DOCUMENTARY_PROVENANCE_QUALIFIED",
                        "CANONICAL_DATE_PARTIAL_ORIGIN",
                        "UNKNOWN_MEMBERSHIP",
                        "FUTURE",
                        "CONTRADICTORY_EPISODE",
                    ],
                },
                "performed_at": {
                    "anyOf": [
                        {"type": "string", "format": "date-time", "pattern": "Z$", "maxLength": 40},
                        {"type": "null"},
                    ]
                },
                "performed_at_estimated": {"anyOf": [{"type": "boolean"}, {"type": "null"}]},
                "performed_at_adjusted": {"anyOf": [{"type": "boolean"}, {"type": "null"}]},
                "reasons": {"$ref": "#/$defs/reasons"},
            },
        },
        "provenance": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "profile",
                "execution_profile_version",
                "evaluation_id",
                "binding_digest",
                "effective_science_digest",
                "origin_operation",
                "effective_operation",
                "source_status",
                "reasons",
            ],
            "properties": {
                "profile": {"type": "string", "enum": ["LEGACY", "V3", "UNKNOWN"]},
                "execution_profile_version": {
                    "anyOf": [{"type": "string", "minLength": 1, "maxLength": 64}, {"type": "null"}]
                },
                "evaluation_id": {
                    "anyOf": [{"type": "string", "minLength": 1, "maxLength": 36}, {"type": "null"}]
                },
                "binding_digest": {
                    "anyOf": [{"type": "string", "pattern": "^[0-9a-f]{64}$"}, {"type": "null"}]
                },
                "effective_science_digest": {
                    "anyOf": [{"type": "string", "pattern": "^[0-9a-f]{64}$"}, {"type": "null"}]
                },
                "origin_operation": {"anyOf": [{"$ref": "#/$defs/operation"}, {"type": "null"}]},
                "effective_operation": {"anyOf": [{"$ref": "#/$defs/operation"}, {"type": "null"}]},
                "source_status": {"type": "string", "enum": ["QUALIFIED", "UNKNOWN"]},
                "reasons": {"$ref": "#/$defs/reasons"},
            },
        },
        "fact": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "key",
                "kind",
                "completed",
                "completed_at",
                "reps",
                "weight_kg",
                "prescribed_name",
                "executed_name",
                "resolution",
                "contributions",
                "context",
                "setting",
                "temporal",
                "provenance",
                "set_index",
            ],
            "properties": {
                "key": {"$ref": "#/$defs/key"},
                "kind": {"const": "work"},
                "completed": {"const": True},
                "completed_at": {
                    "anyOf": [
                        {"type": "string", "format": "date-time", "pattern": "Z$", "maxLength": 40},
                        {"type": "null"},
                    ]
                },
                "reps": {
                    "anyOf": [
                        {"type": "integer", "minimum": 0, "maximum": 2147483647},
                        {"type": "null"},
                    ]
                },
                "weight_kg": {"anyOf": [{"type": "number", "minimum": 0}, {"type": "null"}]},
                "prescribed_name": {
                    "anyOf": [
                        {"type": "string", "minLength": 1, "maxLength": 512},
                        {"type": "null"},
                    ]
                },
                "executed_name": {
                    "anyOf": [
                        {"type": "string", "minLength": 1, "maxLength": 512},
                        {"type": "null"},
                    ]
                },
                "resolution": {"$ref": "#/$defs/resolution"},
                "contributions": {
                    "type": "array",
                    "maxItems": 15,
                    "items": {"$ref": "#/$defs/contribution"},
                },
                "context": {"anyOf": [{"$ref": "#/$defs/context"}, {"type": "null"}]},
                "setting": {"anyOf": [{"$ref": "#/$defs/setting"}, {"type": "null"}]},
                "temporal": {"$ref": "#/$defs/temporal"},
                "provenance": {"$ref": "#/$defs/provenance"},
                "set_index": {"type": "integer", "minimum": 1, "maximum": 2147483647},
            },
        },
        "exclusion": {
            "type": "object",
            "additionalProperties": False,
            "required": ["reason", "inspected_count"],
            "properties": {
                "reason": {
                    "type": "string",
                    "enum": [
                        "SCAN_TRUNCATED",
                        "GRAPH_TRUNCATED",
                        "RECEIPT_CHAIN_TRUNCATED",
                        "NULL_EVENT_TIME",
                        "INVALID_EVENT_TIME",
                        "FUTURE_EVENT_TIME",
                        "CONTRADICTORY_EPISODE",
                        "ESTIMATED_ORIGIN",
                        "ADJUSTED_ORIGIN",
                        "UNKNOWN_ACQUISITION_SOURCE",
                        "UNKNOWN_IDENTITY",
                        "UNKNOWN_ROLE",
                        "EFFECTIVE_CATALOGUE_UNAVAILABLE",
                        "SOURCE_DIGEST_MISMATCH",
                        "PROFILE_MISMATCH",
                        "CONTENT_EXECUTION_MISMATCH",
                        "TEXT_LIMIT",
                        "JSON_LIMIT",
                        "SQL_LIMIT",
                        "TIME_LIMIT",
                        "MEMORY_LIMIT",
                        "OUTPUT_LIMIT",
                        "COMPOSITE_NO_CREDIT_AGGREGATION",
                        "NOT_REPRESENTED",
                        "OUTSIDE_WINDOW",
                        "SESSION_NOT_ELIGIBLE",
                        "LEGACY_PROVENANCE_NOT_PERSISTED",
                        "NO_DOCUMENTED_FACTS",
                    ],
                },
                "inspected_count": {
                    "anyOf": [{"type": "integer", "minimum": 0, "maximum": 4096}, {"type": "null"}]
                },
            },
        },
        "read_response": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "contract_version",
                "availability",
                "state",
                "owner_id",
                "read_id",
                "as_of",
                "window",
                "membership",
                "policy_id",
                "catalogue_versions",
                "mapping_version",
                "coverage",
                "scan",
                "consistency",
                "zones",
                "bodymap_projection",
                "facts",
                "exclusions",
            ],
            "properties": {
                "contract_version": {"const": "muscle-observed-load/1.0.0"},
                "availability": {"const": "AVAILABLE"},
                "state": {"type": "string", "enum": ["OBSERVED", "PARTIAL", "UNKNOWN", "EMPTY"]},
                "owner_id": {"type": "integer", "minimum": 1, "maximum": 9223372036854775807},
                "read_id": {"type": "string", "format": "uuid", "maxLength": 36},
                "as_of": {
                    "type": "string",
                    "format": "date-time",
                    "pattern": "Z$",
                    "maxLength": 40,
                },
                "window": {"$ref": "#/$defs/window"},
                "membership": {"const": "LIVE_BOUNDED_MEMBERSHIP"},
                "policy_id": {"const": "sci-exposure-credit-v1"},
                "catalogue_versions": {
                    "type": "array",
                    "maxItems": 3,
                    "items": {"$ref": "#/$defs/catalogue"},
                },
                "mapping_version": {"const": "sci-p07-bodymap-projection/0.1.0"},
                "coverage": {"$ref": "#/$defs/coverage"},
                "scan": {"$ref": "#/$defs/scan"},
                "consistency": {"$ref": "#/$defs/consistency"},
                "zones": {
                    "type": "array",
                    "maxItems": 15,
                    "items": {"$ref": "#/$defs/zone"},
                    "minItems": 15,
                },
                "bodymap_projection": {"$ref": "#/$defs/bodymap"},
                "facts": {"type": "array", "maxItems": 500, "items": {"$ref": "#/$defs/fact"}},
                "exclusions": {
                    "type": "array",
                    "maxItems": 28,
                    "items": {"$ref": "#/$defs/exclusion"},
                },
            },
        },
        "error_response": {
            "type": "object",
            "additionalProperties": False,
            "required": ["contract_version", "availability", "state", "detail"],
            "properties": {
                "contract_version": {"const": "muscle-observed-load/1.0.0"},
                "availability": {"const": "UNAVAILABLE"},
                "state": {"const": "UNAVAILABLE"},
                "detail": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["error"],
                    "properties": {
                        "error": {
                            "type": "string",
                            "enum": [
                                "unauthorized",
                                "muscle_observed_load_contract_required",
                                "muscle_observed_load_contract_unsupported",
                                "invalid_muscle_observed_load_query",
                                "muscle_observed_load_unavailable",
                            ],
                        }
                    },
                },
            },
        },
    },
}


class ObservedLoadReadError(ValueError):
    def __init__(self, code="muscle_observed_load_unavailable", status=503):
        self.code, self.status = code, status
        super().__init__(code)


@dataclass(frozen=True)
class ObservedLoadQuery:
    window_start: datetime
    window_until: datetime


def instant(value: str) -> datetime:
    if not isinstance(value, str) or len(value) > 40:
        raise ValueError("invalid_instant")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("offset_required")
    return result.astimezone(UTC)


def iso(value: datetime | None):
    if value is None:
        return None
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def parse_query(values, contract_header, *, as_of):
    if contract_header != VERSION:
        raise ObservedLoadReadError(
            "muscle_observed_load_contract_required"
            if contract_header is None
            else "muscle_observed_load_contract_unsupported",
            406,
        )
    try:
        pairs = list(values.items()) if isinstance(values, dict) else list(values)
        if len(pairs) > 3 or len({key for key, _ in pairs}) != len(pairs):
            raise ValueError
        data = dict(pairs)
        if set(data) - {"from", "until", "time_zone"} or data.get("time_zone", "UTC") != "UTC":
            raise ValueError
        start, until = instant(data["from"]), instant(data["until"])
        if not start < until <= as_of.astimezone(UTC):
            raise ValueError
        return ObservedLoadQuery(start, until)
    except (ValueError, TypeError, KeyError, OverflowError):
        raise ObservedLoadReadError("invalid_muscle_observed_load_query", 422) from None


def _format(value, kind):
    if kind == "date-time":
        if not value.endswith("Z"):
            raise ValueError("UTC_required")
        instant(value)
    elif kind == "uuid":
        if str(uuid.UUID(value)) != value:
            raise ValueError("UUID_required")
    return value


def _unique(value):
    held = {json.dumps(x, sort_keys=True, allow_nan=False) for x in value}
    if len(held) != len(value):
        raise ValueError("duplicate_item")
    return value


def _compile(node):
    if "$ref" in node:
        return _compile(_SCHEMA["$defs"][node["$ref"].split("/")[-1]])
    if "anyOf" in node or "oneOf" in node:
        return core_schema.union_schema([_compile(n) for n in node.get("anyOf", node.get("oneOf"))])
    if "const" in node:
        literal = core_schema.literal_schema([node["const"]])
        if type(node["const"]) is bool:
            return core_schema.chain_schema([core_schema.bool_schema(strict=True), literal])
        return literal
    if "enum" in node:
        return core_schema.literal_schema(node["enum"])
    kind = node["type"]
    if kind == "null":
        return core_schema.none_schema()
    if kind == "boolean":
        return core_schema.bool_schema(strict=True)
    if kind == "object":
        return core_schema.typed_dict_schema(
            {
                k: core_schema.typed_dict_field(_compile(v), required=True)
                for k, v in node["properties"].items()
            },
            strict=True,
            extra_behavior="forbid",
        )
    if kind == "array":
        result = core_schema.list_schema(
            _compile(node["items"]),
            strict=True,
            min_length=node.get("minItems"),
            max_length=node["maxItems"],
        )
        return (
            core_schema.no_info_after_validator_function(_unique, result)
            if node.get("uniqueItems")
            else result
        )
    if kind in ("integer", "number"):
        options = {"ge": node.get("minimum"), "le": node.get("maximum"), "strict": True}
        return (
            core_schema.int_schema(**options)
            if kind == "integer"
            else core_schema.float_schema(allow_inf_nan=False, **options)
        )
    result = core_schema.str_schema(
        strict=True,
        min_length=node.get("minLength"),
        max_length=node.get("maxLength"),
        pattern=node.get("pattern"),
    )
    if "format" in node:
        result = core_schema.no_info_after_validator_function(
            lambda v: _format(v, node["format"]), result
        )
    return result


_VALIDATOR = SchemaValidator(_compile(_SCHEMA))
ZONES = tuple(_SCHEMA["$defs"]["zone"]["properties"]["zone"]["enum"])
BODYMAP = {
    "pecs": ["pecs"],
    "lats": ["lats"],
    "upper_back": ["upper_back"],
    "delt_lat": ["lateral_delts"],
    "delt_post": ["rear_delts"],
    "biceps": ["biceps"],
    "triceps": ["triceps"],
    "quads": ["quads"],
    "posterior": ["hamstrings", "glutes"],
    "calves": ["calves"],
    "core": ["abs"],
}


def _semantics(value):
    if value["availability"] == "UNAVAILABLE":
        return
    start, until, now = (
        instant(value["window"]["from"]),
        instant(value["window"]["until"]),
        instant(value["as_of"]),
    )
    if not start < until <= now:
        raise ValueError("invalid_window")
    zones = value["zones"]
    if len({z["zone"] for z in zones}) != 15 or {z["zone"] for z in zones} != set(ZONES):
        raise ValueError("invalid_zones")
    targets = value["bodymap_projection"]["targets"]
    if {t["bodymap_zone"] for t in targets} != set(BODYMAP):
        raise ValueError("invalid_bodymap")
    if set(value["bodymap_projection"]["not_represented"]) != {
        "anterior_delts",
        "adductors",
        "hip_flexors",
    }:
        raise ValueError("invalid_bodymap")
    for t in targets:
        if t["components"] != BODYMAP[t["bodymap_zone"]] or (
            t["bodymap_zone"] == "posterior" and t["window_result"]["resolved_credit"] is not None
        ):
            raise ValueError("invalid_composite")
    coverage = value["coverage"]
    if value["scan"]["truncated"] != (coverage["scan"] == "TRUNCATED"):
        raise ValueError("invalid_coverage")
    complete = all(coverage[k] == "COMPLETE" for k in ("scan", "temporal", "mapping"))
    facts = _fact_semantics(value, start, until)
    _row_semantics(value, facts, complete)
    if value["state"] == "EMPTY" and (not complete or value["facts"]):
        raise ValueError("unproven_empty")


def _fact_semantics(value, start, until):
    keys = set()
    facts = {}
    for fact in value["facts"]:
        key = tuple(fact["key"].values())
        if key in keys:
            raise ValueError("duplicate_fact")
        keys.add(key)
        facts[key] = fact
        if fact["temporal"]["membership"] == "IN_WINDOW":
            if fact["completed_at"] is None or not start <= instant(fact["completed_at"]) < until:
                raise ValueError("invalid_membership")
        roles = [r["zone"] for r in fact["contributions"]]
        if len(roles) != len(set(roles)):
            raise ValueError("duplicate_role")
        for which in ("origin_operation", "effective_operation"):
            op = fact["provenance"][which]
            if op is not None and op["applied_revision"] is not None:
                if (
                    op["expected_revision"] is None
                    or op["applied_revision"] != op["expected_revision"] + 1
                ):
                    raise ValueError("invalid_revision")
    return facts


def _row_semantics(value, facts, complete):
    coverage = value["coverage"]
    for row in [*value["zones"], *value["bodymap_projection"]["targets"]]:
        q = row["window_result"]
        if q["state"] in ("UNKNOWN", "EMPTY"):
            if any(q[k] is not None for k in ("documented_sets", "resolved_credit", "bound")):
                raise ValueError("unknown_is_not_zero")
        elif q["bound"] is None or q["documented_sets"] is None or q["documented_sets"] < 1:
            raise ValueError("quantity_requires_evidence")
        if q["bound"] == "EXACT" and (
            coverage["scan"] != "COMPLETE" or coverage["mapping"] != "COMPLETE"
        ):
            raise ValueError("unproven_exact_window")
        if "evidence" in row and row["evidence"] is not None:
            e = row["evidence"]
            if e["exact_evidence"] != (
                e["bound"] == "EXACT" and e["execution_uncertain_sets"] == 0
            ):
                raise ValueError("invalid_evidence")
        last = row["last_qualified_observation"]
        if last is not None:
            fact = facts.get(tuple(last["key"].values()))
            if (
                not complete
                or fact is None
                or fact["completed_at"] != last["completed_at"]
                or fact["temporal"]["status"] != "DOCUMENTARY_PROVENANCE_QUALIFIED"
            ):
                raise ValueError("unproven_latest")


@dataclass(frozen=True)
class ObservedLoadResponse:
    data: dict[str, Any]

    @classmethod
    def model_validate(cls, value):
        try:
            data = _VALIDATOR.validate_python(value, strict=True)
            _semantics(data)
            return cls(data)
        except (ValueError, TypeError, KeyError, OverflowError):
            raise ValueError("invalid_observed_load_response") from None

    def model_dump(self):
        return copy.deepcopy(self.data)
