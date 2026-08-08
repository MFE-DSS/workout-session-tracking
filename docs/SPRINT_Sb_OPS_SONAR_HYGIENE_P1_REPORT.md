# SPRINT Sb_OPS.sonar-hygiene-p1 — Safe batch : split d'assertions composites (RAPPORT)

**Base canonique :** `038d194` · **Branche :** `sb/ops-sonar-hygiene-p1-safe-batch` · **Tier :** ISOLATED (tests only)
**Livré sous le protocole agentique** (`CLAUDE.md §4`) : `GO BUILD` → autonome jusqu'à `PR GREEN / MERGE PENDING`.

## 1. Objectif

Réduire la dette/bruit d'hygiène Sonar **main-branch** **sans changer le comportement**, par un lot **sûr, à faible cascade, test-only**.

## 2. Retarget — abandon de la 1ʳᵉ tentative (PR #54)

La 1ʳᵉ tentative (dédup `python:S1192` dans `app/routers/squads.py`) a **cascadé** : toucher les lignes `raise HTTPException(detail=…)` a fait compter en **new-code** 16 `python:S8415` latentes (« document HTTPException in responses ») + fait chuter `new_coverage` à **21.1 %** (chemins d'erreur 403/404 non testés). Corriger proprement (responses-docs sur 8 routes + ~16 tests d'erreur) **dépassait « smallest safe batch »** → **PR #54 fermée, non mergée, branche/worktree supprimés** (décision opérateur, Option A).

**Leçon** : dédupliquer des littéraux **dans du code d'error-handling** réveille les smells latents de ces lignes + expose leur non-couverture. Les bonnes cibles hygiène = lignes **déjà couvertes, sans smell latent** → **`python:S9073` en fichiers de test** (aucun impact coverage, aucun smell produit).

## 3. Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

| Option | Verdict |
|---|---|
| **A** `S9073` (split assertions composites) **en tests uniquement** | ✅ **RETENU** — test-only, pas d'error-handling, pas d'HTTPException, **aucun impact coverage** (les tests ne sont pas mesurés), aucun smell produit réveillé |
| B S1192 dans du code d'error-handling | ✗ écarté — cascade prouvée (PR #54) |
| C large `external_ruff:*` | ✗ écarté — multi-fichiers, broad |

**Cluster retenu** : les **2 fichiers de test Body Intelligence** `test_bi01_zone_drill_detail.py` + `test_bi01_zone_intelligence_cards.py` (**mono-subsystem BI**, 6 S9073).

## 4. Fichiers touchés (2 tests + docs)

| Fichier | Changement |
|---|---|
| `tests/test_bi01_zone_drill_detail.py` | 3 `assert A and B` → 2 `assert` (onclick/addEventListener · /100 et / 100 · "score"/'score') |
| `tests/test_bi01_zone_intelligence_cards.py` | 3 `assert A and B` → 2 `assert` (/100 et / 100 · "score"/'score' · "grade"/'grade') |
| docs | ce rapport + registry/roadmap |

**Chaque split préserve l'intention** (les deux faits doivent tenir) et **améliore le diagnostic** (on sait lequel a échoué). **Aucune assertion affaiblie, aucune couverture retirée.** Les 6 vérifiaient des faits **indépendants** (deux `x not in y` distincts) — aucun prédicat logique unique à conserver joint.

## 5. Interdits tenus

**Test-only** · zéro code produit · zéro error-handling/HTTPException/décorateur/responses · zéro migration/schéma/modèle · zéro UI/CSS · zéro ASSET/EKB/Publication · **aucune assertion affaiblie** · pas de réécriture large · mono-subsystem (BI tests).

## 6. Tests / validation

- `tests/test_bi01_zone_drill_detail.py` + `tests/test_bi01_zone_intelligence_cards.py` : **22 passés** (splits sémantiquement équivalents).
- check_scope **ISOLATED** · ruff (fichiers touchés) **clean** · budget **543 ≤ 548** · `check_spec_protocol` PASS.

## 7. Ce qui reste (dette documentée)

- **`S9073` restants (~46)** répartis sur d'autres fichiers de test — réductibles par lots test-only successifs (même patron, faible risque).
- **`S1192` en code d'error-handling** (squads/auth routes) : nécessite un **durcissement de route** dédié (responses-docs + tests d'erreur), **pas un lot hygiène** — abandonné ici (PR #54).
- **`external_ruff:*` (≈450)** · **`S3776` (27)** · main-branch project_status ERROR : réduction **incrémentale**, non posée en hard-gate (per mission).

## Verdict

**Verdict :** 🟢 **Sb_OPS.sonar-hygiene-p1 (safe batch) — PATCH COMPLETE / PR PENDING.** 6 assertions composites `S9073` splittées en tests BI, **test-only, behavior-preserving, aucune assertion affaiblie, aucun impact coverage**, **PR-level Sonar delta 0** attendu. 1ʳᵉ tentative squads (cascade) documentée et abandonnée. **Merge = GO humain.**
