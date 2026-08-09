"""Pure morphology profile layer (Sb_MORPHO_PROFILE_01, spec `Sx_MORPHO_PROGRAM_01`).

Transforms **raw body facts** into **interpreted morphology descriptors with confidence** —
the first build of the morphology-aware programming queue. It is a PURE, deterministic
function of its input: no I/O, no DB, no ORM, no HTTP, no LLM, no randomness. Same input ⇒
same output (patron éprouvé `program_quality_engine` / `overload_engine`, Sx_30).

Frontières dures (spec §0, §11) :
- **FACT vs INFERENCE strictement séparés** (spec §1). Un FACT est une mesure brute ; une
  INFERENCE est une lecture **dérivée** et **traçable** des FACTS. Une INFERENCE ne fabrique
  jamais un FACT.
- **Garde-fou non-médical STRICT** (spec §3, `Sx_BI_01_ACTIVATION §13`) : jamais de composition
  corporelle, body-fat, **posture/pathologie**, dyskinésie, diagnostic, longueur de fémur ni
  d'insertions. Ces descripteurs sont **refusés** (`not_deductible`), jamais produits.
- **Aucune pseudo-précision anthropométrique** : l'ape index est un **tag de levier borné**, pas
  une longueur de segment osseux ; les tags qualitatifs sont des lectures d'orientation non
  contraignantes, jamais des vérités primaires.
- **Ce module ne génère AUCUN programme, ne choisit AUCUN exercice, n'implémente AUCUN slot ni
  substitution** (builds suivants de la file). Les descripteurs `*_priority_candidate` sont de
  simples **candidats** d'orientation, pas des priorités appliquées.

Ce module ne lit ni n'écrit `BodyMeasurement` : il opère sur un **modèle d'entrée pur**
(`MorphologyFacts`). La persistance/branchement éventuels sont des builds ultérieurs — aucune
migration ici.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

MORPHOLOGY_PROFILE_ENGINE_VERSION = 1

# ── Vocabulaires fermés ──────────────────────────────────────────────────────
LAYER_FACT = "FACT"
LAYER_INFERENCE = "INFERENCE"

CONF_MEASURED = "measured"        # dérivé uniquement de mesures numériques confirmées
CONF_DERIVED = "derived"          # combinaison de mesures + hypothèse bornée déclarée
CONF_INFERRED = "inferred"        # lecture qualitative faiblement étayée (réserve)
CONF_NOT_DEDUCTIBLE = "not_deductible"  # refusé par garde-fou (jamais produit)

# Observations qualitatives opérateur admises (clé → tags bornés).
OBSERVATION_VOCAB: dict[str, frozenset[str]] = {
    "clavicular_width": frozenset({"favorable", "neutral"}),
    "quads": frozenset({"relatively_strong", "neutral"}),
    "calves": frozenset({"relative_lag", "neutral"}),
    "lats": frozenset({"acceptable", "weak"}),
}

# Candidats d'orientation admis (jamais une priorité appliquée — build suivant).
FOCUS_CANDIDATE_VOCAB: frozenset[str] = frozenset(
    {"lateral_delts", "upper_chest", "rear_delts_upper_back", "calves"}
)

# Descripteurs que le modèle REFUSE d'affirmer (garde-fou strict, spec §3).
# Toute demande sur ces clés renvoie `not_deductible` ; ils ne sont jamais dérivés.
GUARDED_NOT_DEDUCTIBLE: frozenset[str] = frozenset(
    {
        "femur_length_cm",
        "humerus_length_cm",
        "muscle_insertions",
        "posture_assessment",
        "scapular_dyskinesis",
        "body_fat_percentage",
        "medical_diagnosis",
    }
)

# ── Seuils bornés (heuristiques déclarées, jamais médicaux) ───────────────────
_NARROW_WAIST_TO_HEIGHT_MAX = 0.47   # waist/height <= 0.47 → taille relativement étroite
_LONGILIGNE_MIN_HEIGHT_CM = 178.0    # + taille étroite → orientation longiligne (tag)
_VTAPER_CHEST_TO_WAIST_MIN = 1.15    # chest/waist >= 1.15 → structure V favorable (proxy)
_APE_INDEX_NOT_EXTREME_MAX = 6.0     # 0 < ape <= 6 cm → légèrement positif, non extrême

_GUARD_NON_MEDICAL = (
    "Lecture non médicale et non contraignante — aucune composition corporelle, "
    "aucune posture, aucun diagnostic, aucune longueur osseuse."
)
_GUARD_PROXY = (
    "Proxy structurel (pas une mesure directe de largeur d'épaule) — non médical."
)
_GUARD_CANDIDATE = (
    "Candidat d'orientation d'entraînement seulement — aucun programme, slot ni "
    "exercice généré ici ; non contraignant, non médical."
)


# ── Modèles ───────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class BodyObservation:
    """Observation qualitative opérateur, bornée (clé + tag du vocabulaire fermé)."""

    key: str
    tag: str
    source: str | None = None


@dataclass(frozen=True)
class MorphologyFacts:
    """Entrée pure : mesures numériques (cm) + observations qualitatives bornées.

    Aucune valeur inventée : un champ absent (`None`) n'est jamais estimé. L'ape index est
    fourni OU dérivé de `wingspan - height` (jamais une longueur de segment osseux)."""

    height_cm: float | None = None
    wingspan_cm: float | None = None
    ape_index_cm: float | None = None
    waist_cm: float | None = None
    chest_cm: float | None = None
    thigh_cm: float | None = None
    calf_cm: float | None = None
    observations: tuple[BodyObservation, ...] = ()
    focus_candidates: tuple[str, ...] = ()
    source: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class MorphologyDescriptor:
    """Un descripteur de morphologie (FACT ou INFERENCE), traçable et borné."""

    descriptor_id: str
    layer: str
    value: object
    confidence: str
    evidence: tuple[str, ...]
    non_medical_guardrail: str
    rationale: str
    is_proxy: bool = False
    engine_version: int = MORPHOLOGY_PROFILE_ENGINE_VERSION

    def to_dict(self) -> dict:
        return asdict(self)


# ── Helpers internes (purs) ────────────────────────────────────────────────────

_NUMERIC_FACT_FIELDS = (
    ("height_cm", "Taille"),
    ("wingspan_cm", "Envergure"),
    ("waist_cm", "Tour de taille"),
    ("chest_cm", "Tour de poitrine"),
    ("thigh_cm", "Tour de cuisse"),
    ("calf_cm", "Tour de mollet"),
)


def _observation(facts: MorphologyFacts, key: str) -> BodyObservation | None:
    for obs in facts.observations:
        if obs.key == key:
            return obs
    return None


def _waist_to_height(facts: MorphologyFacts) -> float | None:
    if facts.waist_cm and facts.height_cm:
        return facts.waist_cm / facts.height_cm
    return None


def _chest_to_waist(facts: MorphologyFacts) -> float | None:
    if facts.chest_cm and facts.waist_cm:
        return facts.chest_cm / facts.waist_cm
    return None


def _resolved_ape_index(facts: MorphologyFacts) -> tuple[float | None, str]:
    """(value, confidence-hint). Fourni → measured ; dérivé de wingspan-height → derived."""
    if facts.ape_index_cm is not None:
        return facts.ape_index_cm, CONF_MEASURED
    if facts.wingspan_cm is not None and facts.height_cm is not None:
        return round(facts.wingspan_cm - facts.height_cm, 2), CONF_DERIVED
    return None, CONF_NOT_DEDUCTIBLE


# ── FACT descriptors ────────────────────────────────────────────────────────


def _fact_descriptors(facts: MorphologyFacts) -> list[MorphologyDescriptor]:
    out: list[MorphologyDescriptor] = []
    for field_name, label in _NUMERIC_FACT_FIELDS:
        value = getattr(facts, field_name)
        if value is None:
            continue
        out.append(
            MorphologyDescriptor(
                descriptor_id=f"fact_{field_name}",
                layer=LAYER_FACT,
                value=value,
                confidence=CONF_MEASURED,
                evidence=(f"measurement:{field_name}={value}",),
                non_medical_guardrail=_GUARD_NON_MEDICAL,
                rationale=f"{label} mesuré (fait brut).",
            )
        )
    ape, ape_conf = _resolved_ape_index(facts)
    if ape is not None:
        ev = ("measurement:ape_index_cm",) if facts.ape_index_cm is not None else (
            "derived:wingspan_cm-height_cm",
        )
        out.append(
            MorphologyDescriptor(
                descriptor_id="fact_ape_index_cm",
                layer=LAYER_FACT,
                value=ape,
                confidence=ape_conf,
                evidence=ev,
                non_medical_guardrail=(
                    "Ape index = envergure − taille (tag de levier borné) ; "
                    "JAMAIS une longueur de fémur/humérus. Non médical."
                ),
                rationale="Ape index (fourni ou dérivé de l'envergure et de la taille).",
            )
        )
    return out


# ── INFERENCE descriptors ────────────────────────────────────────────────────


def _infer_longiligne(facts: MorphologyFacts) -> MorphologyDescriptor | None:
    wth = _waist_to_height(facts)
    if facts.height_cm is None or wth is None:
        return None
    if facts.height_cm >= _LONGILIGNE_MIN_HEIGHT_CM and wth <= _NARROW_WAIST_TO_HEIGHT_MAX:
        return MorphologyDescriptor(
            descriptor_id="longiligne_athletic_build",
            layer=LAYER_INFERENCE,
            value="longiligne",
            confidence=CONF_DERIVED,
            evidence=(f"height_cm={facts.height_cm}", f"waist_to_height={round(wth, 3)}"),
            non_medical_guardrail=_GUARD_NON_MEDICAL,
            rationale=(
                "Orientation de charpente (tag non contraignant) : taille élevée + taille "
                "corporelle relativement étroite."
            ),
            is_proxy=True,
        )
    return None


def _infer_ape_index(facts: MorphologyFacts) -> MorphologyDescriptor | None:
    ape, conf = _resolved_ape_index(facts)
    if ape is None or ape <= 0 or ape > _APE_INDEX_NOT_EXTREME_MAX:
        return None
    return MorphologyDescriptor(
        descriptor_id="slightly_positive_ape_index_not_extreme",
        layer=LAYER_INFERENCE,
        value=ape,
        confidence=conf if conf != CONF_NOT_DEDUCTIBLE else CONF_DERIVED,
        evidence=(f"ape_index_cm={ape}",),
        non_medical_guardrail=(
            "Tag de levier borné (léger avantage de bras) — pas une longueur osseuse, "
            "non médical."
        ),
        rationale=f"Ape index légèrement positif (+{ape} cm), non extrême (≤ {int(_APE_INDEX_NOT_EXTREME_MAX)} cm).",
    )


def _infer_favorable_structure(facts: MorphologyFacts) -> MorphologyDescriptor | None:
    ctw = _chest_to_waist(facts)
    obs = _observation(facts, "clavicular_width")
    obs_favorable = obs is not None and obs.tag == "favorable"
    if ctw is None and not obs_favorable:
        return None
    if (ctw is not None and ctw >= _VTAPER_CHEST_TO_WAIST_MIN) or obs_favorable:
        evidence = []
        if ctw is not None:
            evidence.append(f"chest_to_waist={round(ctw, 3)}")
        if obs_favorable:
            evidence.append("observation:clavicular_width=favorable")
        return MorphologyDescriptor(
            descriptor_id="favorable_shoulder_to_waist_structure",
            layer=LAYER_INFERENCE,
            value="favorable",
            confidence=CONF_DERIVED if ctw is not None else CONF_INFERRED,
            evidence=tuple(evidence),
            non_medical_guardrail=_GUARD_PROXY,
            rationale=(
                "Structure V favorable (proxy chest/waist et/ou observation de largeur "
                "claviculaire) — pas une mesure directe d'épaule."
            ),
            is_proxy=True,
        )
    return None


def _infer_narrow_waist(facts: MorphologyFacts) -> MorphologyDescriptor | None:
    wth = _waist_to_height(facts)
    if wth is None or wth > _NARROW_WAIST_TO_HEIGHT_MAX:
        return None
    return MorphologyDescriptor(
        descriptor_id="narrow_waist_pelvis_relative",
        layer=LAYER_INFERENCE,
        value="narrow_relative",
        confidence=CONF_DERIVED,
        evidence=(f"waist_to_height={round(wth, 3)}",),
        non_medical_guardrail=_GUARD_NON_MEDICAL,
        rationale="Tour de taille relativement étroit (ratio taille/hauteur bas) — non médical.",
    )


def _infer_from_observation(
    facts: MorphologyFacts,
    obs_key: str,
    obs_tag: str,
    descriptor_id: str,
    value: str,
    rationale: str,
    extra_evidence: tuple[str, ...] = (),
) -> MorphologyDescriptor | None:
    obs = _observation(facts, obs_key)
    if obs is None or obs.tag != obs_tag:
        return None
    return MorphologyDescriptor(
        descriptor_id=descriptor_id,
        layer=LAYER_INFERENCE,
        value=value,
        confidence=CONF_INFERRED,
        evidence=(f"observation:{obs_key}={obs_tag}", *extra_evidence),
        non_medical_guardrail=_GUARD_NON_MEDICAL,
        rationale=rationale,
    )


def _infer_priority_candidate(
    facts: MorphologyFacts, focus_key: str, descriptor_id: str
) -> MorphologyDescriptor | None:
    if focus_key not in facts.focus_candidates:
        return None
    return MorphologyDescriptor(
        descriptor_id=descriptor_id,
        layer=LAYER_INFERENCE,
        value="candidate",
        confidence=CONF_INFERRED,
        evidence=(f"focus_candidate:{focus_key}",),
        non_medical_guardrail=_GUARD_CANDIDATE,
        rationale=(
            f"Candidat d'orientation « {focus_key} » — signalé pour un build de priorités "
            "ultérieur ; aucun programme/slot généré ici."
        ),
    )


def _inference_descriptors(facts: MorphologyFacts) -> list[MorphologyDescriptor]:
    calf_ev = (f"calf_cm={facts.calf_cm}",) if facts.calf_cm is not None else ()
    candidates = [
        _infer_longiligne(facts),
        _infer_ape_index(facts),
        _infer_favorable_structure(facts),
        _infer_narrow_waist(facts),
        _infer_from_observation(
            facts, "quads", "relatively_strong", "quads_relatively_strong",
            "relatively_strong",
            "Quadriceps relativement développés (observation opérateur) — pas une mesure de force.",
        ),
        _infer_from_observation(
            facts, "calves", "relative_lag", "calves_relative_lag", "relative_lag",
            "Mollets en retard relatif (observation opérateur) — pas un déficit médical.",
            extra_evidence=calf_ev,
        ),
        _infer_from_observation(
            facts, "lats", "acceptable", "lats_acceptable_not_weak", "acceptable",
            "Dorsaux acceptables, non faibles (observation opérateur).",
        ),
        _infer_priority_candidate(facts, "lateral_delts", "lateral_delts_priority_candidate"),
        _infer_priority_candidate(facts, "upper_chest", "upper_chest_priority_candidate"),
        _infer_priority_candidate(
            facts, "rear_delts_upper_back", "rear_delts_upper_back_priority_candidate"
        ),
    ]
    return [c for c in candidates if c is not None]


# ── API publique ───────────────────────────────────────────────────────────


def build_morphology_profile(facts: MorphologyFacts) -> tuple[MorphologyDescriptor, ...]:
    """Faits corporels → descripteurs de morphologie (FACT + INFERENCE), déterministe.

    Pur : même entrée ⇒ même sortie. N'émet jamais un descripteur du garde-fou strict
    (`GUARDED_NOT_DEDUCTIBLE`). Un descripteur dont les entrées manquent est **omis**
    (jamais inventé)."""
    return tuple(_fact_descriptors(facts) + _inference_descriptors(facts))


def guarded_not_deductible(descriptor_id: str) -> MorphologyDescriptor:
    """Descripteur `not_deductible` explicite pour toute clé du garde-fou strict.

    Rend testable le refus : le modèle ne prétend jamais mesurer/inférer un fémur, une
    posture, des insertions, une dyskinésie, un %BF ni un diagnostic médical."""
    if descriptor_id not in GUARDED_NOT_DEDUCTIBLE:
        raise ValueError(
            f"'{descriptor_id}' n'est pas un descripteur gardé. "
            f"Gardés : {sorted(GUARDED_NOT_DEDUCTIBLE)}"
        )
    return MorphologyDescriptor(
        descriptor_id=descriptor_id,
        layer=LAYER_INFERENCE,
        value=None,
        confidence=CONF_NOT_DEDUCTIBLE,
        evidence=(),
        non_medical_guardrail=(
            "Refusé par garde-fou strict — non déductible et jamais revendiqué "
            "(spec §3, Sx_BI_01_ACTIVATION §13)."
        ),
        rationale="Ce descripteur relève du médical/anatomique interdit : non déductible.",
    )
