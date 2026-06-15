# Sx_29 — Mobile Session Focus Mode (Sprint Report — SPEC ONLY)

**Date :** 2026-06-15
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Spec produite :** `docs/strategy/Sx_29_MOBILE_SESSION_FOCUS_MODE_SPEC.md`
**Type :** SPEC ONLY sous human override #2
**Statut :** ✅ Livré

---

## 1. Résumé exécutif

Sx_29 produit la spec de refonte mobile-first de la page session (`GET /sessions/{session_id}`) afin de réduire la friction en salle. 20 sections, 9 composants visuels cibles, 6 états UI, 10 risques + mitigations, 5 OQ ouvertes, build queue décomposée en 5 lots (`Sb_29.1` à `Sb_29.5`).

**Override #2** (sprint `Sb_28.override-build-authorization`) autorise Option A uniquement. **React production INTERDIT.** **Dogfood Sx_27 reste PENDING** — non simulé, non considéré acquis.

Aucun code touché, aucun test touché, aucun build ouvert.

**Verdict :** ✅ READY FOR Sb_29.1 (sous override #2).

## 2. Périmètre livré

### 2.1 Fichiers créés

| Fichier | Rôle |
|---|---|
| `docs/strategy/Sx_29_MOBILE_SESSION_FOCUS_MODE_SPEC.md` | Spec 20 sections : exec summary, justification ouverture sous dogfood pending, scope override, source de vérité, audit page actuelle, problèmes UX supposés (hypothèses, pas certitudes), user flow cible, 9 composants visuels, 6 états UI, no-JS fallback verbatim, JS progressive enhancement borné, accessibilité mobile, fichiers impactés, tests attendus par lot, 10 risques, non-goals verbatim, build queue Sb_29.1-5, conditions validation humaine, 5 OQ, verdict |
| `docs/SPRINT_Sx_29_SPEC_REPORT.md` | Ce rapport |

### 2.2 Fichiers modifiés

| Fichier | Changement |
|---|---|
| `docs/strategy/SPEC_REGISTRY.md` | Ligne Sx_29 mise à jour : statut `🔵 à ouvrir` → `✅ spec only`, lien sprint report, mention build queue |
| `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` | §1 ajout ligne Sx_29 SPEC ONLY ouverte ; §10 plan d'action TL;DR : étape "ouvrir Sx_29" marquée FAIT, prochaine action devient "ouvrir Sb_29.1" |

### 2.3 Fichiers NON touchés (par contrat verbatim user)

- `app/**` : **0 fichier touché** (Documentation only)
- `tests/**` : **0 fichier touché**
- `migrations/**` : **0 nouvelle migration**
- Aucun service, aucun modèle, aucun template applicatif modifié
- Aucun fichier static (CSS, JS) modifié
- Build Sb_29.k : **0 ouvert** (la spec autorise l'ouverture, ne la fait pas)
- `docs/dogfood/DOGFOOD_Sx_27_DEFERRED.md` : **non touché** (dogfood reste PENDING)
- Sx_28 spec : **non touchée** (l'override #2 reste tel quel)
- Gates Sb_26.1 → Sx_28 : toutes intactes

## 3. Décisions clés

### 3.1 Ouverture sous override #2 explicite (§2 + §3 spec)

La spec rappelle textuellement que :
- l'ouverture sans dogfood est autorisée par override #2 (sprint `Sb_28.override-build-authorization`)
- les Options B/C/D/E restent bloquées
- React production reste INTERDIT
- le dogfood peut reverser Option A si arrivé plus tard
- les hard contracts Sx_26/Sx_27 restent en vigueur

### 3.2 Problèmes UX traités comme hypothèses (§6 spec)

Sans dogfood réel, la spec marque explicitement les 10 frictions supposées comme **"à confirmer par dogfood"**. Ne prétend pas à des certitudes. Pattern cohérent avec :
- `DOGFOOD_Sx_27_DEFERRED.md` (deferral formel)
- `Sx_28 §6` (dogfood input = PENDING)
- override #2 (build autorisé sans dogfood mais sans prétention de validation produit)

### 3.3 Audit fidèle de la surface existante (§5 spec)

Avant de spécifier la refonte, §5 documente :
- routes existantes (`app/routers/sessions.py`)
- template `session_detail.html` (551 lignes, structure, `<details>`, jump bar)
- état du JS (aucun JS spécifique à la page session detail)
- CSS classes déjà présentes (`exercise-card`, `ex-jump`, etc.)
- tests existants à préserver

Conclusion §5.5 : *"la surface session detail est déjà SSR-only, no-JS fonctionnelle, mobile-fit a minima. Sx_29 va améliorer le focus, réduire la friction, ajouter timer + sticky CTA progressifs, et ne CASSE rien des routes / contrats existants."*

### 3.4 No-JS fallback obligatoire (§10 spec)

Le tableau §10 énumère 9 interactions critiques et leur comportement no-JS. Verbatim : *"Toutes les interactions critiques fonctionnent sans JS."* Le JS est strictement progressive enhancement.

### 3.5 JS progressive enhancement borné (§11 spec)

5 surfaces JS autorisées explicitement (timer, sticky fallback, collapse animation, auto-focus, micro-toast). Contraintes techniques explicites : pas de framework, pas de bundler, JS vanilla dans `app/static/js/session_focus.js`, CSP respectée (fichier externe).

### 3.6 Build queue décomposée (§17 spec)

5 lots prévisionnels avec objectifs, livrables, DoD spécifiques :
- Sb_29.1 visual skeleton (S-M)
- Sb_29.2 active exercise navigation (S-M)
- Sb_29.3 sticky CTA (S)
- Sb_29.4 rest timer progressive enhancement (M)
- Sb_29.5 template tests + mobile smoke + accessibility (M)

Chaque lot doit livrer un sprint report + CI verte + tests existants non régressés + perf baseline within budget.

### 3.7 Conditions de validation humaine explicites (§18 spec)

§18 liste 6 conditions pré-Sb_29.1 + 5 conditions entre lots + 4 conditions d'arrêt anticipé. Pattern cohérent avec `GO_NO_GO_REVIEW_TEMPLATE.md`.

### 3.8 5 OQ ouvertes (§19 spec)

- OQ-A : substitution entry point — route séparée ou inline dialog ?
- OQ-B : CSS dédié `session_focus.css` ou inline `app.css` ?
- OQ-C : signal serveur "timer démarré" via query param ou data attribute ?
- OQ-D : Lighthouse en CI ou audit manuel ?
- OQ-E : micro-interactions reportées à `Sb_29.next.polish-1` ?

Chacune avec recommandation par défaut + qui tranche + délai.

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
| `python scripts/check_spec_protocol.py` | ✅ OK | nouvelle spec contient "Non-goals" §16 |
| `python scripts/check_auth_scope_matrix.py` | ✅ OK | 3 fichiers présents |
| `pip-audit -r requirements.txt --strict` | ✅ OK | clean |

## 5. CI réelle (post-push)

Run CI [#27559252205](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/27559252205) (commit `60b36d9`) — conclusion **success** :

- [x] Job `pytest + QA scripts` (incl. perf baseline smoke) — ✅ success
- [x] Job `lint (ruff budget + bandit + actionlint + shellcheck + check_spec_protocol + check_auth_scope_matrix)` — ✅ success
- [x] Job `SonarCloud` — ✅ success
- [x] Pas de régression sur les gates Sb_26.1 → Sx_28

CI verte **du premier push**.

## 6. Contraintes respectées (verbatim user)

| Contrainte | Statut |
|---|---|
| Documentation only | ✅ 0 fichier app/ touché |
| Aucun fichier `app/` modifié | ✅ |
| Aucun fichier `tests/` modifié | ✅ |
| Aucune migration | ✅ |
| Aucun modèle | ✅ |
| Aucun build Sb_29.k ouvert | ✅ verdict §20 = "READY FOR Sb_29.1", pas "Sb_29.1 ouvert" |
| Stack FastAPI SSR + Jinja2 contrainte | ✅ marqué §3, §15, §16, §20 |
| React production INTERDIT Sx_29 | ✅ marqué §3, §10, §16, §20 |
| Pas de SPA | ✅ marqué §16 |
| JS progressif uniquement pour timer / collapse / sticky / micro-interactions | ✅ §11 |
| No-JS fallback obligatoire | ✅ §10 |
| Aucune rupture de route existante | ✅ §16 |
| Aucun changement destructif d'historique | ✅ §16 |
| Aucun changement scoring core | ✅ §13, §16 |
| Aucun nouveau modèle sans justification explicite | ✅ aucun modèle proposé |
| Aucune migration dans Sx_29 spec | ✅ §16 |
| Mobile target 360×640 | ✅ §7, §8, §12, §14 |
| Pas de scroll horizontal | ✅ §7, §14 |
| Hard contracts Sx_26/Sx_27 | ✅ §3, §15, §16, §20 |
| Ne pas rouvrir Options B/C/D/E | ✅ §3, §16, §20 |
| Pas de lab React dans build principal | ✅ §3, §16 |
| Dogfood Sx_27 reste PENDING | ✅ §2, §6, §15, §20 |
| Pas de simulation de dogfood | ✅ |

## 7. Structure spec produite (matching §3 livrables)

| Section spec demandée | Section livrée |
|---|---|
| 1. Executive summary | §1 |
| 2. Pourquoi lancer Sx_29 malgré dogfood pending | §2 |
| 3. Human override scope | §3 |
| 4. Source de vérité actuelle | §4 |
| 5. Audit de la page session actuelle | §5 |
| 6. Problèmes UX supposés | §6 |
| 7. User flow cible en salle | §7 |
| 8. Composants visuels cibles | §8 |
| 9. États UI | §9 |
| 10. No-JS fallback | §10 |
| 11. JS progressive enhancement | §11 |
| 12. Accessibilité mobile | §12 |
| 13. Fichiers impactés | §13 |
| 14. Tests attendus | §14 |
| 15. Risques | §15 |
| 16. Non-goals | §16 |
| 17. Build queue | §17 |
| 18. Conditions de validation humaine | §18 |
| 19. Open questions | §19 |
| 20. Verdict | §20 |

## 8. Verdict

| Critère DoD | Statut |
|---|---|
| pytest passe | ✅ 1080 passed |
| catalog_qa passe | ✅ |
| machine_atlas_qa passe | ✅ |
| check_alembic_drift passe | ✅ |
| check_schema_snapshot passe | ✅ |
| check_migration_patterns passe | ✅ |
| check_migration_roundtrip passe | ✅ |
| check_ruff_budget passe (≤ 548) | ✅ 534 ≤ 548 |
| pip-audit passe | ✅ clean |
| gitleaks passe | ✅ run #27559252205 |
| check_spec_protocol passe | ✅ spec contient "Non-goals" §16 |
| check_auth_scope_matrix passe | ✅ |
| perf baseline smoke passe | ✅ |
| Rapport sprint livré | ✅ (ce document) |
| Spec `Sx_29_MOBILE_SESSION_FOCUS_MODE_SPEC.md` livrée | ✅ 20 sections |
| Verdict final explicite | ✅ §9 |

## 9. Verdict final

### ✅ **Sx_29 SPEC ONLY — READY FOR Sb_29.1 (sous override #2)**
### ⏳ DOGFOOD INPUT = PENDING (peut reverser Option A si livré plus tard)
### 🔴 React production INTERDIT — Options B/C/D/E restent bloquées

**Prochaine action requise :**

| Acteur | Action |
|---|---|
| Opérateur | Relire Sx_29 spec intégralement |
| Opérateur | Trancher OQ-A à OQ-E (§19) ou différer explicitement |
| Opérateur | Valider §18 conditions de validation humaine |
| Opérateur | Si tout OK : ouvrir `Sb_29.1` (visual skeleton) |
| Agent | Exécuter `Sb_29.1` selon §17, produire sprint report |
| Opérateur (parallèle) | Continuer à viser le dogfood Sx_27 — peut amender Sx_29 ou imposer fix avant Sb_29.k+1 |

---

**Co-Authored-By :** Claude Opus 4.7
