"""Fail closed for drifted SQLite nutrition tables without performing DDL."""

import re

from sqlalchemy import CheckConstraint, UniqueConstraint, inspect, text
from sqlalchemy.dialects.sqlite import dialect

from app.models.nutrition import NutritionDayRevision, NutritionTargetRevision


def _sql(value):
    # Normalize SQL formatting, preserving case and syntax inside string literals.
    parts = re.split(r"('(?:''|[^'])*')", str(value))
    return "".join(part if index % 2 else re.sub(r"[\s\"`\[\]]", "", part).lower()
                   for index, part in enumerate(parts))


def _columns_match(schema, table):
    actual = {c["name"]: c for c in schema.get_columns(table.name)}
    if set(actual) != set(table.columns.keys()):
        return False
    for column in table.columns:
        found = actual[column.name]
        if (str(found["type"]).upper() != str(column.type.compile(dialect=dialect())).upper()
                or found["nullable"] != column.nullable
                or _sql(found["default"]) != _sql(str(column.server_default.arg.compile(dialect=dialect()))
                                                 if column.server_default is not None else None)):
            return False
    return True


def nutrition_schema_available(db) -> bool:
    if db.get_bind().dialect.name != "sqlite":
        return False
    schema = inspect(db.connection())
    for model in (NutritionTargetRevision, NutritionDayRevision):
        table = model.__table__
        if not schema.has_table(table.name) or not _columns_match(schema, table):
            return False
        if schema.get_pk_constraint(table.name)["constrained_columns"] != ["id"]:
            return False
        ddl = db.scalar(text("SELECT sql FROM sqlite_master WHERE type='table' AND name=:name"), {"name": table.name})
        if not ddl or "primarykeyautoincrement" not in _sql(ddl):
            return False
        unique = {(c["name"], tuple(c["column_names"])) for c in schema.get_unique_constraints(table.name)}
        expected_unique = {(c.name, tuple(c.columns.keys())) for c in table.constraints if isinstance(c, UniqueConstraint)}
        if unique != expected_unique:
            return False
        checks = {_sql(c["sqltext"]) for c in schema.get_check_constraints(table.name)}
        expected_checks = {_sql(c.sqltext.compile(dialect=dialect(), compile_kwargs={"literal_binds": True, "include_table": False}))
                           for c in table.constraints if isinstance(c, CheckConstraint)}
        # Boolean(create_constraint=True) adds an implicit unnamed SQLite CHECK.
        for column in table.columns:
            if getattr(column.type, "create_constraint", False):
                expected_checks.add(_sql(f"{column.name} IN (0, 1)"))
        if checks != expected_checks:
            return False
        fks = set()
        for c in schema.get_foreign_keys(table.name):
            options = c.get("options", {})
            fks.add((tuple(c["constrained_columns"]), c["referred_table"], tuple(c["referred_columns"]),
                     options.get("ondelete", "NO ACTION"), bool(options.get("deferrable", False)), options.get("initially")))
        expected_fks = {(tuple(c.column_keys), c.referred_table.name,
                         tuple(element.column.name for element in c.elements),
                         c.ondelete or "NO ACTION", bool(c.deferrable), c.initially) for c in table.foreign_key_constraints}
        if fks != expected_fks:
            return False
        indexes = {(c["name"], tuple(c["column_names"]), bool(c["unique"])) for c in schema.get_indexes(table.name)}
        if indexes != {(i.name, tuple(i.columns.keys()), bool(i.unique)) for i in table.indexes}:
            return False
    return True
