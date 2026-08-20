"""`UIV3_TARGETS_44_01` — taxonomie des cibles tactiles et sonde de mesure.

Ce module est **pur** : aucun import Playwright, aucun appel réseau, aucun
effet de bord. Il expose la taxonomie versionnée et le source de la sonde,
consommés par `scripts/target_size_audit.py`. Même séparation que
`visual_baseline_matrix.py` / `visual_baseline_capture.py`.

CE QUE 44 EST, ET CE QU'IL N'EST PAS
-------------------------------------
`AUREN_UIUX_V3_FOUNDATION_CONTRACT §3.1`. **Ne jamais rapporter 44 × 44 comme
une obligation WCAG AA** — c'est faux, et faux dans le sens qui expose :

    WCAG 2.2 SC 2.5.8  Target Size (Minimum)   24 × 24 px   ← SEUIL AA
    WCAG 2.2 SC 2.5.5  Target Size (Enhanced)  44 × 44 px     AAA
    Apple HIG                                  44 × 44 pt     recommandation
    AUREN                                      44 × 44 px     standard PRODUIT

`24 × 24` est le **seuil WCAG 2.2 niveau AA**, et rien de plus fort que cela.
Le W3C **ne produit pas les lois** : les obligations varient selon la
juridiction, et l'articulation juridique passe par des textes distincts —
en UE notamment `EN 301 549` et l'`European Accessibility Act`.

Décrire ce seuil comme un « plancher légal » revient à inscrire dans le  VOCAB-INTERDIT
dépôt une affirmation juridique que personne ici n'a qualité pour faire.
Une garde balaie cette formulation ; une ligne qui doit la citer porte le
token d'échappement.

AUREN vise 44 parce qu'on manipule l'interface en salle, une main occupée.
Pas parce qu'un texte réglementaire l'impose.

POURQUOI CLASSIFIER AVANT DE MESURER UN MANQUE
-----------------------------------------------
Le décompte historique est passé de **161 à 69** sur une seule mesure fraîche :
l'original comptait des `input[type=radio]` de 1 × 1 px cachés derrière leurs
labels. Personne ne les touche — le label reçoit le doigt. Appliquer
`min-height: 44px` à une liste non classifiée gonfle des objets jamais touchés
et manque ceux qui le sont.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

Category = Literal["A", "B", "C", "D", "E"]

#: Standard produit AUREN.
PRODUCT_THRESHOLD_PX: Final[int] = 44

#: **Seuil WCAG 2.2 SC 2.5.8, niveau AA.** Le W3C ne produit pas les lois ;
#: les obligations dépendent de la juridiction (`EN 301 549` / `EAA` en UE).
#: C'est un seuil de conformité technique, jamais une cible de conception —
#: et jamais à présenter comme une exigence juridique.
WCAG_AA_MIN_PX: Final[int] = 24

#: Les trois largeurs du contrat produit.
VIEWPORTS: Final[tuple[tuple[int, int], ...]] = ((360, 800), (390, 844), (430, 932))


@dataclass(frozen=True)
class TargetClass:
    """Une catégorie de la taxonomie `§3.2`."""

    key: Category
    name: str
    what: str
    requirement: str
    #: `True` si la catégorie exige d'atteindre `PRODUCT_THRESHOLD_PX`.
    must_reach_product_threshold: bool


TAXONOMY: Final[tuple[TargetClass, ...]] = (
    TargetClass(
        key="A",
        name="FREQUENT_SEQUENTIAL",
        what="bouton, segmented control, summary fréquent, navigation de "
             "séance, action de formulaire",
        requirement="44 × 44 requis",
        must_reach_product_threshold=True,
    ),
    TargetClass(
        key="B",
        name="SECONDARY_STANDALONE",
        what="lien d'historique, disclosure secondaire, action isolée",
        requirement="zone tactile 44 visée, sans chrome visible inutile",
        must_reach_product_threshold=True,
    ),
    TargetClass(
        key="C",
        name="INLINE",
        what="lien réellement intégré à une phrase",
        requirement="NE PAS gonfler — exception WCAG 2.5.8 explicite",
        must_reach_product_threshold=False,
    ),
    TargetClass(
        key="D",
        name="HIDDEN_IMPLEMENTATION",
        what="input de choix (radio/case) clippé derrière son label",
        requirement="mesurer le LABEL, jamais l'input caché",
        must_reach_product_threshold=True,
    ),
    TargetClass(
        key="E",
        name="USER_AGENT_OR_EDITABLE",
        what="textarea, champ texte/nombre dont la cible est l'aire éditable",
        requirement="mesurer le vrai rectangle interactif, pas une sous-partie",
        must_reach_product_threshold=True,
    ),
)

CATEGORIES: Final[dict[str, TargetClass]] = {t.key: t for t in TAXONOMY}


# ── La sonde ────────────────────────────────────────────────────────────────
#
# TROIS DÉFAUTS DE CET INSTRUMENT, TROUVÉS EN LE PLANTANT, ENCODÉS ICI
# ---------------------------------------------------------------------
# Aucun n'aurait été visible en relisant le code. Tous les trois auraient
# produit un inventaire faux et crédible.
#
#   1. `elementFromPoint` travaille en coordonnées VIEWPORT. Sans
#      `scrollIntoView`, tout ce qui vit sous le pli rendait `hit = 0 %` — y
#      compris un lien de 202 px manifestement touchable. Et les points sautés
#      étaient comptés comme « sondés ».
#
#   2. La condition d'acceptation incluait `at.contains(el)`. Comme le `<body>`
#      contient tout, CHAQUE point comptait comme touché : un bouton de 30 px
#      était déclaré conforme. Un ancêtre qui reçoit le doigt ne rend pas
#      l'élément touchable à cet endroit.
#
#   3. Un `<label>` au-dessus d'un champ nombre focalise le champ, mais n'est
#      pas la cible opératoire — l'aire éditable l'est. Les compter en `D`
#      exigeait 44 px sur du texte statique : 19 étiquettes de `/profile`, soit
#      l'erreur du 161 sous une autre forme.
#
# La sonde mesure la **zone qui reçoit réellement le doigt**, pas le rectangle
# CSS. Un lien de 14 px dont un `::after` absolu étend la zone à 44 est
# CONFORME au `§3.3`, et `getBoundingClientRect()` seul le déclarerait fautif.

PROBE_JS: Final[str] = r"""
(cfg) => {
  const T = cfg.threshold;
  const SEL = [
    'a[href]', 'button', 'input', 'select', 'textarea', 'summary',
    '[role="button"]', '[role="link"]', '[role="tab"]', '[onclick]', 'label',
  ].join(',');

  const norm = (s) => (s || '').replace(/\s+/g, ' ').trim();
  const rectOf = (el) => el.getBoundingClientRect();

  const ownedInput = (label) => {
    if (label.tagName !== 'LABEL') return null;
    const forId = label.getAttribute('for');
    if (forId) return document.getElementById(forId);
    return label.querySelector('input, select, textarea');
  };

  /* Le lien vit-il DANS une phrase ? Le bloc porteur contient du texte
     substantiel en plus du lien, et le lien n'est pas mis en page comme un
     bloc. C'est l'exception « inline » de WCAG 2.5.8. */
  const isInline = (el) => {
    if (el.tagName !== 'A' && el.getAttribute('role') !== 'link') return false;
    const disp = getComputedStyle(el).display;
    if (disp !== 'inline' && disp !== 'inline-block') return false;
    let block = el.parentElement;
    while (block && getComputedStyle(block).display === 'inline') {
      block = block.parentElement;
    }
    if (!block) return false;
    const own = norm(el.textContent).length;
    const around = norm(block.textContent).length - own;
    const siblings = block.querySelectorAll('a[href]').length;
    return around >= 30 && siblings <= 2;
  };

  /* Défauts 1 et 2 : voir le commentaire Python au-dessus. */
  const effectiveHit = (el) => {
    el.scrollIntoView({ block: 'center', inline: 'center', behavior: 'instant' });
    let r = rectOf(el);
    /* Un `skip-link` est hors écran tant qu'il n'a pas le focus — c'est son
       contrat. Le mesurer non focalisé, c'est mesurer l'état dans lequel
       personne ne l'actionne. */
    if (r.bottom < 0 || r.top > innerHeight || r.right < 0 || r.left > innerWidth) {
      try { el.focus({ preventScroll: false }); } catch (e) { /* non focusable */ }
      r = rectOf(el);
    }
    const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    const half = T / 2 - 1;
    const pts = [
      [cx, cy], [cx - half, cy], [cx + half, cy],
      [cx, cy - half], [cx, cy + half],
    ];
    let hits = 0, probed = 0;
    for (const [x, y] of pts) {
      if (x < 0 || y < 0 || x > innerWidth || y > innerHeight) continue;
      probed++;
      const at = document.elementFromPoint(x, y);
      if (at && (at === el || el.contains(at))) hits++;
    }
    return {
      probed, hits,
      full: probed === pts.length && hits === pts.length,
      partial: probed < pts.length,
    };
  };

  /* WCAG 2.2 SC 2.5.8 — exception d'ESPACEMENT. Une cible sous 24 × 24 reste
     CONFORME AA si un cercle de 24 px de diamètre centré sur elle n'en croise
     aucun autre. Dire « non conforme » sans tester ça, c'est SUR-déclarer une
     violation — la faute symétrique de sur-déclarer une conformité. */
  const spacingOK = (el, others) => {
    const r = rectOf(el);
    const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    for (const o of others) {
      if (o === el) continue;
      const q = rectOf(o);
      if (q.width === 0 && q.height === 0) continue;
      if (Math.hypot(cx - (q.left + q.width / 2),
                     cy - (q.top + q.height / 2)) < cfg.wcagFloor) return false;
    }
    return true;
  };

  const path = (el) => {
    const bits = [];
    let n = el;
    while (n && n.nodeType === 1 && bits.length < 4) {
      let s = n.tagName.toLowerCase();
      if (n.id) { bits.unshift(s + '#' + n.id); break; }
      const cls = (n.getAttribute('class') || '').split(/\s+/).filter(Boolean).slice(0, 2);
      if (cls.length) s += '.' + cls.join('.');
      bits.unshift(s);
      n = n.parentElement;
    }
    return bits.join(' > ');
  };

  const visible = (n) => {
    if (n.closest('details:not([open])')) return false;
    const s = getComputedStyle(n);
    return s.display !== 'none' && s.visibility !== 'hidden';
  };

  const universe = [...document.querySelectorAll(
    'a[href], button, input, select, textarea, summary, [role="button"]')]
    .filter((n) => {
      if (!visible(n)) return false;
      const q = n.getBoundingClientRect();
      return q.width > 2 && q.height > 2;
    });

  const seen = new Set();
  const rows = [];

  for (const el of document.querySelectorAll(SEL)) {
    /* Un `<details>` fermé ne rend pas de géométrie fiable : Chromium y
       verrouille la mise en page. 23 faux débordements ont eu cette cause. */
    if (!visible(el)) continue;

    let target = el, category = null, note = '', boundary = false;
    const tag = el.tagName;

    if (tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') {
      const lbl = el.id
        ? document.querySelector('label[for="' + CSS.escape(el.id) + '"]')
        : el.closest('label');
      /* Défaut 3 : radio/case ⇒ le label EST la cible. Champ texte ⇒ l'aire
         éditable est la cible, son étiquette n'est qu'une commodité. */
      if (lbl && (el.type === 'radio' || el.type === 'checkbox')) {
        target = lbl; category = 'D';
        note = 'choix : l’input est clippé, le label reçoit le doigt';
      } else {
        category = 'E';
        note = 'aire éditable — la cible est le champ, pas son étiquette';
      }
    } else if (tag === 'LABEL') {
      const owned = ownedInput(el);
      if (!owned) continue;
      const t = (owned.type || '').toLowerCase();
      if (t !== 'radio' && t !== 'checkbox') continue;
      category = 'D';
      note = 'choix : l’input est clippé, le label reçoit le doigt';
    } else if (isInline(el)) {
      category = 'C';
      note = 'lien intégré à une phrase — exception WCAG 2.5.8';
    } else if (
      tag === 'BUTTON'
      || el.getAttribute('role') === 'button'
      || el.closest('.dock, .console, .session-head, .ex-nav, nav, .app-nav, [role="tablist"]')
    ) {
      category = 'A';
      note = 'commande / navigation';
    } else if (tag === 'SUMMARY') {
      category = 'A';
      note = 'disclosure — fréquence à confirmer';
      boundary = true;
    } else {
      category = 'B';
      note = 'action isolée';
      boundary = tag === 'A';
    }

    if (seen.has(target)) continue;
    seen.add(target);

    const r = rectOf(target);
    if (r.width === 0 && r.height === 0) continue;
    const w = Math.round(r.width * 10) / 10;
    const h = Math.round(r.height * 10) / 10;
    const eff = effectiveHit(target);

    rows.push({
      category, boundary, note,
      tag: target.tagName.toLowerCase(),
      path: path(target),
      text: norm(target.textContent).slice(0, 46),
      w, h, min: Math.min(w, h),
      below_product: w < T || h < T,
      below_wcag_size: w < cfg.wcagFloor || h < cfg.wcagFloor,
      wcag_spacing_ok: spacingOK(target, universe),
      hit_full: eff.full,
      hit_partial: eff.partial,
      hit_probed: eff.probed,
      hit_ratio: eff.probed ? Math.round(eff.hits / eff.probed * 100) : null,
      y: Math.round(r.top + scrollY),
    });
  }
  return rows;
}
"""


def is_violation(row: dict) -> bool:
    """Le standard PRODUIT AUREN est-il manqué ?

    Une cible dont la **zone tactile effective** atteint le seuil est conforme,
    quelle que soit la taille de son chrome visible (`§3.3`).
    """
    cat = CATEGORIES.get(row.get("category", ""))
    if cat is None or not cat.must_reach_product_threshold:
        return False
    return bool(row.get("below_product")) and not row.get("hit_full")


def is_wcag_aa_failure(row: dict) -> bool:
    """La conformité **légale** AA est-elle manquée ?

    Trois conditions cumulatives : sous 24 px, exception d'espacement
    inapplicable, et la catégorie n'est pas elle-même une exception de
    `2.5.8` (`C` inline, `E` contrôle du user-agent).
    """
    if row.get("category") not in ("A", "B", "D"):
        return False
    if not row.get("below_wcag_size") or row.get("hit_full"):
        return False
    return not row.get("wcag_spacing_ok")
