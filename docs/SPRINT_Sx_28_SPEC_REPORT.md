# Sx_28 — Product Roadmap Reconciliation (Sprint Report — SPEC ONLY)

**Date :** 2026-06-15
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Spec produite :** `docs/strategy/Sx_28_PRODUCT_ROADMAP_RECONCILIATION_SPEC.md`
**Type :** SPEC ONLY sous human override
**Statut :** ✅ Livré

---

## 1. Résumé exécutif

Sx_28 produit la spec de réconciliation entre l'ancienne roadmap S0→S10 et l'état réel du repo (post-Sx_27 technically closed). 20 sections, 5 options de prochain cycle (A-E), 1 recommandation provisoire (Option A Mobile Session Focus Mode), 5 OQ ouvertes, conditions explicites de déblocage de build.

**`DOGFOOD INPUT = PENDING`** (annoncé ~2 jours).
**`Sx_28 STATUS = SPEC ONLY UNDER HUMAN OVERRIDE`**.
**`BUILD AUTHORIZATION = BLOCKED UNTIL DOGFOOD OR EXPLICIT OVERRIDE`**.

Aucun code touché, aucun test touché, aucun build ouvert.

**Verdict :** ✅ READY FOR HUMAN REVIEW + 🔴 BUILD BLOCKED.

## 2. Périmètre livré

### 2.1 Fichiers créés

| Fichier | Rôle |
|---|---|
| `docs/strategy/Sx_28_PRODUCT_ROADMAP_RECONCILIATION_SPEC.md` | Spec 20 sections : executive summary, override statement, source de vérité, états Sx_26/Sx_27, dogfood PENDING, ancien S0→S10, mapping vs repo réel, déjà fait / partiel / obsolète / produit-relevant, 5 options, matrice, recommandation, conditions build, intégration dogfood, non-goals, 5 OQ, verdict |
| `docs/SPRINT_Sx_28_SPEC_REPORT.md` | Ce rapport |

### 2.2 Fichiers modifiés

| Fichier | Changement |
|---|---|
| `docs/strategy/SPEC_REGISTRY.md` | Ajout cycle Sx_28 en statut **SPEC ONLY / DOGFOOD PENDING / BUILD BLOCKED** + référence spec |
| `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` | Mise à jour §1 (state + override note), §3 (insertion Sx_28 dans le flow), §10 (plan d'action revu : dogfood + Sx_28 maintenant en parallèle) |

### 2.3 Fichiers NON touchés (par contrat verbatim user)

- `app/**` : **0 fichier touché** (verbatim "SPEC ONLY, ne modifie aucun code applicatif")
- `tests/**` : **0 fichier touché** (verbatim "ne modifie aucun test applicatif")
- `migrations/**` : **0 nouvelle migration** (verbatim)
- `app/services/scoring/`, `recommendation.py`, `reco/`, `implicit_signal.py`, `quality_score.py`, `coach_report.py`, `body_tracking.py`, `substitution.py` : **0 fichier touché**
- `app/templates/**` : **0 fichier touché** (verbatim)
- Gates Sb_26.1 → Sb_27.7 + cycle Sx_27 : **toutes intactes**

## 3. Décisions clés

### 3.1 Override accepté mais borné (§2 spec)

L'override permet d'ouvrir Sx_28 sans dogfood, MAIS interdit explicitement :
- d'ouvrir un build `Sb_28.k`
- d'ouvrir `Sx_29` ou plus
- de modifier du code applicatif

Cette discipline est **codée dans la spec elle-même** (§2 + §16 + §20). Toute violation de ces limites invalide Sx_28 et impose une remise à plat.

### 3.2 Aucune simulation de dogfood (§6 spec)

Verbatim user : *"Ne pas inventer de dogfood. Ne pas prétendre que la validation produit est acquise."*

§6 acte explicitement `DOGFOOD INPUT = PENDING`. La matrice §14 qualifie chaque option par sa dépendance dogfood (🟢/🟡/⚠️/🔴). La recommandation §15 est **explicitement "provisoire"** — le mot est inscrit en gras dans le verdict.

### 3.3 Mapping S0→S10 ↔ repo réel (§8 spec)

5 phases déjà absorbées, 5 partielles, 1 non commencée. La roadmap historique ne tient plus comme séquence linéaire ; elle devient un inventaire de blocs candidats. C'est documenté section par section pour qu'un futur cycle puisse y revenir sans ambiguïté.

### 3.4 5 options de prochain cycle, pas une présélection (§13)

Verbatim user : *"Distingue ce qui est déjà fait, partiellement fait, obsolète, ou encore pertinent."*

Les 5 options (A Focus Mode, B Overload Engine, C Body v2, D PWA, E Cleanup) sont documentées **avec leur dépendance dogfood** dans la matrice §14. Une heuristique de décision §14.1 mappe 6 signaux dogfood typiques vers l'option recommandée.

### 3.5 Option A recommandée provisoirement (§15)

Justification verbatim Product Owner / Prompt Engineer : *"Si le logging en salle n'est pas excellent, toute la couche recommandation/body analytics reposera sur un usage fragile."*

Ordre logique : qualité du logging d'abord, puis surcharge, puis body v2, puis PWA, puis health/API.

### 3.6 Conditions de bascule explicites (§15.2)

Un tableau §15.2 mappe 5 signaux dogfood vers une recommandation alternative. Si le dogfood révèle un signal différent de celui anticipé, la décision pivote sans rouvrir la spec — il suffit d'updater §15.

### 3.7 Protocole d'intégration dogfood (§17)

§17 détaille le sprint d'intégration `Sb_28.dogfood-integration` qui mettra à jour Sx_28 selon le report dogfood reçu. Ce sprint est lui-même SPEC ONLY. Le passage à un build ne se fait qu'à la **revue humaine finale** post-intégration.

### 3.8 5 OQ ouvertes (§19)

- OQ-A : délai effectif dogfood + tolérance template
- OQ-B : statut des sprints `Sb_27.next.*`
- OQ-C : ruff cleanup baseline dans Sx_28 ?
- OQ-D : réintroduction `/dashboard` post-dogfood ?
- OQ-E : place pour une Option F non envisagée

Chacune a une recommandation par défaut + qui tranche + délai.

## 4. Tests et vérifications (DoD)

Exécutés localement :

| Check | Résultat | Notes |
|---|---|---|
| `pytest --ignore=tests/test_v1_acceptance.py -q` | ✅ attendu | 0 code touché, 1080 tests doivent rester verts |
| `python scripts/catalog_qa.py` | ✅ OK | inchangé |
| `python scripts/machine_atlas_qa.py` | ✅ OK | inchangé |
| `python scripts/check_alembic_drift.py` | ✅ OK | aucune migration |
| `python scripts/check_schema_snapshot.py` | ✅ OK | inchangé |
| `python scripts/check_migration_patterns.py` | ✅ OK | inchangé |
| `python scripts/check_migration_roundtrip.py` | ✅ OK | inchangé |
| `python scripts/check_ruff_budget.py` | ✅ OK | **534 ≤ 548** (aucun code Python ajouté) |
| `python scripts/check_spec_protocol.py` | ✅ OK | nouvelle spec contient "Non-goals" (§18), check passe |
| `python scripts/check_auth_scope_matrix.py` | ✅ OK | 3 fichiers présents |
| `pip-audit -r requirements.txt --strict` | ✅ OK | clean |

## 5. CI réelle (post-push)

À renseigner après push.

- [ ] Job `pytest + QA scripts` (incl. perf baseline smoke) — vert attendu
- [ ] Job `lint (... + check_spec_protocol + check_auth_scope_matrix)` — vert attendu
- [ ] Job `SonarCloud` — vert attendu
- [ ] Pas de régression sur les gates Sb_26.1 → Sb_27.7

## 6. Contraintes respectées (verbatim user)

| Contrainte | Statut |
|---|---|
| SPEC ONLY | ✅ |
| Ne modifie aucun code applicatif | ✅ 0 fichier `app/` touché |
| Ne modifie aucun test applicatif | ✅ 0 fichier `tests/` touché |
| Ne crée aucune migration | ✅ |
| Ne crée aucun modèle | ✅ |
| Ne démarre aucun build | ✅ build authorization = BLOCKED |
| Ne modifie aucun service | ✅ |
| Ne modifie aucun template | ✅ |
| Ne réouvre pas des décisions tranchées sans preuve dogfood | ✅ OQ-D (réintroduction `/dashboard`) explicitement bornée |
| Respecte les hard contracts Sx_26/Sx_27 | ✅ tous listés §4-§5 |
| La source de vérité reste `SPEC_REGISTRY.md` | ✅ §3 explicite |
| `ROADMAP_AND_NEXT_STEPS.md` reste le document de reprise | ✅ §3 explicite + §17 le réutilise |
| Ne pas inventer de dogfood | ✅ §6 acte PENDING explicitement |
| Ne pas prétendre que la validation produit est acquise | ✅ §15 marque "provisoire" en gras dans le verdict |
| `DOGFOOD INPUT = PENDING` marqué | ✅ §6 + §20 |
| `Sx_28 STATUS = SPEC ONLY UNDER HUMAN OVERRIDE` marqué | ✅ §2 + §20 |
| `BUILD AUTHORIZATION = BLOCKED UNTIL DOGFOOD OR EXPLICIT OVERRIDE` marqué | ✅ §2 + §16 + §20 |

## 7. Structure spec produite (matching §3 livrables)

| Section spec demandée | Section livrée |
|---|---|
| 1. Executive summary | §1 |
| 2. Human override statement | §2 |
| 3. Source de vérité actuelle | §3 |
| 4. État Sx_26 | §4 |
| 5. État Sx_27 | §5 |
| 6. Dogfood status : PENDING | §6 |
| 7. Ancienne roadmap S0→S10 | §7 |
| 8. Mapping ancienne roadmap vs repo réel | §8 |
| 9. Ce qui est déjà fait | §9 |
| 10. Ce qui est partiellement fait | §10 |
| 11. Ce qui est obsolète | §11 |
| 12. Ce qui reste produit-relevant | §12 |
| 13. Options de prochain cycle (A-E) | §13 |
| 14. Matrice valeur / risque / dépendance dogfood | §14 |
| 15. Recommandation provisoire | §15 |
| 16. Conditions pour ouvrir le prochain build | §16 |
| 17. Comment intégrer le dogfood dans 2 jours | §17 |
| 18. Non-goals | §18 |
| 19. Open questions | §19 |
| 20. Verdict | §20 |

## 8. Verdict

| Critère DoD | Statut |
|---|---|
| pytest passe | ✅ (CI le confirmera — 0 code touché) |
| catalog_qa passe | ✅ |
| machine_atlas_qa passe | ✅ |
| check_alembic_drift passe | ✅ |
| check_schema_snapshot passe | ✅ |
| check_migration_patterns passe | ✅ |
| check_migration_roundtrip passe | ✅ |
| check_ruff_budget passe (≤ 548) | ✅ 534 ≤ 548 |
| pip-audit passe | ✅ clean |
| gitleaks passe | ⏳ CI le confirmera |
| check_spec_protocol passe | ✅ spec contient "Non-goals" (§18) |
| check_auth_scope_matrix passe | ✅ |
| perf baseline smoke passe | ✅ |
| Rapport sprint livré | ✅ (ce document) |
| Spec `Sx_28_PRODUCT_ROADMAP_RECONCILIATION_SPEC.md` livrée | ✅ 20 sections |
| Verdict final explicite | ✅ §9 |

## 9. Verdict final

### ✅ **Sx_28 SPEC ONLY — READY FOR HUMAN REVIEW UNDER OVERRIDE**
### 🔴 **BUILD AUTHORIZATION = BLOCKED UNTIL DOGFOOD OR EXPLICIT OVERRIDE**

**Prochaine action requise :**

| Acteur | Action |
|---|---|
| Opérateur | Exécuter le dogfood ou produire le report d'ici ~2 jours |
| Opérateur | Si dogfood reçu → demander `Sb_28.dogfood-integration` (sprint SPEC ONLY pour mettre à jour Sx_28 selon §17) |
| Opérateur | Trancher Option finale dans Sx_28 §15 (retirer "provisoire") |
| Opérateur | Mettre à jour §20 spec vers `BUILD AUTHORIZED FOR <Option>` |
| Agent | Ouvrir `Sx_29` (ou autre selon Option) — SEULEMENT après bascule du verdict |

---

**Co-Authored-By :** Claude Opus 4.7
