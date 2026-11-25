"""Per-capture ceilings. Lowering a budget never licenses raising another."""

from __future__ import annotations

import time
from dataclasses import dataclass, fields


class BudgetExceeded(ValueError):
    def __init__(self, resource: str):
        self.resource = resource
        super().__init__("observed_load_resource_limit")


@dataclass(frozen=True)
class ReadLimits:
    sessions: int = 200
    exercises: int = 200
    work_sets: int = 500
    operations: int = 1000
    graph_rows: int = 500
    statements: int = 4096
    db_input_bytes: int = 2 * 1024 * 1024
    vm_steps: int = 2_000_000
    body_json: int = 8192
    binding_json: int = 131072
    text_bytes: int = 512
    max_depth: int = 16
    max_tokens: int = 65536
    max_string: int = 4096
    source_total: int = 16 * 1024 * 1024
    source_files: int = 128
    output_bytes: int = 1024 * 1024
    cpu_soft: int = 2
    cpu_hard: int = 3
    address_space: int = 512 * 1024 * 1024
    sql_seconds: float = 1.5
    wall_seconds: float = 3.0

    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if type(value) not in (int, float) or not 0 < value <= field.default:
                raise ValueError("invalid_observed_load_limit")
        if self.cpu_soft > self.cpu_hard:
            raise ValueError("invalid_observed_load_cpu_limit")


class ReadBudget:
    def __init__(self, limits: ReadLimits):
        self.limits = limits
        self.used: dict[str, int] = {}
        self.started = time.monotonic()

    def take(self, resource: str, amount: int = 1):
        if type(amount) is not int or amount < 0:
            raise ValueError("invalid_budget_amount")
        limit = getattr(self.limits, resource)
        current = self.used.get(resource, 0)
        if current + amount > limit:
            raise BudgetExceeded(resource)
        self.used[resource] = current + amount

    def deadline(self):
        if time.monotonic() - self.started > self.limits.sql_seconds:
            raise BudgetExceeded("time")
