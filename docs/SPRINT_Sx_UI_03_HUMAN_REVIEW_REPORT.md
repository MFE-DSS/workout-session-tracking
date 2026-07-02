# Sx_UI_03 — Human Review Report

**Spec :** `docs/strategy/Sx_UI_03_APP_SHELL_NAVIGATION_SPEC.md`
**Sprint report source :** `docs/SPRINT_Sx_UI_03_REPORT.md`
**Commit spec :** `b3ae3a9afbd1b8819ec671b5f697350b5280574e`
**Date review :** 2026-07-02
**Reviewer :** opérateur (Martin Feldmann)
**Verdict :** ✅ **SPEC ACCEPTED**

---

## 1. Verdict

**Sx_UI_03 App Shell Navigation Spec est accepté en human review.**

La spec devient la source de vérité normative pour toute décision de navigation dans le cycle `Sx_UI`. Tout sprint aval (`Sx_UI_04` → `Sx_UI_11`) doit respecter la hiérarchie des destinations, le placement contextualisé de Coach, la rétrogradation de Squads/Classement, et les règles mobile/desktop/accessibility définies. Toute exception nécessite un amendement `Sx_UI_03bis`.

## 2. Décisions validées

### 2.1. Bottom nav mobile V1 — 4 entrées

| Ordre | Destination | Rôle |
|---|---|---|
| 1 | **Séance** | Point d'entrée quotidien (Today + reprise session active) |
| 2 | **Programmes** | Bibliothèque templates + planification |
| 3 | **Progression** | Historique + Physique + Coach insights absorbés |
| 4 | **Profil** | Compte + Squads + Classement + settings + Déconnexion |

### 2.2. Mapping surfaces validé

| Actuel | Futur Auren V1 |
|---|---|
| Accueil (`/`) | Absorbé conceptuellement par **Séance / Today**, route `/` conservée V1 |
| Historique | Sous-section de **Progression** |
| Physique | Sous-section de **Progression** |
| Coach | **Contextualisé** : Séance, Progression, Session done (pas top-level) |
| Squads | Surface secondaire opt-in dans **Profil** |
| Classement | Surface secondaire opt-in dans **Profil** |
| Déconnexion | Action en fin de liste dans **Profil** |

### 2.3. Layout desktop

- **Rail latéral gauche** à partir de ≥ 1024px
- Bottom nav mobile en dessous de 1024px
- Cohérence : mêmes 4 destinations, mêmes noms, mêmes ordres

### 2.4. Session active pattern

- **Bloc dominant** sur Séance/Today quand active (teal accent)
- **Point teal** dans bottom nav "Séance" (`--color-accent`, `--radius-full`, 6×6px)
- Screen reader : `aria-label="Séance, en cours"`
- ❌ Jamais bannière modale, jamais orange, jamais notification, jamais vibration

### 2.5. Contraintes de non-modification

- **Aucun nouveau token visuel** — consommation stricte de `Sx_UI_02`
- **Aucun code applicatif touché**
- **Aucun template modifié** (lecture read-only autorisée pour diagnostic §3 uniquement)
- **Aucun CSS / JS / asset** produit ou modifié
- **Build UI toujours bloqué** (`Sx_UI_04` reste en attente)

## 3. OQ résiduelles non bloquantes

Les OQ suivantes restent ouvertes mais n'empêchent pas l'ouverture de `Sx_UI_11`. Elles seront tranchées avant `Sx_UI_04` merge (premier sprint code applicatif).

| OQ | Question | Propriétaire | Décision au plus tard |
|---|---|---|---|
| **OQ-R** | Organisation interne de Progression : sous-onglets SSR (URL `?tab=history`), sections empilées, ou `<details>` ? | opérateur, décision `Sx_UI_04` | `Sx_UI_04` merge |
| **OQ-H** | Palette hex finale exacte (valeurs candidates dans Sx_UI_02 §5-§8) | opérateur + revue UX | `Sx_UI_04` merge |
| **OQ-I** | Font sans final (Inter proposé, alternatives à évaluer) | opérateur, revue perf + licence | `Sx_UI_04` merge |
| **OQ-J** | Font mono final (JetBrains Mono proposé) | opérateur, revue perf + licence | `Sx_UI_04` merge |
| **OQ-K** | Fluid clamp() vs tailles fixes pour la scale typo | opérateur, décision `Sx_UI_04` | `Sx_UI_04` merge |
| **OQ-L** | Dark mode dans `Sx_UI_02bis` ou reporté à `Sx_UI_09bis` | opérateur | ne bloque pas Sx_UI_04/11 |
| **OQ-M** | Naming convention design token : Style Dictionary / Radix vs custom | opérateur, décision `Sx_UI_04` | `Sx_UI_04` merge |
| **OQ-A** | Due diligence juridique Auren (INPI + EUIPO + USPTO + domaines) | opérateur + juridique externe | **bloquant uniquement pour `Sx_UI_10`** (rebrand execution) — n'empêche pas Sx_UI_04-11 |

**OQ résolues dans Sx_UI_03 :** OQ-C, OQ-D, OQ-E, OQ-N, OQ-O, OQ-P, OQ-Q, OQ-S, OQ-T, OQ-U (10 OQ tranchées V1).

## 4. Confirmation docs-only

Ce sprint de review est **strictement documentaire**. Aucun périmètre applicatif touché :

- ❌ `app/` (aucun service, aucun router, aucun template, aucun static, aucun CSS, aucun JS)
- ❌ `tests/`
- ❌ `migrations/`
- ❌ `scripts/`
- ❌ `.github/workflows/`
- ❌ `.env`, config runtime, manifest, favicon
- ❌ Aucun fichier de tokens implémenté
- ❌ Aucun renommage `SPIGNOS` → `Auren` dans le code

Fichiers touchés dans le commit d'acceptance :

- `docs/strategy/SPEC_REGISTRY.md` — Sx_UI_03 ✅ ACCEPTED, Sx_UI_11 🟡 READY TO OPEN, Sx_UI_04 blocked until baseline
- `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` — prochaine action = GO Sx_UI_11 SPEC ONLY
- `docs/SPRINT_Sx_UI_03_HUMAN_REVIEW_REPORT.md` — ce rapport

## 5. Confirmation no build

**BUILD NOT AUTHORIZED.**

Aucune modification code applicatif autorisée par cette review. La navigation V1 définie dans `Sx_UI_03_APP_SHELL_NAVIGATION_SPEC.md` est normative **sur papier** et ne sera implémentée qu'à partir de `Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC` — sprint qui reste bloqué par :

1. `Sx_UI_03` ✅ accepté (cette review)
2. **`Sx_UI_11` baseline screenshots disponible** — précondition dure
3. OQ résiduelles Sx_UI_02 (OQ-H hex, OQ-I font sans, OQ-J font mono, OQ-K scale, OQ-M naming) tranchées
4. OQ résiduelle Sx_UI_03 (OQ-R sous-nav Progression) tranchée en début de Sx_UI_04

`Sx_UI_11` devient donc la **prochaine ouverture SPEC ONLY**, indispensable pour préparer la baseline visuelle avant tout reskin.

## 6. Prochaine action recommandée

**Ouvrir `Sx_UI_11_SCREENSHOT_REGRESSION_SPEC` en SPEC ONLY** sur override explicite opérateur.

Contenu attendu de Sx_UI_11 :

- **Outil retenu** (OQ-G de Sx_UI_01 à trancher) : Playwright vs Puppeteer vs snapshot-py vs autre
- **Viewports** : 360×640 mobile + 1440×900 desktop confirmés par Sx_UI_03 §19
- **Liste des 26 screenshots à produire** (13 écrans × 2 viewports), déjà cadrée par Sx_UI_03 §19
- **Stratégie DB** : empty state (approche recommandée V1) vs scénario de démo avec séances
- **Storage baseline** : git-tracked (versionné) vs artefact CI (référence server-side)
- **Convention nommage baseline** : convention pour identifier écran, viewport, breakpoint, version
- **Politique diff** : seuil de tolérance pixel, gestion polices non installées, gestion timestamps dynamiques
- **Statut BUILD toujours BLOCKED** — la spec reste docs-only, l'implémentation baseline arrive en `Sb_UI_11.k`

Ce prochain sprint bénéficiera du path filter `Sb_OPS.ci-path-filter` : push docs-only → aucun run CI complet.

## 7. Références

- Spec acceptée : `docs/strategy/Sx_UI_03_APP_SHELL_NAVIGATION_SPEC.md`
- Sprint report source : `docs/SPRINT_Sx_UI_03_REPORT.md`
- Roadmap cycle : `docs/strategy/UI_TRANSFORMATION_ROADMAP.md`
- Registry : `docs/strategy/SPEC_REGISTRY.md` §1quinquies
- Roadmap globale : `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`
- Specs précédentes acceptées : `docs/strategy/Sx_UI_02_DESIGN_TOKENS_SPEC.md`, `docs/strategy/Sx_UI_01_BRAND_FOUNDATION_SPEC.md`
- CI cost optimization : `docs/SPRINT_Sb_OPS_ci_path_filter_BUILD_REPORT.md` (validé sur 3 pushes docs-only consécutifs : `b4ed2c6`, `fdfd71a`, `b3ae3a9` — aucun run CI déclenché)

## 8. Verdict final

✅ **Sx_UI_03 SPEC ACCEPTED — READY FOR Sx_UI_11 SPEC ONLY.**
