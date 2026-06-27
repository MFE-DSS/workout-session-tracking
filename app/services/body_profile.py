"""Sb_Body_01 — Manual Body Profile MVP (service layer).

Pure, deterministic logic for the manual body profile:
  * measurement field specs + plausibility bounds ;
  * derived ratios computed ON THE FLY (never persisted) with explicit
    fallback / proxy flags and prudent, non-medical wording ;
  * granular consent helpers (``body_measurements``) ;
  * CRUD with ownership + hard-delete ;
  * a user-scoped Body export payload.

Scope guardrails (cf. docs/strategy/SPIGNOS_BODY_SIGNAL_MODEL_SPEC.md):
  - No medical diagnosis, no body-fat estimation, no protected-class
    inference, no humiliating scoring, "morphotype" is never a primary
    truth. The wording guard (FORBIDDEN_WORDING) is enforced by tests.
  - No external provider, no photo, no image analysis here.
  - Ratios are derived signals: recalculable, never stored.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.body_consent import (
    CONSENT_BODY_MEASUREMENTS,
    CONSENT_TEXT_VERSION,
    BodyConsent,
)
from app.models.measurement import BodyMeasurement

# ---------------------------------------------------------------------------
# Measurement field specs (manual MVP). Keys are the real ORM column names
# on BodyMeasurement (reuse existing columns; additive ones from this
# sprint: shoulder_width_cm, calf_cm_left, calf_cm_right). ``height_cm``
# lives on the User profile and is NOT edited here.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FieldSpec:
    key: str
    label: str
    min: float
    max: float


BODY_MEASUREMENT_FIELDS: list[FieldSpec] = [
    FieldSpec("weight_kg", "Poids (kg)", 30, 300),
    FieldSpec("waist_cm", "Tour de taille (cm)", 40, 200),
    FieldSpec("neck_cm", "Tour de cou (cm)", 25, 60),
    FieldSpec("chest_cm", "Tour de poitrine (cm)", 60, 160),
    FieldSpec("shoulder_width_cm", "Largeur d'épaules (cm)", 30, 60),
    FieldSpec("arm_cm_left", "Bras gauche (cm)", 20, 60),
    FieldSpec("arm_cm_right", "Bras droit (cm)", 20, 60),
    FieldSpec("thigh_cm_left", "Cuisse gauche (cm)", 30, 90),
    FieldSpec("thigh_cm_right", "Cuisse droite (cm)", 30, 90),
    FieldSpec("hip_cm", "Tour de hanches (cm)", 60, 180),
    FieldSpec("calf_cm_left", "Mollet gauche (cm)", 20, 60),
    FieldSpec("calf_cm_right", "Mollet droit (cm)", 20, 60),
]

HEIGHT_BOUNDS = (120.0, 230.0)

_FIELD_BY_KEY = {f.key: f for f in BODY_MEASUREMENT_FIELDS}


# ---------------------------------------------------------------------------
# Wording guard — non-medical, non-discriminatory.
# ---------------------------------------------------------------------------

FORBIDDEN_WORDING: frozenset[str] = frozenset(
    {
        "diagnostic",
        "diagnostique",
        "pathologie",
        "maladie",
        "clinique",
        "body fat",
        "masse grasse médicale",
        "obésité",
        "obesite",
        "morphotype",
        "ectomorphe",
        "mésomorphe",
        "mesomorphe",
        "endomorphe",
        "ethnie",
        "ethnique",
        "race",
        "raciale",
        "attractivité",
        "attractivite",
        "santé mentale",
        "sante mentale",
    }
)


def assert_no_forbidden_wording(text: str) -> None:
    """Raise ValueError if any forbidden (medical / discriminatory) term
    appears in *text* (case-insensitive)."""
    low = text.lower()
    for term in FORBIDDEN_WORDING:
        if term in low:
            raise ValueError(f"forbidden wording detected: {term!r} in {text!r}")


# ---------------------------------------------------------------------------
# Validation / parsing
# ---------------------------------------------------------------------------


def parse_and_validate(raw: dict[str, str]) -> dict[str, float]:
    """Parse a form mapping {field_key: raw_string} into validated floats.

    - Empty / whitespace values are skipped (partial entries allowed).
    - Non-numeric values raise ValueError.
    - Out-of-plausibility-bounds values raise ValueError.
    - At least one field must be provided, else ValueError.

    Returns only the provided, valid fields.
    """
    cleaned: dict[str, float] = {}
    for spec in BODY_MEASUREMENT_FIELDS:
        raw_val = (raw.get(spec.key) or "").strip().replace(",", ".")
        if not raw_val:
            continue
        try:
            value = float(raw_val)
        except (ValueError, TypeError):
            raise ValueError(f"{spec.label} : valeur non numérique") from None
        if value < spec.min or value > spec.max:
            raise ValueError(
                f"{spec.label} : valeur hors plage plausible "
                f"({spec.min:g}–{spec.max:g})"
            )
        cleaned[spec.key] = value
    if not cleaned:
        raise ValueError("Aucune mesure renseignée.")
    return cleaned


# ---------------------------------------------------------------------------
# Derived ratios (on the fly, never persisted). ratio_engine_version is the
# contract marker for reproducibility (cf. signal model spec §1.9).
# ---------------------------------------------------------------------------

RATIO_ENGINE_VERSION = 1


@dataclass(frozen=True)
class RatioResult:
    key: str
    label: str
    value: float | None
    available: bool
    is_proxy: bool
    interpretation: str
    confidence: str  # "ok" | "proxy" | "none"
    engine_version: int = RATIO_ENGINE_VERSION


def _avg(a: float | None, b: float | None) -> float | None:
    if a is not None and b is not None:
        return (a + b) / 2
    return a if a is not None else b


def _ratio(key, label, value, interp, *, is_proxy=False) -> RatioResult:
    if value is None:
        return RatioResult(key, label, None, False, False, interp, "none")
    return RatioResult(
        key, label, round(value, 3), True, is_proxy, interp,
        "proxy" if is_proxy else "ok",
    )


def compute_ratios(
    m: BodyMeasurement | None, height_cm: float | None
) -> list[RatioResult]:
    """Compute the 6 MVP ratios from the latest confirmed measurement.

    Missing inputs degrade gracefully: either a documented proxy
    (flagged ``is_proxy``) or ``available=False`` (never an invented
    value). Interpretations are prudent and non-medical.
    """
    waist = getattr(m, "waist_cm", None) if m else None
    chest = getattr(m, "chest_cm", None) if m else None
    shoulder = getattr(m, "shoulder_width_cm", None) if m else None
    arm_l = getattr(m, "arm_cm_left", None) if m else None
    arm_r = getattr(m, "arm_cm_right", None) if m else None
    thigh_l = getattr(m, "thigh_cm_left", None) if m else None
    thigh_r = getattr(m, "thigh_cm_right", None) if m else None
    calf_l = getattr(m, "calf_cm_left", None) if m else None
    calf_r = getattr(m, "calf_cm_right", None) if m else None

    results: list[RatioResult] = []

    # shoulder/waist — proxy via chest/waist when shoulder is absent.
    if shoulder is not None and waist:
        results.append(_ratio(
            "shoulder_to_waist_ratio", "Épaules / taille",
            shoulder / waist, "Équilibre visuel du haut du corps.",
        ))
    elif chest is not None and waist:
        results.append(_ratio(
            "shoulder_to_waist_ratio", "Épaules / taille (proxy poitrine)",
            chest / waist, "Équilibre visuel du haut du corps (proxy poitrine).",
            is_proxy=True,
        ))
    else:
        results.append(_ratio(
            "shoulder_to_waist_ratio", "Épaules / taille", None,
            "Équilibre visuel du haut du corps.",
        ))

    results.append(_ratio(
        "waist_to_height_ratio", "Taille (tour) / hauteur",
        (waist / height_cm) if (waist and height_cm) else None,
        "Tour de taille relatif à la hauteur (tendance, non médical).",
    ))

    results.append(_ratio(
        "chest_to_waist_ratio", "Poitrine / taille",
        (chest / waist) if (chest is not None and waist) else None,
        "Équilibre torse / taille.",
    ))

    arm_avg = _avg(arm_l, arm_r)
    results.append(_ratio(
        "arm_symmetry_ratio", "Symétrie des bras",
        (abs(arm_l - arm_r) / arm_avg) if (arm_l is not None and arm_r is not None and arm_avg) else None,
        "Écart latéral des bras (indicatif).",
    ))

    thigh_avg = _avg(thigh_l, thigh_r)
    results.append(_ratio(
        "thigh_symmetry_ratio", "Symétrie des cuisses",
        (abs(thigh_l - thigh_r) / thigh_avg) if (thigh_l is not None and thigh_r is not None and thigh_avg) else None,
        "Écart latéral des cuisses (indicatif).",
    ))

    # upper/lower balance — partial proxy when calf is absent.
    calf_avg = _avg(calf_l, calf_r)
    upper = None
    if chest is not None and arm_avg is not None:
        upper = chest + arm_avg
    lower_full = (thigh_avg + calf_avg) if (thigh_avg is not None and calf_avg is not None) else None
    if upper is not None and lower_full:
        results.append(_ratio(
            "upper_lower_balance_proxy", "Équilibre haut / bas",
            upper / lower_full, "Équilibre visuel haut / bas du corps (indicatif).",
        ))
    elif upper is not None and thigh_avg:
        results.append(_ratio(
            "upper_lower_balance_proxy", "Équilibre haut / bas (proxy partiel)",
            upper / thigh_avg,
            "Équilibre visuel haut / bas du corps (proxy partiel, indicatif).",
            is_proxy=True,
        ))
    else:
        results.append(_ratio(
            "upper_lower_balance_proxy", "Équilibre haut / bas", None,
            "Équilibre visuel haut / bas du corps (indicatif).",
        ))

    return results


def all_user_facing_strings() -> list[str]:
    """Every static user-facing label/interpretation — used by the
    wording guard test to assert no medical/discriminatory term leaks."""
    strings = [f.label for f in BODY_MEASUREMENT_FIELDS]
    for r in compute_ratios(None, None):
        strings.append(r.label)
        strings.append(r.interpretation)
    return strings


# ---------------------------------------------------------------------------
# Consent helpers (granular ; MVP = body_measurements)
# ---------------------------------------------------------------------------


def get_consent(
    db: Session, user_id: int, consent_type: str = CONSENT_BODY_MEASUREMENTS
) -> BodyConsent | None:
    return db.execute(
        select(BodyConsent).where(
            BodyConsent.user_id == user_id,
            BodyConsent.consent_type == consent_type,
        )
    ).scalar_one_or_none()


def has_active_consent(
    db: Session, user_id: int, consent_type: str = CONSENT_BODY_MEASUREMENTS
) -> bool:
    c = get_consent(db, user_id, consent_type)
    return bool(c and c.granted)


def set_consent(
    db: Session,
    user_id: int,
    granted: bool,
    consent_type: str = CONSENT_BODY_MEASUREMENTS,
) -> BodyConsent:
    """Grant or withdraw consent. Explicit, versioned, timestamped."""
    now = datetime.now(UTC)
    c = get_consent(db, user_id, consent_type)
    if c is None:
        c = BodyConsent(
            user_id=user_id,
            consent_type=consent_type,
            granted=False,
            consent_version=CONSENT_TEXT_VERSION,
        )
        db.add(c)
    c.granted = granted
    c.consent_version = CONSENT_TEXT_VERSION
    if granted:
        c.granted_at = now
        c.withdrawn_at = None
    else:
        c.withdrawn_at = now
    db.commit()
    db.refresh(c)
    return c


# ---------------------------------------------------------------------------
# Measurement CRUD (ownership + hard-delete)
# ---------------------------------------------------------------------------


def create_measurement(
    db: Session, user_id: int, cleaned: dict[str, float]
) -> BodyMeasurement:
    """Persist a validated measurement row. ``cleaned`` must already be
    validated by ``parse_and_validate``."""
    m = BodyMeasurement(user_id=user_id, measured_at=datetime.now(UTC))
    for key, value in cleaned.items():
        if key in _FIELD_BY_KEY:
            setattr(m, key, value)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


def get_owned_measurement(
    db: Session, user_id: int, measurement_id: int
) -> BodyMeasurement | None:
    """Return the measurement only if it belongs to *user_id* (ownership)."""
    return db.execute(
        select(BodyMeasurement).where(
            BodyMeasurement.id == measurement_id,
            BodyMeasurement.user_id == user_id,
        )
    ).scalar_one_or_none()


def list_measurements(
    db: Session, user_id: int, limit: int = 50
) -> list[BodyMeasurement]:
    return list(
        db.execute(
            select(BodyMeasurement)
            .where(BodyMeasurement.user_id == user_id)
            .order_by(BodyMeasurement.measured_at.desc())
            .limit(limit)
        ).scalars().all()
    )


def update_measurement(
    db: Session, m: BodyMeasurement, cleaned: dict[str, float]
) -> BodyMeasurement:
    """Replace the editable fields of an owned measurement. Fields absent
    from ``cleaned`` are reset to NULL (the form submits the full set)."""
    for spec in BODY_MEASUREMENT_FIELDS:
        setattr(m, spec.key, cleaned.get(spec.key))
    db.commit()
    db.refresh(m)
    return m


def delete_measurement(db: Session, m: BodyMeasurement) -> None:
    """Hard-delete (no soft-delete masking)."""
    db.delete(m)
    db.commit()


# ---------------------------------------------------------------------------
# Body export (user-scoped)
# ---------------------------------------------------------------------------

BODY_EXPORT_SCHEMA_VERSION = 1


def _measurement_dict(m: BodyMeasurement) -> dict:
    out: dict = {"id": m.id, "measured_at": m.measured_at.isoformat() if m.measured_at else None}
    for spec in BODY_MEASUREMENT_FIELDS:
        out[spec.key] = getattr(m, spec.key, None)
    return out


def build_body_export(db: Session, user_id: int) -> dict:
    """User-scoped Body export: measurements + consents + derived ratios
    of the latest measurement. Never includes another user's data."""
    measurements = list_measurements(db, user_id, limit=10_000)
    consents = db.execute(
        select(BodyConsent).where(BodyConsent.user_id == user_id)
    ).scalars().all()
    latest = measurements[0] if measurements else None
    return {
        "schema_version": BODY_EXPORT_SCHEMA_VERSION,
        "exported_at": datetime.now(UTC).isoformat(),
        "ratio_engine_version": RATIO_ENGINE_VERSION,
        "measurements": [_measurement_dict(m) for m in measurements],
        "consents": [
            {
                "consent_type": c.consent_type,
                "granted": c.granted,
                "consent_version": c.consent_version,
                "granted_at": c.granted_at.isoformat() if c.granted_at else None,
                "withdrawn_at": c.withdrawn_at.isoformat() if c.withdrawn_at else None,
            }
            for c in consents
        ],
        "latest_ratios": [
            {
                "key": r.key,
                "value": r.value,
                "available": r.available,
                "is_proxy": r.is_proxy,
                "confidence": r.confidence,
            }
            for r in compute_ratios(latest, None)
        ],
    }
