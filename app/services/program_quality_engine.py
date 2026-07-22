"""Program quality scoring engine (Sb_CUSTOM_PROGRAM_SCORING_01).

Moteur PUR de scoring des programmes custom (spec Sx_CUSTOM_PROGRAM_03) :
aucune I/O, aucune session DB, aucun import ORM, aucun LLM. Même entrée ⇒
même sortie, bit à bit — patron éprouvé d'`overload_engine` (Sx_30).

Ce que le moteur EST :
- une grille **indicative** d'entraînement, explicable sous-score par sous-score ;
- déterministe et versionnée (`PROGRAM_QUALITY_SCORING_VERSION`), avec la
  version de l'EKB consommée pinnée sur chaque sortie (`ekb_version`).

Ce que le moteur N'EST PAS :
- pas une vérité médicale ni scientifique absolue (mention obligatoire §8) ;
- pas un bloqueur : aucun état « non publiable » n'est émis (OQ-SCORE-C) ;
- pas un devin : un sous-score non mesurable est déclaré MANQUANT, jamais
  noté 0 — un faux 0 serait de la pseudo-science.

Couverture V1 (SCORING_01, arbitrage opérateur A(a)) : 4 sous-scores calculables
avec l'EKB_02 livré ; les 4 autres exigent des champs EKB différés à la curation
(`fatigue_class`, `variant_group`, `estimated_slot_minutes`,
`overload_compatibility`). Ils sont déclarés dans `missing_data`, **exclus de la
moyenne**, réduisent la `confidence` et **plafonnent le grade à B**. Quand la
curation EKB arrivera, ils s'activeront de façon additive (`scoring_version` 2).
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

PROGRAM_QUALITY_SCORING_VERSION = 1

_EKB_PATH = Path(__file__).resolve().parents[2] / "data" / "exercise_knowledge_base.json"

# Seuils de grade (constantes versionnées, jamais de config DB — spec §5/§6).
GRADE_A_MIN = 80
GRADE_B_MIN = 60
# Plafonds (règle hybride Option C §6) : un sous-score très bas plafonne le grade.
CAP_TO_C_BELOW = 40
CAP_TO_B_BELOW = 60

# Sous-scores calculables avec l'EKB_02 (couverture partielle assumée).
COMPUTABLE_SUBSCORES = (
    "volume_per_zone",
    "push_pull_legs_balance",
    "frequency_per_zone",
    "equipment_feasibility",
)

# Sous-scores exigés par la spec §5 mais NON calculables en V1 : le champ EKB
# nécessaire n'est pas curé. Déclarés manquants, jamais notés 0.
MISSING_SUBSCORES = {
    "recovery_spacing": "champ EKB `fatigue_class` non curé (curation différée)",
    "redundancy": "champ EKB `variant_group` null sur toutes les entrées (V1)",
    "duration_realism": "champ EKB `estimated_slot_minutes` non curé (curation différée)",
    "overload_compatibility": "champ EKB `overload_compatibility` non curé (curation différée)",
}

_GRADE_CAP_REASON = (
    "Grade plafonné à B : 4 sous-scores sur 8 ne sont pas mesurables tant que "
    "l'EKB n'est pas curé — la couverture partielle ne permet pas de conclure à A."
)

DISCLAIMER = "Grille indicative — pas une vérité médicale ou scientifique absolue."

# Familles de patterns pour l'équilibre push/pull/legs (vocabulaire EKB réel).
_PUSH = {"push_horizontal", "push_vertical"}
_PULL = {"pull_horizontal", "pull_vertical"}
_LEGS = {"squat", "hinge", "lunge", "isolation_lower"}


# ────────────────────────── entrées (payload pur) ──────────────────────────


@dataclass(frozen=True)
class ExerciseSlot:
    """Un slot d'exercice — miroir pur de `UserProgramExercise` (zéro ORM)."""

    exercise_name: str
    position: int = 1
    working_sets: int = 3


@dataclass(frozen=True)
class SessionPlan:
    """Une séance planifiée — miroir pur de `UserProgramSession`."""

    name: str
    position: int = 1
    kind: str = "strength"
    exercises: tuple[ExerciseSlot, ...] = ()


@dataclass(frozen=True)
class ProgramDefinition:
    """Le programme à scorer — payload pur, jamais un objet ORM."""

    title: str
    sessions: tuple[SessionPlan, ...] = ()


@dataclass(frozen=True)
class UserProfile:
    """Profil déclaré (spec §7) — tout champ absent produit une assumption."""

    level: str | None = None
    available_equipment: tuple[str, ...] | None = None
    sessions_per_week: int | None = None


# ────────────────────────── sortie (sérialisable) ──────────────────────────


@dataclass(frozen=True)
class Subscore:
    key: str
    score: int
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class QualityReviewResult:
    """Sortie du moteur — pure, sérialisable, versionnée."""

    grade: str
    global_score: int | None
    subscores: tuple[Subscore, ...]
    alerts: tuple[dict, ...]
    suggestions: tuple[dict, ...]
    assumptions: tuple[str, ...]
    missing_data: tuple[str, ...]
    confidence: str
    coverage_ratio: float
    grade_cap_reason: str | None
    scoring_version: int
    ekb_version: str | None
    disclaimer: str = DISCLAIMER

    def to_dict(self) -> dict:
        """Représentation sérialisable (JSON-ready) de la revue."""
        return asdict(self)


# ─────────────────────────────── EKB access ───────────────────────────────


@dataclass(frozen=True)
class ExerciseKnowledgeBase:
    """Vue en lecture seule du JSON EKB canonique (jamais la DB — EKB_04 différé)."""

    version: str | None
    entries: dict = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path | str | None = None) -> ExerciseKnowledgeBase:
        target = Path(path) if path is not None else _EKB_PATH
        with target.open(encoding="utf-8") as fh:
            payload = json.load(fh)
        return cls(version=payload.get("_version"), entries=payload.get("exercises", {}))

    def lookup(self, name: str) -> dict | None:
        return self.entries.get(name)


# ─────────────────────────────── sous-scores ───────────────────────────────


def _all_slots(definition: ProgramDefinition) -> list[ExerciseSlot]:
    return [slot for session in definition.sessions for slot in session.exercises]


def _score_volume_per_zone(sets_by_zone: dict) -> Subscore:
    """Répartition du volume par zone : pénalise la concentration excessive."""
    if not sets_by_zone:
        return Subscore("volume_per_zone", 50, ("Aucune zone connue — score neutre.",))
    total = sum(sets_by_zone.values())
    top_share = max(sets_by_zone.values()) / total
    zones = len(sets_by_zone)
    if top_share > 0.6:
        score, reason = 35, f"Une seule zone concentre {round(top_share * 100)} % des séries."
    elif zones <= 2:
        score, reason = 50, f"Seulement {zones} zone(s) sollicitée(s) sur le programme."
    elif top_share > 0.4:
        score, reason = 70, "La répartition du volume semble un peu concentrée."
    else:
        score, reason = 85, f"Volume réparti sur {zones} zones."
    return Subscore("volume_per_zone", score, (reason,))


def _score_balance(patterns: list[str]) -> Subscore:
    """Équilibre push / pull / legs d'après `movement_pattern`."""
    if not patterns:
        return Subscore(
            "push_pull_legs_balance", 50, ("Aucun pattern moteur connu — score neutre.",)
        )
    push = sum(1 for p in patterns if p in _PUSH)
    pull = sum(1 for p in patterns if p in _PULL)
    legs = sum(1 for p in patterns if p in _LEGS)
    families = [("poussée", push), ("tirage", pull), ("bas du corps", legs)]
    present = [n for n, c in families if c > 0]
    absent = [n for n, c in families if c == 0]
    if len(present) <= 1:
        return Subscore(
            "push_pull_legs_balance",
            30,
            (f"Le programme ne couvre que : {', '.join(present) or 'aucune famille'}.",),
        )
    if absent:
        return Subscore(
            "push_pull_legs_balance",
            55,
            (f"Famille peu ou pas représentée : {', '.join(absent)}.",),
        )
    counts = [push, pull, legs]
    ratio = max(counts) / max(1, min(counts))
    if ratio >= 3:
        return Subscore(
            "push_pull_legs_balance", 60, ("Un déséquilibre marqué semble présent.",)
        )
    if ratio >= 2:
        return Subscore(
            "push_pull_legs_balance", 75, ("Léger déséquilibre entre familles.",)
        )
    return Subscore(
        "push_pull_legs_balance", 90, ("Poussée, tirage et bas du corps sont représentés.",)
    )


def _score_frequency(definition: ProgramDefinition, zones_by_session: list[set]) -> Subscore:
    """Fréquence de sollicitation par zone sur la semaine déclarée."""
    n_sessions = len(definition.sessions)
    if n_sessions == 0:
        return Subscore("frequency_per_zone", 0, ("Aucune séance dans le programme.",))
    all_zones: set = set()
    for zones in zones_by_session:
        all_zones |= zones
    if not all_zones:
        return Subscore("frequency_per_zone", 50, ("Aucune zone connue — score neutre.",))
    hits = {z: sum(1 for zs in zones_by_session if z in zs) for z in all_zones}
    twice_or_more = sum(1 for c in hits.values() if c >= 2)
    share = twice_or_more / len(all_zones)
    if n_sessions == 1:
        return Subscore(
            "frequency_per_zone", 45, ("Une seule séance : la fréquence reste faible.",)
        )
    if share >= 0.6:
        return Subscore(
            "frequency_per_zone",
            85,
            (f"{twice_or_more}/{len(all_zones)} zones sollicitées au moins 2×/semaine.",),
        )
    if share >= 0.3:
        return Subscore(
            "frequency_per_zone", 70, ("Une partie des zones n'est vue qu'une fois.",)
        )
    return Subscore(
        "frequency_per_zone", 55, ("La plupart des zones ne sont vues qu'une fois.",)
    )


def _score_equipment(known: list[dict], profile: UserProfile | None) -> Subscore:
    """Faisabilité matériel : slots exigeant du matériel non déclaré."""
    families = [e.get("equipment_family") for e in known if e.get("equipment_family")]
    if not families:
        return Subscore(
            "equipment_feasibility", 50, ("Aucun matériel connu — score neutre.",)
        )
    if profile is None or not profile.available_equipment:
        return Subscore(
            "equipment_feasibility",
            60,
            ("Matériel disponible non déclaré — faisabilité supposée.",),
        )
    available = set(profile.available_equipment)
    missing = [f for f in families if f not in available]
    if not missing:
        return Subscore(
            "equipment_feasibility", 95, ("Tout le matériel requis est déclaré disponible.",)
        )
    share = len(missing) / len(families)
    distinct = sorted(set(missing))
    if share > 0.4:
        return Subscore(
            "equipment_feasibility",
            35,
            (f"Beaucoup de slots exigent du matériel non déclaré : {', '.join(distinct)}.",),
        )
    return Subscore(
        "equipment_feasibility",
        65,
        (f"Certains slots exigent du matériel non déclaré : {', '.join(distinct)}.",),
    )


# ──────────────────────────────── moteur ────────────────────────────────


def _aggregate(definition: ProgramDefinition, ekb: ExerciseKnowledgeBase) -> dict:
    """Agrégats déterministes du programme (ordre du programme préservé)."""
    slots = _all_slots(definition)
    known: list[dict] = []
    unknown_names: list[str] = []
    sets_by_zone: dict[str, int] = {}
    for slot in slots:
        entry = ekb.lookup(slot.exercise_name)
        if entry is None:
            unknown_names.append(slot.exercise_name)
            continue
        known.append(entry)
        zone = entry.get("zone_primary")
        if zone:
            sets_by_zone[zone] = sets_by_zone.get(zone, 0) + slot.working_sets

    zones_by_session = []
    for session in definition.sessions:
        zones = {
            (ekb.lookup(slot.exercise_name) or {}).get("zone_primary")
            for slot in session.exercises
        }
        zones_by_session.append({z for z in zones if z})

    usable = sum(
        1 for s in slots if (ekb.lookup(s.exercise_name) or {}).get("zone_primary")
    )
    return {
        "slots": slots,
        "known": known,
        "unknown_names": unknown_names,
        "sets_by_zone": sets_by_zone,
        "patterns": [e["movement_pattern"] for e in known if e.get("movement_pattern")],
        "zones_by_session": zones_by_session,
        "coverage_ratio": round(usable / len(slots), 3) if slots else 0.0,
    }


def _resolve_grade(computed: list[int], global_score: int | None) -> tuple[str, str | None]:
    """Grade hybride (§6) puis plafond V1 à B — 4 sous-scores sur 8 manquants."""
    if global_score is None:
        grade = "C"
    elif global_score >= GRADE_A_MIN:
        grade = "A"
    elif global_score >= GRADE_B_MIN:
        grade = "B"
    else:
        grade = "C"

    worst = min(computed) if computed else 0
    if worst < CAP_TO_C_BELOW:
        grade = "C"
    elif worst < CAP_TO_B_BELOW and grade == "A":
        grade = "B"

    if grade in {"A", "B"}:
        # V1 : A inatteignable tant que la couverture EKB est partielle.
        return "B", _GRADE_CAP_REASON
    return grade, None


def _build_assumptions(
    profile: UserProfile | None, unknown_names: list[str], known: list[dict]
) -> list[str]:
    """Hypothèses visibles (§7) — jamais de certitude implicite."""
    assumptions: list[str] = []
    if profile is None or profile.level is None:
        assumptions.append("Niveau non déclaré — lecture prudente des volumes.")
    if profile is None or not profile.available_equipment:
        assumptions.append(
            "Matériel disponible non déclaré — faisabilité matériel supposée."
        )
    if unknown_names:
        assumptions.append(
            f"{len(unknown_names)} exercice(s) hors EKB — exclus des calculs de zone "
            "et de pattern."
        )
    partial = [
        e for e in known if not e.get("zone_primary") or not e.get("movement_pattern")
    ]
    if partial:
        assumptions.append(
            f"{len(partial)} exercice(s) EKB à métadonnées partielles — couverture réduite."
        )
    return assumptions


def _confidence_for(coverage_ratio: float) -> str:
    """La couverture EKB pilote la confiance — les gaps la réduisent, sans casser."""
    if coverage_ratio >= 0.8:
        return "moderate"
    if coverage_ratio >= 0.5:
        return "low"
    return "very_low"


def score_program(
    definition: ProgramDefinition,
    ekb: ExerciseKnowledgeBase | None = None,
    profile: UserProfile | None = None,
) -> QualityReviewResult:
    """Score un programme custom. Pur, déterministe, sans I/O ni ORM.

    Les sous-scores non mesurables (champs EKB non curés) sont déclarés dans
    `missing_data`, exclus de la moyenne, réduisent `confidence` et plafonnent
    le grade à B — jamais notés 0.
    """
    ekb = ekb if ekb is not None else ExerciseKnowledgeBase.load()
    agg = _aggregate(definition, ekb)

    subscores = (
        _score_volume_per_zone(agg["sets_by_zone"]),
        _score_balance(agg["patterns"]),
        _score_frequency(definition, agg["zones_by_session"]),
        _score_equipment(agg["known"], profile),
    )

    # Missing data : les 4 sous-scores non mesurables (jamais notés 0).
    missing_data = tuple(
        f"{key} — {reason}" for key, reason in sorted(MISSING_SUBSCORES.items())
    )
    assumptions = _build_assumptions(profile, agg["unknown_names"], agg["known"])
    coverage_ratio = agg["coverage_ratio"]
    confidence = _confidence_for(coverage_ratio)

    computed = [s.score for s in subscores]
    global_score = round(sum(computed) / len(computed)) if computed else None
    grade, grade_cap_reason = _resolve_grade(computed, global_score)

    alerts = tuple(
        {"subscore": s.key, "severity": "warn" if s.score < 40 else "info",
         "message": s.reasons[0] if s.reasons else ""}
        for s in subscores
        if s.score < 60
    )
    suggestions = tuple(
        {"subscore": s.key, "message": _suggestion_for(s.key)}
        for s in subscores
        if s.score < 60
    )

    return QualityReviewResult(
        grade=grade,
        global_score=global_score,
        subscores=subscores,
        alerts=alerts,
        suggestions=suggestions,
        assumptions=tuple(assumptions),
        missing_data=missing_data,
        confidence=confidence,
        coverage_ratio=coverage_ratio,
        grade_cap_reason=grade_cap_reason,
        scoring_version=PROGRAM_QUALITY_SCORING_VERSION,
        ekb_version=ekb.version,
    )


def _suggestion_for(key: str) -> str:
    """Suggestions indicatives — jamais d'injonction (« tu dois » interdit, §8)."""
    return {
        "volume_per_zone": "Répartir quelques séries vers les zones les moins vues peut aider.",
        "push_pull_legs_balance": "Ajouter un mouvement de la famille absente peut aider à équilibrer.",
        "frequency_per_zone": "Revoir une même zone deux fois par semaine est souvent utile.",
        "equipment_feasibility": "Vérifier le matériel déclaré, ou choisir des variantes compatibles.",
    }.get(key, "À vérifier selon ton contexte.")
