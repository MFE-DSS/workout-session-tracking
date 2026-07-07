# Sx_UI_05 Today / Readiness Home — Human Review Report

**Spec :** `Sx_UI_05_TODAY_READINESS_HOME_SPEC`
**Spec source :** `docs/strategy/Sx_UI_05_TODAY_READINESS_HOME_SPEC.md`
**Sprint report source :** `docs/SPRINT_Sx_UI_05_REPORT.md`
**Commit spec :** `0d4be33`
**Type :** Human review docs-only (CI skippée — push docs-only via `paths-ignore: ['docs/**']`)
**Date review :** 2026-07-07
**Reviewer :** opérateur (Martin Feldmann)
**Verdict :** ✅ **SPEC ACCEPTED — Human Review PASS**

---

## 1. Verdict

**La spec `Sx_UI_05_TODAY_READINESS_HOME_SPEC` est acceptée en human review.**

Elle cadre le Home comme une **surface de décision quotidienne** (« quoi faire aujourd'hui »), pas un tableau de bord lourd. La readiness reste **honnête** (self-report existant 1-5, non médicale). Le data contract est **existing-data-only**. Le Home réutilise les acquis Sx_UI_04 sans rouvrir le Focus Mode. Le build split est clair en 5 sous-sprints, les non-goals sont explicites, et les 10 OQ sont tranchées.

## 2. Nature du sprint

Human review **docs-only**. Aucune CI lourde (commit spec `0d4be33` docs-only, correctement skippé par `paths-ignore: ['docs/**']` — aucun run CI créé). Aucun code, template, CSS, JS, migration, ni service touché.

## 3. OQ confirmées

| ID | Décision confirmée |
|---|---|
| **OQ-05-A** | Route `/` reste **Today**, pas de redirect forcé. |
| **OQ-05-B** | Readiness = **bande qualitative / self-report**, pas de score médical. |
| **OQ-05-C** | Session active + séance prévue → **active session domine**. |
| **OQ-05-D** | Recommandation repos **autorisée mais non impérative**. |
| **OQ-05-E** | Body Representation sur Home V1 = **résumé léger**, pas de heatmap. |
| **OQ-05-F** | Progression tab garde l'analyse ; Home = **snapshot + lien**. |
| **OQ-05-G** | Coach = **micro-note contextuelle**, pas bloc bavard. |
| **OQ-05-H** | Nouvel utilisateur = hero **« Commencer »**. |
| **OQ-05-I** | Home **entièrement no-JS**. |
| **OQ-05-J** | **Aucune nouvelle préférence** / personalization setting V1. |

Ces confirmations correspondent aux recommandations produit de la spec (§23). Aucun écart.

## 4. Rationale d'acceptance

- ✅ La spec cadre le Home comme **surface décisionnelle du jour**, pas dashboard lourd.
- ✅ La readiness est **honnête** : basée sur self-report existant 1-5 (sommeil/fatigue/courbatures/stress/motivation), **non médicale**.
- ✅ Le **data contract reste existing-data-only** (sessions, readiness, KPIs, reco, atlas) — aucun modèle/migration/service nouveau.
- ✅ Le Home **réutilise les acquis Sx_UI_04** (tokens Auren, couche Worked Area légère) **sans rouvrir le Focus Mode**.
- ✅ Le **build split** est clair en 5 sous-sprints (IA/hero → active/next → readiness → progress/body → empty/a11y).
- ✅ Les **non-goals** sont suffisamment explicites (pas de dashboard, pas de score médical, pas de heatmap, pas de gamification, pas de React).
- ✅ **Sx_UI_06 reste future**, non ouvert.
- ✅ **Aucun build ouvert** dans cette acceptance.

## 5. Décisions produit validées

- Home = surface de décision quotidienne avec **CTA principale unique** (reprendre / démarrer / choisir / repos).
- Session active **domine** si elle existe.
- Readiness V1 = **repère qualitatif self-report**, jamais diagnostic ni score.
- Progress = **snapshot + lien** vers Progression, pas dashboard inline.
- Body continuity = **résumé léger** (zones récentes / prochaine zone), pas de heatmap.
- Home **100% no-JS** (SSR), mobile-first 360×640, Auren scoped.
- **Aucune donnée inventée** ; agrégats nouveaux marqués future/deferred.

## 6. Cadre pour l'ouverture de Sb_UI_05.1 (rappel invariants)

Le futur build `Sb_UI_05.1` devra respecter (§19/§20/§24 de la spec) :
- **Data contract existing-data-only** : recomposer/présenter le contexte Home déjà exposé, jamais créer de donnée DB.
- **Aucun modèle readiness backend**, aucune migration, aucun changement `scoring/`, `overload_engine.py`, `coach_report.py`, `body_intelligence.py`, `recommendation.py`.
- **Aucune modification du Focus Mode** (Sx_UI_04 clos) — le Home renvoie vers `/sessions/{id}` existant.
- **No-JS + WCAG 44×44 + focus visible + reduced-motion + mobile 360×640** préservés.
- **Auren scoped** (pas de fuite globale).
- Baseline P0 Home capturable ; **aucun PNG committé** ; anti-404 obligatoire.
- Aucun rebrand SPIGNOS → Auren dans le code.

## 7. Confirmations sécurité et compat

- ✅ Aucun secret / cookie / token affiché ou committé
- ✅ Aucun PNG / runtime / DB committé
- ✅ Aucun compte prod cité ou utilisé
- ✅ Aucun changement de contrat métier (services/models/migrations intacts)
- ✅ Aucun claim médical / physiologique dans la spec
- ✅ Sx_UI_04 non rouvert (référence produit uniquement)

## 8. Confirmation docs-only (ce commit d'acceptance)

Fichiers touchés dans ce commit d'acceptance :

- `docs/SPRINT_Sx_UI_05_HUMAN_REVIEW_REPORT.md` — ce rapport
- `docs/strategy/SPEC_REGISTRY.md` — Sx_UI_05 ✅ SPEC HUMAN REVIEW ACCEPTED
- `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` — Sx_UI_05 accepté + Sb_UI_05.1 ready to be proposed

Aucun périmètre applicatif touché : ❌ `app/`, `tests/`, `scripts/`, `migrations/`, `.github/`, deps, PNG, runtime, DB, secret.

## 9. Statut post-acceptance

| Item | Statut |
|---|---|
| `Sx_UI_05_TODAY_READINESS_HOME_SPEC` | ✅ **SPEC HUMAN REVIEW ACCEPTED** |
| `Sb_UI_05.1 Home IA + Hero Decision Surface` | 🟡 **READY TO BE PROPOSED, not opened** |
| `Sb_UI_05.2 → .5` | ⏸️ **BLOCKED** until `.1` delivered and reviewed |
| `Sx_UI_06 Exercise Intelligence Presentation` | ⚪ **future, not opened** |
| Release tag baseline-preauren | ⏸️ deferred |

## 10. Prochaine action recommandée

**Ouvrir `Sb_UI_05.1 Home IA + Hero Decision Surface`** sur override explicite opérateur.

Contenu attendu (aperçu, cf. spec §21) :
- Topologie Home (IA §7) : header léger + **Hero Decision Surface** (CTA unique, Today Decision Model §8).
- Bascule perception board → décision.
- Auren scoped, faible chrome, no-JS.
- Data contract existing-data-only respecté.
- Baseline P0 Home capturable après build.

## 11. Références

- Spec acceptée : `docs/strategy/Sx_UI_05_TODAY_READINESS_HOME_SPEC.md`
- Sprint report source : `docs/SPRINT_Sx_UI_05_REPORT.md`
- Cycle précédent (clos) : `docs/SPRINT_Sx_UI_04_FINAL_CLOSEOUT_REPORT.md`
- Tokens : `docs/strategy/Sx_UI_02_DESIGN_TOKENS_SPEC.md`
- App shell : `docs/strategy/Sx_UI_03_APP_SHELL_NAVIGATION_SPEC.md`
- Home actuel (lecture only) : `app/templates/index.html` + `app/routers/pages.py::home` + `app/services/readiness.py`
- Registry : `docs/strategy/SPEC_REGISTRY.md`
- Roadmap : `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`

## 12. Verdict final

✅ **Sx_UI_05 Today / Readiness Home SPEC ACCEPTED — Human Review PASS.**

**Sb_UI_05.1 Home IA + Hero Decision Surface : READY TO BE PROPOSED, not opened.**
**Sb_UI_05.2 → .5 : blocked until .1 delivered and reviewed.**
**Sx_UI_06 : future, not opened. Release tag deferred.**
