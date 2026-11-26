"""Owner-scoped, read-only SQLite capture. No ORM identity map or writer calls."""

from __future__ import annotations

import json
import math
import sqlite3
from collections import Counter
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy.engine import make_url

from .contracts import ObservedLoadReadError
from .limits import BudgetExceeded, ReadBudget, ReadLimits

# All identifiers below are internal constants, never request input.
_TEXT = {
    "workout_sessions": {"status", "started_at", "template_slug_snapshot"},
    "session_exercises": {"exercise_name_snapshot", "substituted_name"},
    "set_logs": {"completed_at"},
    "first_plan_set_observations": {
        "id",
        "op_id",
        "body_digest",
        "recorded_at",
        "observation_json",
        "receipt_json",
    },
    "first_plan_execution_bindings": {
        "execution_profile_version",
        "scientific_session_id",
        "evaluation_id",
        "binding_digest",
        "immutable_payload_json",
    },
    "first_plan_evaluations": {"id", "result_json", "request_json", "body_digest", "created_at"},
    "first_plan_runtime_authorities": {
        "profile_key",
        "state",
        "publication_json",
        "packaging_digest",
        "approval_ref",
    },
    "exercises": {"name"},
}


def _json_lexical_admission(text, limits):
    depth = tokens = string_start = 0
    inside = escaped = False
    for i, char in enumerate(text):
        if inside:
            if char == '"' and not escaped:
                if len(text[string_start:i].encode("utf-8")) > limits.max_string:
                    raise ValueError("json_string_limit")
                inside = False
            if char == "\\" and not escaped:
                escaped = True
            else:
                escaped = False
        elif char == '"':
            inside = True
            string_start = i + 1
            tokens += 1
        elif char in "[{":
            depth += 1
            tokens += 1
            if depth > limits.max_depth:
                raise ValueError("json_depth_limit")
        elif char in "]}":
            depth -= 1
        elif char in ",:":
            tokens += 1
        if tokens > limits.max_tokens:
            raise ValueError("json_token_limit")


def _inspect_json(value, limits):
    if isinstance(value, str):
        if len(value.encode("utf-8")) > limits.max_string:
            raise ValueError("json_string_limit")
    elif isinstance(value, float) and not math.isfinite(value):
        raise ValueError("json_nonfinite")
    elif isinstance(value, dict):
        for key, child in value.items():
            _inspect_json(key, limits)
            _inspect_json(child, limits)
    elif isinstance(value, list):
        for child in value:
            _inspect_json(child, limits)


def bounded_json(raw: bytes, limits: ReadLimits):
    """Resource admission precedes JSON materialization; duplicate keys fail."""
    text = raw.decode("utf-8", errors="strict")
    _json_lexical_admission(text, limits)

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("json_duplicate_key")
            result[key] = value
        return result

    def no_constant(_):
        raise ValueError("json_nonfinite")

    result = json.loads(text, object_pairs_hook=pairs, parse_constant=no_constant)

    _inspect_json(result, limits)
    return result


class OwnedReadCapture:
    def __init__(self, connection, owner_id, query, limits, budget=None):
        self.connection = connection
        self.owner_id = owner_id
        self.query = query
        self.budget = budget or ReadBudget(limits)
        self.truncated = False
        self.reasons: set[str] = set()
        self._candidates = None
        self._sets = {}
        self._operations = {}
        self._bindings = {}
        self._graphs = {}
        self.exclusions = Counter()
        self.sentinels = 0
        self.frontiers = 0
        connection.set_progress_handler(self._progress, 1000)
        connection.set_authorizer(self._authorize)

    @staticmethod
    def _authorize(action, _arg1, _arg2, _database, _trigger):
        return (
            sqlite3.SQLITE_OK
            if action
            in {
                sqlite3.SQLITE_SELECT,
                sqlite3.SQLITE_READ,
                sqlite3.SQLITE_FUNCTION,
                sqlite3.SQLITE_TRANSACTION,
            }
            else sqlite3.SQLITE_DENY
        )

    def _progress(self):
        try:
            self.budget.take("vm_steps", 1000)
            self.budget.deadline()
            return 0
        except BudgetExceeded:
            return 1

    def rows(self, sql, params=()):
        self.budget.deadline()
        self.budget.take("statements")
        try:
            return self.connection.execute(sql, params)
        except sqlite3.DatabaseError as exc:
            raise ObservedLoadReadError() from exc

    def text(self, table, column, rowid, *, cap=None, json_body=False):
        """Read length before bytes; caller must first prove the owned row chain."""
        if table not in _TEXT or column not in _TEXT[table]:
            raise ValueError("unapproved_text_column")
        cap = self.budget.limits.text_bytes if cap is None else cap
        # Read-only blob handles include TEXT and avoid materializing oversize values.
        self.budget.deadline()
        self.budget.take("statements")
        kind = self.rows(
            f"SELECT typeof({column}) FROM {table} WHERE rowid=?",  # noqa: S608  # nosec B608
            (rowid,),
        ).fetchone()
        if kind is None or kind[0] == "null":
            return None, []
        if kind[0] != "text":
            return None, ["TEXT_LIMIT"]
        try:
            with self.connection.blobopen(table, column, rowid, readonly=True) as blob:
                size = len(blob)
                if size > cap:
                    return None, ["TEXT_LIMIT"]
                self.budget.take("db_input_bytes", size)
                raw = blob.read(size)
            return (bounded_json(raw, self.budget.limits) if json_body else raw.decode("utf-8")), []
        except (UnicodeError, ValueError, RecursionError, OverflowError):
            return None, ["JSON_LIMIT" if json_body else "TEXT_LIMIT"]

    def _prefix(self, sql, params, resource):
        available = getattr(self.budget.limits, resource) - self.budget.used.get(resource, 0)
        result = self.rows(sql + " LIMIT ?", (*params, available + 1)).fetchall()
        if len(result) > available:
            self.truncated = True
            self.reasons.add("SCAN_TRUNCATED")
            self.sentinels += 1
            self.frontiers += 1
        result = result[:available]
        self.budget.take(resource, len(result))
        return result

    def candidates(self):
        if self._candidates is not None:
            return iter(self._candidates)
        result = []
        # Selection precedes temporal filtering, so an old prefix is NEVER a recent sample.
        sessions = self._prefix(
            "SELECT id,CASE WHEN typeof(excluded_from_stats)='integer' THEN excluded_from_stats END FROM workout_sessions WHERE user_id=? ORDER BY id",
            (self.owner_id,),
            "sessions",
        )
        for sid, excluded in sessions:
            status, errors = self.text("workout_sessions", "status", sid)
            self.reasons.update(errors)
            if (
                status not in {"completed", "in_progress", "abandoned"}
                or type(excluded) is not int
                or excluded not in (0, 1)
            ):
                self.reasons.add("SESSION_NOT_ELIGIBLE")
                self.exclusions["SESSION_NOT_ELIGIBLE"] += 1
                for error in set(errors):
                    self.exclusions[error] += 1
                continue
            if errors or status != "completed" or excluded != 0:
                self.exclusions["SESSION_NOT_ELIGIBLE"] += 1
                continue
            marker, marker_errors = self.text("workout_sessions", "template_slug_snapshot", sid)
            started, start_errors = self.text("workout_sessions", "started_at", sid)
            exercises = self._prefix(
                "SELECT id,CASE WHEN typeof(position)='integer' THEN position ELSE -1 END,CASE WHEN typeof(template_exercise_id)='integer' THEN template_exercise_id WHEN template_exercise_id IS NULL THEN NULL ELSE -1 END FROM session_exercises WHERE session_id=? ORDER BY id",
                (sid,),
                "exercises",
            )
            for eid, position, template_id in exercises:
                name, name_errors = self.text("session_exercises", "exercise_name_snapshot", eid)
                substitute, substitute_errors = self.text(
                    "session_exercises", "substituted_name", eid
                )
                sets = self._prefix(
                    "SELECT id,CASE WHEN typeof(set_index)='integer' THEN set_index ELSE -1 END,CASE WHEN typeof(reps)='integer' THEN reps END,CASE WHEN typeof(weight_kg) IN ('integer','real') THEN weight_kg END FROM set_logs WHERE session_exercise_id=? AND kind='work' AND completed=1 ORDER BY id",
                    (eid,),
                    "work_sets",
                )
                for set_id, set_index, reps, weight in sets:
                    completed_at, time_errors = self.text("set_logs", "completed_at", set_id)
                    row = dict(
                        session_id=sid,
                        session_exercise_id=eid,
                        set_log_id=set_id,
                        position=position,
                        template_exercise_id=template_id,
                        set_index=set_index,
                        exercise_name_snapshot=name,
                        substituted_name=substitute,
                        reps=reps,
                        weight_kg=weight,
                        completed_at=completed_at,
                        started_at=started,
                        template_slug_snapshot=marker,
                        reasons=marker_errors
                        + start_errors
                        + name_errors
                        + substitute_errors
                        + time_errors,
                    )
                    self._sets[set_id] = row
                    result.append(row)
        self._candidates = result
        return iter(result)

    def operation_rows(self, set_id):
        if set_id in self._operations:
            return self._operations[set_id]
        # Populate the same capture's owned prefix before using an arbitrary ID.
        list(self.candidates())
        if set_id not in self._sets:
            return []
        candidate = self._sets[set_id]
        records = self._prefix(
            "SELECT rowid,CASE WHEN typeof(owner_id)='integer' THEN owner_id END,CASE WHEN typeof(session_id)='integer' THEN session_id END,CASE WHEN typeof(session_exercise_id)='integer' THEN session_exercise_id END,CASE WHEN typeof(expected_revision)='integer' THEN expected_revision END,CASE WHEN typeof(applied_revision)='integer' THEN applied_revision END FROM first_plan_set_observations WHERE set_id=? ORDER BY applied_revision",
            (set_id,),
            "operations",
        )
        result = []
        for rowid, owner, sid, eid, expected, applied in records:
            item = dict(
                owner_id=owner,
                session_id=sid,
                session_exercise_id=eid,
                set_id=set_id,
                expected_revision=expected,
                applied_revision=applied,
                reasons=[],
            )
            if (owner, sid, eid) != (
                self.owner_id,
                candidate["session_id"],
                candidate["session_exercise_id"],
            ):
                item["reasons"] = ["OWNERSHIP_MISMATCH"]
                result.append(item)
                continue
            for column in (
                "id",
                "op_id",
                "body_digest",
                "recorded_at",
                "observation_json",
                "receipt_json",
            ):
                is_json = column.endswith("_json")
                value, errors = self.text(
                    "first_plan_set_observations",
                    column,
                    rowid,
                    cap=self.budget.limits.body_json if is_json else None,
                    json_body=is_json,
                )
                item[column.removesuffix("_json")] = value
                item["reasons"].extend(errors)
            result.append(item)
        self._operations[set_id] = result
        return result

    def has_table(self, table):
        return (
            self.rows(
                "SELECT 1 FROM sqlite_master WHERE type=? AND name=?", ("table", table)
            ).fetchone()
            is not None
        )

    def alias_name(self, normalized):
        if not self.has_table("exercise_aliases"):
            return None
        row = self.rows(
            "SELECT CASE WHEN typeof(exercise_id)='integer' THEN exercise_id END FROM exercise_aliases WHERE normalized=? LIMIT 1",
            (normalized,),
        ).fetchone()
        if row is None:
            return None
        name, errors = self.text("exercises", "name", row[0])
        return None if errors else name

    def binding_for(self, session_id):
        list(self.candidates())
        if session_id not in {r["session_id"] for r in self._candidates}:
            return None
        if session_id in self._bindings:
            return self._bindings[session_id]
        if not self.has_table("first_plan_execution_bindings"):
            return None
        row = self.rows(
            "SELECT rowid,CASE WHEN typeof(owner_id)='integer' THEN owner_id END FROM first_plan_execution_bindings WHERE session_id=?",
            (session_id,),
        ).fetchone()
        if row is None:
            return None
        if row[1] != self.owner_id:
            return {"reasons": ["PROFILE_MISMATCH"]}
        result = {"reasons": []}
        for column in (
            "execution_profile_version",
            "scientific_session_id",
            "evaluation_id",
            "binding_digest",
            "immutable_payload_json",
        ):
            is_json = column.endswith("_json")
            value, errors = self.text(
                "first_plan_execution_bindings",
                column,
                row[0],
                cap=self.budget.limits.binding_json if is_json else None,
                json_body=is_json,
            )
            result[column.removesuffix("_json")] = value
            result["reasons"].extend(errors)
        self._bindings[session_id] = result
        return result

    def evaluation_for(self, evaluation_id):
        row = self.rows(
            "SELECT rowid,CASE WHEN typeof(owner_id)='integer' THEN owner_id END,CASE WHEN typeof(authority_generation)='integer' THEN authority_generation END FROM first_plan_evaluations WHERE id=?",
            (evaluation_id,),
        ).fetchone()
        if row is None or row[1] != self.owner_id:
            return None
        result = {"authority_generation": row[2], "reasons": []}
        for column in ("id", "result_json"):
            value, errors = self.text(
                "first_plan_evaluations",
                column,
                row[0],
                cap=self.budget.limits.binding_json if column.endswith("_json") else None,
                json_body=column.endswith("_json"),
            )
            result[column.removesuffix("_json")] = value
            result["reasons"].extend(errors)
        return result

    def runtime_authority(self):
        row = self.rows(
            "SELECT rowid,CASE WHEN typeof(generation)='integer' THEN generation END FROM first_plan_runtime_authorities WHERE profile_key=?",
            ("first-session-runtime/3.0.0",),
        ).fetchone()
        if row is None:
            return None
        result = {"generation": row[1], "reasons": []}
        for column in ("state", "publication_json", "packaging_digest", "approval_ref"):
            value, errors = self.text(
                "first_plan_runtime_authorities",
                column,
                row[0],
                cap=self.budget.limits.body_json if column.endswith("_json") else None,
                json_body=column.endswith("_json"),
            )
            result[column.removesuffix("_json")] = value
            result["reasons"].extend(errors)
        return result

    def graph_for(self, session_id):
        list(self.candidates())
        if session_id not in {r["session_id"] for r in self._candidates}:
            return None
        if session_id in self._graphs:
            return self._graphs[session_id]
        # Includes incomplete/preparation rows solely to validate the immutable graph.
        rows = self._prefix(
            "SELECT e.id,CASE WHEN typeof(e.position)='integer' THEN e.position ELSE -1 END,CASE WHEN typeof(e.template_exercise_id)='integer' THEN e.template_exercise_id WHEN e.template_exercise_id IS NULL THEN NULL ELSE -1 END,s.id,CASE WHEN typeof(s.set_index)='integer' THEN s.set_index ELSE -1 END,s.kind='work' FROM session_exercises e LEFT JOIN set_logs s ON s.session_exercise_id=e.id WHERE e.session_id=? ORDER BY e.position,e.id,s.set_index,s.id",
            (session_id,),
            "graph_rows",
        )
        self._graphs[session_id] = rows
        return rows


@contextmanager
def open_owned_capture(database_url, owner_id, query, limits=ReadLimits()):
    url = make_url(database_url)
    if (
        url.drivername != "sqlite"
        or not url.database
        or url.database == ":memory:"
        or url.query
        or type(owner_id) is not int
        or owner_id <= 0
    ):
        raise ObservedLoadReadError()
    path = Path(url.database).resolve(strict=True)
    budget = ReadBudget(limits)
    connection = sqlite3.connect(
        path.as_uri() + "?mode=ro", uri=True, timeout=0.1, isolation_level=None
    )
    try:
        budget.take("statements", 2)
        connection.execute("PRAGMA query_only=ON")
        connection.execute("BEGIN")
        yield OwnedReadCapture(connection, owner_id, query, limits, budget)
    except BudgetExceeded as exc:
        raise ObservedLoadReadError() from exc
    finally:
        connection.close()
