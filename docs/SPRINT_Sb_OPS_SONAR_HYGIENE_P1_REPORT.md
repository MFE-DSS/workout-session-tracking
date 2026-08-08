# SPRINT Sb_OPS.sonar-hygiene-p1 — Dédup littéraux squads (RAPPORT)

**Base canonique :** `038d194` · **Branche :** `sb/ops-sonar-hygiene-p1` · **Tier :** ISOLATED
**Livré sous le protocole agentique** (`CLAUDE.md §4`) : `GO BUILD` → autonome jusqu'à `PR GREEN / MERGE PENDING`.

## 1. Objectif

Réduire la dette/bruit d'hygiène Sonar **main-branch** (project_status ERROR depuis `previous_version 2026-04-10`) **sans changer le comportement produit**, par un **lot focalisé, mono-fichier, haut-signal**.

## 2. Préflight — sélection du lot (le plus petit lot sûr)

État Sonar canonique : **757 issues** ouvertes. Distribution (top) : `external_ruff:*` (UP017 136, I001 135, UP045 122, F401 63…), `python:S9073` 52 (assertions composites de test), `S3776` 27 (complexité cognitive — **risqué, écarté**), **`python:S1192` 18** (littéraux dupliqués — **priorité #1 mission, behavior-preserving**).

**Choix : `python:S1192` (littéraux dupliqués), cluster de `app/routers/squads.py`** — critères d'arrêt respectés :
- **mono-fichier / mono-subsystem** (squads, feature sociale) — « plus d'un subsystem = STOP » évité ;
- **non sensible** — pas d'auth/sécurité (« sensitive auth/security semantics = STOP » évité ; le cluster auth_routes.py écarté par prudence) ;
- **haut signal** : 3 issues dont deux à **8×** de duplication.

## 3. Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

| Option | Verdict |
|---|---|
| **A** S1192 cluster `squads.py` (3 issues, 19 occurrences) | ✅ **RETENU** — mono-fichier, non sensible, behavior-preserving |
| B S1192 cluster `auth_routes.py` (6 issues) | ✗ écarté — module auth (condition d'arrêt « sensitive auth ») bien que les littéraux soient bénins |
| C lot large `external_ruff:*` (des centaines) | ✗ écarté — multi-fichiers/subsystems, « broad refactor » interdit |
| D `S3776` complexité | ✗ écarté — refactor risqué |

**Risque** : nul — extraction de constantes = mêmes valeurs, nommées une fois. **Zéro logique modifiée.**

## 4. Fichiers touchés (1 + docs)

| Fichier | Changement |
|---|---|
| `app/routers/squads.py` | 3 constantes : `_SQUAD_NOT_FOUND` (« Squad introuvable », **8×** → 1), `_ACCESS_DENIED` (« Accès refusé », **8×** → 1), `_CHALLENGE_CREATE_TEMPLATE` (« squad_challenge_create.html », **3×** → 1). **19 littéraux dupliqués → 3 constantes.** Zéro logique/route/comportement modifié. |
| docs | ce rapport + registry/roadmap |

## 5. Interdits tenus

Zéro changement de feature/comportement · zéro migration · zéro modèle/schéma · zéro CSS/UI · zéro ASSET/EKB/Publication-lifecycle · **aucun test affaibli** · **aucune exclusion Sonar** · **pas de broad refactor** (1 fichier, 1 règle).

## 6. Tests / validation

- **Broad sweep ciblé** (squads_routes · challenge · squad_privacy · squad_service · sharing · compare) : **35 passés** — les routes rendant les 3 littéraux (via constantes) inchangées.
- check_scope **ISOLATED** · `check_spec_protocol` PASS · budget ruff **543 ≤ 548** (la dédup n'ajoute aucun warning ruff ; S1192 est une règle Sonar, hors ruff).

## 7. Ce qui reste (dette documentée, hors ce lot)

- **S1192 restants (15)** : `auth_routes.py` (6, module auth — lot séparé prudent), `pages.py` (2), `services/dashboard.py` (2), `body.py`/`session_review.py`/`briefing.py`/`admin.py`/`models/squad.py` (1 chacun).
- **`external_ruff:*` (≈450)** : UP017/I001/UP045/F401… répartis sur tout le repo — réductibles par des lots `ruff --fix` ciblés par module (dont **4 nits pré-existants dans `squads.py` même** : `Optional`/`VALID_METRICS` F401, UP017 ligne 195, I001 — **volontairement laissés** hors ce lot S1192 pour ne pas mêler les catégories ni déclencher une cascade I001).
- **`S9073` (52)** : assertions composites de test (`assert X and Y`) — lot test-hygiene séparé.
- **`S3776` (27)** : complexité cognitive — nécessite des refactors ciblés (décision par cas).
- **main-branch project_status** : restera probablement ERROR après ce lot (delta minime sur 757) — la réduction est **incrémentale et sûre**, pas un big-bang. Non posé en hard-gate (per mission).

## Verdict

**Verdict :** 🟢 **Sb_OPS.sonar-hygiene-p1 — PATCH COMPLETE / PR PENDING.** Hygiène **behavior-preserving** : 19 littéraux dupliqués → 3 constantes dans `squads.py` (1 fichier, 1 règle S1192), zéro comportement/schéma/test affaibli, **PR-level Sonar delta 0** attendu. Reste documenté. **Merge = GO humain.**
