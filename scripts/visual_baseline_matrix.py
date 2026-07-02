"""Sb_UI_11.1 — Visual baseline matrix.

Matrice déterministe des écrans à capturer pour la baseline visuelle
pré-Auren, alignée avec `docs/strategy/Sx_UI_11_SCREENSHOT_REGRESSION_BASELINE_SPEC.md`
et `docs/strategy/Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC.md`.

Ce module ne fait AUCUN import Playwright et AUCUN appel réseau. Il expose
uniquement la structure de données consommée par
`scripts/visual_baseline_capture.py`.

Contrats :
* Pure Python, aucun side effect à l'import.
* Aucune valeur secrète encodée.
* Aucun mot de passe, token, ou credential dans les données.
* Slugs kebab-case stricts.
* Viewports standardisés : mobile 360×640, desktop 1440×900.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Priority = Literal["P0", "P1", "P2"]
ViewportName = Literal["mobile", "desktop"]

VIEWPORTS: dict[ViewportName, tuple[int, int]] = {
    "mobile": (360, 640),
    "desktop": (1440, 900),
}


@dataclass(frozen=True)
class BaselineEntry:
    """Une entrée de la matrice baseline.

    Chaque entrée décrit un écran à capturer, pas la capture elle-même.
    """

    slug: str
    route: str
    priority: Priority
    auth_required: bool
    state: str
    data_fixture: str
    viewports: tuple[ViewportName, ...] = ("mobile", "desktop")
    notes: str = ""


# Matrice P0 obligatoire (14 screenshots min V1, 16 acceptable si split home).
#
# Alignement Sx_UI_04 §18 :
# - home_authenticated + home_no_active_session : split home autorisé, protège empty state
# - session_detail_active + session_detail_done : deux states critiques focus mode
# - progression / profile / login / register : shell + auth entry points
#
# Total P0 : 8 slugs × 2 viewports = 16 screenshots.
# Ce léger sur-comptage vs 14 est documenté dans le sprint report.
_P0_ENTRIES: tuple[BaselineEntry, ...] = (
    BaselineEntry(
        slug="home-authenticated",
        route="/",
        priority="P0",
        auth_required=True,
        state="authenticated-with-active-session",
        data_fixture="db.user.with_active_session",
        notes="Point d'entrée quotidien absorbé par Séance V1 Auren (Sx_UI_03).",
    ),
    BaselineEntry(
        slug="home-no-active-session",
        route="/",
        priority="P0",
        auth_required=True,
        state="authenticated-no-active-session",
        data_fixture="db.user.standard",
        notes="Empty state home critique (Sx_UI_04 §3).",
    ),
    BaselineEntry(
        slug="session-detail-active",
        route="/sessions/${AUREN_BASELINE_ACTIVE_SESSION_ID}",
        priority="P0",
        auth_required=True,
        state="in-progress-3-exos-done-active-future",
        data_fixture="db.user.with_active_session",
        notes="Focus mode Sx_29 cible reskin Sx_UI_04.",
    ),
    BaselineEntry(
        slug="session-detail-done",
        route="/sessions/${AUREN_BASELINE_DONE_SESSION_ID}",
        priority="P0",
        auth_required=True,
        state="completed",
        data_fixture="db.user.with_history",
        notes="Review post-séance.",
    ),
    BaselineEntry(
        slug="progression",
        route="/progress",
        priority="P0",
        auth_required=True,
        state="with-history",
        data_fixture="db.user.with_history",
        notes="Absorbe Historique + Physique en V1 Auren (Sx_UI_03).",
    ),
    BaselineEntry(
        slug="profile",
        route="/profile",
        priority="P0",
        auth_required=True,
        state="authenticated",
        data_fixture="db.user.standard",
        notes="Contient carte Body Intelligence (Sx_31 OQ-G).",
    ),
    BaselineEntry(
        slug="login",
        route="/login",
        priority="P0",
        auth_required=False,
        state="anonymous",
        data_fixture="db.empty",
        notes="Point d'entrée public.",
    ),
    BaselineEntry(
        slug="register",
        route="/register",
        priority="P0",
        auth_required=False,
        state="anonymous",
        data_fixture="db.empty",
        notes="Point d'entrée public.",
    ),
)

# Matrice P1 recommandée (Sx_UI_11 §5, complète le P0).
_P1_ENTRIES: tuple[BaselineEntry, ...] = (
    BaselineEntry(
        slug="library",
        route="/library",
        priority="P1",
        auth_required=True,
        state="authenticated",
        data_fixture="db.user.standard",
        notes="Bibliothèque templates.",
    ),
    BaselineEntry(
        slug="library-detail",
        route="/library/${AUREN_BASELINE_TEMPLATE_SLUG}",
        priority="P1",
        auth_required=True,
        state="authenticated",
        data_fixture="db.user.standard",
        notes="Détail template avant lancement.",
    ),
    BaselineEntry(
        slug="progression-empty",
        route="/progress",
        priority="P1",
        auth_required=True,
        state="authenticated-no-history",
        data_fixture="db.user.standard",
        notes="Empty state critique.",
    ),
    BaselineEntry(
        slug="history",
        route="/history",
        priority="P1",
        auth_required=True,
        state="with-history",
        data_fixture="db.user.with_history",
        notes="Absorbé sous Progression en V1 Auren.",
    ),
    BaselineEntry(
        slug="physique",
        route="/physique",
        priority="P1",
        auth_required=True,
        state="with-measurements",
        data_fixture="db.user.with_measurements",
        notes="Absorbé sous Progression en V1 Auren.",
    ),
    BaselineEntry(
        slug="coach-report",
        route="/coach-report",
        priority="P1",
        auth_required=True,
        state="with-history",
        data_fixture="db.user.with_history",
        notes="Contextualisé en V1 Auren (Sx_UI_03 §11).",
    ),
    BaselineEntry(
        slug="body-intelligence",
        route="/body/intelligence",
        priority="P1",
        auth_required=True,
        state="flag-on-with-history",
        data_fixture="db.body_intelligence.enabled",
        notes="7 blocs + badges Mesuré/Dérivé/Inféré/Hors de portée.",
    ),
)

# Matrice P2 différables (Sx_UI_11 §5).
_P2_ENTRIES: tuple[BaselineEntry, ...] = (
    BaselineEntry(
        slug="leaderboard",
        route="/leaderboard",
        priority="P2",
        auth_required=True,
        state="opt-in",
        data_fixture="db.user.standard",
        notes="Rétrogradé vers Profil secondaire V1 Auren.",
    ),
    BaselineEntry(
        slug="squads",
        route="/squads",
        priority="P2",
        auth_required=True,
        state="opt-in",
        data_fixture="db.user.standard",
        notes="Rétrogradé vers Profil secondaire V1 Auren.",
    ),
    BaselineEntry(
        slug="forgot-password",
        route="/forgot-password",
        priority="P2",
        auth_required=False,
        state="anonymous",
        data_fixture="db.empty",
        notes="Écran occasionnel.",
    ),
)


BASELINE_MATRIX: tuple[BaselineEntry, ...] = _P0_ENTRIES + _P1_ENTRIES + _P2_ENTRIES


def entries_for_priority(priority: Priority | Literal["all"]) -> list[BaselineEntry]:
    """Retourne les entrées filtrées par priorité."""
    if priority == "all":
        return list(BASELINE_MATRIX)
    return [entry for entry in BASELINE_MATRIX if entry.priority == priority]


def viewport_size(name: ViewportName) -> tuple[int, int]:
    """Retourne (width, height) pour un viewport nommé."""
    if name not in VIEWPORTS:
        raise ValueError(
            f"Unknown viewport '{name}'. Valid: {sorted(VIEWPORTS.keys())}"
        )
    return VIEWPORTS[name]


def output_path(
    out_dir: str,
    slug: str,
    viewport: ViewportName,
    state_suffix: str | None = None,
) -> str:
    """Construit un chemin de sortie normalisé.

    Convention Sx_UI_11 §11 :
        {out_dir}/{page-slug}/{viewport}-{state}.png

    Kebab-case strict. Ne crée pas le fichier — retourne juste le chemin.
    """
    if not slug or slug != slug.lower() or " " in slug:
        raise ValueError(f"Slug must be lowercase kebab-case, got: {slug!r}")
    if viewport not in VIEWPORTS:
        raise ValueError(f"Unknown viewport '{viewport}'")
    suffix = state_suffix or _default_state_suffix(slug)
    return f"{out_dir.rstrip('/')}/{slug}/{viewport}-{suffix}.png"


def _default_state_suffix(slug: str) -> str:
    """Retourne un suffixe d'état par défaut basé sur les entrées matrix."""
    for entry in BASELINE_MATRIX:
        if entry.slug == slug:
            if entry.auth_required:
                return "authenticated"
            return "anonymous"
    return "default"


# Environment variables allowed for auth / fixture references.
# NEVER read these values in this module. Only their names.
REQUIRED_ENV_VARS_FOR_AUTH: tuple[str, ...] = (
    "AUREN_BASELINE_USERNAME",
    "AUREN_BASELINE_PASSWORD",
)

REQUIRED_ENV_VARS_FOR_ACTIVE_SESSION: tuple[str, ...] = (
    "AUREN_BASELINE_ACTIVE_SESSION_ID",
)

REQUIRED_ENV_VARS_FOR_DONE_SESSION: tuple[str, ...] = (
    "AUREN_BASELINE_DONE_SESSION_ID",
)

OPTIONAL_ENV_VARS: tuple[str, ...] = (
    "AUREN_BASELINE_TEMPLATE_SLUG",
)


@dataclass(frozen=True)
class CapturePlan:
    """Une capture unitaire planifiée (slug × viewport)."""

    entry: BaselineEntry
    viewport: ViewportName
    output_path: str
    width: int
    height: int


def build_plan(
    entries: list[BaselineEntry],
    viewport_filter: ViewportName | Literal["all"],
    out_dir: str,
) -> list[CapturePlan]:
    """Développe une liste d'entrées en captures unitaires (entry × viewport)."""
    plans: list[CapturePlan] = []
    for entry in entries:
        for vp in entry.viewports:
            if viewport_filter != "all" and vp != viewport_filter:
                continue
            width, height = viewport_size(vp)
            plans.append(
                CapturePlan(
                    entry=entry,
                    viewport=vp,
                    output_path=output_path(out_dir, entry.slug, vp),
                    width=width,
                    height=height,
                )
            )
    return plans
