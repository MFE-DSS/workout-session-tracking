# SPRINT Sb_CUSTOM_PROGRAM_PUBLICATION_04 — Cycle de republication sûr (RAPPORT)

**Base canonique :** `e1bcca1` · **Branche :** `sb/custom-program-publication-04` · **Tier :** ISOLATED (**zéro code app · zéro migration**)
**Spec :** [`Sb_CUSTOM_PROGRAM_PUBLICATION_04_SPEC.md`](strategy/Sb_CUSTOM_PROGRAM_PUBLICATION_04_SPEC.md)
**Livré sous le protocole agentique** (`CLAUDE.md §4`) : `GO BUILD` → préflight → **STOP + arbitrage** → autonome jusqu'à `PR GREEN / MERGE PENDING`.

## 1. Ce qui change

Le cycle complet de republication — `publish v{n}` → nouveau cycle d'édition (PUBLICATION_02) → édition/validation → **republication `v{n+1}`** — est **prouvé sûr et verrouillé** par une suite de tests de régression. **Aucun code applicatif n'est modifié** : le lifecycle requis est déjà exprimable par les briques existantes (slug versionné + liens de séance effacés/repointés). La décision de schéma (pas d'archivage, pas de migration) est documentée.

## 2. Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

**Préflight = STOP + arbitrage** (conditions d'arrêt de la mission atteintes). Lecture : spec 04 §6-7, spec 05 publication/versioning, PUBLICATION_01/02/03, modèle `WorkoutTemplate`, `user_program_publish.py`, `user_program_versioning.py`, `pages.py` (`/library`), `seed.py` (wipe-guard).

**Constat clé** : le cycle **requis** fonctionne déjà (slugs `…-v{n+1}-…` ≠ `v{n}` → nouveaux templates ; PUBLICATION_02 a effacé les liens → `v{n}` non lançables ; `catalog_section="user"` → exclus de `/library` + protégés du reseed). L'archivage **préféré** n'est **pas** exprimable sûrement (voir risques).

| Option | Verdict |
|---|---|
| **A** — pin + docs, **zéro archivage / zéro migration** ; verrouiller les invariants par tests | ✅ **RETENU (opérateur)** — satisfait tout l'« Expected product behavior » + tous les hard constraints |
| **B** — migration additive `archived_at` + garde `/library` | ✗ non nécessaire (lifecycle déjà exprimable) → viole « no migration unless schema cannot express » |
| **C** — re-label `catalog_section="archived"` + durcir `/library/{slug}` | ✗ expose via `/library/{slug}`, casse le wipe-guard reseed, touche la sémantique système |

**Risques traités** :
1. **Exposition globale** d'un ancien template via `/library/{slug}` → écartée : les `v{n}` restent `"user"`, la route détail 404 sur `"user"`. *Testé.*
2. **Suppression au reseed** → écartée : `"user"` est préservé par le wipe-guard (`catalog_section != "user"`). *Décision documentée + immuabilité testée.*
3. **Collision de slug v{n}/v{n+1}** → impossible : version dans le slug. *Testé (ids disjoints, slugs `v2`).*
4. **Mutation de contenu ancien** → l'édition frappe le brouillon `v{n+1}` ; snapshot `v{n}` byte-identique après republication. *Testé.*
5. **Double quality write** → 1 trace/version (freeze) ; nouveau cycle + édition = 0. *Testé.*

## 3. Fichiers touchés (1 test + docs, 0 code app)

| Fichier | Changement |
|---|---|
| `tests/test_user_program_republication.py` (**neuf**) | 11 tests verrouillant tout le contrat §3 de la spec |
| docs | spec (décision schéma) + rapport + registry + roadmap |
| **code applicatif** | **aucun** — lifecycle déjà sûr |

## 4. Interdits tenus

Zéro suppression de `WorkoutTemplate` · zéro mutation d'exercices/séries anciens · zéro exposition `/library` · zéro partage · zéro navigateur d'historique · **zéro table** · **zéro migration** · zéro `WorkoutTemplate.user_id` · zéro réécriture `session_builder` · zéro EKB/ASSET/BodyMap · zéro UI d'unpublish · zéro re-label `catalog_section`.

## 5. Tests

`tests/test_user_program_republication.py` — **11 passés** :
republish v2 crée de nouveaux templates v2 (#1) · anciens v1 non supprimés (#2) · contenu v1 inchangé + édition sur v2 (#3) · v1 non lançable via programme + slug (#4) · programme lié uniquement aux v2 + resolve→v2 (#5) · v2 lançable par le propriétaire (#6) · `/library` exclut v1 **et** v2 (listing + slug), système visible (#7) · étranger → 404 (#8) · système intact (#9) · idempotence, zéro duplicata (#10) · zéro quality write hors freeze, 1/version (#11).

**Broad sweep ciblé** (republication + publish service/http + new_version + launch + library + session_builder + catalog_integrity) : **94 passés**.

## 6. Validation

check_scope **ISOLATED** (1 fichier neuf ; full sweep local skippé par le garde-fou CLAUDE.md §1) · `check_spec_protocol` PASS · `check_ruff_budget` **543 ≤ 548** · `ruff check` fichier neuf **clean**. CI PR = filet de vérité du blast radius.

## Verdict

**Verdict :** 🟢 **Sb_CUSTOM_PROGRAM_PUBLICATION_04 — PATCH COMPLETE / PR PENDING.** Cycle de republication **prouvé sûr et verrouillé** par 11 tests ; anciens `v{n}` préservés/immuables/non-lançables/non-exposés, nouveaux `v{n+1}` liés & lançables ; `/library` inchangé. **Décision schéma : zéro archivage, zéro migration** (le lifecycle requis s'exprime déjà ; l'archivage sûr exigerait une migration additive, hors périmètre). **Zéro code applicatif modifié. Merge = GO humain.**

---
