# Sx_UI_02b — Auren Terminal Design Tokens Spec (Direction Revision)

**Spec ID :** `Sx_UI_02b_AUREN_TERMINAL_SPEC`
**Cycle :** `Sx_UI` — Auren Visual & Product Transformation
**Type :** SPEC ONLY (docs-only) — **révision de direction visuelle** (amendement de `Sx_UI_02`)
**Date d'ouverture :** 2026-07-07
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code
**Amende :** `Sx_UI_02_DESIGN_TOKENS_SPEC.md` (§6 accent teal, §9 typo, §13 shadows, §19 dark mode, §20 OQ-H/I/J/L)
**Depends on :** `Sx_UI_01_BRAND_FOUNDATION_SPEC.md` ✅ · `Sx_UI_02_DESIGN_TOKENS_SPEC.md` ✅ (révisé ici) · `Sx_UI_03_APP_SHELL_NAVIGATION_SPEC.md` ✅ · `Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC.md` ✅ CLOSED

---

## §0. Status

- **SPEC ONLY** — **BUILD NOT AUTHORIZED**
- **Docs-only strict** — aucun `app/`, `tests/`, `migrations/`, `scripts/`, `.github/` touché
- Aucun CSS / template / JS modifié ; aucun token implémenté
- Ce document **révise la direction visuelle** actée par `Sx_UI_02` (Clinical Lab clair + teal chirurgical) vers **Auren Terminal** (graphite dense + typographie mono + accent unique rare).
- Sx_UI_02 §19 déférait explicitement le dark mode à un « `Sx_UI_02bis` » (OQ-L) et §20 déclarait les valeurs hex « ajustables sous amendement `Sx_UI_02bis` ». **Ce document EST ce `Sx_UI_02bis`** — un amendement sanctionné, pas une contradiction.

## §1. Executive summary

**Décision de direction (opérateur, brainstorm 2026-07-07) :** l'identité visuelle du produit devient **« Auren Terminal »** — le *Palantir du bodybuilding*. Concrètement, trois choix radicaux et cohérents :

1. **Fond graphite dense (Gotham)** — surface sombre instrument, plus le « Clinical Lab clair ».
2. **Typographie tout-mono (terminal)** — une seule famille monospace, texte ET chiffres, hiérarchie par taille/graisse/couleur.
3. **Quasi-monochrome + un seul accent rare** — la couleur devient un **événement** (action primaire · état actif · alerte), tout le reste en niveaux de gris.

Objectif : sortir de la grammaire « app santé/wellness grand public » (teal spa, gros titres bold, cards arrondies à ombres) vers une grammaire **d'instrument de commandement** : densité assumée sans bruit, chrome quasi invisible, autorité tranquille, la donnée traitée comme donnée.

## §2. Why this revision exists

Le hero Home `Sb_UI_05.1` (teal `#0F8A85`, Inter bold 32-40px, radius 16px, ombres teal) a été perçu en revue comme **« application bas de gamme »** / trop wellness. Diagnostic de fond :
- **Le teal** connote spa / Calm / Headspace, pas instrument.
- **Inter en gros bold** = grammaire marketing/consumer, pas terminal.
- **Radius large + ombres portées colorées** = « app store featured », zéro instrument.
- **Les chiffres ne sont pas traités comme des données** (pas de mono systématique).

Le contraire de « bas de gamme » n'est **pas plus de couleur** : c'est **retenue + densité + précision typographique**. D'où Auren Terminal.

## §3. Ce que cette révision NE change PAS

Point critique de gouvernance : **on re-skin, on ne re-architecture pas.**

- ✅ Tous les **invariants structurels** de Sx_UI_04 (cockpit actif, mini-stepper, console de logging, worked area, alternatives, up-next) sont **acquis et conservés**.
- ✅ Tous les **contrats** (routes, services, models, migrations, forms, input names, rest timer `data-*`, substitution, no-JS, macros) restent **intacts**.
- ✅ Les **règles de composition** de Sx_UI_02 (§18) restent valides — seules les **valeurs** (couleurs, familles typo, radius, ombres) changent.
- ✅ Aucun rebrand SPIGNOS → Auren dans le code (réservé Sx_UI_10).

Seule la **couche visuelle** (palette, typographie, chrome) migre. C'est un **re-skin de tokens**, pas une refonte produit.

## §4. Révision explicite de Sx_UI_02

| Sx_UI_02 (acté) | Sx_UI_02b (révisé) |
|---|---|
| §6 accent = **teal chirurgical `#0F8A85`** (OQ-B/OQ-H) | accent = **ambre readout `#C8A24B`** unique (§7 ci-dessous), teal **retiré** |
| §5 surfaces = **blanc / off-white** (Clinical Lab clair) | surfaces = **graphite** (§6 ci-dessous) |
| §9 typo = Inter (sans) + mono pour metrics | typo = **mono partout** (texte + chiffres), une seule famille (§8) |
| §13 shadows minimales mais présentes | shadows **quasi supprimées** ; séparation par **1px line + luminosité** (§10) |
| §11 radius 4/8/12px | radius **réduit 2/4/6px** (§11) |
| §19 dark mode **hors-scope** | dark **devient l'identité primaire** (résout OQ-L) |

**OQ résolues par cette révision :** OQ-H (hex figées → graphite/ambre), OQ-I/J (une seule famille mono système), OQ-L (dark = identité, pas option). OQ-B (accent) est **ré-ouverte** puis re-tranchée (ambre).

## §5. Design principles (Auren Terminal)

1. **Densité sans bruit.** Beaucoup d'information, chaque pixel justifié. Le vide est structurel.
2. **La donnée est traitée comme donnée.** Tout chiffre en mono tabular, aligné en colonnes.
3. **Chrome invisible.** Lignes 1px, surfaces distinguées par 2-4% de luminosité, pas d'ombres décoratives.
4. **Couleur = signal rare.** Un seul accent, réservé action primaire / état actif / alerte. Ailleurs = gris.
5. **Autorité tranquille.** Pas de gros bold, pas de dégradé, pas de glow, pas de célébration. L'interface *sait*.
6. **Retenue typographique.** Hiérarchie par taille + graisse (400/500/600 max) + couleur + letter-spacing, jamais par changement de famille.

## §6. Color tokens — surfaces graphite (candidats V1)

```
--color-bg-void:      #0A0C0F   /* fond le plus profond (page derrière panels) */
--color-bg-base:      #0E1116   /* surface page */
--color-bg-panel:     #141821   /* panneaux / cards */
--color-bg-raised:    #1B2029   /* survol / actif subtil / inputs */
--color-bg-sunken:    #0B0E13   /* zones en creux */
```

Séparation des surfaces par **luminosité** (≈2-4%), pas par ombre. Un panel = `bg-panel` + `1px line`, rien d'autre.

## §7. Color tokens — foreground + accent unique (candidats V1)

**Foreground (niveaux de gris froids) :**
```
--color-fg:           #E6EAF0   /* texte principal */
--color-fg-muted:     #8B96A5   /* labels, secondaire */
--color-fg-dim:       #5A6472   /* méta, désactivé, hint */
--color-fg-faint:     #3A424E   /* ultra-secondaire, watermark */
```

**Lignes / bordures :**
```
--color-line:         #232A34   /* séparateur 1px standard */
--color-line-strong:  #313A46   /* séparateur marqué / focus subtil */
```

**Accent UNIQUE — ambre readout (candidat V1, OQ-B re-tranché) :**
```
--color-accent:       #C8A24B   /* l'unique couleur : action primaire, état actif */
--color-accent-hover: #D8B25C
--color-accent-dim:   #8A7538   /* accent atténué (états secondaires) */
--color-accent-weak:  rgba(200, 162, 75, 0.14)  /* fond actif subtil */
--color-on-accent:    #0A0C0F   /* texte sur l'accent (graphite profond) */
```

**États sémantiques — désaturés, réservés, jamais décor :**
```
--color-ok:    #6E9E7A   /* validation (rare) */
--color-warn:  #C77B54   /* alerte douce */
--color-danger:#B85C5C   /* erreur */
```

**Règle d'or accent (§5.4) :** l'ambre n'apparaît QUE sur : (a) le bouton d'action primaire, (b) l'item/état actif, (c) une alerte critique. Tout le reste — titres, métriques, labels, navigation inactive — est en **niveaux de gris**. La couleur est un événement, pas un thème.

### §7.1 — Rationale de l'ambre
- **Pas teal** : élimine la connotation wellness/spa qui a déclenché le rejet.
- **Pas bleu enterprise générique** : évite le « SaaS B2B interchangeable ».
- **Ambre = readout d'instrument** (cadran, terminal ambre, oscilloscope) : « brille » sur graphite, connote la mesure et la précision. Distinctif et défendable pour un produit d'entraînement instrumental.
- **Alternative de secours** (si l'ambre déplaît en review) : bleu acier froid `#3B82C4` désaturé, ou vert phosphore `#4A9E6B` très sobre. Voir OQ-02b-A.

## §8. Typography tokens — tout-mono (candidats V1)

**Une seule famille (stack système, zéro webfont — cohérent OQ-I/J) :**
```
--font-family-mono: ui-monospace, "SF Mono", "JetBrains Mono", "Roboto Mono", Menlo, Consolas, monospace;
--font-family:      var(--font-family-mono);  /* alias : le texte EST mono */
```

**Graisses (retenue — jamais 700+) :**
```
--font-weight-regular: 400;
--font-weight-medium:  500;
--font-weight-strong:  600;   /* graisse maximale autorisée */
```

**Échelle (fixe, pas de clamp — résout OQ-K) :**
```
--font-size-eyebrow:  11px;   /* uppercase, letter-spacing 0.12em */
--font-size-meta:     12px;
--font-size-body:     14px;
--font-size-title:    20px;   /* titres — PAS 32-40px */
--font-size-title-lg: 26px;   /* hero mobile max */
--font-size-metric:   32px;   /* grande métrique / weight display */
```

**Règles mono :**
- `font-variant-numeric: tabular-nums` **partout**.
- Gros titres : `letter-spacing: -0.02em` (le mono s'étale sinon).
- Eyebrows / labels : `text-transform: uppercase; letter-spacing: 0.08–0.12em`.
- **Phrases courtes obligatoires** (le mono fatigue sur du long) — discipline déjà imposée par §22 Sx_UI_04 (≤3 cues, « pourquoi » en 1 phrase). Le tout-mono **renforce** cette contrainte produit.
- `line-height` : 1.2 titres, 1.45 corps (le mono a besoin d'air vertical).

## §9. Chrome tokens — radius, borders, shadows (candidats V1)

```
--radius-xs: 2px;
--radius-sm: 4px;
--radius-md: 6px;   /* maximum — plus de 12/16px */
--border-width: 1px;
--shadow-none: none;                         /* défaut : AUCUNE ombre */
--shadow-focus: 0 0 0 1px var(--color-accent);  /* seul usage : focus/actif */
```

Principe : **une card = surface + 1px line.** Pas d'ombre portée. La profondeur vient de la **luminosité** entre surfaces (`bg-base` < `bg-panel` < `bg-raised`), pas d'ombres. Le seul « glow » autorisé est un rail 1-2px accent sur l'élément actif.

## §10. Grammaire visuelle (composition Auren Terminal)

- **Card / panel** : `background: bg-panel; border: 1px solid line; border-radius: 4-6px; box-shadow: none`.
- **Séparateur** : `1px solid line`, jamais d'ombre.
- **CTA primaire** : `background: accent; color: on-accent`, radius 4px, mono 600, pas d'ombre colorée (au plus `shadow-focus` au focus). **Un seul par écran.**
- **CTA/lien secondaire** : `color: fg-muted`, hover `fg` + underline. Pas de fond.
- **Métrique** : mono, `font-size-metric`, `fg` (jamais accent sauf si c'est LA valeur de décision), unité en `fg-dim`.
- **Ligne de données** : colonnes alignées mono tabular, label `fg-dim` uppercase 11px + valeur `fg` mono.
- **État actif** (item, tab, set) : `bg-raised` + rail 2px `accent` + code/label `accent`. Non-actifs : `fg-muted`, aucun accent.
- **Eyebrow** : uppercase, `fg-dim`, letter-spacing 0.12em, optionnel point signal `accent` (le seul endroit décoratif toléré).

## §11. Accessibilité sur graphite

- **Contraste AA obligatoire** : `fg #E6EAF0` sur `bg-base #0E1116` ≈ 14:1 ✅ ; `fg-muted #8B96A5` sur `bg-base` ≈ 6:1 ✅ (AA) ; `fg-dim #5A6472` réservé au texte ≥ large ou non-essentiel (à vérifier ≥ 4.5:1 sinon remonter la valeur).
- **Accent `#C8A24B` sur `bg-base`** ≈ 8:1 ✅ ; **`on-accent #0A0C0F` sur accent** ≈ 10:1 ✅ (texte sur bouton lisible).
- **Focus visible** : rail accent 1-2px (`shadow-focus`), jamais uniquement une couleur.
- **Non-color cues préservés** (héritage Sx_UI_04) : les états gardent leurs cues typographiques / bordures, pas seulement l'ambre.
- **Luminosité extérieure** (salle de sport) : le graphite dense + fort contraste texte est **meilleur** en environnement variable qu'un blanc éblouissant — argument en faveur du dark ici.
- **`prefers-reduced-motion`**, **WCAG 44×44**, **reduced-transparency** préservés.

> ⚠️ Les hex sont **candidats V1**. Validation AA via outil dédié obligatoire au build (comme Sx_UI_02 §20). Ajustables sous amendement léger.

## §12. Plan de migration — Home + Focus Mode (une vague cohérente)

Décision opérateur : **Home ET Focus Mode migrent ensemble** vers Auren Terminal (pas de transition à deux mondes durable). Exécution séquentielle, review-gated :

| Étape | Portée | Type |
|---|---|---|
| **Sx_UI_02b** (ce doc) | Tokens Auren Terminal | SPEC (docs) |
| **Sb_UI_02b.1** | Fichier tokens implémenté (ex. `tokens_terminal.css` ou variables scoped) + re-skin **Home** (`.today-home` : graphite/mono/ambre, remplace le patch teal) | BUILD |
| **Sb_UI_02b.2** | Re-skin **Focus Mode** (`session_focus.css` : migration graphite/mono/ambre, invariants structurels intacts) | BUILD |
| **Sb_UI_02b.3** | Hardening cross-écran (contraste AA vérifié, baseline P0 re-capturée, cohérence Home↔Session) + éventuel shell/nav | BUILD |

**Note working tree :** le patch « Visual Decision Depth » teal/clair actuellement non commité est **obsolète** vis-à-vis de cette direction. Décision opérateur : le **garder dans le working tree**, la spec est écrite par-dessus. Au moment des commits, les docs de cette spec sont commités **séparément** du patch teal ; le re-skin `Sb_UI_02b.1` **remplacera** le teal.

## §13. Data contract / invariants (rappel)

Aucun changement fonctionnel dans toute la migration :
- Routes / services / models / migrations **inchangés**.
- Forms, input names, rest timer `data-*`, substitution route/radios **inchangés**.
- No-JS fallback, macros Jinja **inchangés**.
- Structure cockpit / console / worked area (Sx_UI_04) **inchangée** — seul le skin change.
- Aucun asset / GIF / image ajouté (le graphite est CSS pur).
- Aucun rebrand code.

## §14. Baseline visuelle

- La bascule graphite fait **bouger toute la baseline P0** (tous les écrans). Attendu et assumé.
- Chaque build `Sb_UI_02b.k` : after-capture P0 `ok=16`, anti-404, **aucun PNG committé**.
- Re-capture de référence recommandée après `Sb_UI_02b.2` (Home + Session migrés) pour figer la nouvelle baseline Auren Terminal.

## §15. Open Questions (avec recommandation)

| ID | Question | Options | **Recommandation V1** |
|---|---|---|---|
| **OQ-02b-A** | Accent unique définitif ? | (a) ambre readout `#C8A24B` ; (b) bleu acier `#3B82C4` ; (c) vert phosphore `#4A9E6B` ; (d) autre | **(a) ambre** — instrument, distinctif, non-wellness. Comparables à valider sur maquette. |
| **OQ-02b-B** | Tout-mono strict, ou mono chiffres + grotesque texte ? | (a) tout mono (choix opérateur) ; (b) hybride | **(a) tout mono** confirmé — phrases courtes obligatoires. Réévaluer si fatigue de lecture avérée en dogfood. |
| **OQ-02b-C** | Fond : graphite pur ou graphite légèrement bleuté/verdi ? | (a) neutre `#0E1116` ; (b) bleuté ; (c) verdi | **(a) neutre froid** — laisse l'accent porter la couleur. |
| **OQ-02b-D** | Migration Home+Focus en une PR ou 2 builds séquentiels ? | (a) 2 builds review-gated ; (b) 1 gros build | **(a) 2 builds** (Sb_UI_02b.1 Home, .2 Focus) — reviewable, moins risqué. |
| **OQ-02b-E** | Dark = identité unique, ou dark + option clair future ? | (a) dark unique V1 ; (b) dark + toggle clair futur | **(a) dark unique** V1 — pas de double thème à maintenir maintenant ; toggle = future si demandé. |
| **OQ-02b-F** | Sort du teal `#0F8A85` déjà mergé (Sb_UI_04.1→.5, hero teal) ? | (a) migré vers ambre au re-skin ; (b) conservé qq part | **(a) migré** — le teal disparaît intégralement avec Auren Terminal. |
| **OQ-02b-G** | Densité : compacte (Palantir strict) ou aérée ? | (a) compacte instrument ; (b) intermédiaire ; (c) aérée | **(b) intermédiaire** V1 — dense mais pas illisible mobile ; ajustable. |
| **OQ-02b-H** | Le shell/nav (Sx_UI_03 bottom nav) migre-t-il aussi ? | (a) oui en Sb_UI_02b.3 ; (b) plus tard | **(a) oui .3** — sinon incohérence nav claire / contenu sombre. |

## §16. Non-goals

- ❌ Aucun CSS / template / JS / token implémenté dans cette spec (docs only).
- ❌ Aucun changement fonctionnel / route / service / model / migration.
- ❌ Aucune re-architecture Sx_UI_04 (re-skin uniquement).
- ❌ Aucun webfont / asset / package / GIF ajouté (graphite = CSS pur).
- ❌ Aucun rebrand SPIGNOS → Auren code.
- ❌ Aucun double thème (dark unique V1).
- ❌ Aucun release tag.
- ❌ Aucune ouverture Sx_UI_06 / Sx_UI_10.

## §17. Acceptance criteria (de cette spec)

- ✅ Direction Auren Terminal (graphite + mono + accent unique) documentée et tranchée.
- ✅ Révision de Sx_UI_02 explicite (§4) — pas de contradiction cachée.
- ✅ Tokens candidats V1 (surfaces, fg, accent, typo, chrome) posés avec rationale.
- ✅ Accessibilité AA sur graphite cadrée (§11).
- ✅ Plan de migration Home + Focus Mode séquentiel review-gated (§12).
- ✅ Invariants structurels/fonctionnels garantis (§3, §13).
- ✅ 8 OQ avec recommandation (§15).

## §18. Verdict attendu

- **READY FOR HUMAN REVIEW**
- **Aucun build ouvert** (Sb_UI_02b.1 reste bloqué tant que la spec + OQ ne sont pas validées)
- **Aucune capture screenshot** dans ce sprint
- **Aucun release tag**

## §19. Références

- Spec parente révisée : `docs/strategy/Sx_UI_02_DESIGN_TOKENS_SPEC.md` (§6/§9/§13/§19/§20)
- Brand : `docs/strategy/Sx_UI_01_BRAND_FOUNDATION_SPEC.md`
- App shell : `docs/strategy/Sx_UI_03_APP_SHELL_NAVIGATION_SPEC.md`
- Cycle Focused Exercise Flow (clos, re-skin visé) : `docs/SPRINT_Sx_UI_04_FINAL_CLOSEOUT_REPORT.md` + `docs/strategy/Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC.md`
- Home (patch teal obsolète, à remplacer) : `docs/SPRINT_Sb_UI_05_1_REPORT.md`
- Registry : `docs/strategy/SPEC_REGISTRY.md`
- Roadmap : `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`
