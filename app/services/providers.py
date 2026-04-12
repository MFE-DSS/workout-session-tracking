"""MetricsProvider abstraction for external data sources.

Defines a Protocol for metrics providers (manual entry, Apple Health,
Garmin, Withings, etc.) and a simple registry.

Currently only ManualProvider is implemented - it reads physical
profile fields from the User model. NOT connected to any route.
This is a documented contract for future extension.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


@dataclass
class BodyMetrics:
    weight_kg: Optional[float] = None
    height_cm: Optional[int] = None
    resting_hr: Optional[int] = None
    waist_cm: Optional[float] = None
    bp_systolic: Optional[int] = None
    bp_diastolic: Optional[int] = None


@dataclass
class ActivitySummary:
    steps: Optional[int] = None
    calories_burned: Optional[int] = None
    distance_km: Optional[float] = None
    active_minutes: Optional[int] = None
    period_days: int = 30


class MetricsProvider(Protocol):
    def get_body_metrics(self, db: Session, user_id: int) -> Optional[BodyMetrics]: ...
    def get_activity_summary(self, db: Session, user_id: int, days: int = 30) -> Optional[ActivitySummary]: ...
    def supports(self) -> list[str]: ...


class ManualProvider:
    """Reads physical profile fields from the User model."""

    def get_body_metrics(self, db: Session, user_id: int) -> Optional[BodyMetrics]:
        user = db.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()
        if user is None:
            return None
        fields = (user.height_cm, user.weight_kg, user.resting_hr,
                  user.waist_cm, user.bp_systolic, user.bp_diastolic)
        if all(f is None for f in fields):
            return None
        return BodyMetrics(
            weight_kg=user.weight_kg,
            height_cm=user.height_cm,
            resting_hr=user.resting_hr,
            waist_cm=user.waist_cm,
            bp_systolic=user.bp_systolic,
            bp_diastolic=user.bp_diastolic,
        )

    def get_activity_summary(
        self, db: Session, user_id: int, days: int = 30
    ) -> Optional[ActivitySummary]:
        return None

    def supports(self) -> list[str]:
        return ["body_metrics"]


class ProviderRegistry:
    """Simple dict-based registry for metrics providers."""

    def __init__(self) -> None:
        self._providers: dict[str, MetricsProvider] = {}

    def register(self, name: str, provider: MetricsProvider) -> None:
        self._providers[name] = provider

    def get(self, name: str) -> Optional[MetricsProvider]:
        return self._providers.get(name)

    def list_available(self) -> list[str]:
        return list(self._providers.keys())
