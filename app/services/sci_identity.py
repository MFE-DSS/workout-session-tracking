"""Résolveur d'identité scientifique (`Sb_SCI_V2_02`, spec §6).

    nom historique / variant_key  →  identité scientifique  →  fiche canonique

**Deux couches d'identité, jamais confondues.** L'identité d'EXERCICE (`exercises` /
`exercise_aliases`, `exercise_identity`) décide de la continuité des charges et reste l'autorité
du produit servi. L'identité SCIENTIFIQUE (bloc `identity` du catalogue) ne décide que de la
comptabilité d'exposition et des candidats. Ce module lit la première, ne l'écrit jamais, et
n'étend aucune fusion scientifique à l'historique de charges.

**Ordre de résolution, déterministe :**

1. `variant_key` connu du catalogue ;
2. forme normalisée du nom ∈ index dérivé de l'EKB (noms canoniques + `_aliases`) ;
3. sinon, identité d'exercice en base (`resolve_exercise`, lecture seule) dont le nom est dans
   l'index ;
4. sinon `UNKNOWN_IDENTITY`, avec sa raison.

`normalize` est une forme canonique EXACTE : aucune ressemblance, aucune distance d'édition,
aucun « meilleur candidat ». Une fiche alias est toujours ramenée à sa fiche canonique : un
alias n'est jamais un candidat.

**Aucun consommateur servi** : une garde vérifie qu'aucun module du produit ne l'importe.
"""
from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType
from typing import Any

from sqlalchemy.orm import Session

from app.services.exercise_identity import normalize, resolve_exercise
from app.services.sci_catalogue import SciCatalogue, load_catalogue

_EKB_PATH = Path(__file__).resolve().parents[2] / "data" / "exercise_knowledge_base.json"

RESOLVED = "RESOLVED"
UNKNOWN_IDENTITY = "UNKNOWN_IDENTITY"
STEP_VARIANT_KEY = 1
STEP_NAME_INDEX = 2
STEP_DATABASE = 3


class SciIdentityError(ValueError):
    """Index de noms incohérent — refusé à la construction, jamais résolu en silence."""


@dataclass(frozen=True)
class IdentityResolution:
    status: str
    query: str | None
    step: int | None
    variant_key: str | None
    scientific_identity_id: str | None
    canonical_exercise_id: str | None
    catalogue_version: str
    reason: str | None

    @property
    def is_resolved(self) -> bool:
        return self.status == RESOLVED


def _name_entries(ekb: Mapping[str, Any]) -> list[tuple[str, str]]:
    """(nom, variant_key) pour chaque nom canonique de l'EKB et chaque alias déclaré."""
    exercises = ekb["exercises"]
    entries = [(name, entry["variant_key"]) for name, entry in exercises.items()]
    for alias, target in ekb.get("_aliases", {}).items():
        if target not in exercises:
            raise SciIdentityError(f"alias EKB {alias!r} vers un nom inconnu {target!r}")
        entries.append((alias, exercises[target]["variant_key"]))
    return entries


def _identity_of(catalogue: SciCatalogue, variant_key: str) -> str:
    try:
        return catalogue.record(variant_key)["identity"]["scientific_identity_id"]
    except KeyError:
        raise SciIdentityError(f"variant_key EKB sans fiche scientifique : {variant_key!r}") from None


def build_name_index(ekb: Mapping[str, Any], catalogue: SciCatalogue) -> Mapping[str, str]:
    """Forme normalisée → `variant_key` de la fiche que ce nom désigne.

    Deux noms de même forme normalisée ne sont admis que s'ils désignent la même identité
    scientifique (mesuré : « Curl marteau câble (corde) » / « … corde ») ; ne pouvant plus les
    distinguer, l'index retient alors la fiche canonique. Deux identités distinctes sous une même
    forme sont une erreur de donnée.
    """
    index: dict[str, str] = {}
    for name, variant_key in _name_entries(ekb):
        key = normalize(name)
        if not key:
            raise SciIdentityError(f"nom EKB sans forme normalisée : {name!r}")
        identity = _identity_of(catalogue, variant_key)
        held = index.get(key)
        if held is None:
            index[key] = variant_key
        elif held != variant_key:
            if _identity_of(catalogue, held) != identity:
                raise SciIdentityError(f"{name!r} : forme {key!r} déjà tenue par une autre identité ({held!r})")
            index[key] = catalogue.canonical_of(variant_key)["exercise_id"]
    return MappingProxyType(index)


class SciIdentityResolver:
    def __init__(self, catalogue: SciCatalogue, name_index: Mapping[str, str]):
        self._catalogue = catalogue
        self._index = name_index
        self._version = catalogue.header["catalogue_version"]

    @property
    def catalogue(self) -> SciCatalogue:
        return self._catalogue

    def _resolved(self, query: str | None, step: int, variant_key: str) -> IdentityResolution:
        canonical = self._catalogue.canonical_of(variant_key)
        return IdentityResolution(
            status=RESOLVED, query=query, step=step, variant_key=variant_key,
            scientific_identity_id=canonical["identity"]["scientific_identity_id"],
            canonical_exercise_id=canonical["exercise_id"], catalogue_version=self._version, reason=None)

    def _unknown(self, query: str | None, reason: str) -> IdentityResolution:
        return IdentityResolution(status=UNKNOWN_IDENTITY, query=query, step=None, variant_key=None,
                                  scientific_identity_id=None, canonical_exercise_id=None,
                                  catalogue_version=self._version, reason=reason)

    def resolve_variant_key(self, variant_key: str) -> IdentityResolution:
        try:
            self._catalogue.record(variant_key)
        except KeyError:
            return self._unknown(variant_key, f"variant_key absent du catalogue : {variant_key!r}")
        return self._resolved(variant_key, STEP_VARIANT_KEY, variant_key)

    def resolve_through_database(self, name: str | None, db: Session) -> IdentityResolution:
        """Étape 3 seule : identité d'exercice en base, en lecture seule (jamais `ensure_exercise`)."""
        exercise = resolve_exercise(db, name or "")
        if exercise is None:
            return self._unknown(name, "nom inconnu de l'index EKB comme de l'identité d'exercice")
        variant_key = self._index.get(normalize(exercise.name))
        if variant_key is None:
            return self._unknown(name, f"identité d'exercice {exercise.slug!r} connue en base, "
                                       "sans fiche scientifique")
        return self._resolved(name, STEP_DATABASE, variant_key)

    def resolve_name(self, name: str | None, db: Session | None = None) -> IdentityResolution:
        key = normalize(name or "")
        if not key:
            return self._unknown(name, "nom vide")
        variant_key = self._index.get(key)
        if variant_key is not None:
            return self._resolved(name, STEP_NAME_INDEX, variant_key)
        if db is None:
            return self._unknown(name, "nom inconnu de l'index EKB (identité d'exercice non consultée)")
        return self.resolve_through_database(name, db)

    def resolve(self, *, variant_key: str | None = None, name: str | None = None,
                db: Session | None = None) -> IdentityResolution:
        if variant_key is not None:
            by_key = self.resolve_variant_key(variant_key)
            if by_key.is_resolved:
                return by_key
        return self.resolve_name(name, db)


def _read_ekb(path: Path = _EKB_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_resolver(catalogue: SciCatalogue | None = None,
                   ekb: Mapping[str, Any] | None = None) -> SciIdentityResolver:
    catalogue = catalogue or load_catalogue()
    ekb = ekb if ekb is not None else _read_ekb()
    return SciIdentityResolver(catalogue, build_name_index(ekb, catalogue))


@lru_cache(maxsize=1)
def load_resolver() -> SciIdentityResolver:
    """Le résolveur des données versionnées du dépôt. Pur : mêmes fichiers ⇒ mêmes réponses."""
    return build_resolver()
