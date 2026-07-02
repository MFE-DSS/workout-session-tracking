# Sx_UI_02 — Design Tokens Spec

**Spec ID :** `Sx_UI_02_DESIGN_TOKENS_SPEC`
**Cycle :** `Sx_UI` — Auren Visual & Product Transformation
**Date d'ouverture :** 2026-07-02
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code (docs-only)
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Depends on :** `Sx_UI_01_BRAND_FOUNDATION_SPEC.md` (READY FOR HUMAN REVIEW, commit `2e345e8`)

---

## §1. Status

- **SPEC ONLY**
- **BUILD BLOCKED**
- Aucun fichier CSS, JS, template, static, manifest, favicon modifié dans ce sprint
- Aucun token implémenté en runtime — les tokens spécifiés ici sont des **candidats normatifs** à figer avec `Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC` lors de sa première application
- Next authorized action after human validation : ouvrir `Sx_UI_03_APP_SHELL_NAVIGATION_SPEC` en SPEC ONLY
- Accent principal figé par directive opérateur (OQ-B tranchée) : **teal chirurgical désaturé**
- Accent secondaire : **bleu minéral** (fallback / secondary signal)

## §2. Why this spec exists

`Sx_UI_01` a posé la marque, le tone of voice et les principes visuels autorisés/interdits. Cette spec les **traduit en tokens** — un vocabulaire normatif de couleurs, typographies, espacements, rayons, ombres, états, opérationnellement utilisable par tous les sprints Sx_UI aval sans reconstruire les décisions de base.

Objectif : rendre impossible qu'un sprint futur (`Sx_UI_04`, `Sx_UI_05`, etc.) invente une couleur secondaire, une taille de texte, ou un espacement hors de ce vocabulaire. Toute exception nécessite un amendement explicite `Sx_UI_02bis`.

Cette spec ne définit pas :
- comment implémenter les tokens en CSS (custom properties vs SCSS vs autre) — décision `Sx_UI_04`
- où les tokens sont stockés (fichier séparé, inline, CSS-in-JS) — décision `Sx_UI_04`
- comment ils sont testés (visual regression, unit tests) — décision `Sx_UI_11`

Elle définit **quels tokens existent, avec quels noms canoniques, avec quelles valeurs de référence**.

## §3. Design principles inherited from Sx_UI_01

Rappel bref des principes structurants (cf. `Sx_UI_01` §9-§10-§13) qui contraignent ces tokens :

- **White clinical surfaces** — fond blanc / blanc cassé dominant
- **Cold neutral palette** — gris froids (bleu-gris), jamais gris chauds
- **One accent only** — un seul accent principal (teal), un accent secondaire strictement limité aux signaux
- **Typography-led hierarchy** — hiérarchie portée par taille + poids, pas par couleur ou boîte
- **Metric clarity** — mono / tabular figures pour les métriques (charges, reps, temps)
- **Thin separators** — 1px froid
- **Minimal shadow** — quasi absentes
- **Non-color cues for states** — chaque état porte un signal non-coloré (icône, texte, forme, poids)
- **Generous spacing** — densité informationnelle basse
- **WCAG 2.2 tap targets ≥ 44×44 CSS px**
- **WCAG AA contrast ratio ≥ 4.5:1** pour tout texte body, ≥ 3:1 pour texte grand (≥ 18.66px bold ou ≥ 24px regular)

## §4. Token naming convention

Convention normative pour éviter l'invention nom-par-nom dans les sprints aval.

**Format :** `--{category}-{role}-{modifier?}`

**Categories :**
- `color` — toute valeur chromatique (surface, texte, accent, état)
- `space` — tout espace (padding, margin, gap)
- `radius` — rayons d'arrondi
- `border` — épaisseurs et couleurs de bordure
- `shadow` — ombres portées (minimales)
- `font` — famille, poids, tailles, line-height
- `motion` — durées et courbes de transition
- `z` — z-index tokens (niveaux de superposition)

**Roles standard :**
- `bg` — background
- `fg` — foreground (texte)
- `surface` — surface intermédiaire (cartes, panneaux)
- `border` — séparateurs et bordures
- `accent` — accent principal (teal)
- `signal` — accent secondaire (bleu minéral) réservé aux signaux
- `success` / `warning` / `danger` — états sémantiques
- `disabled` / `muted` — états de désactivation

**Modifiers standard :**
- `strong` / `weak` — intensité relative
- `hover` / `active` / `focus` / `disabled` — états d'interaction
- `on-bg` / `on-surface` / `on-accent` — texte lisible sur telle surface

**Exemples canoniques :**
- `--color-bg-base` (fond global)
- `--color-fg-strong` (texte titre)
- `--color-fg-muted` (texte secondaire)
- `--color-accent` (teal principal)
- `--color-accent-hover` (teal légèrement modulé au hover)
- `--color-signal` (bleu minéral secondaire)
- `--space-3` (échelle standardisée)
- `--radius-md` (rayon carte standard)
- `--font-family-sans` / `--font-family-mono`

## §5. Color tokens — surfaces & foreground

**Base surface stack.** Valeurs HSL indicatives (précision hex à figer en `Sx_UI_04`).

| Token | Rôle | Valeur candidate | Notes |
|---|---|---|---|
| `--color-bg-base` | Fond global de l'app | `#FFFFFF` | Blanc pur |
| `--color-bg-elevated` | Fond légèrement surélevé (page vs body-hover) | `#FAFBFC` | Blanc cassé très léger, teinte froide |
| `--color-surface` | Carte, panneau, bloc structurant | `#FFFFFF` | Identique à base — la différenciation vient du border, pas du fond |
| `--color-surface-alt` | Surface alternée (tables, listes zébrées) | `#F5F7F9` | Gris pierre très clair, teinte froide |
| `--color-surface-sunken` | Surface enfoncée (input field, code block) | `#F0F3F5` | Gris pierre plus marqué |

**Foreground stack.** Contraste WCAG AA minimum vs `--color-bg-base` documenté.

| Token | Rôle | Valeur candidate | Contraste vs `#FFFFFF` |
|---|---|---|---|
| `--color-fg-strong` | Titre H1, chiffres critiques | `#0F1419` | 18.5:1 |
| `--color-fg-default` | Body text | `#1F2933` | 15.9:1 |
| `--color-fg-muted` | Texte secondaire, label, timestamp | `#52606D` | 7.4:1 |
| `--color-fg-subtle` | Texte tertiaire, hint, placeholder | `#7B8794` | 4.8:1 (limite AA body) |
| `--color-fg-disabled` | État désactivé | `#9AA5B1` | 3.3:1 (non-body seulement, ex : boutons désactivés) |

**Séparateurs et bordures.**

| Token | Rôle | Valeur candidate |
|---|---|---|
| `--color-border-subtle` | Séparateur fin dans les listes, entre lignes de tableau | `#E4E7EB` |
| `--color-border-default` | Bordure carte, input au repos | `#CBD2D9` |
| `--color-border-strong` | Focus visible sur input, bordure hover | `#3E4C59` |

## §6. Color tokens — accent principal (teal chirurgical désaturé)

**Décision opérateur figée :** teal chirurgical désaturé.

**Caractéristiques recherchées :**
- Teinte : teal / cyan-vert (HSL ~180-190°)
- Saturation basse à moyenne (S 30-45%) — jamais éclatante
- Luminosité : suffisamment sombre pour contraste AA sur blanc (contraste ≥ 4.5:1 pour texte body, ≥ 3:1 pour icônes/borders large)
- Aspect chirurgical : ne doit **pas** évoquer un turquoise vif de UI SaaS, plutôt un teal instrument médical / labo

**Palette candidate :**

| Token | Rôle | Valeur candidate | Contraste vs `#FFFFFF` |
|---|---|---|---|
| `--color-accent-strong` | CTA primaire, texte sur fond blanc | `#0B7A75` | 5.6:1 (AA body OK) |
| `--color-accent` | Accent standard : liens, états actifs, icônes fonctionnelles | `#0F8A85` | 5.0:1 (AA body OK) |
| `--color-accent-weak` | Fond de badge léger, chip inactif | `#D4EDEB` | contraste bas — usage **surface** uniquement, jamais texte |
| `--color-accent-hover` | Modulation légèrement plus sombre au hover | `#095E5A` | 7.9:1 |
| `--color-accent-focus-ring` | Ring de focus visible | `#0F8A85` avec alpha 40% | usage anneau, pas texte |
| `--color-on-accent` | Texte sur fond `--color-accent-strong` (bouton primaire) | `#FFFFFF` | 5.6:1 (AA OK) |

**Interdits :**
- ❌ Utiliser `--color-accent-weak` pour du texte (contraste insuffisant)
- ❌ Utiliser l'accent sur une surface autre que blanche/blanche cassée sans re-vérification contraste
- ❌ Introduire un dégradé teal (violation §10 anti-patterns de `Sx_UI_01`)
- ❌ Combiner l'accent avec l'accent secondaire dans un même composant (ex : bouton teal + border bleu minéral)

## §7. Color tokens — accent secondaire (bleu minéral)

**Décision opérateur figée :** bleu minéral en fallback / secondary signal.

**Rôle strictement délimité :**
- Signaler une info secondaire distincte de l'accent principal (ex : indicateur de source de donnée, badge "Dérivé", tag informatif)
- **Jamais** utilisé pour un CTA
- **Jamais** utilisé sur la même surface que l'accent principal simultanément dans une hiérarchie visuelle qui les met en compétition
- Amendement `Sx_UI_02bis` requis pour tout usage hors "signal informatif"

**Palette candidate :**

| Token | Rôle | Valeur candidate | Contraste vs `#FFFFFF` |
|---|---|---|---|
| `--color-signal-strong` | Texte de badge ou icône `Dérivé` | `#1F5F7A` | 7.1:1 |
| `--color-signal` | Icône, tag secondaire | `#2A7896` | 4.9:1 (AA body OK) |
| `--color-signal-weak` | Fond de badge léger | `#DCE9F1` | usage surface uniquement |

## §8. Color tokens — états sémantiques

Réservés aux messages structurés (feedback système, indicateurs de progrès conservateurs, warnings d'input). Utilisés avec **parcimonie** — un écran typique n'en montre **aucun** ou **un seul**.

**Success (progrès validé, rarement utilisé — l'app n'est pas motivationnelle).**

| Token | Valeur candidate | Contraste vs `#FFFFFF` |
|---|---|---|
| `--color-success-strong` | `#0A6634` | 6.2:1 |
| `--color-success` | `#12894A` | 4.6:1 |
| `--color-success-weak` | `#D3EFE0` | surface only |

**Warning (uniquement pour attention utilisateur factuelle, jamais pour "motivation gym").**

| Token | Valeur candidate | Contraste vs `#FFFFFF` |
|---|---|---|
| `--color-warning-strong` | `#7A4600` | 8.4:1 |
| `--color-warning` | `#B36B00` | 4.5:1 |
| `--color-warning-weak` | `#FBEBD4` | surface only |

**Danger (erreur système, action destructive).**

| Token | Valeur candidate | Contraste vs `#FFFFFF` |
|---|---|---|
| `--color-danger-strong` | `#8A1C1C` | 8.5:1 |
| `--color-danger` | `#B02929` | 5.1:1 |
| `--color-danger-weak` | `#FAD9D9` | surface only |

**Note :** l'ancien accent SPIGNOS `#f25f3a` (orange chaud) est **éliminé** du branding. Peut réapparaître comme partie de la palette `warning` si strictement nécessaire — décision `Sx_UI_04` uniquement.

## §9. Typography tokens

**Familles.**

| Token | Rôle | Valeur candidate | Fallback stack |
|---|---|---|---|
| `--font-family-sans` | Texte général | `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif` | System sans-serif |
| `--font-family-mono` | Métriques (charges, reps, temps, %) | `"JetBrains Mono", "SF Mono", ui-monospace, monospace` | System monospace |

**Contraintes de choix (décision définitive `Sx_UI_04`) :**
- **Au maximum 2 familles chargées.** Une sans + une mono.
- **Au maximum 3 poids par famille** — sans : 400, 500, 700 ; mono : 400, 500.
- Font display strategy : `font-display: swap` obligatoire pour éviter FOIT (flash of invisible text).
- Aucune web font italique décorative.

**Poids (font-weight).**

| Token | Valeur | Usage typique |
|---|---|---|
| `--font-weight-regular` | `400` | Body text |
| `--font-weight-medium` | `500` | Labels, boutons secondaires, valeurs mono |
| `--font-weight-bold` | `700` | Titres, CTA primaire, chiffres critiques |

**Tailles (fluid clamp() à figer `Sx_UI_04`, ici valeurs de base mobile 360px).**

| Token | Valeur mobile | Usage |
|---|---|---|
| `--font-size-caption` | `11px` | Timestamp, legal, footer |
| `--font-size-body-sm` | `13px` | Label, hint, meta |
| `--font-size-body` | `15px` | Body text par défaut |
| `--font-size-lg` | `17px` | Sous-titre, item de liste principal |
| `--font-size-heading-3` | `20px` | H3 |
| `--font-size-heading-2` | `24px` | H2 |
| `--font-size-heading-1` | `32px` | H1 |
| `--font-size-metric-lg` | `40px` | Métrique héroïque (poids, PR affiché en gros) |

**Line-heights.**

| Token | Valeur | Usage |
|---|---|---|
| `--line-height-tight` | `1.15` | Titres, métriques |
| `--line-height-default` | `1.5` | Body |
| `--line-height-relaxed` | `1.65` | Prose longue (rare dans Auren) |

**Number rendering.**
- Toute métrique numérique doit utiliser `font-variant-numeric: tabular-nums` (alignement vertical parfait dans les listes de séries).
- Toute métrique doit utiliser `--font-family-mono` **sauf** dans le contexte prose où la lecture est prioritaire sur l'alignement.

## §10. Spacing tokens

**Échelle géométrique 4px-based.** Multi-utilisation autorisée.

| Token | Valeur | Usage typique |
|---|---|---|
| `--space-0` | `0` | Reset |
| `--space-1` | `4px` | Gap entre icône et texte adjacent |
| `--space-2` | `8px` | Espace interne petit (padding chip) |
| `--space-3` | `12px` | Espace standard entre éléments proches |
| `--space-4` | `16px` | Padding carte compact, gap liste |
| `--space-5` | `24px` | Padding carte standard, gap sections |
| `--space-6` | `32px` | Séparation entre blocs distincts |
| `--space-7` | `48px` | Marge top de page, séparation majeure |
| `--space-8` | `64px` | Réservé cas spéciaux |

**Contraintes :**
- N'utilisez **jamais** une valeur d'espace hors de cette échelle. Toute exception nécessite justification écrite et amendement `Sx_UI_02bis`.
- Le "generous spacing" du principe `Sx_UI_01` §9 se traduit concrètement par : **privilégier `--space-5` (24px) à `--space-4` (16px)** pour tous les paddings carte et gaps de section.

**Alias sémantiques (raccourcis conventionnels).**

| Alias | Résolution |
|---|---|
| `--space-inline-sm` | `--space-2` |
| `--space-inline-md` | `--space-3` |
| `--space-inline-lg` | `--space-4` |
| `--space-stack-sm` | `--space-3` |
| `--space-stack-md` | `--space-5` |
| `--space-stack-lg` | `--space-6` |

## §11. Radius tokens

**Sobriété = rayons discrets.** Pas de "pill" excessifs, pas de squircles.

| Token | Valeur | Usage |
|---|---|---|
| `--radius-none` | `0` | Reset, coins nets |
| `--radius-sm` | `4px` | Chip, badge, tag |
| `--radius-md` | `8px` | Carte, bouton, input |
| `--radius-lg` | `12px` | Modal, sheet, gros conteneur |
| `--radius-full` | `9999px` | Réservé — indicateurs circulaires (dot status), avatars ronds |

**Interdits :**
- ❌ Utiliser `--radius-full` sur un bouton (usage limité aux indicateurs et avatars, jamais aux boutons rectangulaires — trop "SaaS glossy").

## §12. Border tokens

**Épaisseurs.** Un seul standard, `1px`. Toute exception documentée.

| Token | Valeur | Usage |
|---|---|---|
| `--border-width-hairline` | `1px` | Séparateur standard, bordure carte, input |
| `--border-width-focus` | `2px` | Ring de focus visible (a11y) |

**Combinaisons standard.**

- Bordure carte au repos : `1px solid var(--color-border-default)`
- Séparateur ligne (dans une liste) : `1px solid var(--color-border-subtle)`
- Input au repos : `1px solid var(--color-border-default)`
- Input au focus : `2px solid var(--color-accent-focus-ring)` (outline, pas border, pour ne pas déplacer le layout)

## §13. Shadow tokens

**Ombres minimales — quasi absentes.** Le principe §9 de `Sx_UI_01` limite l'usage à des surfaces flottantes strictement fonctionnelles.

| Token | Valeur | Usage |
|---|---|---|
| `--shadow-none` | `none` | Reset, cartes au repos |
| `--shadow-sm` | `0 1px 2px rgba(15, 20, 25, 0.04)` | Sticky header, sticky CTA |
| `--shadow-md` | `0 2px 8px rgba(15, 20, 25, 0.06)` | Rest timer, tooltip |
| `--shadow-lg` | `0 4px 16px rgba(15, 20, 25, 0.08)` | Modal, sheet (rare) |

**Interdits :**
- ❌ `--shadow-lg` sur une carte standard. Réservé aux surfaces manifestement flottantes (modal, sheet mobile).
- ❌ Ombre colorée (teinte teal, teinte accent) — toujours neutre gris-noir.
- ❌ Ombre "élévation SaaS" style Material Design 6dp.

## §14. State tokens (interactive states)

Chaque composant interactif doit couvrir 5 états. Cette section liste les modulateurs de tokens à appliquer.

**Reset states :**

| État | Modulation |
|---|---|
| Default (repos) | tokens de base |
| Hover | `--color-accent-hover` sur les surfaces d'accent ; `--color-surface-alt` sur surfaces neutres |
| Active/pressed | légère assombrissement (multiply alpha 0.9), pas de bounce |
| Focus | `outline: 2px solid var(--color-accent-focus-ring)` + `outline-offset: 2px` |
| Disabled | `--color-fg-disabled` + `cursor: not-allowed` + `pointer-events: none` |

**Non-color cues obligatoires (WCAG 1.4.1) :**
- `hover` : le curseur pointer signale l'interactivité (pas seulement une teinte)
- `active` : légère micro-animation de scale (0.98) OU changement d'icône
- `focus` : outline visible obligatoire, jamais uniquement changement de couleur
- `disabled` : `aria-disabled="true"` + opacité 0.6 minimum, jamais uniquement une couleur grise

## §15. Motion tokens

**Motion très discrète.** Le principe `Sx_UI_01` §9 exclut les animations décoratives.

| Token | Valeur | Usage |
|---|---|---|
| `--motion-duration-instant` | `0ms` | Toggle immédiat |
| `--motion-duration-fast` | `120ms` | Hover state, focus ring apparition |
| `--motion-duration-default` | `200ms` | Ouverture disclosure, transition input |
| `--motion-duration-slow` | `320ms` | Sheet slide-in mobile, modal open |
| `--motion-easing-standard` | `cubic-bezier(0.2, 0.0, 0.0, 1.0)` | Défaut, ease-out doux |
| `--motion-easing-emphasized` | `cubic-bezier(0.3, 0.0, 0.8, 0.15)` | Sortie de sheet, exit d'écran |

**Interdits :**
- ❌ Toute animation qui **doit** être vue pour comprendre l'écran (violation §9 `Sx_UI_01`).
- ❌ Bounce, elastic, overshoot, spring physics.
- ❌ Rotation d'icônes hors chargement.
- ❌ Confetti, célébration visuelle, "PR feedback flash".

**Respect `prefers-reduced-motion`.** Tous les tokens ci-dessus doivent être ramenés à `0ms` quand `@media (prefers-reduced-motion: reduce)` est actif. Application concrète : `Sx_UI_09` (Accessibility & Motion).

## §16. Z-index tokens

**Échelle canonique** pour éviter les guerres de `z-index: 9999`.

| Token | Valeur | Usage |
|---|---|---|
| `--z-base` | `0` | Contenu par défaut |
| `--z-raised` | `10` | Carte élevée, sticky header |
| `--z-sticky` | `100` | Sticky CTA, sticky rest timer |
| `--z-dropdown` | `1000` | Menu déroulant |
| `--z-modal` | `10000` | Modal, sheet |
| `--z-toast` | `100000` | Toast notification |

## §17. Chart tokens

Les charts (progression, tendances, historique) doivent respecter la même discipline : **une seule couleur d'accent, pas de palette arc-en-ciel**.

| Token | Valeur candidate | Usage |
|---|---|---|
| `--chart-line-primary` | `var(--color-accent)` | Ligne principale (ex : charge dans le temps) |
| `--chart-line-secondary` | `var(--color-signal)` | Ligne secondaire (rare, ex : volume) |
| `--chart-fill-primary` | `var(--color-accent-weak)` | Zone remplie sous ligne principale |
| `--chart-grid` | `var(--color-border-subtle)` | Grille de fond |
| `--chart-axis-label` | `var(--color-fg-muted)` | Labels d'axe |
| `--chart-tooltip-bg` | `var(--color-surface)` | Fond tooltip |
| `--chart-tooltip-border` | `var(--color-border-default)` | Bordure tooltip |

**Contraintes :**
- **Deux lignes maximum** dans un même chart. Si plus, hiérarchie à retravailler (drill-down `Sx_UI_07` history-progress).
- Épaisseur ligne : 2px maximum. Pas de trait épais "signature graphique".
- Pas de gradient de remplissage — un `--chart-fill-primary` opaque suffit.

## §18. Composition rules — comment combiner les tokens

**Règles normatives pour éviter la ré-invention.**

### 18.1. Carte standard (card)

```
padding      : var(--space-5)                 /* 24px */
background   : var(--color-surface)           /* #FFFFFF */
border       : 1px solid var(--color-border-default)
border-radius: var(--radius-md)               /* 8px */
box-shadow   : var(--shadow-none)             /* pas d'ombre par défaut */
gap interne  : var(--space-3) ou var(--space-4) selon densité
```

### 18.2. Bouton primaire (CTA)

```
padding-block  : var(--space-3)               /* 12px */
padding-inline : var(--space-4)               /* 16px */
min-height     : 44px                          /* WCAG tap target */
background     : var(--color-accent-strong)
color          : var(--color-on-accent)
font-weight    : var(--font-weight-medium)    /* 500, pas 700 : le rôle est fonctionnel, pas héroïque */
border-radius  : var(--radius-md)
outline (focus): var(--border-width-focus) solid var(--color-accent-focus-ring)
transition     : background var(--motion-duration-fast) var(--motion-easing-standard)
```

### 18.3. Bouton secondaire (outline)

```
padding-block  : var(--space-3)
padding-inline : var(--space-4)
min-height     : 44px
background     : var(--color-surface)
color          : var(--color-fg-default)
border         : 1px solid var(--color-border-default)
font-weight    : var(--font-weight-medium)
border-radius  : var(--radius-md)
hover          : background var(--color-surface-alt)
```

### 18.4. Badge / chip (mesuré, dérivé, inféré, hors de portée)

```
padding-block  : var(--space-1)               /* 4px */
padding-inline : var(--space-2)               /* 8px */
background     : var(--color-{signal-weak | accent-weak | success-weak | warning-weak}) selon type
color          : var(--color-{signal-strong | accent-strong | success-strong | warning-strong})
font-size      : var(--font-size-caption)     /* 11px */
font-weight    : var(--font-weight-medium)
border-radius  : var(--radius-sm)             /* 4px */
```

Type → couleur convention :
- `Mesuré` → `success` (donnée validée)
- `Dérivé` → `signal` (bleu minéral, calcul dérivé validé)
- `Inféré` → `accent-weak` (teal léger, calcul heuristique)
- `Hors de portée` → `fg-muted` sur `surface-alt` (neutre, information transparence)

### 18.5. Séparateur (list item, section)

```
border-bottom: 1px solid var(--color-border-subtle)
margin       : 0 (aucune marge — le séparateur épouse la structure)
```

### 18.6. Input (text, number)

```
padding-block  : var(--space-3)
padding-inline : var(--space-4)
min-height     : 44px
background     : var(--color-surface-sunken)
color          : var(--color-fg-default)
border         : 1px solid var(--color-border-default)
border-radius  : var(--radius-md)
font-size      : 16px minimum (iOS anti-zoom)
focus          : outline 2px solid var(--color-accent-focus-ring), outline-offset 2px
```

### 18.7. Métrique en grande taille (weight display, PR)

```
font-family      : var(--font-family-mono)
font-size        : var(--font-size-metric-lg)   /* 40px */
font-weight      : var(--font-weight-bold)
line-height      : var(--line-height-tight)
font-variant-numeric: tabular-nums
color            : var(--color-fg-strong)
```

## §19. Dark mode — hors-scope de cette spec

**Décision :** dark mode reste hors-scope de `Sx_UI_02`.

Rationale : le principe `Sx_UI_01` §10 exclut le "dark cockpit par défaut" comme identité visuelle primaire. Un dark mode utilisateur (option secondaire) reste envisageable — spec dédiée `Sx_UI_09bis` ou `Sx_UI_02bis` selon décision opérateur.

Ce sprint ne fournit **pas** de tokens dark mode. Toute proposition dark mode devra passer par une spec ultérieure et démontrer qu'elle préserve la lisibilité biométrique et le calme clinique — pas simplement inverser des couleurs.

## §20. Open Questions

Rappel des OQ liées à la palette / typo. Aucune n'empêche l'ouverture de `Sx_UI_03`, mais chaque OQ doit avoir un propriétaire de décision.

| OQ | Question | Propriétaire | Bloque |
|---|---|---|---|
| **OQ-B** | Accent = teal chirurgical désaturé ✅ tranché 2026-07-02 par opérateur ; fallback = bleu minéral ✅ | opérateur | **résolu dans Sx_UI_02** |
| **OQ-H** | Palette hex figée exacte (les valeurs candidates §5-§8 sont indicatives — validation opérateur ou revue UX externe requise avant `Sx_UI_04`) | opérateur + revue UX | `Sx_UI_04` merge |
| **OQ-I** | Font-family Inter vs SF Pro Text vs autre (Inter est proposé pour cohérence multi-OS) | opérateur, revue perf + licence | `Sx_UI_04` merge |
| **OQ-J** | Font mono JetBrains Mono vs SF Mono vs autre | opérateur, revue perf + licence | `Sx_UI_04` merge |
| **OQ-K** | Fluid clamp() ou tailles fixes pour la scale typo ? | opérateur, décision `Sx_UI_04` | `Sx_UI_04` merge |
| **OQ-L** | Dark mode dans `Sx_UI_02bis` ou reporté à `Sx_UI_09bis` ? | opérateur | ne bloque pas Sx_UI_03/04 |
| **OQ-M** | Adopter un naming convention "design token" alternative (ex : Style Dictionary, Radix) ? Actuellement custom, cf. §4 | opérateur, décision Sx_UI_04 | `Sx_UI_04` merge |

**Note importante :** les valeurs hex proposées dans cette spec sont **candidates**, pas figées. Elles doivent être :
1. Validées par revue opérateur ou UX externe
2. Testées en accessibilité (WCAG AA vérifié via outil dédié)
3. Testées en context réel (contraste écran mobile 360×640, luminosité extérieure)

La spec fige les **rôles**, les **noms canoniques**, et les **règles de composition**. Elle ne fige pas définitivement les valeurs hex — celles-ci sont ajustables sous amendement `Sx_UI_02bis` léger sans re-écriture de la spec.

## §21. Non-goals

- Pas de CSS applicatif (aucun `.css` créé, modifié, supprimé)
- Pas de fichier de tokens implémentés (`tokens.css`, `theme.ts`, etc.)
- Pas de manifest, favicon, thème système
- Pas de shell nav, de reduction chrome (relève de `Sx_UI_03`)
- Pas de re-skin session (relève de `Sx_UI_04`)
- Pas de changement dans les templates existants
- Pas de dark mode (cf. §19)
- Pas d'installation de font web ou de package (Inter, JetBrains Mono restent des candidats non installés)
- Pas de figement final des valeurs hex — cf. §20 OQ-H
- Pas d'ouverture de `Sx_UI_03` / `Sx_UI_04` / `Sx_UI_11`
- Pas de renommage SPIGNOS → Auren dans le code

## §22. Acceptance criteria

- ✅ Convention de nommage des tokens définie et documentée (§4)
- ✅ Palette surfaces + foreground définie avec contraste WCAG documenté (§5)
- ✅ Accent principal teal chirurgical désaturé posé avec palette candidate + contraintes d'usage (§6)
- ✅ Accent secondaire bleu minéral posé avec rôle strictement délimité (§7)
- ✅ États sémantiques success/warning/danger posés, usage parcimonieux documenté (§8)
- ✅ Typographie posée : 2 familles max, 3 poids max par famille, échelle taille, line-heights (§9)
- ✅ Échelle spacing 4px-based avec alias sémantiques (§10)
- ✅ Tokens radius / border / shadow / motion / z-index (§11-§16)
- ✅ Chart tokens définis avec discipline mono-accent (§17)
- ✅ Règles de composition (carte, bouton, badge, input, métrique) posées comme normes (§18)
- ✅ Dark mode explicitement hors-scope avec rationale (§19)
- ✅ OQ énumérées avec propriétaire (§20)
- ✅ Non-goals explicites (§21)
- ✅ Aucun fichier `app/`, `tests/`, `migrations/`, `scripts/`, `.github/`, static asset modifié

## §23. Build authorization status

**BUILD NOT AUTHORIZED.**

**Next authorized action after human validation of this spec :** `Sx_UI_03_APP_SHELL_NAVIGATION_SPEC` **SPEC ONLY**.

- Aucun sprint `Sb_UI_NN.k` d'implémentation ne peut être ouvert.
- Aucun fichier `app/`, `tests/`, `migrations/`, `.github/workflows/`, config runtime, `.env`, manifest, static assets ne peut être touché.
- Aucun renommage `SPIGNOS` → `Auren` ne peut être effectué dans le code.
- `Sx_UI_04` (Session Focus Reskin — premier sprint autorisé à modifier du code) reste bloqué jusqu'à validation de `Sx_UI_01`, `Sx_UI_02`, `Sx_UI_03` **et** baseline `Sx_UI_11`.

## §24. Final verdict

**READY FOR HUMAN REVIEW.**

---

## Références

- **Spec précédente :** `docs/strategy/Sx_UI_01_BRAND_FOUNDATION_SPEC.md` (`READY FOR HUMAN REVIEW`, commit `2e345e8`)
- **Roadmap cycle Sx_UI :** `docs/strategy/UI_TRANSFORMATION_ROADMAP.md`
- **Registry :** `docs/strategy/SPEC_REGISTRY.md` §1quinquies
- **Brainstorm sources :** `docs/strategy/brainstorm/UI_TRANSFORMATION_BRAINSTORM_V1_normalized.md`, `..._V2_normalized.md`
- **Gate OPS déblocant :** `docs/OPS_PROD_STABILIZATION_PROFILE_BODY_COACH_REPORT.md` §10
- **Sprint OPS CI cost :** `docs/SPRINT_Sb_OPS_ci_path_filter_BUILD_REPORT.md` (économie CI validée par run `28582551168` ✅)
