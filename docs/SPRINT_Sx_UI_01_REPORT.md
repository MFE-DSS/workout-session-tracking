# Sprint Report — Sx_UI_01 Brand Foundation Spec

**Sprint ID :** `Sx_UI_01`
**Type :** SPEC ONLY (docs-only)
**Date :** 2026-07-02
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Verdict :** ✅ **READY FOR HUMAN REVIEW**

---

## 1. Résumé

Premier sprint du cycle `Sx_UI` (Auren Visual & Product Transformation), ouvert après signature du gate `PROD_STABILIZATION_PROFILE_BODY_COACH_REPORT` (verdict `PROD STRUCTURALLY STABLE FOR UI RENOVATION` — commit `ddd476b`).

Objectif : produire la spec de fondation de marque `Sx_UI_01` en documentant :

- Auren comme **working brand candidate** (product direction approved, legal/domain due diligence pending) ;
- diagnostic produit (SPIGNOS robuste fonctionnellement, langage visuel à moderniser) ;
- tone of voice clinique / instrumental / non motivationnel ;
- principes visuels autorisés (fond blanc, un accent froid, mono pour métriques, WCAG 44×44) ;
- anti-patterns interdits (gradients AI, dashboard gamer, illustrations fitness cliché) ;
- benchmarks cadrés (Strong, Hevy, Levels, Oura, WHOOP, Apple Health, Material, Apple HIG) ;
- dépendances aval (`Sx_UI_02` / `Sx_UI_03` / `Sx_UI_11` / `Sx_UI_04`) ;
- OQ explicites (A à G) avec propriétaire de décision.

Ce sprint **n'ouvre aucun build**, ne touche aucun code applicatif, aucun template, aucun asset. Rebrand code strictement reporté à `Sx_UI_10`.

## 2. Fichiers créés / modifiés

### Créés

- `docs/strategy/Sx_UI_01_BRAND_FOUNDATION_SPEC.md` — spec principale, 20 sections structurantes
- `docs/SPRINT_Sx_UI_01_REPORT.md` — ce rapport de sprint

### Modifiés

- `docs/strategy/SPEC_REGISTRY.md` — cycle `Sx_UI` mis à jour : Sx_UI_01 status ✅ **SPEC delivered — pending human review**
- `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` — position actuelle mise à jour : prochaine action = human review Sx_UI_01

## 3. Confirmation docs-only

**Scope strict respecté.** Aucun fichier des périmètres suivants n'a été touché dans ce sprint :

- ❌ `app/` (services, routers, templates, static)
- ❌ `tests/`
- ❌ `migrations/`
- ❌ `scripts/`
- ❌ `.github/workflows/`
- ❌ `.env`, config runtime
- ❌ Manifest, favicon, assets
- ❌ Routes, models, services métier
- ❌ Aucun renommage `SPIGNOS` → `Auren` dans le code

Sanity check exécuté en fin de sprint via `git diff --name-only` (voir §7 DoD).

## 4. Décisions prises

| # | Décision | Section spec |
|---|---|---|
| 1 | Nom cible Auren posé comme **working brand candidate** (pas figé juridiquement) | §4 |
| 2 | Legal/domain due diligence documentée comme checklist pending — non exécutée dans ce sprint | §5 |
| 3 | Positionnement : « application de performance corporelle qui aide à exécuter, mesurer et piloter l'entraînement avec une interface calme, précise et mobile-first » | §6 |
| 4 | 3 formulations de product promise proposées (anglais avec traductions FR possibles) | §7 |
| 5 | Tone of voice défini avec 8 règles + tableau Do/Don't sur 7 contextes | §8 |
| 6 | 10 principes visuels autorisés (white clinical surfaces, cold neutrals, one accent, mono metrics, WCAG cues, generous spacing) | §9 |
| 7 | 11 anti-patterns interdits (gradients AI, hero 3D, dark cockpit, orange-as-brand, dashboard gamer) | §10 |
| 8 | 8 références benchmark verrouillées avec point spécifique à copier | §11 |
| 9 | 6 risques d'usage benchmark documentés (surpromesse AI, wellness, médical, social, dashboard) | §12 |
| 10 | Philosophie de hiérarchie informationnelle par contexte (séance / après / home / progression / physique / coach) | §13 |
| 11 | SPIGNOS reste identité legacy interne, Auren = brand candidate future, aucun mélange autorisé | §14 |
| 12 | Dépendances aval documentées : Sx_UI_02 → Sx_UI_03 → Sx_UI_11 baseline → Sx_UI_04 | §15 |
| 13 | 7 OQ explicites avec propriétaire de décision assigné | §16 |
| 14 | Direction visuelle retenue : hybride **Clinical Lab + Quiet Instrument** (V2 territoires 1 + 2) | §3 + §9 |
| 15 | Accent pressenti : teal chirurgical désaturé, fallback bleu minéral (décision définitive `Sx_UI_02`) | §16 OQ-B |

## 5. OQ list (Open Questions)

Rappel des 7 OQ ouvertes par `Sx_UI_01`. Chacune a un propriétaire et un blocage aval identifiés.

| OQ | Question | Propriétaire | Bloque |
|---|---|---|---|
| **OQ-A** | Auren juridiquement disponible ? (INPI + EUIPO + USPTO + domaines) | opérateur + juridique externe | Sx_UI_10 execution |
| **OQ-B** | Accent final = teal chirurgical ou bleu minéral ? | opérateur, décision Sx_UI_02 | Sx_UI_02 merge |
| **OQ-C** | Bottom nav = 4 ou 5 destinations ? | opérateur, décision Sx_UI_03 | Sx_UI_03 merge |
| **OQ-D** | Physique top-level ou secondaire ? | opérateur, décision Sx_UI_03 | Sx_UI_03 merge |
| **OQ-E** | Coach top-level ou contextualisé ? | opérateur, décision Sx_UI_03 | Sx_UI_03 merge |
| **OQ-F** | Rebrand complet Sx_UI_10 ou dual-label transitoire ? | opérateur, décision Sx_UI_10 | Sx_UI_10 execution |
| **OQ-G** | Playwright pour screenshot regression ? | opérateur + revue tooling, Sx_UI_11 | Sx_UI_11 merge + baseline avant Sx_UI_04 |

**Critique :** OQ-A doit être exécutée le plus tôt possible (hors-scope de ce sprint). Un verdict défavorable déclenche `Sx_UI_01bis` de renommage. Les autres OQ n'empêchent pas l'ouverture de `Sx_UI_02`.

## 6. Non-goals respectés

Rappel des non-goals de la spec (§17), tous respectés dans ce sprint :

- ✅ Aucun code applicatif
- ✅ Aucun CSS
- ✅ Aucun token CSS définitif
- ✅ Aucun logo / favicon
- ✅ Aucun update manifest
- ✅ Aucun renommage route
- ✅ Aucun remplacement SPIGNOS dans templates
- ✅ Aucune update PWA
- ✅ Aucun shell nav ou reduction chrome
- ✅ Aucun screenshot tooling installé
- ✅ Aucun re-skin session
- ✅ Aucune refonte UX
- ✅ Aucune modification métier
- ✅ Aucun changement de flag
- ✅ Aucune ouverture de Sx_UI_02 / Sx_UI_03 / Sx_UI_04 / autres sprints Sx_UI

## 7. DoD local (Definition of Done)

Sanity checks exécutés en fin de sprint. Résultats réels :

- [x] `git diff --name-only` docs-only strict : ✅ **4 fichiers, tous dans `docs/`**
- [x] `git status` hors `docs/` : ✅ **vide**
- [x] `python scripts/check_spec_protocol.py` : ✅ **OK (35 reports, 32 specs)**
- [x] `python scripts/check_ruff_budget.py` : ✅ **OK (529 ≤ 548)**
- [x] `python scripts/catalog_qa.py` : ✅ **PASS (16 templates, 98 exercices)**
- [x] `python scripts/machine_atlas_qa.py` : ✅ **PASS (29 machines, 8 familles)**
- [x] `PYTHONPATH=. python scripts/check_alembic_drift.py` : ✅ **OK (no diff)**
- [x] `python scripts/check_schema_snapshot.py` : ✅ **matches head `7i0f5d1e2g43`**
- [x] `pytest` subset critique (Sx_30 + Sx_31 + capture-quality gate) : ✅ **55/55 passed** en 21.14 s
- [x] `git diff HEAD -- app/ tests/ migrations/ scripts/ .github/` : ✅ **no match — docs-only strict confirmé**

**Verdict DoD locale :** ✅ **all green — docs-only strict validé.**

## 8. DoD CI

CI réelle : **pending until push.** À renseigner après GitHub Actions run.

## 9. Prochain sprint recommandé

**`Sx_UI_02_DESIGN_TOKENS_SPEC`** — SPEC ONLY.

Contenu attendu :

- palette complète (fond, texte, surfaces, séparateurs, états, accent unique retenu — OQ-B tranchée)
- typographie (famille, poids, tailles, line-height, mono pour métriques)
- espacements, rayons, bordures, ombres tokens
- système d'icônes (trait, 24×24, sans remplissage)
- chart tokens (couleur unique, épaisseurs, opacités)
- règles de composition des tokens (comment les combiner sans réinventer)
- statut BUILD toujours BLOCKED

**Ne pas ouvrir avant validation humaine de Sx_UI_01.**

## 10. Références

- **Spec principale de ce sprint :** `docs/strategy/Sx_UI_01_BRAND_FOUNDATION_SPEC.md`
- **Roadmap cycle Sx_UI :** `docs/strategy/UI_TRANSFORMATION_ROADMAP.md`
- **Registry :** `docs/strategy/SPEC_REGISTRY.md` §1quinquies
- **Roadmap globale :** `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`
- **Gate OPS déblocant :** `docs/OPS_PROD_STABILIZATION_PROFILE_BODY_COACH_REPORT.md` §10
- **Focus mode précurseur :** `docs/strategy/Sx_29_CLOSURE_REPORT.md`

## 11. Verdict

✅ **READY FOR HUMAN REVIEW.**

Aucun code applicatif modifié. Aucun sprint de build ouvert. Aucun rebrand exécuté. Direction produit posée, tone of voice défini, principes visuels cadrés, benchmarks verrouillés. Dépendances aval explicites. Prochaine action : human review de la spec + décision d'ouverture de `Sx_UI_02` en SPEC ONLY.
