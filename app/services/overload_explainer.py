"""Sb_30.2 — Progressive Overload Engine UI explainer.

Couche purement présentation : transforme un :class:`OverloadHint` en
un dict prêt pour le template Jinja, sans réimplémenter la logique
métier de :mod:`overload_engine`.

Contrat (Sx_30 §6/§7) :
- Wording sobre, jamais autoritaire ("tu dois" interdit).
- Si ``state == "unknown"`` → ``is_silent = True`` : le template peut
  choisir de ne rien afficher.
- ``engine_version`` propagé tel quel.
- Aucune dépendance DB, aucun I/O, fonction pure.
"""

from __future__ import annotations

from app.services.overload_engine import OverloadHint, OverloadState

# Libellés courts par état. Aucun verbe autoritaire.
_INTENT_LABELS: dict[OverloadState, str] = {
    "unknown": "Première fois sur cet exercice",
    "progress": "Tenter d'augmenter la charge",
    "consolidate": "Consolider la charge actuelle",
    "top-range": "Atteindre le bas de range",
    "deload": "Alléger temporairement",
}


def _format_weight(weight_kg: float | None) -> str | None:
    if weight_kg is None:
        return None
    # ``:g`` supprime les ``.0`` superflus (90.0 → 90, 2.5 → 2.5).
    return f"{weight_kg:g} kg"


def _format_reps(reps_min: int | None, reps_max: int | None) -> str | None:
    if reps_min is None and reps_max is None:
        return None
    if reps_min == reps_max:
        return f"{reps_min} reps"
    if reps_min is None or reps_max is None:
        # Cas dégradé conservateur : retourne la valeur connue.
        v = reps_min if reps_min is not None else reps_max
        return f"{v} reps"
    return f"{reps_min}-{reps_max} reps"


def _format_target_summary(hint: OverloadHint) -> str | None:
    """Construit ``"102.5 kg · 6-10 reps"`` ou ``None`` si ``state``
    ne porte pas de cible chiffrée (``unknown``)."""
    w = _format_weight(hint.target_weight_kg)
    r = _format_reps(hint.target_reps_min, hint.target_reps_max)
    if w is None and r is None:
        return None
    if w is None:
        return r
    if r is None:
        return w
    return f"{w} · {r}"


def explain_overload_hint(hint: OverloadHint) -> dict:
    """Traduit un :class:`OverloadHint` en payload de template.

    Sortie (clés stables, voir Sb_30.3 pour la consommation Jinja) :

    - ``state`` : str, 1 des 5 états
    - ``intent_label`` : str court, sobre, sans verbe autoritaire
    - ``target_summary`` : str | None
    - ``reasons`` : tuple[str, ...]  (≤ 3, vient du moteur)
    - ``engine_version`` : int
    - ``is_silent`` : bool (True ssi le template peut ne rien afficher,
      pour ``state == "unknown"``)
    """
    state = hint.state
    return {
        "state": state,
        "intent_label": _INTENT_LABELS.get(state, _INTENT_LABELS["unknown"]),
        "target_summary": _format_target_summary(hint),
        "reasons": hint.reasons,
        "engine_version": hint.engine_version,
        "is_silent": state == "unknown",
    }
