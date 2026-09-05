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


def format_trace(prog: ExerciseProgression) -> list[str]:
    """Les charges des occurrences RETENUES, du plus ancien au plus récent.

    `KEEP_OCCURRENCES` en retient six ; `latest` et `previous` n'en lisaient
    que **deux**. Les quatre autres étaient calculées, puis jetées avant la
    vue — la même perte que `MaterializationReadiness` infligeait aux séances
    du plan hebdomadaire.

    Ce que la trace ajoute n'est pas décoratif. `30 · 29 · 26 · 25 · 24 · 23`
    et `−1 kg` décrivent la même dernière séance ; seule la première dit qu'il
    s'agit d'une décrue **régulière** plutôt que d'un accident. L'écart entre
    26 et 29 dit lui aussi quelque chose : l'exercice n'a pas été pratiqué
    entre les deux.

    **Aucun jugement n'est ajouté** : ce sont les charges, dans l'ordre où
    elles ont été notées. Pas de seuil, pas de tendance nommée, pas de couleur
    de verdict — les trois interdits du contrat tiennent.
    """
    return [_fmt_weight(o.weight) for o in reversed(prog.occurrences)]


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
            # ── Les grandeurs SÉPARÉES, pour le relevé souverain.
            #
            # `previous` et `latest` restent des chaînes soudées (`70 × 10`) :
            # la liste les lit ainsi, et rien ne le change. Le relevé, lui,
            # a deux puits — charge et répétitions — et ne peut pas découper
            # une chaîne déjà formatée sans refaire le formatage à l'envers.
            "latest_weight": _fmt_weight(p.latest.weight),
            "latest_reps": (str(p.latest.reps) if p.latest.reps is not None
                            else NO_VALUE),
            "previous_weight": _fmt_weight(p.previous.weight),
            "previous_reps": (str(p.previous.reps)
                              if p.previous.reps is not None else NO_VALUE),
            "delta_weight": _fmt_signed(p.delta.weight_delta, "kg"),
            "delta_reps": _fmt_signed(
                p.delta.reps_delta,
                "rep" if (p.delta.reps_delta is not None
                          and abs(p.delta.reps_delta) == 1) else "reps",
            ),
            "trace": format_trace(p),
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
    """Le premier niveau, ce qu'il PROMEUT, et ce qu'il replie.

    `lead` — LE RELEVÉ SOUVERAIN, ET POURQUOI IL EST LÉGITIME.

    Le patron d'instrument (`AUREN_VISUAL_BACKBONE §4`, validé sur rendu le
    2026-09-04) veut un readout souverain : une valeur, très grande, comprise
    « sans lire ». L'écran n'en avait pas — mesuré, ses cinq plus grosses
    typographies étaient des COMPTAGES (« 3 zones », « 3 », « 10 », « 100 % »,
    « 4 ») entre 28 et 34 px, tandis que la progression elle-même tenait en
    13 px et son écart en 11 px, le plus petit texte de la page.

    **`lead` n'est pas un classement.** C'est `rows[0]`, et `rows` est déjà
    trié par la pratique, du plus récemment pratiqué au moins. La docstring de
    `build_progression_rows` interdit explicitement tout tri par ampleur
    d'écart — « classer par plus gros progrès reviendrait à décider que
    l'écart est un mérite ». Promouvoir le plus RÉCENT ne décide rien : c'est
    la chronologie, qui n'affirme pas.

    Élire un « plus gros progrès » aurait de toute façon exigé de comparer des
    kilos entre exercices — 6 kg au tirage vertical contre 1 kg au développé
    haltères — c'est-à-dire exactement l'addition sans référent que la voie
    cardio refuse déjà entre deux machines.

    `lead` sort de `rows` : le rendre deux fois ferait passer une promotion
    pour une duplication.
    """
    rows = build_progression_rows(facts)
    lead = rows[0] if rows else None
    return {
        "lead": lead,
        "rows": rows[1:TOP_N],
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
    "format_trace",
]
