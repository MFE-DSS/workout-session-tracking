"""Sb_27.4 — Recommendation Explainer (read-only wrapper).

Consumes the dict returned by `app.services.recommendation.recommend_next_session`
and produces a small explanation payload the UI can render:

* `available`       — boolean
* `primary_reason`  — the single most relevant short reason (string or None)
* `reasons`         — list of 1..3 short reasons (deduped, ordered)
* `confidence`      — "ok" | "low" derived from the source payload
* `fallback_note`   — explicit "Non déductible" / cold start phrase if applicable

Contract (Sx_27 §11, §16 + OQ-4 verbatim):
* NEVER touches `recommendation.py` or any service in `scoring/`, `reco/`,
  `substitution.py`, `implicit_signal.py`, `quality_score.py`,
  `coach_report.py` — purely consumes the existing payload.
* NEVER re-runs the recommendation logic. Reads only the public fields
  already present in `reco_payload` (top, context, alternatives).
* NEVER invents a reason: if a field is missing/None we either skip the
  rule or surface an explicit "Non déductible" / fallback note.
* Phrases are deterministic (no LLM).

Public API:

    from app.services.recommendation_explainer import explain_recommendation
    explanation = explain_recommendation(reco_payload)
"""
from __future__ import annotations

import math
from typing import Any

_MAX_REASONS = 3

# ── Sb_FATIGUE_SCALE_FIX_01 — explicit fatigue scale boundary ──────────────
#
# `behavioral.compute_behavioral_state` produces `fatigue_score` on a 0–100
# scale; `recommendation.py` forwards it verbatim into `context`. This module
# used to compare that value against 0.7 / 0.2 as if it were 0–1, so the
# "fatigue élevée" branch fired for essentially every real value (20, 50 and 80
# are all >= 0.7) and the "fatigue basse" branch was unreachable.
#
# The producer is not redesigned and `recommendation.py` is not touched (hard
# architectural constraint). The conversion lives here, at the consumer
# boundary, and is explicit, bounded, named and unit tested.
FATIGUE_RAW_SCALE_MAX = 100.0

# Lowest value `behavioral` can actually emit, DERIVED not guessed:
# compute_session_fatigue = (global_state + concentration) / 2 with
# global_state in {80, 50, 20} (default 50) and concentration in {70, 40, 10}
# (default 40) → minimum (20 + 10) / 2 = 15. compute_weighted_fatigue is a
# convex combination of such values, so it cannot leave [15, 75] either, and an
# empty history returns the 50 default. A test derives this bound from those
# dicts so it cannot drift silently.
FATIGUE_RAW_MIN_PRODUCIBLE = 15.0

# Normalised bands. FATIGUE_HIGH is deliberately 0.7 == 70/100 ==
# recommendation.FATIGUE_HIGH_THRESHOLD: after normalisation the explainer
# speaks of "high fatigue" exactly when the recommendation engine itself
# filters on high fatigue. No new number is invented. Pinned by a test.
FATIGUE_HIGH = 0.7
FATIGUE_LOW = 0.2


def normalize_fatigue_score(raw: Any) -> float | None:
    """Convert a raw 0–100 fatigue score to 0.0–1.0, or ``None`` if unusable.

    ``None`` means "no usable fatigue reading" and the caller must stay silent
    rather than invent a band. Rejected: non-numeric values, booleans (``True``
    is an ``int`` and would otherwise read as 0.01), NaN, and anything outside
    the 0–100 contract.

    Also rejected: anything **below** ``FATIGUE_RAW_MIN_PRODUCIBLE``.
    ``recommendation.py`` degrades to ``fatigue_score = 0.0`` when
    ``compute_behavioral_state`` raises, and 0.0 is provably not producible by
    ``behavioral`` — so it is a failure sentinel, not a measurement. Reading it
    as 0.0 normalised would tell a user whose data we failed to compute that
    they are fresh and should push. That is the one direction where guessing
    can do harm.

    The bound is deliberately one-sided: we refuse to invent good news, but we
    do not suppress bad news. A value above the producible ceiling still maps
    to high fatigue rather than to silence — worst case the user is advised to
    take it easy on a reading we could not fully vouch for.
    """
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        return None
    value = float(raw)
    # NaN needs its own guard: every comparison against it is False, so the
    # range check below would let it straight through. `math.isnan` rather than
    # the `value != value` idiom — same result, and it does not read as a typo
    # (Sonar python:S1764 flags the self-comparison form, correctly).
    if math.isnan(value):
        return None
    if value < FATIGUE_RAW_MIN_PRODUCIBLE or value > FATIGUE_RAW_SCALE_MAX:
        return None
    return value / FATIGUE_RAW_SCALE_MAX

_FALLBACK_PHRASE = "Recommandation basée sur ton historique récent."
_LOW_DATA_PHRASE = "Pas assez de données pour expliquer plus finement."
_COLD_START_PHRASE = "Première séance — démarrage doux suggéré."
_FALLBACK_NOTE = "Pas encore assez de données pour personnaliser."

# `REC-CP3` — distinct de `_FALLBACK_NOTE` : « je n'ai pas assez d'historique »
# et « je n'ai pas su lire un exercice de ton historique » ne disent pas la même
# chose, et les confondre ferait passer une lacune de classement pour une
# absence de données.
_NOTE_OBSERVATION_PARTIELLE = (
    "Un exercice de ton historique n'a pas pu être classé."
)


def explain_recommendation(reco_payload: Any) -> dict[str, Any]:
    """Produce an explanation dict for the home/launcher UI.

    `reco_payload` is the dict returned by `recommend_next_session` or
    None. Any shape we don't recognise degrades gracefully — we surface
    a generic fallback, never crash.
    """
    if not isinstance(reco_payload, dict) or "top" not in reco_payload:
        return _empty(available=False)

    top = reco_payload.get("top") or {}
    context = reco_payload.get("context") or {}
    if not isinstance(top, dict) or not isinstance(context, dict):
        return _empty(available=False)

    # ── `REC-CP4 §14` — LA CONSÉQUENCE D'UN REFUS, DITE UNE FOIS.
    #
    # Quand l'utilisateur a explicitement écarté un conseil, Mission a changé
    # POUR CETTE RAISON. Ne pas le dire laisserait croire à une girouette : la
    # veille il fallait faire du LISS, aujourd'hui plus — sans qu'on sache que
    # c'est parce qu'on a dit non.
    #
    # ⚠ UNE LIGNE, ET SEULEMENT QUAND ELLE EXPLIQUE VRAIMENT UN CHANGEMENT.
    # Pas de tableau de bord de rétroaction, pas de bavardage. Si le conseil
    # écarté reste la recommandation faute d'alternative, on le dit AUSSI —
    # c'est l'autre moitié de l'honnêteté (`§7`).
    consequence = _consequence_du_refus(context)

    # ── `REC-CP3` — SI LE MOTEUR A TRANSMIS SA TRACE, ON LA LIT.
    #
    # Tout ce qui suit cette branche re-dérive des raisons depuis un contexte
    # appauvri : quatre clés et la phrase déjà écrite. C'était le seul moyen
    # disponible tant que le moteur ne disait pas ce qui avait décidé.
    #
    # Une politique qui transmet sa trace rend cette reconstruction non
    # seulement inutile mais nuisible : deux logiques parallèles finissent par
    # diverger, et c'est la reconstruction qui a tort, puisqu'elle devine.
    trace = top.get("explication")
    if isinstance(trace, dict):
        return _depuis_la_trace(trace, top, consequence)

    reasons: list[str] = []
    if consequence:
        reasons.append(consequence)
    confidence = "ok"
    fallback_note: str | None = None

    # ── Rule A: cold start (highest priority — context flag explicit)
    if context.get("cold_start") is True:
        reasons.append(_COLD_START_PHRASE)
        confidence = "low"
        fallback_note = _FALLBACK_NOTE

    # ── Rule B: existing top.phrase verbatim (deterministic, pre-computed
    # by recommendation.py — primary signal). Always included if present.
    phrase = _clean(top.get("phrase"))
    if phrase and phrase not in reasons:
        reasons.append(phrase)

    # ── Rule C: explicit fallback flag → generic explanation
    if context.get("fallback") is True:
        if _FALLBACK_PHRASE not in reasons:
            reasons.append(_FALLBACK_PHRASE)
        confidence = "low"

    # ── Rule D: zone-freshness derived from days_since_last_*
    zone_reason = _zone_freshness_reason(top, context)
    if zone_reason and zone_reason not in reasons:
        reasons.append(zone_reason)

    # ── Rule E: fatigue level (informational, never invents)
    fatigue_reason = _fatigue_reason(context)
    if fatigue_reason and fatigue_reason not in reasons:
        reasons.append(fatigue_reason)

    # Cap to MAX, keeping order (most-relevant first).
    reasons = reasons[:_MAX_REASONS]

    if not reasons:
        # Top exists but we have no narrative material at all.
        reasons = [_FALLBACK_PHRASE]
        confidence = "low"
        fallback_note = _FALLBACK_NOTE

    primary_reason = reasons[0]
    return {
        "available": True,
        "primary_reason": primary_reason,
        "reasons": reasons,
        "confidence": confidence,
        "fallback_note": fallback_note,
    }


def _consequence_du_refus(context: dict) -> str | None:
    """`§14` — ce qu'il faut dire quand un conseil a été écarté.

    ⚠ ELLE N'INVENTE AUCUNE PRÉFÉRENCE. Elle constate un geste et son effet —
    « tu as écarté X, voici l'option suivante » — jamais « tu n'aimes pas X ».
    Un refus appartient à une décision, dans un contexte (`§8`).

    ⚠ ELLE NE PARLE QUE SI ELLE EXPLIQUE UN CHANGEMENT. Sans refus dans ce
    contexte, elle se tait : une ligne affichée à chaque visite cesserait
    d'être une explication pour devenir du décor.
    """
    nom = _clean(context.get("conseil_ecarte_nom"))
    if not nom:
        return None
    if context.get("sans_alternative"):
        # `§7` — il revient, et il doit dire pourquoi.
        return (
            f"{nom} revient : aucune autre séance n'est éligible maintenant."
        )
    return f"{nom} écarté — voici l'option suivante."


# ───────── `REC-CP3` — lecture de la trace ─────────


def _depuis_la_trace(
    trace: dict, top: dict, consequence: str | None = None
) -> dict[str, Any]:
    """Construit l'explication **en lisant** ce que le moteur a décidé.

    Aucune re-dérivation : les facteurs viennent du moteur, dans son ordre de
    précédence. La seule chose que cette fonction décide est la mise en forme.

    ⚠ Aucun nombre ne traverse. Ni score, ni déficit, ni jours. La trace n'en
    contient pas, et cette fonction n'en fabrique pas : l'utilisateur reçoit
    les raisons, pas la mécanique.
    """
    gagnants = [_clean(r) for r in trace.get("facteurs_gagnants") or ()]
    limitants = [_clean(r) for r in trace.get("facteurs_limitants") or ()]
    justification = _clean(trace.get("justification_repetition"))

    raisons: list[str] = []
    if consequence:
        raisons.append(consequence)
    phrase = _clean(top.get("phrase"))
    if phrase:
        raisons.append(phrase)
    for r in gagnants:
        # La phrase est déjà une lecture du premier facteur gagnant : la
        # répéter mot pour mot ferait deux fois la même raison.
        if r and not _dit_la_meme_chose(r, raisons):
            raisons.append(_en_phrase(r))
    if justification:
        raisons.append(justification)
    for r in limitants:
        if r and not _dit_la_meme_chose(r, raisons):
            raisons.append(_en_phrase(r, prefixe="Mais "))

    partielle = trace.get("provenance") == "partielle"
    if not raisons:
        raisons = [_FALLBACK_PHRASE]

    return {
        "available": True,
        "primary_reason": raisons[0],
        "reasons": raisons[:_MAX_REASONS],
        # L'incertitude vient de l'observation, pas d'une heuristique locale :
        # la même grammaire que `zone_exposure`, sans en créer une seconde.
        "confidence": "low" if partielle else "ok",
        "fallback_note": _NOTE_OBSERVATION_PARTIELLE if partielle else None,
    }


def _en_phrase(facteur: str, *, prefixe: str = "") -> str:
    """Un facteur du moteur, présenté comme une raison autonome.

    Les facteurs sont rédigés en minuscule et sans point, pour se composer dans
    la phrase compacte. Affichés tels quels comme raisons séparées, ils rendent
    « zones récupérées » — sans capitale ni ponctuation. Aucune garde de
    structure ne voyait cela ; la garde de RENDU l'a attrapé au premier essai.

    La mise en forme appartient bien ici : le moteur dit ce qui a décidé, ce
    module décide comment ça se lit.
    """
    texte = prefixe + facteur
    texte = texte[:1].upper() + texte[1:]
    return texte if texte.endswith(".") else texte + "."


def _dit_la_meme_chose(candidat: str, deja: list[str]) -> bool:
    """La phrase compacte étant tirée du premier facteur gagnant, elle le
    contient mot pour mot à la capitalisation et au point près."""
    noyau = candidat.rstrip(".").lower()
    return any(noyau in existant.rstrip(".").lower() for existant in deja)


# ───────── helpers (pure, no side effects) ─────────


def _empty(*, available: bool) -> dict[str, Any]:
    return {
        "available": available,
        "primary_reason": _FALLBACK_PHRASE if available else None,
        "reasons": [_FALLBACK_PHRASE] if available else [],
        "confidence": "low",
        "fallback_note": _FALLBACK_NOTE,
    }


def _clean(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()


def _zone_freshness_reason(top: dict, context: dict) -> str | None:
    """Build a short zone-freshness reason from `days_since_last_*` + zones.

    Never invents : if `days_since_last_strength` is None and primary_zones
    is empty, we return None rather than fabricate "muscles frais".
    """
    primary_zones = top.get("primary_zones")
    if not isinstance(primary_zones, (list, tuple)) or not primary_zones:
        return None

    days_strength = context.get("days_since_last_strength")
    days_cardio = context.get("days_since_last_cardio")

    # We pick the longest "freshness" signal we have. Only surface it
    # if it's clearly meaningful (≥ 2 days) — otherwise the phrase is
    # noise.
    candidates = [
        (d, label)
        for d, label in (
            (days_strength, "strength"),
            (days_cardio, "cardio"),
        )
        if isinstance(d, (int, float)) and d >= 2
    ]
    if not candidates:
        return None
    days, label = max(candidates, key=lambda x: x[0])

    zones_text = ", ".join(str(z) for z in primary_zones[:2]).lower()
    if not zones_text:
        return None
    if label == "strength":
        return f"{zones_text.capitalize()} {int(days)} j sans muscu — frais à travailler."
    return f"{zones_text.capitalize()} {int(days)} j sans cardio — créneau idéal."


def _fatigue_reason(context: dict) -> str | None:
    """Surface a fatigue note only when the score is explicitly informative."""
    score = normalize_fatigue_score(context.get("fatigue_score"))
    if score is None:
        return None
    # Higher = more fatigued. We never tell the user a precise number — only a
    # qualitative band, and only when the band is meaningful enough to act on.
    if score >= FATIGUE_HIGH:
        return "Niveau de fatigue élevé — séance légère privilégiée."
    if score <= FATIGUE_LOW:
        return "Niveau de fatigue bas — bon moment pour pousser."
    return None
