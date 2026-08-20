"""`UIV3_VISUAL_BASELINE_01` — couche B : le manifeste de géométrie.

POURQUOI UN GOLDEN STATE N'EST PAS UN PNG
------------------------------------------
Décision opérateur du 2026-08-19 : chaque état golden porte **deux couches
synchronisées** — une capture, et un manifeste JSON du **même** état. Une PR
échoue si les pixels changent **ou** si la géométrie dérive.

Ce n'est pas une précaution théorique. Deux défauts de cette tranche étaient
**invisibles à l'œil et invisibles au CSS** :

  · un `id` dupliqué en état `CORRECTION` (phase 2) — deux séries rendues au
    même endroit, mêmes `name` de champs masqués. Aucun pixel ne bouge ;
  · `TERMINER LA SÉANCE` rabotée de 56 à 44 px par une règle d'accessibilité
    plus spécifique chargée plus tard. Une garde lisant les noms de sélecteurs
    n'a rien vu : la collision était dans la CASCADE, pas dans le texte.

Le second a été trouvé en comparant les hauteurs élément par élément entre
deux serveurs. C'est cette comparaison qui devient un instrument versionné.

MODULE PUR — aucun import Playwright, aucun appel réseau, aucun effet de bord
à l'import. Même séparation que `visual_baseline_matrix.py`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final

#: Champs minimaux exigés par l'opérateur pour tout état golden.
#: Élargir cette liste est un geste conscient : chaque champ est une propriété
#: qu'une PR peut désormais casser bruyamment.
REQUIRED_FIELDS: Final[tuple[str, ...]] = (
    "viewport",
    "document_width",
    "document_height",
    "hard_overflow_count",
    "target_below_44_count",
    "dominant_action_count",
    "open_disclosure_count",
    "sticky_layer_count",
    "primary_action_y",
    "active_instrument_y",
    "duplicate_id_count",
)


# ── Statut de surface — décision opérateur du 2026-08-20 ────────────────────
#
# UNE BASELINE TRANSFORME CE QU'ELLE CAPTURE EN CONTRAT. Appliquée sans
# discernement, elle **gèle la dette en la rendant contractuelle**.
#
# La fermeture 44 px a rendu le risque concret : elle améliore la qualité
# MÉCANIQUE de surfaces dont le MODÈLE D'INTERACTION est hérité. Agrandir
# proprement les zones tactiles d'un formulaire Profil qui restera pénible à
# remplir ne transforme pas ce formulaire en bonne UX.
#
#   SOVEREIGN     Design Lab + dogfood + validation humaine.
#                 Une dérive est une RÉGRESSION.
#   TRANSITIONAL  capture versionnable comme ARCHIVE de départ.
#                 Une refonte structurelle N'EST PAS une régression.
#   UTILITY       garde mécanique et accessibilité seulement ; la baseline
#                 ne prétend rien sur leur direction artistique.

SOVEREIGN: Final[str] = "sovereign"
TRANSITIONAL: Final[str] = "transitional"
UTILITY: Final[str] = "utility"

SURFACE_STATUS: Final[dict[str, str]] = {
    "home": SOVEREIGN,
    "session-active": SOVEREIGN,
    "session-done": SOVEREIGN,
    "profile": TRANSITIONAL,
    "library": TRANSITIONAL,
    "progress": TRANSITIONAL,
    "dashboard": TRANSITIONAL,
    "history": TRANSITIONAL,
    "login": UTILITY,
    "register": UTILITY,
    "forgot-password": UTILITY,
}

#: Ce qu'une baseline a le droit de faire échouer, par statut.
#: `pixel` gèle l'apparence ; `architecture` gèle la structure d'information.
#: Une surface `TRANSITIONAL` n'admet QUE les gardes mécaniques — c'est la
#: garantie que sa refonte future ne sera pas traitée comme une régression.
ALLOWED_GATES: Final[dict[str, frozenset[str]]] = {
    SOVEREIGN: frozenset({"pixel", "architecture", "mechanical"}),
    TRANSITIONAL: frozenset({"mechanical"}),
    UTILITY: frozenset({"mechanical"}),
}

#: Une capture de surface `TRANSITIONAL` est versionnable sous ce drapeau :
#: preuve de l'état de départ, jamais design à préserver.
LEGACY_REFERENCE_FLAG: Final[str] = "legacy_reference"


def gate_is_allowed(surface: str, gate: str) -> bool:
    """Cette garde a-t-elle le droit de faire échouer une PR sur cette surface ?

    Une surface inconnue est traitée en `TRANSITIONAL` — le statut le plus
    conservateur du point de vue de la refonte. Promouvoir une surface en
    `SOVEREIGN` doit être un geste délibéré, jamais un défaut d'inscription.
    """
    status = SURFACE_STATUS.get(surface, TRANSITIONAL)
    return gate in ALLOWED_GATES[status]


@dataclass(frozen=True)
class EnvironmentStamp:
    """L'environnement dans lequel une baseline fait foi.

    Comparer un Chromium macOS à un Chromium Linux CI teste la rastérisation,
    pas le design. Les golden officielles sont produites dans l'environnement
    canonique ; les captures locales sont **informatives**.
    """

    browser: str
    browser_version: str
    viewport: tuple[int, int]
    device_scale_factor: int
    locale: str
    timezone: str
    color_scheme: str
    reduced_motion: str
    font_stack: str
    fixture: str
    db_signature: str


#: Le manifeste mesure ce que les pixels ne disent pas. Chaque expression est
#: évaluée dans la page ; aucune ne dépend d'un état interne du harnais.
MANIFEST_JS: Final[str] = r"""
() => {
  const norm = (s) => (s || '').replace(/\s+/g, ' ').trim();

  /* Un débordement DUR, pas un simple dépassement de contenu : la piste
     déborde ET rien ne la contient ET aucune ellipse ne le rattrape. Un
     élément dans un `<details>` fermé est exclu — Chromium y verrouille la
     mise en page et rendait 23 faux positifs. */
  let hardOverflow = 0;
  for (const el of document.querySelectorAll('*')) {
    if (el.closest('details:not([open])')) continue;
    if (el.scrollWidth <= el.clientWidth) continue;
    const s = getComputedStyle(el);
    if (s.overflowX !== 'visible') continue;
    if (s.textOverflow === 'ellipsis') continue;
    hardOverflow++;
  }

  let sticky = 0;
  for (const el of document.querySelectorAll('*')) {
    const p = getComputedStyle(el).position;
    if (p === 'sticky' || p === 'fixed') sticky++;
  }

  const ids = [...document.querySelectorAll('[id]')].map((n) => n.id);
  const dupes = ids.length - new Set(ids).size;

  const topOf = (sel) => {
    const el = document.querySelector(sel);
    return el ? Math.round(el.getBoundingClientRect().top + scrollY) : null;
  };

  return {
    viewport: `${innerWidth}x${innerHeight}`,
    document_width: Math.round(document.documentElement.scrollWidth),
    document_height: Math.round(document.documentElement.scrollHeight),
    hard_overflow_count: hardOverflow,
    dominant_action_count: document.querySelectorAll('.dock__cmd').length,
    open_disclosure_count: document.querySelectorAll('details[open]').length,
    sticky_layer_count: sticky,
    duplicate_id_count: dupes,
    primary_action_y: topOf('.dock__cmd') ?? topOf('.btn--primary'),
    active_instrument_y:
      topOf('.session-focus__card--active .setline--current')
      ?? topOf('.session-focus__card--active'),
    /* `target_below_44_count` est renseigné par `target_size_taxonomy`, qui
       sait distinguer une zone tactile étendue d'un rectangle nu. Le laisser
       à `null` ici plutôt que de le recalculer à moitié : un décompte
       approximatif dans un manifeste de non-régression est pire qu'absent. */
    target_below_44_count: null,
    _element_heights: (() => {
      const out = {};
      let i = 0;
      const SEL = 'a[href], button, input, select, textarea, summary, label';
      for (const el of document.querySelectorAll(SEL)) {
        if (el.closest('details:not([open])')) continue;
        const s = getComputedStyle(el);
        if (s.display === 'none' || s.visibility === 'hidden') continue;
        const r = el.getBoundingClientRect();
        if (r.width === 0 && r.height === 0) continue;
        const cls = (el.getAttribute('class') || '-').split(/\s+/).slice(0, 2).join('.');
        out[`${i++}|${el.tagName.toLowerCase()}.${cls}|${norm(el.textContent).slice(0, 30)}`]
          = Math.round(r.height * 10) / 10;
      }
      return out;
    })(),
  };
}
"""


def missing_fields(manifest: dict) -> list[str]:
    """Les champs exigés absents du manifeste.

    Un manifeste incomplet qui passe silencieusement, c'est une baseline qui
    a l'air de garder plus qu'elle ne garde.
    """
    return [f for f in REQUIRED_FIELDS if f not in manifest]


def shrunk_elements(before: dict, after: dict, *, tolerance: float = 0.5
                    ) -> list[tuple[str, float, float]]:
    """Ce qui a RÉTRÉCI entre deux manifestes.

    Une passe de fermeture d'accessibilité ne rapetisse rien : `min-height`
    ne peut que relever un plancher. Tout rétrécissement vient donc d'un autre
    effet — `display`, une collision de spécificité — et doit être justifié
    explicitement, jamais découvert après coup.

    C'est la fonction qui a attrapé `TERMINER LA SÉANCE` à 56 → 44.
    """
    b = before.get("_element_heights", {})
    a = after.get("_element_heights", {})
    out = []
    for key, h0 in b.items():
        h1 = a.get(key)
        if h1 is not None and h1 < h0 - tolerance:
            out.append((key, h0, h1))
    return sorted(out, key=lambda t: t[2] - t[1])


def drifted_fields(before: dict, after: dict) -> dict[str, tuple]:
    """Les champs du manifeste qui ont changé, hors hauteurs élémentaires.

    C'est la couche qui attrape ce qu'une comparaison de pixels manque :
    un `id` dupliqué, une couche collante de plus, une disclosure ouverte
    par accident.
    """
    return {
        f: (before.get(f), after.get(f))
        for f in REQUIRED_FIELDS
        if before.get(f) != after.get(f)
    }
