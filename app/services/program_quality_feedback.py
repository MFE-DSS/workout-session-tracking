"""Program quality feedback layer (Sb_CUSTOM_PROGRAM_SCORING_02).

Wrapper PUR de présentation autour de `QualityReviewResult` (SCORING_01) :
il traduit un résultat de scoring en langage produit, prêt à afficher, sans
jamais recalculer un score ni toucher au moteur.

Séparation stricte (spec Sx_CUSTOM_PROGRAM_03 §15) :
- le **moteur** (`program_quality_engine`) produit des faits chiffrés ;
- cette **couche** produit le langage : titres, messages, actions, limites.

Ce que la couche APPORTE par rapport au brut du moteur — les trous mesurés
au préflight, invisibles pour l'utilisateur en SCORING_01 :
1. le **plafond de grade** est expliqué (`grade_cap_reason`) ;
2. les **4 dimensions non mesurables** (`missing_data`) sont restituées ;
3. la **fiabilité** (`confidence` / `coverage_ratio`) est verbalisée ;
4. un programme équilibré reçoit **toujours** un retour utile (le moteur seul
   n'émettait presque rien quand tout allait bien).

Doctrine de microcopy (spec §8, non négociable) :
- **jamais** de niveau bloquant — le scoring informe, il ne bloque pas
  (OQ-SCORE-C : un grade C reste publiable) ;
- **jamais** « tu dois », « optimal », « parfait », ni claim médical ;
- **jamais** de formulation culpabilisante : pour les limites de mesure, le
  sujet grammatical est l'OUTIL (« ces dimensions ne sont pas encore
  mesurables »), jamais l'utilisateur ;
- formulations indicatives : « peut aider », « souvent utile », « à vérifier ».

Pur : aucune I/O, aucune DB, aucun ORM, aucun LLM. Déterministe, ordre stable.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

# Niveaux de feedback. Volontairement SANS niveau bloquant (OQ-SCORE-C).
LEVEL_INFO = "info"        # contexte, limites de l'outil, grade cap, confiance
LEVEL_WARNING = "warning"  # déséquilibre réel constaté
LEVEL_TIP = "tip"          # option d'amélioration actionnable

FEEDBACK_LEVELS = (LEVEL_INFO, LEVEL_WARNING, LEVEL_TIP)

# Ordre d'affichage : le constat d'abord, puis les options, puis le contexte.
_LEVEL_ORDER = {LEVEL_WARNING: 0, LEVEL_TIP: 1, LEVEL_INFO: 2}

# Plafond par niveau (règle « ≤ 3 » héritée de Sx_30) — évite la sur-verbosité.
MAX_ITEMS_PER_LEVEL = 3

# Libellés lisibles des sous-scores (aucun jargon technique côté produit).
_SUBSCORE_LABELS = {
    "volume_per_zone": "Répartition du volume",
    "push_pull_legs_balance": "Équilibre poussée / tirage / bas du corps",
    "frequency_per_zone": "Fréquence par zone",
    "equipment_feasibility": "Faisabilité matériel",
    "recovery_spacing": "Espacement de récupération",
    "redundancy": "Redondance des variantes",
    "duration_realism": "Réalisme de la durée",
    "overload_compatibility": "Compatibilité surcharge progressive",
}

# Actions proposées — des options, jamais des ordres.
_ACTIONS = {
    "volume_per_zone": "Répartir quelques séries vers les zones les moins vues peut aider.",
    "push_pull_legs_balance": (
        "Ajouter un mouvement de la famille absente peut aider à équilibrer."
    ),
    "frequency_per_zone": "Revoir une même zone deux fois par semaine est souvent utile.",
    "equipment_feasibility": (
        "Vérifier le matériel déclaré, ou choisir des variantes compatibles."
    ),
}

_GRADE_HEADLINES = {
    "A": "Ton programme semble très cohérent d'après les dimensions mesurées.",
    "B": "Ton programme semble cohérent sur les dimensions mesurées.",
    "C": "Quelques points d'équilibre méritent un coup d'œil.",
}


@dataclass(frozen=True)
class FeedbackItem:
    """Un élément de retour prêt à afficher."""

    level: str
    category: str
    title: str
    message: str
    action: str | None = None
    subscore: str | None = None


@dataclass(frozen=True)
class ProgramQualityFeedback:
    """Retour produit complet — sérialisable, ordonné, plafonné."""

    headline: str
    grade: str
    grade_note: str | None
    confidence_note: str
    items: tuple[FeedbackItem, ...]
    limitations: tuple[str, ...]
    disclaimer: str
    scoring_version: int
    ekb_version: str | None

    def to_dict(self) -> dict:
        """Représentation sérialisable (JSON-ready)."""
        return asdict(self)


def _label(key: str) -> str:
    return _SUBSCORE_LABELS.get(key, key)


def _missing_key(entry: str) -> str:
    """`missing_data` arrive sous la forme "clé — raison" (SCORING_01)."""
    return entry.split(" — ", 1)[0].strip()


def _missing_reason(entry: str) -> str:
    parts = entry.split(" — ", 1)
    return parts[1].strip() if len(parts) > 1 else ""


def _confidence_note(result) -> str:
    """Verbalise la fiabilité — limite de l'outil, jamais un reproche."""
    percent = round(result.coverage_ratio * 100)
    if result.confidence == "moderate":
        return (
            f"Lecture indicative : {percent} % des exercices du programme sont "
            "reconnus par la base d'exercices."
        )
    if result.confidence == "low":
        return (
            f"Lecture à prendre avec prudence : seuls {percent} % des exercices "
            "sont reconnus par la base d'exercices."
        )
    return (
        f"Lecture très partielle : {percent} % des exercices sont reconnus par la "
        "base d'exercices — les constats portent sur peu de données."
    )


def _grade_items(result) -> list[FeedbackItem]:
    """Explique le plafond de grade quand il s'applique (trou n°1 de SCORING_01)."""
    if not result.grade_cap_reason:
        return []
    return [
        FeedbackItem(
            level=LEVEL_INFO,
            category="grade",
            title="Pourquoi le grade est plafonné",
            message=(
                "La note maximale reste B pour l'instant : plusieurs dimensions ne "
                "sont pas encore mesurables par l'outil. Ce n'est pas un défaut de "
                "ton programme."
            ),
            action=None,
        )
    ]


def _missing_items(result) -> list[FeedbackItem]:
    """Restitue les dimensions non mesurables — sujet = l'outil, pas l'utilisateur."""
    if not result.missing_data:
        return []
    listed = ", ".join(_label(_missing_key(entry)) for entry in result.missing_data)
    return [
        FeedbackItem(
            level=LEVEL_INFO,
            category="coverage",
            title="Dimensions pas encore mesurables",
            message=(
                f"Ces dimensions ne sont pas encore mesurables par l'outil : {listed}. "
                "Elles seront prises en compte quand la base d'exercices sera enrichie."
            ),
            action=None,
        )
    ]


def _subscore_items(result) -> list[FeedbackItem]:
    """Constats et options dérivés des sous-scores — contexte nommé quand possible."""
    items: list[FeedbackItem] = []
    for sub in result.subscores:
        reason = sub.reasons[0] if sub.reasons else ""
        if sub.score < 60:
            level = LEVEL_WARNING
        elif sub.score < 80:
            level = LEVEL_TIP
        else:
            continue
        items.append(
            FeedbackItem(
                level=level,
                category="balance",
                title=_label(sub.key),
                message=reason,
                action=_ACTIONS.get(sub.key),
                subscore=sub.key,
            )
        )
    return items


def _strength_item(result) -> list[FeedbackItem]:
    """Un programme sain mérite aussi un retour (trou n°4 de SCORING_01)."""
    strong = [s for s in result.subscores if s.score >= 80]
    if not strong:
        return []
    best = max(strong, key=lambda s: (s.score, s.key))
    detail = best.reasons[0] if best.reasons else "point favorable."
    return [
        FeedbackItem(
            level=LEVEL_INFO,
            category="strength",
            title="Point solide",
            message=f"{_label(best.key)} : {detail}",
            action=None,
            subscore=best.key,
        )
    ]


def _assumption_items(result) -> list[FeedbackItem]:
    """Hypothèses appliquées — affichées, jamais tues (spec §7)."""
    if not result.assumptions:
        return []
    return [
        FeedbackItem(
            level=LEVEL_INFO,
            category="assumption",
            title="Hypothèses utilisées",
            message=" ".join(result.assumptions),
            action=None,
        )
    ]


def build_program_quality_feedback(result) -> ProgramQualityFeedback:
    """Traduit un `QualityReviewResult` en retour produit prêt à afficher.

    Pur et déterministe : aucune I/O, aucun recalcul de score, ordre stable.
    Aucun niveau bloquant n'est jamais émis — un grade C reste publiable.
    """
    raw = (
        _subscore_items(result)
        + _grade_items(result)
        + _missing_items(result)
        + _strength_item(result)
        + _assumption_items(result)
    )

    # Ordre stable et priorisé : warning → tip → info, puis ordre d'apparition.
    ordered = sorted(
        enumerate(raw), key=lambda pair: (_LEVEL_ORDER[pair[1].level], pair[0])
    )

    # Plafonnement par niveau (anti-verbosité), sans casser l'ordre global.
    kept: list[FeedbackItem] = []
    per_level: dict[str, int] = {}
    for _idx, item in ordered:
        count = per_level.get(item.level, 0)
        if count >= MAX_ITEMS_PER_LEVEL:
            continue
        per_level[item.level] = count + 1
        kept.append(item)

    limitations = tuple(
        f"{_label(_missing_key(entry))} — {_missing_reason(entry)}"
        for entry in result.missing_data
    )

    grade_note = None
    if result.grade_cap_reason:
        grade_note = (
            "La note maximale reste B tant que certaines dimensions ne sont pas "
            "mesurables — le grade n'empêche jamais de garder ton programme."
        )

    return ProgramQualityFeedback(
        headline=_GRADE_HEADLINES.get(result.grade, _GRADE_HEADLINES["C"]),
        grade=result.grade,
        grade_note=grade_note,
        confidence_note=_confidence_note(result),
        items=tuple(kept),
        limitations=limitations,
        disclaimer=result.disclaimer,
        scoring_version=result.scoring_version,
        ekb_version=result.ekb_version,
    )
