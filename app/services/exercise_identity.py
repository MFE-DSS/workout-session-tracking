"""`Sb_EXERCISE_IDENTITY_01` — engendrer et retrouver une identité d'exercice.

Deux fonctions pures (``normalize``, ``slugify``) et deux accès base
(``resolve_exercise``, ``ensure_exercise``). Rien d'autre : ce module ne décide
rien sur l'entraînement et n'est importé par aucun moteur de décision.

**Le slug est engendré une fois.** ``ensure_exercise`` ne le recalcule jamais
pour une ligne existante : un renommage produit met à jour ``name`` et laisse
``slug`` intact. Régénérer serait rendre l'identité aussi fragile que le nom
qu'elle remplace.
"""
from __future__ import annotations

import re
import unicodedata

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import SOURCE_CATALOG, Exercise, ExerciseAlias

#: Longueur maxi du slug — alignée sur la colonne. Tronquer au-delà romprait
#: l'unicité en silence, donc on vérifie plutôt que de couper (cf. `slugify`).
SLUG_MAX = 96

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def normalize(name: str) -> str:
    """Forme de comparaison : sans accent, sans casse, sans ponctuation.

    C'est ce qui fait tenir ``Curl marteau câble (corde)`` et
    ``Curl marteau câble corde`` — deux écritures présentes dans deux fichiers
    de données du dépôt — pour **le même** exercice. Mesuré : leur similarité
    après normalisation vaut 1,00.
    """
    folded = unicodedata.normalize("NFKD", name or "")
    folded = "".join(c for c in folded if not unicodedata.combining(c))
    return _NON_ALNUM.sub(" ", folded.lower()).strip()


def slugify(name: str) -> str:
    """Slug déterministe, dérivé du nom **au moment de la création**.

    Lisible à dessein : un identifiant opaque rendrait indéchiffrables les
    fichiers de graine, les traces et les rapports. La stabilité ne vient pas
    de l'opacité, elle vient de ce qu'on ne le régénère jamais.
    """
    slug = _NON_ALNUM.sub("-", normalize(name)).strip("-")
    if not slug:
        raise ValueError(f"nom sans caractère exploitable : {name!r}")
    if len(slug) > SLUG_MAX:
        raise ValueError(
            f"slug de {len(slug)} caractères pour {SLUG_MAX} permis : {slug!r}. "
            "Tronquer romprait l'unicité en silence."
        )
    return slug


def resolve_exercise(db: Session, name: str) -> Exercise | None:
    """Retrouve l'exercice désigné par ce nom, alias compris.

    Un seul chemin de résolution : la forme normalisée, via la table d'alias.
    L'exercice lui-même y possède toujours une entrée — son propre nom — de
    sorte qu'il n'existe pas de « chemin principal » et de « chemin alias » à
    tenir en accord.
    """
    key = normalize(name)
    if not key:
        return None
    return db.execute(
        select(Exercise)
        .join(ExerciseAlias, ExerciseAlias.exercise_id == Exercise.id)
        .where(ExerciseAlias.normalized == key)
    ).scalars().first()


def ensure_exercise(
    db: Session, name: str, *, source: str = SOURCE_CATALOG
) -> Exercise:
    """Idempotent. Rend l'exercice existant, ou le crée avec son alias propre.

    Ne met **pas** à jour le ``name`` d'une ligne existante : renommer est un
    geste produit délibéré, pas un effet de bord de graine.
    """
    found = resolve_exercise(db, name)
    if found is not None:
        return found

    ex = Exercise(slug=slugify(name), name=name, source=source)
    db.add(ex)
    db.flush()
    db.add(ExerciseAlias(
        exercise_id=ex.id, alias=name, normalized=normalize(name), source=source
    ))
    db.flush()
    return ex


def add_alias(
    db: Session, exercise: Exercise, alias: str, *, source: str = SOURCE_CATALOG
) -> ExerciseAlias | None:
    """Rattache un nom alternatif. Rend ``None`` s'il est déjà pris.

    Déjà pris **par un autre exercice** est un conflit réel, pas un doublon
    bénin : on refuse plutôt que de repointer en silence. Repointer est une
    fusion, et une fusion est un jugement produit.
    """
    key = normalize(alias)
    if not key:
        return None
    existing = resolve_exercise(db, alias)
    if existing is not None:
        return None
    row = ExerciseAlias(
        exercise_id=exercise.id, alias=alias, normalized=key, source=source
    )
    db.add(row)
    db.flush()
    return row


#: Préfixes des clés de comparaison. Ils sont **dans** la clé pour qu'un slug
#: et une forme normalisée ne puissent jamais se confondre : sans eux, un
#: exercice de slug `curl-marteau` et un nom brut normalisé « curl marteau »
#: produiraient deux chaînes différentes aujourd'hui et pourraient coïncider
#: demain, au gré d'un changement de slugification.
KEY_IDENTITY = "id:"
KEY_RAW = "raw:"


def identity_key(db: Session, name: str | None) -> str | None:
    """Clé de comparaison de **ce qui a été exécuté**.

    `TRAIN 3` / `A2` étape B. Deux endroits du produit décident si deux séances
    portent sur le même mouvement, et tous deux le faisaient par **égalité de
    chaîne exacte** : `overload_inputs._matches_substitution_policy` et
    `stats._matches_current_substitution`.

    DÉFAUT PROUVÉ, PAS DÉDUIT. `Curl marteau câble (corde)` et
    `Curl marteau câble corde` sont **toutes deux présentes dans les données du
    dépôt** et désignent le même mouvement — leur forme normalisée est
    identique. Appelée avec ces deux écritures, la politique de substitution
    rendait `False` : le même mouvement ne partageait pas son historique de
    charges, sans le moindre signal à l'écran.

    Trois valeurs possibles, et aucune n'est un trou :

    * ``None`` — rien n'a été substitué (le **prescrit**). Se compare à
      lui-même, comme avant.
    * ``id:<slug>`` — le nom est reconnu par le référentiel d'identités. Deux
      écritures d'un même mouvement rendent **la même** clé.
    * ``raw:<forme normalisée>`` — aucune identité ne reconnaît ce nom. Il se
      compare alors **à lui-même**, jamais à rien d'autre : un inconnu ne
      devient pas comparable à tout, il reste comparable à son égal.

    Cette fonction n'élargit l'appariement qu'entre écritures d'un **même**
    mouvement : deux mouvements distincts ont des formes normalisées
    distinctes, donc des lignes d'alias distinctes, donc des identités
    distinctes. Les fusionner resterait une **décision produit** — c'est ce que
    `Sb_EXERCISE_IDENTITY_01` a délibérément laissé ouvert.
    """
    key = normalize(name or "")
    if not key:
        return None
    found = resolve_exercise(db, name or "")
    return f"{KEY_IDENTITY}{found.slug}" if found is not None else f"{KEY_RAW}{key}"


__all__ = [
    "KEY_IDENTITY",
    "KEY_RAW",
    "SLUG_MAX",
    "add_alias",
    "ensure_exercise",
    "identity_key",
    "normalize",
    "resolve_exercise",
    "slugify",
]
