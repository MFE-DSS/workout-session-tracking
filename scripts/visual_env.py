"""`UIV3_VISUAL_BASELINE_01` — `VISUAL_ENV_V1`, l'environnement canonique.

POURQUOI CE FICHIER EXISTE AVANT LA PREMIÈRE CAPTURE
=====================================================
Une capture d'écran dépend du système, de la version du navigateur, des
polices, du matériel et du mode headless. Comparer une référence produite sur
un portable macOS à un rendu Chromium Linux en CI, **c'est tester la
rastérisation, pas le design** — et le premier run transformerait chaque
golden en bruit.

Décision opérateur du 2026-08-20 : **une référence produite hors de cet
environnement ne peut pas devenir canonique.** Pas « déconseillé » : refusé.

CE QUE CE MODULE FAIT, ET CE QU'IL NE FAIT PAS
-----------------------------------------------
Il **déclare** l'environnement et **vérifie** qu'un tampon lui correspond. Il
ne lance aucun navigateur, n'importe pas Playwright et n'a aucun effet de bord
à l'import — même séparation que `visual_baseline_matrix.py`.

CE QUI BLOQUE AUJOURD'HUI, ET QU'IL FAUT DIRE
----------------------------------------------
`pyproject.toml` déclare `playwright>=1.40` — une **plage ouverte**. Tant
qu'elle n'est pas épinglée, `VISUAL_ENV_V1` est une intention, pas un
environnement : un bump mineur change Chromium, donc la rastérisation, donc
toutes les références d'un coup. `REQUIRES_PINNED_DEPENDENCY` porte ce constat,
et une garde le vérifie plutôt que de l'espérer.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

#: Version du contrat d'environnement. **Changer une seule valeur ci-dessous
#: invalide toutes les références existantes** — donc incrémenter ce nom, et
#: régénérer, jamais « ajuster discrètement ».
ENV_VERSION: Final[str] = "VISUAL_ENV_V1"


@dataclass(frozen=True)
class VisualEnvironment:
    """L'environnement dans lequel une référence visuelle fait autorité."""

    version: str
    playwright: str
    chromium: str
    platform: str
    #: Image de conteneur / runner. `ubuntu-latest` est un alias MOUVANT :
    #: il est nommé ici pour ce qu'il est, pas pour ce qu'on aimerait qu'il
    #: soit. L'épingler est un travail de `ci_infra`, pas de cette tranche.
    runner_image: str
    device_scale_factor: int
    locale: str
    timezone: str
    color_scheme: str
    reduced_motion: str
    #: Pile de polices attendue. AUREN est **tout-mono, zéro webfont**
    #: (`app.css`) : la référence dépend donc des polices SYSTÈME du runner,
    #: ce qui est précisément pourquoi le runner doit être figé.
    font_stack: str
    widths: tuple[int, ...]
    fixture: str


VISUAL_ENV_V1: Final[VisualEnvironment] = VisualEnvironment(
    version=ENV_VERSION,
    playwright="1.61.0",
    chromium="149.0.7827.55",
    platform="linux",
    runner_image="ubuntu-latest",
    device_scale_factor=2,
    locale="fr-FR",
    timezone="Europe/Paris",
    color_scheme="dark",
    reduced_motion="reduce",
    font_stack="ui-monospace, DejaVu Sans Mono, Liberation Mono, monospace",
    widths=(360, 390, 430),
    fixture="SESSION_RICH",
)

#: Ce qui empêche encore `VISUAL_ENV_V1` d'être réellement reproductible.
#: Une liste vide vaut « environnement scellé ». Tant qu'elle ne l'est pas,
#: aucune référence ne doit être promue canonique.
REQUIRES_PINNED_DEPENDENCY: Final[tuple[str, ...]] = (
    "pyproject.toml [baseline] déclare playwright>=1.40 — plage OUVERTE. "
    "Un bump mineur change Chromium, donc la rastérisation, donc toutes les "
    "références d'un coup.",
    "runner_image='ubuntu-latest' est un alias mouvant : l'image change sous "
    "le même nom, et avec elle les polices système dont dépend un rendu "
    "tout-mono sans webfont.",
)


@dataclass(frozen=True)
class EnvironmentStamp:
    """Ce qu'une exécution DIT d'elle-même, à confronter au contrat."""

    playwright: str
    chromium: str
    platform: str
    device_scale_factor: int
    locale: str
    timezone: str
    color_scheme: str
    reduced_motion: str
    notes: tuple[str, ...] = field(default_factory=tuple)


#: Champs confrontés lorsqu'on décide si une référence peut être canonique.
#: `runner_image`, `font_stack`, `widths` et `fixture` n'y figurent pas : ils
#: ne sont pas lisibles depuis le navigateur et relèvent de la configuration
#: CI, vérifiée ailleurs.
COMPARED_FIELDS: Final[tuple[str, ...]] = (
    "playwright", "chromium", "platform", "device_scale_factor",
    "locale", "timezone", "color_scheme", "reduced_motion",
)


def stamp_mismatches(stamp: EnvironmentStamp,
                     env: VisualEnvironment = VISUAL_ENV_V1) -> list[str]:
    """Les écarts entre une exécution et le contrat, champ par champ."""
    out = []
    for name in COMPARED_FIELDS:
        want, got = getattr(env, name), getattr(stamp, name)
        if want != got:
            out.append(f"{name}: attendu {want!r}, obtenu {got!r}")
    return out


def may_promote_to_canonical(stamp: EnvironmentStamp,
                             env: VisualEnvironment = VISUAL_ENV_V1
                             ) -> tuple[bool, list[str]]:
    """Cette exécution peut-elle produire des références **canoniques** ?

    Deux conditions, cumulatives et non négociables :

    1. le tampon correspond au contrat champ par champ ;
    2. l'environnement lui-même est **scellé** — tant qu'une dépendance vit
       en plage ouverte, « ça correspond aujourd'hui » ne dit rien de demain.

    Un `False` n'interdit pas de **capturer** : il interdit de **promouvoir**.
    Une capture locale reste utile comme preuve et comme comparaison humaine ;
    elle ne devient simplement jamais la référence.
    """
    reasons = stamp_mismatches(stamp, env)
    reasons.extend(REQUIRES_PINNED_DEPENDENCY)
    return (not reasons), reasons
