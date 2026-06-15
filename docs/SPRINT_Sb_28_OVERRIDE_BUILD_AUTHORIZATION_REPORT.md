# Sb_28.override-build-authorization — Authorize Option A Build Under Human Override (Sprint Report)

**Date :** 2026-06-15 (override #2, après-midi)
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Cycle parent :** Sx_28 — Product Roadmap Reconciliation
**Spec parente :** `docs/strategy/Sx_28_PRODUCT_ROADMAP_RECONCILIATION_SPEC.md`
**Type :** Documentation only — override administratif
**Statut :** ✅ Livré

---

## 1. Résumé exécutif

L'opérateur a explicitement décidé de **basculer le verdict Sx_28** :
- de : `BUILD AUTHORIZATION = BLOCKED UNTIL DOGFOOD OR EXPLICIT OVERRIDE`
- vers : `BUILD AUTHORIZED FOR OPTION A UNDER EXPLICIT HUMAN OVERRIDE`

Sans attendre le dogfood Sx_27 (qui reste PENDING, non simulé, non considéré acquis).

L'override est **borné à Option A uniquement** (Sx_29 Mobile Session Focus Mode). Options B/C/D/E restent bloquées. React production interdit dans Sx_29. Aucun code touché par ce sprint — uniquement bascule documentaire des verdicts dans 3 documents stratégiques + ce rapport.

**Verdict :** ✅ `BUILD AUTHORIZED FOR OPTION A UNDER EXPLICIT HUMAN OVERRIDE`.

## 2. Contexte de l'override

### 2.1 Position avant ce sprint

- Sx_26 clôturé
- Sx_27 technically closed
- Sx_28 SPEC ONLY livrée le matin (override #1 — ouverture spec sans dogfood)
- Build authorization : 🔴 BLOCKED
- Dogfood Sx_27 : PENDING, annoncé ~2 jours

### 2.2 Décision opérateur (override #2)

| Item | Décision |
|---|---|
| Attendre le dogfood pour basculer ? | ❌ NON — décision de ne pas attendre |
| Option à autoriser ? | ✅ Option A uniquement (Mobile Session Focus Mode / Visual Interaction Layer) |
| Options B/C/D/E ? | 🔴 restent bloquées (override séparé requis pour chacune) |
| Prochain cycle Sx_ autorisé ? | ✅ Sx_29 — Mobile Session Focus Mode |
| Stack | FastAPI SSR + Jinja2 conservé ; React production INTERDIT dans Sx_29 |
| Lab React exploratoire | Acceptable comme proposition documentaire séparée ; jamais dans le build principal Sx_29 |
| Considérer Sx_27 comme product-validé ? | ❌ NON — dogfood reste PENDING |
| Considérer le dogfood comme acquis ? | ❌ NON — non simulé, non inventé |

### 2.3 Risques assumés (verbatim Sx_28 §16.bis)

| Risque | Mitigation prévue |
|---|---|
| Dogfood futur révèle Option A non prioritaire | Sx_28 §15.2 reste actif : possibilité de reverser Option A et imposer fix avant suite |
| Build Sx_29 ne répond pas à la friction réelle | Sx_29 décomposable en `Sb_29.1-5` avec dogfood léger entre chaque |
| Override réutilisé pour B/C/D/E sans rigueur | Borné à Option A — tout autre option = override séparé |
| Lab React production hors contrôle | React production INTERDIT Sx_29 ; lab séparé optionnel |

## 3. Périmètre livré

### 3.1 Fichiers modifiés

| Fichier | Changement |
|---|---|
| `docs/strategy/Sx_28_PRODUCT_ROADMAP_RECONCILIATION_SPEC.md` | Header : note amendement 2026-06-15. §15 : "Recommandation provisoire" → "DÉCISION SOUS OVERRIDE". Ajout §15.1bis (portée et limites). §16 : tableau conditions annoté SATISFAITES. Ajout §16.bis (risques assumés). §20 : verdict basculé vers BUILD AUTHORIZED FOR OPTION A. |
| `docs/strategy/SPEC_REGISTRY.md` | §1ter Sx_28 : titre passe à "BUILD AUTHORIZED FOR OPTION A UNDER OVERRIDE". Table mise à jour avec : sprint override-build-authorization livré, Sx_29 marqué autorisé, Sx_30-33+ marqués bloqués. |
| `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` | §1 : ligne Sx_28 → SPEC AMENDED. Build authorization → AUTHORIZED FOR OPTION A. Note double override explicite avec limites. §3 : diagramme roadmap mis à jour. §10 : plan d'action révisé post-override #2 + anti-patterns mis à jour. |

### 3.2 Fichiers créés

| Fichier | Rôle |
|---|---|
| `docs/SPRINT_Sb_28_OVERRIDE_BUILD_AUTHORIZATION_REPORT.md` | Ce rapport |

### 3.3 Fichiers NON touchés (par contrat verbatim user)

- `app/**` : **0 fichier touché** (Documentation only)
- `tests/**` : **0 fichier touché**
- `migrations/versions/` : **0 nouvelle migration**
- Aucun service, aucun modèle, aucun template modifié
- `docs/dogfood/DOGFOOD_Sx_27_DEFERRED.md` : **non touché** (le dogfood reste PENDING, sa position formelle reste valide)
- Gates Sb_26.1 → Sb_27.7 + Sx_27 + Sx_28 spec ONLY : toutes intactes
- Aucun cycle Sx_29 ouvert dans ce sprint (la bascule du verdict autorise l'ouverture, ne la fait pas)

## 4. Décisions clés

### 4.1 Override #2 borné à Option A (verbatim user)

L'override n'autorise PAS toutes les options. Il autorise **Option A uniquement** (Mobile Session Focus Mode / Visual Interaction Layer).

| Option | Statut post-override #2 |
|---|---|
| A — Mobile Session Focus Mode | ✅ AUTORISÉE (Sx_29 ouvrable) |
| B — Progressive Overload Engine | 🔴 BLOQUÉE (override séparé requis) |
| C — Body Tracking v2 | 🔴 BLOQUÉE |
| D — PWA Premium | 🔴 BLOQUÉE |
| E — Cleanup only | 🔴 BLOQUÉE comme cycle Sx_ (mais peut être ouverte à part comme `Sb_27.next.*` opportuniste) |

### 4.2 Dogfood reste PENDING explicitement

Verbatim user :
> - Ne pas prétendre que le dogfood Sx_27 est fait.
> - Ne pas prétendre que Sx_27 est product-validé.
> - Dogfood reste PENDING.

Ces trois interdictions sont marquées textuellement dans :
- Sx_28 header
- Sx_28 §15
- Sx_28 §16
- Sx_28 §20
- SPEC_REGISTRY §1ter
- ROADMAP_AND_NEXT_STEPS §1 + §3 + §10

Aucune phrase ne simule, n'invente, ou ne suggère qu'un dogfood a été exécuté. Le sprint `Sb_28.dogfood-integration` reste explicitement disponible si le dogfood arrive plus tard et révèle qu'Option A doit être reversée.

### 4.3 React production interdit Sx_29 (verbatim user)

> - Le build doit rester compatible avec FastAPI SSR + Jinja2.
> - React n'est pas autorisé en production dans ce sprint.
> - Un lab React peut être proposé comme option exploratoire future, mais non livré dans le build principal.

Marqué textuellement dans Sx_28 §15.1bis + §20 + ROADMAP §1 + §3 + §10. Tout futur sprint Sx_29 / Sb_29.k devra respecter cette contrainte verbatim.

### 4.4 Sx_29 doit produire sa spec d'abord (protocole §4)

L'override autorise l'ouverture de Sx_29 — il n'autorise pas un raccourci vers un build direct. Sx_29 suit le protocole spec-driven :
- ouvrir `Sx_29_MOBILE_SESSION_FOCUS_MODE_SPEC.md` (SPEC ONLY)
- validation humaine
- puis `Sb_29.1`, `Sb_29.2`, ..., `Sb_29.5` selon le découpage de la spec

Ceci est rappelé dans ROADMAP §10 anti-patterns ("Ouvrir Sx_29 directement en BUILD `Sb_29.k` sans produire la spec d'abord — INTERDIT").

### 4.5 Override #1 et override #2 distincts

| Override | Date | Portée |
|---|---|---|
| #1 (matin 2026-06-15) | Sx_28 SPEC ONLY ouvert sans dogfood reçu | spec only, aucun build |
| #2 (après-midi 2026-06-15) | Bascule Sx_28 §20 → BUILD AUTHORIZED FOR OPTION A | Sx_29 ouvrable |

Les deux overrides sont documentés explicitement (avec date) dans Sx_28, SPEC_REGISTRY, et ROADMAP. Cette traçabilité garantit qu'un futur lecteur comprend la chronologie sans ambiguïté.

## 5. Tests et vérifications (DoD)

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
| `python scripts/check_spec_protocol.py` | ✅ OK | spec contient toujours "Non-goals" §18 |
| `python scripts/check_auth_scope_matrix.py` | ✅ OK | 3 fichiers présents |
| `pip-audit -r requirements.txt --strict` | ✅ OK | clean |

## 6. CI réelle (post-push)

À renseigner après push.

- [ ] Job `pytest + QA scripts` (incl. perf baseline smoke) — vert attendu
- [ ] Job `lint (... + check_spec_protocol + check_auth_scope_matrix)` — vert attendu
- [ ] Job `SonarCloud` — vert attendu
- [ ] Pas de régression sur les gates Sb_26.1 → Sx_28

## 7. Contraintes respectées (verbatim user)

| Contrainte | Statut |
|---|---|
| Documentation only | ✅ 0 fichier app/ touché |
| Ne modifie aucun code applicatif | ✅ |
| Ne modifie aucun test applicatif | ✅ |
| Ne crée aucune migration | ✅ |
| Ne crée aucun modèle | ✅ |
| Ne démarre pas encore Sx_29 dans ce sprint | ✅ Sx_29 reste à ouvrir séparément |
| Ne simule pas de dogfood | ✅ PENDING marqué partout, jamais inventé |
| Ne baisse pas le ruff budget | ✅ 548 inchangée |
| Ne désactive aucune gate | ✅ |
| Override borné à Option A | ✅ explicitement marqué dans Sx_28 + SPEC_REGISTRY + ROADMAP |
| Options B/C/D/E bloquées | ✅ marquées 🔴 |
| FastAPI SSR + Jinja2 conservé | ✅ contrainte marquée pour Sx_29 |
| React production NON autorisé Sx_29 | ✅ marqué verbatim partout |
| Lab React acceptable séparément | ✅ marqué Sx_28 §15.1bis + §20 |
| Dogfood Sx_27 reste PENDING | ✅ |

## 8. Verdict final

### ✅ **BUILD AUTHORIZED FOR OPTION A UNDER EXPLICIT HUMAN OVERRIDE**

| Critère | Statut |
|---|---|
| Sx_28 §15 : décision Option A inscrite sous override | ✅ |
| Sx_28 §16 : conditions satisfaites par override | ✅ |
| Sx_28 §20 : verdict basculé vers BUILD AUTHORIZED FOR OPTION A | ✅ |
| SPEC_REGISTRY §1ter : Sx_28 statut mis à jour, Sx_29 marqué autorisé | ✅ |
| ROADMAP §1 + §3 + §10 : override #2 documenté, anti-patterns mis à jour | ✅ |
| Override borné à Option A | ✅ |
| Options B/C/D/E restent bloquées | ✅ |
| Sx_29 = prochain cycle autorisé (Mobile Session Focus Mode) | ✅ |
| React production interdit Sx_29 | ✅ |
| Dogfood reste PENDING (non simulé) | ✅ |
| Rapport sprint livré | ✅ (ce document) |

### Prochaine action autorisée

| Acteur | Action |
|---|---|
| Opérateur | Ouvrir `Sx_29` SPEC ONLY — copier le prompt `ROADMAP_AND_NEXT_STEPS.md §7.3` |
| Agent | Produire `docs/strategy/Sx_29_MOBILE_SESSION_FOCUS_MODE_SPEC.md` selon la structure du prompt |
| Opérateur (parallèle) | Viser le dogfood Sx_27 — peut reverser Option A si arrivé et signal différent |
| Opérateur (si besoin) | Proposer un lab React exploratoire **séparé** (documentaire), jamais dans Sx_29 build |

---

**Co-Authored-By :** Claude Opus 4.7
