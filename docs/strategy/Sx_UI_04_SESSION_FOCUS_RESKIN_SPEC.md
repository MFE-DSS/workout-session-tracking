# Sx_UI_04 — Session Focus Reskin Spec

**Spec ID :** `Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC`
**Cycle :** `Sx_UI` — Auren Visual & Product Transformation
**Date d'ouverture :** 2026-07-02
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code (docs-only)
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Depends on :**
- `Sx_UI_01_BRAND_FOUNDATION_SPEC.md` ✅ accepté
- `Sx_UI_02_DESIGN_TOKENS_SPEC.md` ✅ accepté
- `Sx_UI_03_APP_SHELL_NAVIGATION_SPEC.md` ✅ accepté
- `Sx_UI_11_SCREENSHOT_REGRESSION_BASELINE_SPEC.md` ✅ accepté

---

## §1. Status

- **SPEC ONLY**
- **BUILD NOT AUTHORIZED**
- **Docs-only strict** — aucun `app/`, `tests/`, `migrations/`, `scripts/`, `.github/` touché
- Aucun CSS modifié (`session_focus.css`, `app.css` intacts)
- Aucun template modifié (`session_detail.html`, `_partials/*.html` intacts)
- Aucun JS modifié (`session_focus.js` intact)
- Aucun screenshot capturé
- Aucun outil installé (Playwright reste hors du repo)
- Aucun renommage `SPIGNOS` → `Auren` dans le code

**BUILD BLOCKED UNTIL BASELINE P0 OR EXPLICIT OPERATOR OVERRIDE.**

## §2. Why this spec exists

Le Focus Mode session est la meilleure surface pour ouvrir la mise en application concrète des specs `Sx_UI_01` à `Sx_UI_03` :

- **Cœur d'usage réel.** Chaque séance loggée passe par cette surface, plusieurs fois par utilisation. Les gains ou régressions y sont amplifiés.
- **Déjà mobile-first.** Sx_29 a livré un shell mobile spécifique (`session_focus.css`), extrait de `app.css`, chargé conditionnellement — cascade CSS déjà maîtrisée.
- **Déjà no-JS compatible.** `<details>` natifs HTML, `<form method="post">`, rest timer avec fallback statique. Aucune dépendance JS pour naviguer ou logger.
- **Déjà extrait proprement.** Les partials `session_focus_header.html`, `exercise_card.html`, `rest_timer.html` isolent le domaine sans mélange avec le shell global.
- **Déjà stabilisé.** `Sx_29_CLOSURE_REPORT` acté avec dogfood ✅ PASS 2026-06-16. Aucun bugfix ouvert. Point de départ non-flou.
- **Contient tous les composants Auren cibles.** header sticky, jump bar, cards à états, sticky CTA, rest timer, tap targets — matière pour valider tokens + shell Sx_UI_03 dans un contexte réel.

Cette spec **prépare le futur build** sans l'exécuter. Elle définit :
- ce que le build est autorisé à modifier
- ce qui doit rester intact (invariants métier + fonctionnels)
- comment les tokens Sx_UI_02 sont consommés par composant
- où la bottom nav Sx_UI_03 s'insère pendant une session
- quel plan de sous-sprints (`Sb_UI_04.1` → `Sb_UI_04.5`) sera proposé quand le build sera débloqué

Cette spec **ne définit pas** :
- l'implémentation exacte des tokens en CSS custom properties (décision au premier `Sb_UI_04.k`)
- les valeurs hex figées définitives (OQ-H à trancher par cette spec ou lors du merge)
- la conversion de `app.css` à un système de tokens globaux (hors scope, `Sx_UI_04` reste focalisé)

## §3. Current Focus Mode diagnosis

Diagnostic direct des fichiers lus en read-only à `fc3433a` (HEAD local au moment de l'ouverture de cette spec).

**Structure fichier :**

| Fichier | Rôle | Lignes | Introduit par |
|---|---|---|---|
| `app/static/css/session_focus.css` | CSS scoped focus mode | 547 | Sx_29 (Sb_29.5 extraction) |
| `app/static/css/app.css` | CSS global historique | 3020 | héritage V1 |
| `app/templates/session_detail.html` | Page principale focus mode | 175 | Sx_29 + Sb_02.1 |
| `app/templates/_partials/session_focus_header.html` | Header sticky | 33 lignes | Sx_29 (Sb_29.1) |
| `app/templates/_partials/exercise_card.html` | Carte exercice à états | 200+ | Sx_29 (Sb_29.1) + Sb_30.3 (overload hint) + Sb_30.next.placeholder |
| `app/templates/_partials/rest_timer.html` | Timer de repos progressive enhancement | 40 | Sb_29.4 |
| `app/static/js/session_focus.js` | JS vanilla countdown timer | 95 | Sb_29.4 |

**Structure CSS session_focus.css observée (grep top-level selectors) :**

- Racine : `.session-focus` avec sub-BEM `session-focus__header`, `session-focus__sticky-header`, `session-focus__jump`, `session-focus__sticky-jump`, `session-focus__card`, `session-focus__tap-target`, `session-focus__rest-timer`
- États cards : `--pending`, `--active`, `--partial`, `--done`, `--skipped`, `--substituted` — 6 états orthogonaux
- Cibles `.ex-jump__*` : items jump bar avec états miroirs
- Media queries : `@media (max-width: 380px)` pour mobile étroit, `@media (prefers-reduced-motion: reduce)` pour a11y

**Points de friction visuelle identifiés (cible reskin) :**

1. **Palette utilitaire cockpit.** Fond sombre historique, accent orange `#f25f3a`, cards contrastées sombres — antinomique avec la posture Clinical Lab + Quiet Instrument.
2. **Hiérarchie typographique implicite.** Titres et métriques utilisent souvent la même famille sans distinction `mono` pour les valeurs numériques — perte de lisibilité alignement listes de séries.
3. **Bordures + ombres épaisses par endroits.** Le principe "minimal shadow" Sx_UI_02 n'est pas honoré.
4. **Accent orange sur états d'action.** Sera migré vers teal chirurgical désaturé Sx_UI_02.
5. **Bottom nav absente.** Sx_29 n'avait pas cette notion — Sx_UI_03 la définit maintenant, `Sx_UI_04` doit décider de sa présence en focus mode (cf. §14).
6. **Header sticky visuellement dense.** Titre + meta + progression + note — hiérarchie à alléger.

**Points structurels à préserver (invariants Sx_29 confirmés au dogfood) :**

- Sticky header + sticky jump bar (défilement conservé pendant scroll)
- Jump bar navigation intra-session (accès rapide aux exercices)
- Sticky CTA sur carte active (submit set toujours à portée)
- Rest timer progressive enhancement (JS vanilla, no-JS fallback intégral)
- Tap targets `44×44` respectés (`session-focus__tap-target`)
- 6 états orthogonaux sur cards (pending/active/partial/done/skipped/substituted)
- No-JS `<details>` natif pour développer les cards

## §4. Product invariants

Liste **normative** de ce qui **ne doit pas changer** dans `Sx_UI_04` ni dans ses sous-sprints `Sb_UI_04.k`.

**Fonctionnel métier — intact :**

- ❌ Création / lecture de session — aucun changement de route, de model, de service
- ❌ Logging sets (poids × reps) — form POST `url_for('update_exercise_card', ...)` inchangé
- ❌ Rest timer : `data-start-rest`, `data-rest-duration`, `data-rest-skip` — attributs data conservés, JS ne change pas de contrat
- ❌ Substitution routes (`substitute_session_exercise` et associés) — accessibles depuis la card, jamais modifiées par le reskin
- ❌ Completion flow (`/sessions/{id}/done`) — aucun changement
- ❌ Scoring (`app/services/scoring/*`) — aucune modification
- ❌ Overload engine (`overload_engine.py`, `overload_inputs.py`, `overload_explainer.py`) — hint consommé par `exercise_card.html` mais **contexte inchangé**
- ❌ Coach report (`coach_report.py`, `coach_inference.py`) — aucun changement
- ❌ Body intelligence (`body_intelligence.py`, `body_intelligence_inputs.py`) — aucun changement
- ❌ Auth / rate limit / CSRF — aucun changement
- ❌ Routes (`app/routers/sessions.py`) — aucun ajout, aucune modification, aucune suppression
- ❌ Models SQLAlchemy — aucune migration Alembic
- ❌ No-JS fallback — chaque écran doit rester utilisable JS désactivé

**Structure DOM — largement préservée :**

- ✅ Classes CSS legacy `exercise-card`, `session-header`, `page-title`, `badge`, `btn`, `card`, `field-group`, etc. **conservées** (le reskin peint sans casser la structure)
- ✅ IDs d'ancre `#exercise-{id}` — conservés (utilisés par jump bar)
- ✅ Hooks `session-focus__*` — conservés (extension par ajout de propriétés, pas suppression)
- ✅ Attributs data (`data-start-rest`, `data-rest-skip`, `data-rest-duration`, `data-rest-display`) — conservés (contrat JS)
- ✅ Ancres `name="nav" value="prev|next"` — conservées (nav SSR sans JS)

**Contrats de macros Jinja :**

- ✅ `_macros.html` : `segmented`, `field_group` — appelés depuis `session_detail.html`, non modifiés dans Sx_UI_04

## §5. Files candidate map

Périmètre **autorisé** au futur build `Sb_UI_04.k`. Chaque fichier a un rôle actuel, un type de changement projeté, un niveau de risque, et une autorisation binaire.

| Fichier | Rôle actuel | Type de changement futur | Risque | Autorisé Sb_UI_04.k ? |
|---|---|---|---|---|
| `app/static/css/session_focus.css` | CSS scoped focus mode (547 lignes) | **Réécriture ciblée** : palette teal, spacing 4px, mono metrics, minimal shadows, focus visible. Structure BEM conservée. | Moyen (impact visuel majeur, structurellement contenu par la cascade extraite Sb_29.5) | ✅ **oui** |
| `app/static/css/app.css` | CSS global (3020 lignes) | **Modifications minimales et localisées** au strict nécessaire pour les partials session (badges partagés, buttons partagés). Extraction globale hors-scope. | Élevé (fuite globale possible) | ✅ **oui, mais limité** : seuls les sélecteurs référencés par les partials session, jamais des changements globaux hors scope |
| `app/templates/session_detail.html` | Page principale focus mode | **Ajustements structurels minimaux** : classes / wrappers pour honorer la bottom nav Sx_UI_03. Aucun changement de logique conditionnelle Jinja. | Moyen | ✅ **oui, structure uniquement** |
| `app/templates/_partials/session_focus_header.html` | Header sticky (33 lignes) | **Ajustements structurels** : classes token, ordre visuel des méta. Contenu conditionnel préservé. | Faible | ✅ **oui** |
| `app/templates/_partials/exercise_card.html` | Carte exercice (200+ lignes) | **Ajustements structurels** : classes token pour badges, boutons, inputs. Zéro changement de champs, ni d'action forms. | Faible-Moyen | ✅ **oui, structure uniquement** |
| `app/templates/_partials/rest_timer.html` | Timer partial (40 lignes) | **Ajustements structurels** : classes token pour label, countdown, skip button. Data-attrs préservés. | Faible | ✅ **oui, structure uniquement** |
| `app/static/js/session_focus.js` | JS timer vanilla (95 lignes) | **Aucune modification fonctionnelle** V1. Peut recevoir un patch trivial (ajout classes CSS via `classList.add`) si nécessaire, jamais un changement de contrat. | Faible | ⚠️ **oui, patch trivial uniquement** — contrat JS invariant |

**Fichiers strictement interdits au reskin Sx_UI_04 :**

- ❌ `app/services/*` (tous les services métier)
- ❌ `app/routers/sessions.py`, `app/routers/*` (routes)
- ❌ `app/models/*` (models SQLAlchemy)
- ❌ `migrations/*` (Alembic)
- ❌ Fichiers de tests métier (`tests/test_session_*.py` uniquement pour ajouts de tests **visuels/structurels**, jamais pour modifier des tests logique)
- ❌ Manifest, favicon, icônes de brand (relèvent de `Sx_UI_10` rebrand)
- ❌ Nouveaux assets (SVG, images, polices web) — les fonts sont référencées via CSS `@font-face` ou stack système au maximum

## §6. Visual direction for Focus Mode

Direction visuelle **normative** consommant `Sx_UI_01 §9-10` et `Sx_UI_02 §5-8` :

- **Fond blanc / blanc cassé** — `--color-bg-base` (`#FFFFFF`) sur la page, `--color-bg-elevated` (`#FAFBFC`) éventuel pour les zones de section
- **Cartes froides** — `--color-surface` avec `1px solid var(--color-border-default)`, pas d'ombre au repos
- **Séparateurs fins** — `1px` `--color-border-subtle` entre exercices ou sections
- **Accent teal chirurgical désaturé** — uniquement pour :
  - CTA primaire (submit set actif, "Marquer done")
  - État `active` sur la card (bordure ou barre latérale teal, jamais fond teal saturé)
  - Focus ring input (2px outline)
  - Icône jump bar item actif
- **Bleu minéral** — uniquement pour info secondaire :
  - Badge `Dérivé` (Body Intelligence, si visible dans focus mode contextuellement — actuellement non)
  - Tag `substituted` sur card (si visible visuellement, à décider en `Sb_UI_04.3`)
- **Métriques mono** — `--font-family-mono` avec `font-variant-numeric: tabular-nums` sur :
  - Compteur "X / Y work sets" du header
  - Résumé `weights_str kg · reps_str reps` dans compact card
  - Countdown rest timer (`60s`, `45s`, `30s`)
  - Inputs weight_kg et reps (valeur mono, label sans)
  - Overload hint chiffré (`≈ N kg`)
- **Interdits :**
  - ❌ Orange `#f25f3a` ou variante — éliminé du branding
  - ❌ Gradient (aucun linear-gradient, radial-gradient, aucune texture)
  - ❌ Dark cockpit — le mode par défaut reste blanc, dark mode reporté à `Sx_UI_02bis` ou `Sx_UI_09bis`
  - ❌ Celebration / confetti — après logging set, feedback textuel calme uniquement
  - ❌ Emoji dans les labels UI (les emoji présents dans les inputs utilisateur restent, mais les libellés système utilisent typo + icônes SVG stroke uniquement)
  - ❌ Illustration ou hero visual

## §7. Token consumption map

Mapping normatif des tokens `Sx_UI_02` **consommés** par le focus mode. Aucun nouveau token n'est créé dans `Sx_UI_04`. Si un token manque, la spec ouvre une **OQ**, jamais un token.

| Rôle focus mode | Token Sx_UI_02 consommé |
|---|---|
| Fond page | `--color-bg-base` |
| Fond section élevée | `--color-bg-elevated` |
| Carte exercice | `--color-surface` |
| Carte état alterné (partial, done grisé) | `--color-surface-alt` |
| Input weight/reps arrière-plan | `--color-surface-sunken` |
| Titre H1 (nom template) | `--color-fg-strong` |
| Body text (labels, note) | `--color-fg-default` |
| Meta (weekday, timestamp) | `--color-fg-muted` |
| Hint / placeholder input | `--color-fg-subtle` |
| Exercice future (pending) | `--color-fg-muted` sur `--color-surface-alt` |
| Séparateur card | `--color-border-subtle` |
| Bordure card | `--color-border-default` |
| Focus ring input | `--color-accent-focus-ring` |
| Accent principal (submit CTA fond, active state) | `--color-accent-strong` (CTA), `--color-accent` (état actif visuel) |
| Accent secondaire (Dérivé badge, tag info) | `--color-signal` + `--color-signal-weak` (surface) |
| Success (état `done`) | `--color-success` (badge / border-left card), `--color-success-weak` (surface) — usage parcimonieux |
| Warning (état `skipped`) | `--color-warning` / `--color-warning-weak` — usage parcimonieux |
| Danger (erreur system) | `--color-danger` — actions destructives uniquement |
| Spacing gap header | `--space-3` (12px) |
| Spacing padding card | `--space-5` (24px) — "generous spacing" |
| Spacing gap intra-card | `--space-3` |
| Spacing bottom safe-area | `--space-4` + `env(safe-area-inset-bottom)` |
| Radius card | `--radius-md` (8px) |
| Radius badge | `--radius-sm` (4px) |
| Radius bouton | `--radius-md` |
| Shadow header sticky (au scroll seulement) | `--shadow-sm` |
| Shadow sticky CTA | `--shadow-sm` |
| Shadow rest timer flottant | `--shadow-md` (petit, éphémère) |
| Motion transition état card | `--motion-duration-fast` + `--motion-easing-standard` |
| Motion rest timer countdown | aucune animation (statique) |
| Z-index sticky header | `--z-raised` (10) |
| Z-index sticky jump bar | `--z-raised` |
| Z-index sticky CTA | `--z-sticky` (100) |
| Z-index rest timer flottant | `--z-sticky` |
| Font sans (titres, labels) | `--font-family-sans` |
| Font mono (métriques, inputs numériques) | `--font-family-mono` |
| Poids titre H1 | `--font-weight-bold` (700) |
| Poids body | `--font-weight-regular` (400) |
| Poids CTA / labels forts | `--font-weight-medium` (500) |
| Tailles typo | `--font-size-heading-1` (32px H1), `--font-size-body` (15px), `--font-size-body-sm` (13px meta), `--font-size-metric-lg` (40px pour weight display si mis en avant) |

**Tokens absents pouvant être requis (OQ à trancher) :**

- Aucun token de "state layer" (Material Design) — inutile V1, la modulation d'état passe par swap de background/border/color simple.
- Aucun token "elevation" au-delà de 3 niveaux d'ombre — suffisant V1.

## §8. Header reskin rules

- **Sticky préservé** : `position: sticky; top: 0;` déjà en place via `session-focus__sticky-header` — conservé
- **Hauteur compacte** : cible ≤ 88px de hauteur avec méta une ligne, badge status petit. Actuellement 3 lignes (titre + meta + progression + optional note) — condense possible en 2 lignes
- **Titre court** : `page-title` avec `--font-family-sans`, `--font-weight-bold`, `--font-size-heading-2` (24px) — pas `heading-1` (32px) pour laisser place aux méta
- **Truncate ellipsis** : `text-overflow: ellipsis; white-space: nowrap; overflow: hidden;` sur `page-title` si nom template long
- **État session lisible** : badge `.badge--in_progress` / `.badge--completed` avec `--color-accent-weak` (in_progress) / `--color-success-weak` (completed) — non alarmant
- **Retour discret** : lien `.back` (actuellement "← Accueil") repositionné dans le header, `--color-fg-muted`, taille `--font-size-body-sm`
- **Pas de gros logo** : header ne porte pas de wordmark SPIGNOS ni Auren — cohérent avec Sx_UI_03 §14
- **Pas de rebrand Auren code** : les strings texte ("Accueil", "En cours", "Séance terminée") restent inchangées, `Sx_UI_10` seule ownership du rebrand
- **Pas de JS requis** : le header reste 100% SSR, même le shadow au scroll (`--shadow-sm`) peut être appliqué via `position: sticky` + `box-shadow` conditionnel CSS si supporté ; sinon appliqué en permanence — la spec ne demande pas de scroll detection JS
- **Ordre visuel proposé** :
  1. Ligne 1 : `page-title` (nom template)
  2. Ligne 2 : meta compacte inline (weekday · timestamp · badge status · "X/Y sets")
  3. Ligne 3 conditionnelle : note "Séance terminée — éditable via *Rouvrir*." uniquement si `session.status == 'completed'`

## §9. Jump bar reskin rules

- **Rôle** : navigation intra-session, saut rapide entre exercices. Ancres `href="#exercise-{id}"`.
- **États visualisés (héritage Sx_29) :**
  - `active` : bordure teal accent 2px + poids typo `medium`, `aria-current="location"` optionnel
  - `done` : icône check (ou glyphe unicode) + couleur `--color-success` + `text-decoration: line-through` léger
  - `partial` : icône indicateur partiel + `--color-warning-weak` background
  - `pending` : neutre `--color-fg-muted`
  - `skipped` : `--color-warning` icône
  - `substituted` : `--color-signal` icône (bleu minéral) — cohérent §6
- **Scroll horizontal** : `overflow-x: auto;` + `scroll-snap-type: x mandatory;` conservé. Sur mobile 360×640, 4-5 items visibles max sans scroll ; scroll horizontal accessible sinon.
- **Tap target 44×44** : `min-width: 44px; min-height: 44px;` obligatoire sur chaque item — `session-focus__tap-target` déjà en place
- **Non-color cue** : chaque état porte un glyphe unicode ou une icône stroke, jamais uniquement une couleur (conformité WCAG 1.4.1)
- **`aria-current`** : sur l'item actif (`aria-current="location"` cohérent avec Sx_UI_03 §17 pour la bottom nav)
- **Pas d'animation défilement** : le scrollBy JS n'est pas ajouté ; le navigateur gère le smooth scroll natif via `scroll-behavior: smooth;` CSS (respecte `prefers-reduced-motion`)

## §10. Exercise card reskin rules

- **Hiérarchie** compacte (summary) :
  1. `exercise-card__code` (ex. `E5`) — `--font-family-mono`, `--font-size-body-sm`, `--color-fg-muted`
  2. `exercise-card__name` — `--font-family-sans`, `--font-weight-medium`, `--font-size-body`
  3. `exercise-card__progress` (`3/4`) — `--font-family-mono`, `tabular-nums`
  4. `exercise-card__recap` conditionnel (weights · reps résumé) — mono, `--color-fg-muted`
  5. `exercise-card__chip` conditionnel (briefing scheme) — badge selon convention Sx_UI_02 §18.4
- **États cards (hérités Sx_29, conservés) :**
  - `--pending` : neutre, opacité légèrement réduite (0.85), `--color-surface-alt`
  - `--active` : bordure gauche `4px solid var(--color-accent)` + `--color-surface` + card ouverte (`open` sur `<details>`)
  - `--partial` : dot `--color-warning` sur summary + `--color-surface`
  - `--done` : icône check `--color-success` + `text-decoration` léger sur nom
  - `--skipped` : nom `--color-fg-muted` + icône skip
  - `--substituted` : icône `--color-signal` + tag "modifié" discret
- **Input poids / reps lisibles :**
  - Padding généreux (`--space-3` block, `--space-4` inline), `min-height: 44px`
  - `font-size: 16px` minimum (anti-zoom iOS)
  - `--font-family-mono` sur la valeur
  - `--font-family-sans` sur label associé
  - Border `--color-border-default` au repos, focus `2px solid var(--color-accent-focus-ring)` outline
  - Placeholder `--color-fg-subtle` avec `≈ N kg` si `overload_placeholders[se.id]` (Sb_30.next.placeholder)
- **Actions secondaires discrètes** : boutons `substituer`, `voir historique`, `voir explanation` en `--color-fg-muted`, style `btn--ghost` avec `--font-weight-medium`, jamais dominants
- **Substitution accessible mais non dominante** : lien vers action présente dans une zone secondaire de la card (bas ou coin), jamais en CTA primaire
- **Badges Mesuré / Dérivé / Inféré / Hors de portée** : si présents dans un contexte donné, respect strict de la convention Sx_UI_02 §18.4 :
  - `Mesuré` → `--color-success-weak` fond + `--color-success-strong` texte
  - `Dérivé` → `--color-signal-weak` fond + `--color-signal-strong` texte
  - `Inféré` → `--color-accent-weak` fond + `--color-accent-strong` texte
  - `Hors de portée` → `--color-surface-alt` fond + `--color-fg-muted` texte
- **Aucune modification logique** : les conditions Jinja (`if is_active`, `if done > 0 and summary`, etc.) sont préservées verbatim. Le reskin travaille sur classes et tokens visuels, jamais sur `{% if %}`.

## §11. Set logging form rules

- **Friction ≤ actuelle** : le nombre d'étapes utilisateur pour logger une série ne peut pas augmenter. Cible : ≤ 3 secondes en usage réel (validation dogfood Sx_29 déjà atteinte).
- **Pas d'ajout de champ** : `set_{id}_weight_kg` et `set_{id}_reps` restent les seuls inputs V1. Aucun nouveau champ (RPE, tempo, notes) introduit par le reskin.
- **Pas de modal obligatoire** : le formulaire reste inline dans la card, jamais dans une modal ou une sheet — préserve one-hand reach.
- **Submit accessible** :
  - Sur mobile : sticky CTA visible en bas de viewport (cf. §13)
  - Sur desktop : bouton submit intégré au bas de la card active
- **Focus visible** : `outline: 2px solid var(--color-accent-focus-ring); outline-offset: 2px;` (jamais `outline: none`)
- **Layout mobile one-hand** : les inputs se trouvent dans la zone atteignable au pouce (haut ≤ 75% du viewport), le CTA en zone basse (avec safe-area respectée)
- **No-JS fallback identique** : `<form method="post" action="{{ url_for('update_exercise_card', ...) }}">` reste standard HTML POST. Aucun JS requis pour soumettre.
- **Auto-focus optionnel** : le focus au premier input non rempli de la card active peut rester (déjà présent Sx_29 ?) ou être ajouté par patch trivial JS, jamais bloquant.

## §12. Rest timer rules

- **Préserver `data-start-rest`, `data-rest-duration`, `data-rest-skip`, `data-rest-display`** — contrat JS invariant (`session_focus.js` doit continuer à fonctionner sans patch, ou avec patch trivial classes CSS uniquement)
- **Préserver JS enhancement** : countdown vanilla, aucune régression sur `setInterval` cleanup, aucune notification sonore/push ajoutée V1
- **Fallback HTML lisible** : `"Repos suggéré : 90s"` reste visible et lisible sans JS
- **Motion réduite** : aucune animation nouvelle. Le countdown reste un remplacement de texte (`60s → 45s → 30s`), pas une animation ring/circulaire. `prefers-reduced-motion` déjà respecté (aucun impact).
- **État actif non agressif** :
  - Container `session-focus__rest-timer` : `--color-surface` + `--color-border-default` + `--radius-md`, aucune pulsation
  - Label "Repos suggéré :" en `--font-family-sans`, `--color-fg-muted`
  - Countdown en `--font-family-mono`, `--font-weight-medium`, `--color-fg-strong`
  - Bouton "Skip rest" en `btn--ghost` avec `--color-fg-muted` — cliquable mais discret
- **Aucune notification sonore/push V1** — hors-scope, réservé à un futur `Sx_UI_08` (Portability) ou spec dédiée

## §13. Sticky CTA rules

- **Rôle** : bouton submit primaire toujours accessible sur mobile pendant le scroll de la card active — "Logger" ou "Continuer"
- **Visible sans masquer contenu** :
  - Le body scroll doit avoir un `padding-bottom` ≥ hauteur sticky CTA + `env(safe-area-inset-bottom)` + éventuelle bottom nav (cf. §14)
  - Le sticky CTA ne recouvre jamais le dernier input de la card active
- **Safe-area bottom** : `padding-bottom: env(safe-area-inset-bottom);` obligatoire — hérité Sx_29 (Sb_29.3)
- **Conflit avec future bottom nav** (cf. §14 et OQ-AD) :
  - Si bottom nav visible pendant focus mode : sticky CTA + bottom nav empilés, empilement CSS via `bottom: calc(env(safe-area-inset-bottom) + var(--bottom-nav-height));`
  - Si bottom nav absente pendant focus mode : sticky CTA se colle à `bottom: 0;` avec safe-area seule
- **Desktop non sticky si inutile** : sur ≥ 1024px, le CTA reste intégré au bas de la card active dans le flux normal, pas de sticky (rail latéral remplace la navigation, viewport haut permet de voir le CTA sans sticky)
- **Tap target 44×44** : `min-height: 44px; min-width: 44px;` obligatoire
- **Style** : `--color-accent-strong` background, `--color-on-accent` texte, `--font-weight-medium`, `--radius-md`, `--shadow-sm` très discret

## §14. Bottom nav during session

**Deux options considérées (rappel de Sx_UI_03 §13) :**

- **Option V1a** : bottom nav visible mais **très discrète** pendant session (opacité réduite ou hauteur légèrement réduite), destination Séance active avec point teal.
- **Option V1b** : bottom nav **absente** pendant focus mode, remplacée par une "persistent resume affordance" ailleurs (banner Today ou similaire).

**Décision V1 (recommandation cette spec) : Option V1a — bottom nav visible mais discrète.**

**Rationale :**

1. **Cohérence Sx_UI_03** : la bottom nav est présentée comme le shell canonique de l'app authentifiée. La faire disparaître pendant la surface la plus utilisée créerait une exception à cadrer.
2. **One-hand reach** : sur mobile, un utilisateur peut vouloir vérifier son profil ou sa progression sans quitter formellement la séance. La nav reste accessible, la session n'est pas "perdue".
3. **Non-invasif** : rendue discrète (opacité ~0.7 au repos, plein contrast au tap), la nav ne compête pas avec le focus mode.
4. **Session active indicator** : le point teal sur la destination "Séance" rappelle que la session est en cours — cohérent §13 Sx_UI_03 (aria-label "Séance, en cours").

**Implémentation cible :**

- Bottom nav CSS opacité `0.7` par défaut pendant focus mode (variable `--session-focus-nav-opacity`)
- Full opacité `1` au `:hover`, `:focus-within`, `:active`
- Hauteur légèrement réduite : ~52px au lieu de ~64px standard
- Sticky CTA se positionne **au-dessus** de la bottom nav (empilement : safe-area bottom → bottom nav → sticky CTA)
- Aucune JS d'auto-hide — CSS-only

**Alternative Option V1b** ouverte comme OQ-AC si dogfood futur montre que la bottom nav visible perturbe le flow. Réversibilité facile CSS-only.

## §15. Mobile layout rules

- **Viewport principal** : 360×640 (référence Sx_UI_03 §19 baseline)
- **Safe-area** : `env(safe-area-inset-bottom)` sur sticky CTA + bottom nav, `env(safe-area-inset-top)` sur sticky header
- **Aucun horizontal scroll** : `overflow-x: hidden;` sur body ; tout composant s'adapte au viewport, aucun élément fixe > 100vw
- **CTA et nav ne se chevauchent pas** : empilement §14 respecté, padding-bottom du body inclut CTA + nav + safe-area
- **Cards lisibles** : padding `--space-5` (24px), gap intra `--space-3` (12px), text ≥ 15px
- **Inputs accessibles** : `min-height: 44px`, `font-size: 16px` minimum, focus outline visible
- **Reach one-hand** : CTA primaire dans la zone atteignable (bas du viewport), navigation dans la zone atteignable (bottom nav en bas)

## §16. Desktop layout rules

- **Max-width** contenu focus mode : `640px` centré sous le rail Sx_UI_03 (cohérent §16 Sx_UI_03)
- **Rail desktop cohérent** avec Sx_UI_03 : rail à gauche fixe, destination Séance active avec point teal
- **Cards non étirées** : la carte ne prend pas toute la largeur du viewport, se limite à ~640px pour préserver l'ergonomie mobile
- **Whitespace** : marge horizontale `--space-6` (32px) entre rail et contenu, `--space-6` verticalement entre sections
- **Pas de dashboard dense** : le desktop ne devient pas une opportunité de tout afficher. Même hiérarchie one-decision-per-screen que mobile.
- **Sticky CTA** non appliqué desktop (cf. §13) — le CTA reste dans le flux normal de la card active

## §17. Accessibility

- **WCAG 2.2 tap targets 44×44** — obligatoire sur tous les boutons, links, inputs interactifs
- **Focus visible** : `outline: 2px solid var(--color-accent-focus-ring); outline-offset: 2px;` — jamais `outline: none`
- **`aria-current="location"`** sur jump bar item actif
- **`aria-current="page"`** sur bottom nav destination Séance quand active
- **Label inputs** : chaque input a un `<label for>` ou `aria-label` explicite. `field_group` macro (existante) gère ça — vérifier consommation en Sb_UI_04.3.
- **Non-color cues** : chaque état (done, active, substituted, skipped) porte un signal non-coloré (icône, weight typo, `text-decoration`)
- **Contrast** : palette teal candidate `#0F8A85` a un contraste 5.0:1 vs `#FFFFFF` (AA body OK). Vérification finale à `Sb_UI_04.1` merge.
- **Reduced motion** : `@media (prefers-reduced-motion: reduce)` — transitions ramenées à `0ms`, `scroll-behavior: auto`
- **Keyboard path** :
  - Skip link `<a href="#main-content" class="skip-link">` en premier tab
  - Tab order logique : header → jump bar → carte active → CTA → bottom nav
  - Enter sur jump bar item → scroll vers exercice cible
  - Escape optionnel pour retour au sommet (V1 : non requis, gestion navigateur natif suffit)

## §18. Screenshot baseline dependency

Rappel des screenshots P0 requis avant tout code `Sb_UI_04.k` (cf. `Sx_UI_11 §5` matrice, §14 dépendance) :

| # | Écran | Route | Viewport mobile | Viewport desktop |
|---|---|---|---|---|
| 1 | Home / Today (avec active session) | `/` | ✅ | ✅ |
| 2 | Session detail active | `/sessions/{id}` (in_progress) | ✅ | ✅ |
| 3 | Session detail done | `/sessions/{id}` (completed) | ✅ | ✅ |
| 4 | Progression | `/progress` (avec historique) | ✅ | ✅ |
| 5 | Profil | `/profile` | ✅ | ✅ |
| 6 | Login | `/login` | ✅ | ✅ |
| 7 | Register | `/register` | ✅ | ✅ |

**Total baseline P0 : 7 écrans × 2 viewports = 14 screenshots minimum.**

**Le build futur `Sb_UI_04.k` ne peut pas commencer sans :**

- Ces 14 screenshots P0 capturés via `Sb_UI_11.1` (screenshot tooling build)
- **OU** dérogation opérateur explicite documentée dans un sprint override léger (comme `Sb_28.override-build-authorization`)

**Rationale de la règle stricte :**

Sans baseline, la review humaine du reskin devient "à l'aveugle". Impossible de comparer avant/après pour valider que :
- le mode session détail active reste utilisable
- le empty state du login reste identifiable
- la carte "Lecture corporelle" du profile n'est pas cassée
- la home avec active session reste fonctionnelle

## §19. Build plan proposal

Découpe future proposée pour le build `Sb_UI_04.k`. **Aucun sous-sprint n'est ouvert dans Sx_UI_04.** L'opérateur ouvre chaque `Sb_UI_04.k` sur override explicite, en séquence.

| Sub-sprint | Objet | Fichiers touchés (autorisés) | Contrainte |
|---|---|---|---|
| `Sb_UI_04.1` | **CSS foundation session focus** : introduire CSS custom properties tokens (Sx_UI_02) dans `session_focus.css`, mapper les tokens de §7, appliquer la palette teal + clinical white sur le container racine, préparer variables `--session-focus-*` locales | `app/static/css/session_focus.css` uniquement | Baseline P0 comparée avant/après. Aucun template modifié. Ruff budget respecté. |
| `Sb_UI_04.2` | **Header + jump bar reskin** : appliquer §8 (header) + §9 (jump bar) sur `session_focus_header.html` structure + CSS étendu | `session_focus_header.html` (structure), `session_focus.css` (styles) | Aucun changement de logique conditionnelle Jinja. Aucun changement de macro. |
| `Sb_UI_04.3` | **Exercise cards + set logging** : appliquer §10 (cards) + §11 (set logging) sur `exercise_card.html` structure + CSS étendu | `exercise_card.html` (structure), `session_focus.css` (styles), `app.css` (uniquement classes partagées `.badge`, `.btn`, `.field-group` référencées) | Aucun changement de champs form. Aucun changement de macro `field_group`. |
| `Sb_UI_04.4` | **Rest timer + sticky CTA** : appliquer §12 (rest timer) + §13 (sticky CTA) + §14 (bottom nav during session) | `rest_timer.html` (structure), `session_detail.html` (wrapper + bottom nav integration), `session_focus.css` (styles), éventuellement patch trivial `session_focus.js` (classes CSS uniquement, contrat JS invariant) | JS contract invariant. No-JS fallback intact. |
| `Sb_UI_04.5` | **Mobile / desktop / a11y polish + closure report** : audit final §15-§17, ajustements finaux, tests visuels, dogfood template, sprint closure | `session_focus.css`, tests visuels si ajoutés dans `tests/`, docs closure | Ruff, ID/hash CSS budget, dogfood template dans `docs/dogfood/`. |

**Chaque sous-sprint devra :**

- Toucher uniquement le périmètre autorisé
- Garder services métier intacts (sanity `git diff --name-only app/services/ app/routers/ app/models/` = vide)
- Lancer CI complète au push (aucun `paths-ignore` — le sprint touche du code)
- Comparer screenshots avant/après si baseline disponible (via `Sb_UI_11.1` livré)
- Ne pas ouvrir le sous-sprint suivant automatiquement

**Ordre strict :** `Sb_UI_04.1` → `Sb_UI_04.2` → `Sb_UI_04.3` → `Sb_UI_04.4` → `Sb_UI_04.5`. Chaque sub-sprint doit être accepté avant le suivant.

## §20. Open Questions

Rappel des OQ liées au reskin session focus + résolutions V1.

| OQ | Question | Recommandation V1 (cette spec) | Statut |
|---|---|---|---|
| **OQ-R** | Progression sous-nav — reporté hors Sx_UI_04 ou tranché si nécessaire ? | **reporté** hors Sx_UI_04 (le focus mode ne concerne pas Progression). Reste à trancher dans `Sx_UI_05` (Today/Home) ou `Sx_UI_07` (History/Progress). | ✅ tranché (reporté) |
| **OQ-H** | hex final exact `#0F8A85` ou ajustement ? | **`#0F8A85` retenu V1**, ajustable en `Sb_UI_04.1` merge si contraste réel écran < 4.5:1 sur mesure device. Validation dogfood mobile. | ⚠️ à confirmer `Sb_UI_04.1` |
| **OQ-I** | font sans final ? | **stack système** par défaut V1 (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`). Web font Inter reportée à `Sx_UI_08` (Portability/PWA) pour éviter FOIT et charge réseau au premier reskin. | ✅ tranché V1 |
| **OQ-J** | font mono final ? | **stack système** par défaut V1 (`"SF Mono", ui-monospace, monospace`). Web font JetBrains Mono reportée à `Sx_UI_08`. | ✅ tranché V1 |
| **OQ-K** | fluid clamp() vs tailles fixes ? | **tailles fixes V1** avec media query `@media (max-width: 380px)` pour très petit mobile. `clamp()` reporté à `Sb_UI_04.5` polish si nécessaire. | ✅ tranché V1 (réversible) |
| **OQ-M** | Style Dictionary vs custom naming ? | **custom naming** V1 (convention Sx_UI_02 §4 respectée). Style Dictionary reporté si le tokenset s'étend au-delà des specs UI actuelles. | ✅ tranché V1 |
| **OQ-AC** | bottom nav visible ou cachée pendant focus mode ? | **visible mais discrète** (Option V1a, §14). Réversible en `Sb_UI_04.4` si dogfood montre friction. | ✅ tranché V1 |
| **OQ-AD** | sticky CTA + bottom nav coexistence ? | **empilement CSS** : sticky CTA au-dessus de bottom nav, hauteurs cumulées ajoutées au padding-bottom du body. | ✅ tranché V1 |
| **OQ-AE** | quels fichiers app.css vs session_focus.css pour éviter fuite globale ? | **session_focus.css uniquement** pour tout ce qui est scoped au focus mode. `app.css` uniquement pour les classes partagées existantes (`.badge`, `.btn`, `.field-group`) qui reçoivent un patch **minimal et non-breaking** si nécessaire. | ✅ tranché V1 |
| **OQ-AF** | baseline P0 obligatoire ou override ? | **obligatoire V1**, dérogation opérateur explicite documentée reste autorisée si opérateur décide de démarrer `Sb_UI_04.1` sans baseline. Non recommandé mais possible. | ✅ tranché V1 |

## §21. Non-goals

- Pas de code (aucun fichier `app/`, `tests/`, `migrations/`, `scripts/`, `.github/` modifié)
- Pas de CSS applicatif modifié
- Pas de template modifié (`session_detail.html`, `_partials/*.html` intacts)
- Pas de JS modifié
- Pas d'asset (icône, image, police web) ajouté
- Pas de route ajoutée / modifiée / redirigée
- Pas de modèle SQLAlchemy modifié
- Pas de migration Alembic
- Pas de service métier touché : **scoring, overload_engine, overload_inputs, overload_explainer, substitution, coach_report, coach_inference, body_intelligence, body_intelligence_inputs, recommendation, implicit_signal, quality_score, body_tracking — intacts**
- Pas de Playwright installé
- Pas de screenshot capturé
- Pas de fixture DB créée
- Pas de rebrand code (SPIGNOS reste dans les templates)
- Pas de logo, favicon, manifest modifié
- Pas de build (`Sb_UI_04.k` non ouvert)
- Pas de test structurel visuel ajouté (relève de `Sb_UI_04.5` + `Sx_UI_11` baseline)
- Pas d'ouverture de `Sx_UI_05` (Today) / `Sx_UI_06` / `Sx_UI_07` / `Sx_UI_08` / `Sx_UI_09` / `Sx_UI_10` / `Sb_UI_11.1`
- Pas de flag toggle modifié

## §22. Acceptance criteria

La spec est acceptable si :

- ✅ Périmètre futur build clair (§5 : 7 fichiers autorisés avec niveau de risque et scope de changement)
- ✅ Fichiers candidats mappés (§5)
- ✅ Invariants métier verrouillés (§4 : services, routes, models, migrations intacts ; contrats JS et macros Jinja préservés)
- ✅ Token consumption mappé exhaustivement (§7 : ~30 rôles → tokens Sx_UI_02, aucun nouveau token)
- ✅ Header (§8), jump bar (§9), cards (§10), set logging (§11), rest timer (§12), sticky CTA (§13) cadrés
- ✅ Bottom nav during session tranchée (§14, Option V1a, réversible)
- ✅ Mobile (§15) + desktop (§16) layout rules
- ✅ Accessibility (§17) : WCAG 2.2 44×44, focus visible, `aria-current`, non-color cues, `prefers-reduced-motion`, keyboard path
- ✅ Baseline dependency explicite (§18 : 14 P0 requis ou dérogation)
- ✅ Build plan proposé (§19 : 5 sous-sprints `Sb_UI_04.1` → `Sb_UI_04.5`)
- ✅ OQ list complète (§20 : 10 OQ, 9 tranchées V1, 1 à confirmer merge)
- ✅ Aucun code touché (§21 non-goals)

## §23. Build authorization status

**BUILD NOT AUTHORIZED.**

**Sx_UI_04 build (`Sb_UI_04.k`) remains BLOCKED until :**

1. **`Sx_UI_04` spec accepted** — human review post-livraison
2. **`Sx_UI_11` P0 baseline available** via `Sb_UI_11.1` (screenshot tooling build) livré
3. **OR** — **explicit operator override** documented (sprint override léger comme `Sb_28.override-build-authorization`)

**Non autorisé sans les préconditions ci-dessus :**

- Ouverture de `Sb_UI_04.1_CSS_FOUNDATION_BUILD`
- Ouverture de `Sb_UI_04.2_HEADER_JUMP_BAR_BUILD`
- Ouverture de `Sb_UI_04.3_EXERCISE_CARDS_BUILD`
- Ouverture de `Sb_UI_04.4_REST_TIMER_STICKY_CTA_BUILD`
- Ouverture de `Sb_UI_04.5_POLISH_A11Y_CLOSURE_BUILD`

**Toute modification `app/static/css/session_focus.css`, `app/templates/session_detail.html`, `app/templates/_partials/session_focus_*`, ou `app/static/js/session_focus.js` interdite dans le repo tant que build non autorisé.**

## §24. Final verdict

**READY FOR HUMAN REVIEW.**

---

## Références

- **Spec précédente :** `docs/strategy/Sx_UI_11_SCREENSHOT_REGRESSION_BASELINE_SPEC.md` ✅ accepted
- **Specs avant :** `docs/strategy/Sx_UI_03_APP_SHELL_NAVIGATION_SPEC.md`, `docs/strategy/Sx_UI_02_DESIGN_TOKENS_SPEC.md`, `docs/strategy/Sx_UI_01_BRAND_FOUNDATION_SPEC.md` ✅ accepted
- **Focus mode précurseur (source du diagnostic §3) :** `docs/strategy/Sx_29_CLOSURE_REPORT.md` + `docs/dogfood/DOGFOOD_Sx_29_FOCUS_MODE_TEMPLATE.md`
- **Sprint reports Sx_29 pour trace des choix structurels :** `docs/SPRINT_Sb_29_1_REPORT.md` (partials extraction), `docs/SPRINT_Sb_29_5_REPORT.md` (extraction `session_focus.css`)
- **Fichiers lus en read-only pour §3 :** `app/static/css/session_focus.css` (547 lignes), `app/templates/_partials/session_focus_header.html`, `app/templates/_partials/exercise_card.html`, `app/templates/_partials/rest_timer.html`, `app/static/js/session_focus.js`
- **Roadmap cycle :** `docs/strategy/UI_TRANSFORMATION_ROADMAP.md`
- **Registry :** `docs/strategy/SPEC_REGISTRY.md` §1quinquies
- **Roadmap globale :** `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`
- **CI cost optimization :** `docs/SPRINT_Sb_OPS_ci_path_filter_BUILD_REPORT.md` — path filter opérationnel, ce push docs-only skippera la CI (7ᵉ consécutif attendu)
