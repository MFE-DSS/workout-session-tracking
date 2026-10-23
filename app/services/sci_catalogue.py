"""Catalogue scientifique d'exercices — chargeur (`Sb_SCI_V2_01`).

Donnée **statique et versionnée** (`data/sci/`), produite par
`scripts/generate_sci_catalogue.py` et validée par `scripts/validate_sci_catalogue.py`.
Spec : `Sx_SCI_V2_CATALOGUE_INTEGRATION_01`.

**Ce que ce module ne fait pas.** Il ne sert rien. Aucun appelant du produit ne l'importe :
ni résolveur d'historique, ni registre d'exposition, ni recommandation. Il rend la donnée
lisible, déterministe et immuable — rien de plus.

**Deux autorités distinctes.** Le catalogue porte les **rôles bruts** de chaque contribution
(`PRIMARY`, `SECONDARY`, `MINOR`, `UNKNOWN`) ; la politique de crédit, dans son propre fichier,
dit ce que chaque rôle crédite. On ne stocke jamais le crédit à la place du rôle : il se
recalcule, et changer de politique ne réécrit aucune fiche.

**`UNKNOWN` n'est pas zéro.** Le crédit d'un rôle inconnu est la sentinelle `UNKNOWN_CREDIT`,
qui refuse l'arithmétique : une somme qui la rencontre échoue au lieu de la compter pour rien.
"""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any

_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "sci"
CATALOGUE_PATH = _DATA_DIR / "exercise_catalogue.json"
CREDIT_POLICY_PATH = _DATA_DIR / "exposure_credit_policy.json"

ROLES = frozenset({"PRIMARY", "SECONDARY", "MINOR", "UNKNOWN"})
CANONICAL = "CANONICAL"
LEGACY_ALIAS = "LEGACY_ALIAS"
_HEADER_KEYS = ("catalogue_version", "schema_id", "credit_policy_version", "sources_digest")


class SciCatalogueError(ValueError):
    """Donnée scientifique incohérente — refusée au chargement, jamais lue à moitié."""


class _UnknownCredit:
    """Crédit d'un rôle `UNKNOWN` : ni 0, ni 0,5, et inutilisable dans une somme."""

    __slots__ = ()

    def __repr__(self) -> str:
        return "UNKNOWN_CREDIT"

    def __bool__(self) -> bool:
        raise TypeError("UNKNOWN_CREDIT n'a pas de valeur de vérité : tester `is UNKNOWN_CREDIT`")


UNKNOWN_CREDIT = _UnknownCredit()


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({k: _freeze(v) for k, v in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(v) for v in value)
    return value


# ---------------------------------------------------------------------------
# Catalogue
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SciCatalogue:
    header: Mapping[str, Any]
    records: tuple[Mapping[str, Any], ...]
    digest: str
    _by_id: Mapping[str, Mapping[str, Any]] = field(repr=False, compare=False)

    def record(self, exercise_id: str) -> Mapping[str, Any]:
        """La fiche de ce `exercise_id` (variant_key de l'EKB). `KeyError` s'il n'existe pas."""
        return self._by_id[exercise_id]

    def canonical_of(self, exercise_id: str) -> Mapping[str, Any]:
        """La fiche canonique de l'identité scientifique de cet exercice (lui-même s'il l'est)."""
        record = self.record(exercise_id)
        alias_of = record["identity"]["alias_of"]
        return record if alias_of is None else self.record(alias_of)

    def compiler_candidates(self) -> tuple[Mapping[str, Any], ...]:
        """Un mouvement = un candidat : les fiches CANONICAL seulement, jamais un alias."""
        return tuple(r for r in self.records if r["identity"]["identity_relation"] == CANONICAL)

    def raw_roles(self, exercise_id: str) -> dict[str, str]:
        """Rôle brut par zone, tel qu'écrit dans la fiche."""
        return {c["zone"]: c["role"] for c in self.record(exercise_id)["exercise_science"]["contributions"]}


def requirement_is_known(record: Mapping[str, Any]) -> bool:
    """Vrai si l'exigence d'équipement est RÉSOLUE. Une liste vide ne le dit jamais à elle seule :
    `[]` + `UNKNOWN` signifie « on ne sait pas », pas « aucun matériel »."""
    return record["exercise_operational"]["equipment_requirement_status"] == "RESOLVED"


def _check_identities(by_id: Mapping[str, Mapping[str, Any]]) -> None:
    for rid, record in by_id.items():
        identity = record.get("identity")
        if identity is None:
            raise SciCatalogueError(f"{rid} : bloc identity absent")
        if identity["identity_relation"] == LEGACY_ALIAS:
            target = by_id.get(identity["alias_of"])
            if target is None or target["identity"]["identity_relation"] != CANONICAL:
                raise SciCatalogueError(f"{rid} : alias_of {identity['alias_of']!r} n'est pas une fiche canonique")


def load_catalogue(path: Path = CATALOGUE_PATH) -> SciCatalogue:
    raw = path.read_bytes()
    doc = json.loads(raw)
    header = doc.get("catalogue_header")
    if not isinstance(header, dict) or any(k not in header for k in _HEADER_KEYS):
        raise SciCatalogueError(f"en-tête incomplet : {_HEADER_KEYS} requis")
    ids = [r["exercise_id"] for r in doc["records"]]
    if ids != sorted(ids):
        raise SciCatalogueError("fiches non triées par exercise_id")
    if len(set(ids)) != len(ids):
        raise SciCatalogueError("exercise_id en double")
    records = tuple(_freeze(r) for r in doc["records"])
    by_id = MappingProxyType({r["exercise_id"]: r for r in records})
    _check_identities(by_id)
    return SciCatalogue(header=_freeze(header), records=records,
                        digest=hashlib.sha256(raw).hexdigest(), _by_id=by_id)


# ---------------------------------------------------------------------------
# Politique de crédit d'exposition
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CreditPolicy:
    policy_id: str
    credits: Mapping[str, float | _UnknownCredit]

    def credit(self, role: str) -> float | _UnknownCredit:
        if role not in self.credits:
            raise ValueError(f"rôle hors vocabulaire : {role!r}")
        return self.credits[role]


def _credit_value(role: str, value: Any) -> float | _UnknownCredit:
    if role == "UNKNOWN":
        if value != "UNKNOWN":
            raise SciCatalogueError("UNKNOWN doit créditer UNKNOWN — jamais un nombre")
        return UNKNOWN_CREDIT
    if isinstance(value, bool) or not isinstance(value, int | float) or not 0.0 <= value <= 1.0:
        raise SciCatalogueError(f"crédit de {role} invalide : {value!r}")
    return float(value)


def load_credit_policy(path: Path = CREDIT_POLICY_PATH) -> CreditPolicy:
    doc = json.loads(path.read_text(encoding="utf-8"))
    credits = doc.get("credits", {})
    if set(credits) != ROLES:
        raise SciCatalogueError(f"la politique doit créditer exactement {sorted(ROLES)}")
    policy_id = doc.get("policy_id")
    if not isinstance(policy_id, str) or not policy_id:
        raise SciCatalogueError("policy_id manquant")
    return CreditPolicy(policy_id=policy_id,
                        credits=MappingProxyType({r: _credit_value(r, v) for r, v in credits.items()}))
