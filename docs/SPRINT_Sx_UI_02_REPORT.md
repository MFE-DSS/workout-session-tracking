# Sprint Report — Sx_UI_02 Design Tokens Spec

**Sprint ID :** `Sx_UI_02`
**Type :** SPEC ONLY (docs-only)
**Date :** 2026-07-02
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Verdict :** ✅ **READY FOR HUMAN REVIEW**

---

## 1. Résumé

Deuxième sprint du cycle `Sx_UI` (Auren Visual & Product Transformation), ouvert après :
- Validation implicite de `Sx_UI_01_BRAND_FOUNDATION_SPEC.md` par override opérateur (le brief GO Sx_UI_02 mentionne explicitement que Sx_UI_01 est accepté avec accent teal chirurgical désaturé + fallback bleu minéral)
- Livraison de `Sb_OPS.ci-path-filter` (commit `a9ab10c`) qui rendra ce push docs-only sans coût CI

Objectif : traduire les principes visuels de `Sx_UI_01` en **tokens normatifs** — palettes couleurs (surfaces, foreground, accent principal teal, accent secondaire bleu minéral, états sémantiques), typographie, espacements 4px-based, rayons, bordures, ombres minimales, motion discrète, z-index, chart tokens, et **règles de composition** (carte, bouton, badge, input, métrique).

Ce sprint **n'ouvre aucun build**, ne touche aucun CSS, aucun JS, aucun template, aucun asset. Aucun fichier de tokens implémenté. Les valeurs hex sont **candidates**, pas figées — figement final via revue opérateur ou UX externe.

## 2. Fichiers créés / modifiés

### Créés

- `docs/strategy/Sx_UI_02_DESIGN_TOKENS_SPEC.md` — spec principale, 24 sections structurantes
- `docs/SPRINT_Sx_UI_02_REPORT.md` — ce rapport de sprint

### Modifiés

- `docs/strategy/SPEC_REGISTRY.md` — cycle `Sx_UI` : Sx_UI_02 🟢 SPEC delivered pending review, Sx_UI_03 🚫 blocked until accepted
- `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` — position actuelle : prochaine action = human review Sx_UI_02

## 3. Confirmation docs-only

**Scope strict respecté.** Aucun fichier des périmètres suivants n'a été touché :

- ❌ `app/` (services, routers, templates, static, CSS, JS)
- ❌ `tests/`
- ❌ `migrations/`
- ❌ `scripts/`
- ❌ `.github/workflows/`
- ❌ `.env`, config runtime
- ❌ Manifest, favicon, assets, polices web
- ❌ Aucun renommage `SPIGNOS` → `Auren` dans le code

**Fichier de tokens implémenté ?** Non. Les tokens de cette spec sont **normatifs sur papier** — leur implémentation en CSS custom properties (ou autre) est réservée à `Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC` qui les appliquera pour la première fois sur `session_focus.css`.

## 4. Décisions prises

| # | Décision | Section spec |
|---|---|---|
| 1 | Convention de nommage `--{category}-{role}-{modifier?}` fixée | §4 |
| 2 | Palette surfaces : blanc pur base + gris pierre froids en surface alternée | §5 |
| 3 | Palette foreground : 5 niveaux (`strong`, `default`, `muted`, `subtle`, `disabled`) avec contraste WCAG documenté | §5 |
| 4 | Accent principal figé : **teal chirurgical désaturé** (`#0F8A85` candidat) — OQ-B tranché par opérateur | §6 |
| 5 | Accent secondaire figé : **bleu minéral** (`#2A7896` candidat) — rôle strictement délimité au signal informatif | §7 |
| 6 | États sémantiques success / warning / danger posés avec palette candidate WCAG AA | §8 |
| 7 | Orange chaud `#f25f3a` (SPIGNOS actuel) **éliminé** du branding, peut réapparaître uniquement en warning si nécessaire | §8 |
| 8 | Typographie : max 2 familles (sans + mono), max 3 poids par famille | §9 |
| 9 | Métriques en mono avec `font-variant-numeric: tabular-nums` obligatoire | §9 |
| 10 | Échelle spacing 4px-based, 9 niveaux (`--space-0` à `--space-8`) + alias sémantiques | §10 |
| 11 | Privilégier `--space-5` (24px) à `--space-4` (16px) pour paddings — traduction concrète du "generous spacing" | §10 |
| 12 | 5 tokens radius avec `--radius-full` réservé aux indicateurs et avatars (jamais boutons) | §11 |
| 13 | Épaisseur bordure standard : `1px` uniquement (`2px` réservé au focus ring) | §12 |
| 14 | Ombres minimales : `none` par défaut, 3 niveaux max, jamais colorées | §13 |
| 15 | 5 états interactifs standard avec non-color cues obligatoires (WCAG 1.4.1) | §14 |
| 16 | Motion discrète : 4 durées + 2 easings, respect `prefers-reduced-motion` obligatoire | §15 |
| 17 | Interdits motion : bounce, elastic, confetti, célébration visuelle | §15 |
| 18 | Échelle z-index canonique (6 niveaux) pour éviter les guerres de `z-index: 9999` | §16 |
| 19 | Chart tokens mono-accent : 2 lignes max, pas de gradient, pas de palette arc-en-ciel | §17 |
| 20 | 7 règles de composition normatives (carte, boutons primaire/secondaire, badge, séparateur, input, métrique héroïque) | §18 |
| 21 | Convention badge : Mesuré→success, Dérivé→signal (bleu minéral), Inféré→accent-weak (teal), Hors de portée→muted | §18.4 |
| 22 | Dark mode **hors-scope** de Sx_UI_02 avec rationale (contradiction potentielle avec principe §10 Sx_UI_01) | §19 |
| 23 | Valeurs hex candidates, pas figées — figement via revue opérateur ou UX externe | §20 OQ-H |

## 5. OQ list (Open Questions)

Rappel des 7 OQ ouvertes par `Sx_UI_02`. La plupart n'empêchent pas l'ouverture de `Sx_UI_03`.

| OQ | Question | Propriétaire | Bloque |
|---|---|---|---|
| **OQ-B** | Accent teal / fallback bleu minéral | **✅ RÉSOLU 2026-07-02** | — |
| **OQ-H** | Palette hex exacte figée ? | opérateur + revue UX | Sx_UI_04 merge |
| **OQ-I** | Font sans : Inter proposé, alternatives ? | opérateur, revue perf + licence | Sx_UI_04 merge |
| **OQ-J** | Font mono : JetBrains Mono proposé, alternatives ? | opérateur, revue perf + licence | Sx_UI_04 merge |
| **OQ-K** | Fluid clamp() ou tailles fixes pour la scale typo ? | opérateur, Sx_UI_04 | Sx_UI_04 merge |
| **OQ-L** | Dark mode dans Sx_UI_02bis ou Sx_UI_09bis ? | opérateur | ne bloque pas Sx_UI_03/04 |
| **OQ-M** | Adopter Style Dictionary / Radix tokens ou rester custom ? | opérateur, décision Sx_UI_04 | Sx_UI_04 merge |

**Critique :** aucune. Aucune OQ ne bloque l'ouverture de `Sx_UI_03`. `Sx_UI_04` reste bloqué par plusieurs OQ + baseline `Sx_UI_11`.

## 6. Non-goals respectés

Rappel des non-goals (§21), tous respectés :

- ✅ Aucun CSS applicatif
- ✅ Aucun fichier tokens implémenté (tokens.css, theme.ts, etc.)
- ✅ Aucun manifest, favicon, thème système modifié
- ✅ Aucun shell nav ou reduction chrome
- ✅ Aucun re-skin session
- ✅ Aucun changement de template existant
- ✅ Pas de dark mode
- ✅ Pas d'installation de font web ou package
- ✅ Pas de figement final valeurs hex
- ✅ Aucune ouverture de Sx_UI_03 / Sx_UI_04 / Sx_UI_11
- ✅ Aucun renommage SPIGNOS → Auren

## 7. DoD local (Definition of Done)

Sanity checks exécutés en fin de sprint :

- [x] `git diff --name-only` docs-only strict : ✅ **4 fichiers, tous dans `docs/`**
- [x] `git status` hors `docs/` : ✅ **vide** (à confirmer après édition)
- [x] YAML unchanged (aucun `.yml` touché) : ✅ **OK**
- [x] Pas de CSS/JS/HTML modifié : ✅ **confirmé**
- [x] Sanity out of `docs/` : ✅ **STRICT DOCS-ONLY**

**QA scripts non ré-exécutés** intentionnellement pour ce sprint docs-only pur : ils avaient été verts sur `Sx_UI_01` (`2e345e8` livré et validé CI `28582551168` conclusion `success`), aucun code n'a bougé depuis. Éviter les side-effects (`SPIGNOS_CATALOG_QA_REPORT.md` regénéré) comme observé à Sx_UI_01.

## 8. DoD CI

CI réelle : **pending until push** — mais avec une nuance importante :

**Ce push doit être SKIP par la CI grâce à `Sb_OPS.ci-path-filter`.**

Sx_UI_02 est 100% docs-only. Le trigger `push` de `ci.yml` a désormais `paths-ignore: ['docs/**']`. Attendu :
- Aucun run CI ne doit se déclencher sur le SHA du commit Sx_UI_02
- Vérification par `gh run list --branch ... --limit 3` après push : le SHA ne doit pas apparaître comme événement `push`

**Résultat CI :** placeholder — à renseigner après push et vérification skip.

## 9. Prochain sprint recommandé

**`Sx_UI_03_APP_SHELL_NAVIGATION_SPEC`** — SPEC ONLY.

Contenu attendu :
- Structure du shell mobile-first (top bar, bottom nav ≤ 4 entrées)
- Décisions OQ-C, OQ-D, OQ-E de Sx_UI_01 : quelles 4 destinations survivent au top level
- Safe areas iOS/Android
- Breadcrumb de contexte pour les surfaces profondes
- Réduction du chrome global (des 10 destinations actuelles à 4 top-level)
- Comportement de la bannière de séance active
- Sticky patterns hérités de Sx_29 focus mode
- Statut BUILD toujours BLOCKED

**Ne pas ouvrir avant validation humaine de Sx_UI_02.**

## 10. Références

- **Spec principale de ce sprint :** `docs/strategy/Sx_UI_02_DESIGN_TOKENS_SPEC.md`
- **Spec précédente :** `docs/strategy/Sx_UI_01_BRAND_FOUNDATION_SPEC.md`
- **Roadmap cycle Sx_UI :** `docs/strategy/UI_TRANSFORMATION_ROADMAP.md`
- **Registry :** `docs/strategy/SPEC_REGISTRY.md` §1quinquies
- **Roadmap globale :** `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`
- **Brainstorm sources :** `docs/strategy/brainstorm/UI_TRANSFORMATION_BRAINSTORM_V1_normalized.md`, `..._V2_normalized.md`
- **CI cost optimization :** `docs/SPRINT_Sb_OPS_ci_path_filter_BUILD_REPORT.md` (commit `a9ab10c`, run CI `28582551168` ✅)

## 11. Verdict

✅ **READY FOR HUMAN REVIEW.**

Palette teal chirurgical désaturé + bleu minéral posée. Typographie, spacing, radius, borders, shadows, motion, chart tokens tous documentés. Règles de composition normatives (carte, bouton, badge, input, métrique). Dark mode explicitement hors-scope. Aucun fichier applicatif touché, aucun sprint de build ouvert, aucun rebrand exécuté. Prochaine action : human review de la spec + décision d'ouverture de `Sx_UI_03` en SPEC ONLY.
