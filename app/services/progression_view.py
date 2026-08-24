"""`TRAIN1-B` — vue-modèle de l'instrument PROGRESSIF. **Pure.**

Ce module ne calcule rien et ne touche à rien : il met en forme des
`ProgressionFacts` et des `CardioFacts` déjà produits. Même patron que
`progress_signals`, et pour la même raison — une garde vérifie qu'il n'importe
ni `sqlalchemy` ni `datetime`, ce qui permet d'éprouver chaque état de rendu
sans base ni serveur.

CE QUE LA SURFACE REND, ET CE QU'ELLE REFUSE DE RENDRE
--------------------------------------------------------
Elle rend, par exercice :

    Développé incliné haltères
    70 × 10   →   72,5 × 10

Elle ne rend **pas** :

    2 progressent · 1 stable

La seconde formulation exige une fonction de jugement — un seuil au-delà
duquel un écart « compte ». Ce seuil n'existe nulle part dans ce produit, et
l'inventer ici en ferait une revendication. La première montre les faits et
laisse le cockpit exact.

POURQUOI AUCUNE FLÈCHE VERTE NI ROUGE
---------------------------------------
Un `+2,5 kg` est un fait. « Mieux » est un jugement, et il est faux au moins
une fois sur dix : une charge en baisse peut être un allègement voulu, une
reprise, un travail de technique. Le socle `UIV3_COCKPIT_LADDER_01` réserve
l'ambre à l'action de l'utilisateur ; l'écart, lui, est produit par le système
et reste dans le vocabulaire neutre.
"""
from __future__ import annotations

from typing import Any

from app.services.cardio_lane import CardioFacts
from app.services.progression_facts import TOP_N, ExerciseProgression, ProgressionFacts

#: Rendu d'une grandeur absente. Un tiret, parce qu'il n'y a rien à nommer —
#: à distinguer de « inconnu », qui qualifie une déclaration jamais faite.
NO_VALUE = "—"


def _fmt_weight(w: float | None) -> str:
    if w is None:
        return NO_VALUE
    if w == int(w):
        return str(int(w))
    # Virgule décimale : le produit est en français, et `72.5 kg` détonne à
    # côté des libellés de séance.
    return f"{w:g}".replace(".", ",")


def format_performance(weight: float | None, reps: int | None) -> str:
    """`70 × 10`, ou ce qui est connu, ou rien.

    On n'invente pas la moitié manquante : une série notée sans charge rend
    `— × 10`, pas un poids supposé.
    """
    if weight is None and reps is None:
        return NO_VALUE
    return f"{_fmt_weight(weight)} × {reps if reps is not None else NO_VALUE}"


def _fmt_signed(value: float | None, unit: str) -> str | None:
    """`+2,5 kg`, `−1 rep`, `= reps`. Jamais « mieux », jamais « moins bien ».

    L'unité est portée **même sur une égalité**. `delta.py` note un écart nul
    « `=` » ; rendu seul à côté d'un autre morceau, cela donnait `+2,5 kg =`,
    où rien ne dit ce qui est égal. Vu au rendu, pas déduit.
    """
    if value is None:
        return None
    if value == 0:
        return f"= {unit}"
    sign = "+" if value > 0 else "−"
    return f"{sign}{_fmt_weight(abs(value))} {unit}"


def format_delta_parts(prog: ExerciseProgression) -> list[str]:
    """Les morceaux de l'écart, dans l'ordre charge puis répétitions.

    Le `score_trend` de `Delta` n'est **pas** repris : c'est le seul champ de
    la primitive qui porte un jugement (`up` / `down`), et le contrat de cette
    tranche l'exclut. Le laisser passer réintroduirait par la petite porte
    l'appréciation que « pas de score de progrès » interdit.
    """
    if prog.delta is None:
        return []
    # Singulier pour ±1 SEULEMENT. `<= 1` mettait aussi l'écart nul au
    # singulier — « = rep » là où « = reps » est la forme naturelle.
    reps = prog.delta.reps_delta
    unit = "rep" if reps is not None and abs(reps) == 1 else "reps"
    parts = [
        _fmt_signed(prog.delta.weight_delta, "kg"),
        _fmt_signed(reps, unit),
    ]
    return [p for p in parts if p]


def build_progression_rows(facts: ProgressionFacts) -> list[dict[str, Any]]:
    """Les exercices comparables, du plus récemment pratiqué au moins.

    **Aucun tri par ampleur d'écart.** Classer par « plus gros progrès »
    reviendrait à décider que l'écart est un mérite ; l'ordre est celui de la
    pratique, qui n'affirme rien.
    """
    rows = []
    for p in facts.comparable:
        rows.append({
            "slug": p.slug,
            "name": p.name,
            "previous": format_performance(p.previous.weight, p.previous.reps),
            "latest": format_performance(p.latest.weight, p.latest.reps),
            "parts": format_delta_parts(p),
            # `TRAIN1-B` — le drill-down converge sur l'IDENTITÉ STABLE, pas
            # sur la dernière séance. Ouvrir la séance ne montrerait qu'un
            # point ; c'est la SUITE des occurrences qui explique l'écart, et
            # elle est désormais entière plutôt qu'éclatée par gabarit.
            "href": f"/exercise-history/{p.slug}",
            # Plusieurs gabarits = l'identité stable a réuni ce que la clé
            # héritée séparait. Rendu comme PROVENANCE, et COMPTÉ plutôt que
            # nommé : vu au rendu, deux noms de programme complets
            # (« Pull B — Dos épaisseur + Biceps · Push A — Pecs épaisseur +
            # Delts + Triceps ») débordaient sur deux lignes à 390 px et
            # prenaient plus de place que le fait qu'ils annotent. Le détail
            # par occurrence vit dans le drill-down, à sa place.
            "templates": p.templates,
            "crossed": len(p.templates) > 1,
            "provenance": (f"{len(p.templates)} programmes"
                           if len(p.templates) > 1 else None),
        })
    return rows


def build_awaiting_rows(facts: ProgressionFacts) -> list[dict[str, Any]]:
    """Pratiqués, mais rien à comparer **encore**.

    Ce n'est pas une absence de progrès, et le libellé doit l'empêcher : une
    seule occurrence, ou une occurrence sans série complétée.
    """
    rows = []
    for p in facts.awaiting:
        latest = p.latest
        rows.append({
            "slug": p.slug,
            "name": p.name,
            "latest": (format_performance(latest.weight, latest.reps)
                       if latest else NO_VALUE),
            "reason": ("une seule séance" if len(p.occurrences) < 2
                       else "aucune série notée"),
        })
    return rows


def build_progression_view(facts: ProgressionFacts) -> dict[str, Any]:
    """Le premier niveau, et ce qu'il replie."""
    rows = build_progression_rows(facts)
    return {
        "rows": rows[:TOP_N],
        "more": rows[TOP_N:],
        "awaiting": build_awaiting_rows(facts),
        "unresolved": facts.unresolved,
        "unresolved_names": facts.unresolved_names,
        # ⚠ `unresolved` COMPTE dans la présence de la section.
        #
        # La première écriture ne testait que `rows` et `awaiting` : un compte
        # dont TOUTES les occurrences portent un nom non rattachable rendait
        # une section absente, donc un compte de non-rattachés **invisible**.
        # C'est précisément ce que la règle interdit — taire la donnée
        # manquante fait passer une couverture nulle pour une absence de
        # pratique. Trouvé par un test migré, pas par relecture.
        "any": bool(rows) or bool(facts.awaiting) or facts.unresolved > 0,
    }


def build_cardio_view(facts: CardioFacts) -> dict[str, Any]:
    """La voie cardio. Une ligne par machine, jamais de total inter-machines.

    Additionner du rameur et du tapis produirait un nombre sans référent. La
    condition de comparabilité est la machine, donc l'unité d'affichage aussi.
    """
    lanes = []
    for lane in facts.lanes:
        latest = lane.latest
        if latest is None:
            continue
        lanes.append({
            "machine": lane.machine,
            "duration": (f"{latest.duration_min} min"
                         if latest.duration_min is not None else NO_VALUE),
            # `bpm` est un CONTEXTE : rendu à côté, jamais comparé, jamais
            # transformé en écart.
            "bpm": (f"{latest.bpm_avg} bpm"
                    if latest.bpm_avg is not None else None),
            "delta": _fmt_signed(lane.duration_delta, "min"),
            "href": f"/sessions/{latest.session_id}/done",
            "bouts": len(lane.bouts),
        })
    return {
        "lanes": lanes,
        "untyped": facts.untyped,
        "any": facts.any_data,
    }


__all__ = [
    "NO_VALUE",
    "build_awaiting_rows",
    "build_cardio_view",
    "build_progression_rows",
    "build_progression_view",
    "format_delta_parts",
    "format_performance",
]
