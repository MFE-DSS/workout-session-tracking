# Sb_26.5 — Spec / Process Discipline (Sprint Report)

**Date :** 2026-06-14
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Spec parente :** `docs/strategy/Sx_26_ENGINEERING_CONTROL_PLANE_AND_ANTI_DRIFT_HARDENING_SPEC.md`
**Lot Sx_26 :** §16 — Sb_26.5 (Spec/Process discipline — cinquième lot du cycle)
**Statut :** ✅ Livré

---

## 1. Résumé exécutif

Sb_26.5 formalise la méthodologie spec-driven du projet : 6 templates verrouillés, 1 protocole engineering, 1 registry, 1 workflow opérateur, 1 gate CI required `check_spec_protocol.py`. Zéro touche à `app/`, zéro migration, zéro feature produit. La spec d'ouverture précisait explicitement que Sb_26.5 = "spec/process discipline", pas "test quality hardening" — respecté.

**Verdict :** ✅ **Sb_26.6 PRÊT**.

## 2. Périmètre livré

### 2.1 Fichiers créés

| Fichier | Rôle |
|---|---|
| `docs/templates/SPEC_TEMPLATE.md` | Template Sx_NN (12 sections obligatoires) |
| `docs/templates/BUILD_SPRINT_PROMPT_TEMPLATE.md` | Template prompt user pour ouvrir un Sb_NN.k |
| `docs/templates/SPRINT_REPORT_TEMPLATE.md` | Template rapport de fin de sprint |
| `docs/templates/AMENDMENT_TEMPLATE.md` | Template §Nbis pour amender une spec validée |
| `docs/templates/DOGFOOD_REPORT_TEMPLATE.md` | Template rapport dogfooding post-cycle |
| `docs/templates/GO_NO_GO_REVIEW_TEMPLATE.md` | Template review humaine GO/WAIT/REVERT |
| `docs/strategy/SPEC_DRIVEN_ENGINEERING_PROTOCOL_v1.md` | Protocole formel (cycle, rôles, gates, lotissement max 8) |
| `docs/strategy/SPEC_REGISTRY.md` | Index des Sx_NN et Sb_NN.k livrés (V1 reconstituée) |
| `docs/SPEC_DRIVEN_WORKFLOW.md` | Mode d'emploi opérateur (5 prompts, anti-patterns) |
| `scripts/check_spec_protocol.py` | Linter robust string-presence (pas de NLP) |
| `.spec-protocol-allowlist.json` | Politique + grandfathered (35 reports + 30 specs historiques) |
| `tests/test_spec_protocol.py` | 7 tests (passe-réel, violations synthétiques, templates, registry, protocole, strict mode) |
| `docs/SPRINT_Sb_26_5_REPORT.md` | Ce rapport |

### 2.2 Fichiers modifiés

| Fichier | Changement |
|---|---|
| `.github/workflows/ci.yml` | Job `lint` : ajout step `spec protocol check (required — Sb_26.5)` |

### 2.3 Fichiers NON touchés (par contrat)

- `app/**` : **aucune** modification
- `app/models/*` : **aucun** modèle SQLAlchemy modifié
- `migrations/versions/` : **aucune** nouvelle migration
- `app/templates/*.html` : **aucun** template produit modifié
- `app/services/scoring/`, `reco/`, `substitution.py`, `coach_report.py`, `body_tracking.py` : **0 fichier touché**
- `app/main.py:RateLimitMiddleware` + `_init_sentry_if_enabled` : **non touchés** (Sb_26.4 + Sb_26.3 intacts)
- `scripts/deploy_prod.sh`, `.github/workflows/deploy-production.yml` : **non touchés**
- Gates Sb_26.1 → Sb_26.4 : **aucune désactivée**, 1 nouvelle ajoutée (Sb_26.5)

## 3. Décisions clés

### 3.1 6 templates plutôt que 1 mega-template

Découpage par cas d'usage (spec, build, report, amendement, dogfood, review) plutôt qu'un mega-template polyvalent. Avantage : chaque template tient en une lecture rapide, le copy-paste est ciblé, l'opérateur ne se trompe pas de phase.

### 3.2 Protocol v1 = formalisation du de-facto

Les cycles Sx_20 → Sx_26 ont déjà suivi (de facto) le protocole : SPEC ONLY pour Sx_NN, lotissement Sb_NN.k, non-goals + hard contracts, sprint report avec verdict. Le doc v1 **formalise** cet existant plutôt que d'inventer une méthodologie. Argument : l'adoption est immédiate parce que les pratiques sont déjà internes.

### 3.3 Registry V1 reconstitué (best-effort)

User explicite : "Ne pas chercher à reconstruire parfaitement tout l'historique si trop long. Faire une V1 à partir des docs existants et documenter les limites." Respecté : cycles récents (Sx_24, Sx_26) bien mappés, anciens (Sb_02 → Sb_19) listés en bloc historique avec note de limite §9 du registry.

### 3.4 Checker robust string-presence, pas NLP

Choix : ne pas faire d'analyse sémantique. Le linter cherche des **marqueurs littéraux** ("Non-goals", "Périmètre interdit", "## 11. Verdict", "**Verdict :**", etc.) dans la liste de markers configurable. Avantages :

- aucun risque de faux positif sur formulations alternatives
- ré-exécutable, déterministe, rapide (< 100ms)
- maintenable : ajouter un marker = 1 ligne JSON
- "ne pas faire de NLP fragile" verbatim user respecté

### 3.5 Allowlist grandfather de 65 fichiers (35 reports + 30 specs)

Tous les fichiers pré-Sb_26.5 sont allowlistés. Le check vise le **flux entrant** : tout nouveau Sx_/Sb_ à partir de maintenant doit passer le linter. `--strict` permet de mesurer l'état historique pour un futur cleanup éventuel (non priorité V1).

### 3.6 CI gate required vs advisory

User : "Le check peut être ajouté en CI si stable. S'il risque d'être trop fragile, le documenter advisory V1." Évaluation : le check est trivial (présence de strings + glob), pas de risque de flap. **Required** retenu. Si demain un faux positif apparait : l'allowlist permet de l'absorber sans changer le code.

## 4. Tests et vérifications (DoD)

Exécutés localement le 2026-06-14 :

| Check | Résultat | Notes |
|---|---|---|
| `pytest --ignore=tests/test_v1_acceptance.py -q` | ✅ (voir §6) | +7 nouveaux tests Sb_26.5 |
| `python scripts/catalog_qa.py` | ✅ OK | inchangé |
| `python scripts/machine_atlas_qa.py` | ✅ OK | inchangé |
| `PYTHONPATH=. python scripts/check_alembic_drift.py` | ✅ OK | aucune migration |
| `python scripts/check_schema_snapshot.py` | ✅ OK | snapshot inchangé |
| `python scripts/check_migration_patterns.py` | ✅ OK | aucune migration ajoutée |
| `python scripts/check_migration_roundtrip.py` | ✅ OK | inchangé |
| `python scripts/check_ruff_budget.py` | ✅ OK | **546 ≤ 548** |
| `python scripts/check_spec_protocol.py` | ✅ OK | 35 reports + 30 specs grandfathered, nouveaux fichiers conformes |
| `pip-audit -r requirements.txt --strict` | ✅ OK | clean |

## 5. Sécurité / secrets

| Vérification | Statut |
|---|---|
| Aucun secret committé | ✅ aucun |
| Pas de modification de surfaces sensibles (auth, deploy, models) | ✅ |
| Pas de désactivation de gates Sb_26.1 → Sb_26.4 | ✅ toutes intactes + Sb_26.5 ajoutée |
| Protocole anti-drift verrouille `RATE_LIMIT_*`, `SENTRY_DSN`, etc. comme hard contracts implicites | ✅ via `SPEC_REGISTRY.md` §1 |

## 6. CI réelle (post-push)

Run CI [#27500839234](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/27500839234) (commit `cc6305a`) — conclusion **success** :

- [x] Job `pytest + QA scripts` — ✅ success
- [x] Job `lint (ruff budget + bandit + actionlint + shellcheck + pip-audit + gitleaks + spec protocol)` — ✅ success
- [x] Job `SonarCloud` — ✅ success
- [x] Pas de régression sur les gates Sb_26.1 → Sb_26.4

**Note** : premier run ([#27500515823](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/27500515823)) a échoué — gitleaks a re-flag le report Sb_26.4 lui-même parce qu'il citait littéralement la chaîne du précédent faux-positif. Fix commit `cc6305a` : rephrase de la trace pour conserver l'historique sans re-déclencher la rule. Démontre que la procédure §6.3 du runbook (rephrase plutôt qu'allowlist) tient à la 2ème occurrence.

## 7. Risques

| Risque | Probabilité | Mitigation |
|---|---|---|
| Allowlist devient un « endroit où on cache les nouveaux torts » | moyenne | `--strict` reste exécutable manuellement ; PR review humaine sur toute ajoute à `grandfathered_*` |
| Templates non utilisés par l'opérateur faute d'habitude | moyenne | `docs/SPEC_DRIVEN_WORKFLOW.md` documente les 5 prompts ; protocole §13 liste les gates auto |
| Registry obsolète si un sprint oublie de l'updater | élevée sans gate | protocole §13 : updater dans le **même commit** que le sprint report ; gate auto candidate Sb_26.next |
| Définition trop rigide bloque un usage légitime | basse | Workflow §11 documente les cas spéciaux (REVERT, amendement, dogfood blocker) |
| Sb_26.5 dévie vers "test quality hardening" | basse | user a explicitement précisé "Sb_26.5 = Spec/process discipline" — réglé en amont |

## 8. Contraintes respectées (verbatim user)

| Contrainte verbatim | Statut |
|---|---|
| Ne touche pas à app/ sauf nécessité absolument justifiée | ✅ aucun fichier `app/` touché |
| Ne modifie pas les modèles SQLAlchemy | ✅ |
| Ne crée pas de migration Alembic | ✅ |
| Ne touche pas aux features produit | ✅ |
| Ne touche pas au deploy production | ✅ |
| Ne modifie pas le rate limiter | ✅ Sb_26.4 intact |
| Ne modifie pas Sentry/observability | ✅ Sb_26.3 intact |
| Ne désactive aucune gate Sb_26.1/Sb_26.2/Sb_26.3/Sb_26.4 | ✅ toutes intactes + 1 ajoutée |
| Ne baisse pas la baseline ruff dans ce sprint | ✅ 548 inchangée |
| Pas de pre-commit obligatoire | ✅ aucun pre-commit ajouté |
| Sb_26.5 ≠ test quality hardening | ✅ scope strictement spec/process |
| Sb_26.5 ≠ performance baseline | ✅ |
| Sb_26.5 ≠ multi-tenant prep | ✅ |
| Sb_26.5 ≠ product features | ✅ |

## 9. Limites assumées et reportées

| Item | Pourquoi pas dans Sb_26.5 | Reporté à |
|---|---|---|
| Reconstitution complète historique Sb_02 → Sb_19 dans le registry | "Ne pas chercher à reconstruire parfaitement tout l'historique si trop long" verbatim user | acceptable V1 |
| Gate automatique "tout sprint mergé est dans le registry" | difficile sans NLP / sans label PR | Sb_26.next.spec-traceability-1 |
| Auto-link spec ↔ commits (via tags, commit-msg parsing) | complexité hors V1 | Sb_26.next.spec-traceability-1 |
| Pre-commit hook `check_spec_protocol` | "optionnel seulement" verbatim user | post-Sb_26 |
| Validation NLP cohérence spec ↔ code | trop fragile V1 | post-Sx_26 |
| Templates auto-applied (genre `gh issue` ouverture) | hors scope tooling V1 | post-Sx_26 |
| Strict registry mainteneurship gate | dépend d'un commit hook ou bot | Sb_26.next |
| Cleanup ruff baseline 548 → 546 | contrat sprint dédié | `Sb_26.next.ruff-cleanup-N` |
| Sonar warnings sur `pip install` (S8541/S8544) | déjà documenté Sb_26.4 §9 | Sb_26.next |

## 10. Backlog immédiat (Sx_26 §16)

| Lot | Objet | Bloquant ? |
|---|---|---|
| **Sb_26.6** | Performance baseline (p95 endpoints, slow query log) | Non bloqué par Sb_26.5 |
| Sb_26.7 | Multi-tenant prep (read-only V1, scope auth) | Non bloqué |

## 11. Verdict

| Critère DoD | Statut |
|---|---|
| pytest passe | ✅ 945 passed |
| catalog_qa passe | ✅ |
| machine_atlas_qa passe | ✅ |
| check_alembic_drift passe | ✅ |
| check_schema_snapshot passe | ✅ |
| check_migration_patterns passe | ✅ |
| check_migration_roundtrip passe | ✅ |
| check_ruff_budget passe (total ≤ 548) | ✅ 546 ≤ 548 |
| pip-audit passe | ✅ clean |
| gitleaks passe | ✅ run #27500839234 |
| lint job passe | ✅ |
| tests spec protocol passent | ✅ 7/7 |
| Aucun code produit modifié | ✅ |
| Aucune migration créée | ✅ |
| Rapport sprint livré | ✅ (ce document) |

### ✅ **Sb_26.6 PRÊT**

---

**Co-Authored-By :** Claude Opus 4.7
