# SPRINT Sx_AUREN_ORCHESTRATOR_01 — Gap Consolidation (RAPPORT)

**Base canonique :** `8d9631c` · **Branche :** `sx/auren-orchestrator-01-spec` · **Tier :** DOCS (spec-only)
**Livrable :** `docs/strategy/Sx_AUREN_ORCHESTRATOR_01_GAP_CONSOLIDATION_SPEC.md` + ce rapport + registry + roadmap.
**Livré sous** DELIVERY AUTONOMY ENVELOPE + `CLAUDE.md §4` : `GO BUILD` → `PR GREEN / MERGE PENDING`. **Pas de merge. 0 code, 0 migration.**

## 1. Ce qui est livré

La **roadmap canonique pilotée par les manques** d'AUREN comme orchestrateur d'entraînement
déterministe et conscient de la biomécanique, en 9 sections imposées (A → I) plus un périmètre
interdit explicite. Elle **réconcilie** — sans réécrire — l'existant réellement livré, le blueprint
opérateur, la file morphologie, l'Exercise System V2, `Sx_30`, Body Intelligence, les systèmes
recommandation/readiness/cardio, la fondation zones/muscles, les garde-fous scientifiques et les
manques produit restants.

## 2. Méthode — audit du code actif, pas des rapports

Consigne respectée : *« Do NOT classify from old reports alone. »* J'ai lancé **4 explorations
parallèles en lecture seule** sur la canonique, chacune tenue de produire des preuves `fichier:ligne` :

1. Fondation corps/exercices (zones, EKB, properties, substitution).
2. Fragmentation readiness / fatigue / récupération / disponibilité / cardio.
3. Body Intelligence, `/physique`, overload, export/backup, capture morphologie, slices closes.
4. État déclaré des documents de stratégie + règles de `check_spec_protocol`.

Chaque classification de la §A/§C porte sa preuve. **Là où un rapport ancien contredit le code, le
code fait foi** — signalé explicitement (cas BI/prod, §C.5).

## 3. Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

| Option de structure | Verdict |
|---|---|
| **A** — audit code-first, file ordonnée, contrat unique **conçu mais non implémenté** | ✅ **RETENU** — conforme au mode SPEC ONLY et au blueprint |
| **B** — réécrire la roadmap historique en une seule | ✗ interdit par la mission (« NOT to rewrite old roadmaps ») + détruirait la traçabilité |
| **C** — spécifier ET implémenter le contrat de récupération | ✗ viole SPEC ONLY et heurte l'interdiction de modifier `recommendation.py` |

**Risques traités** : (a) rouvrir du travail clos → §Non-goals liste nominativement les cycles clos ;
(b) inventer des identifiants en collision → vérifiés un par un contre le repo ; (c) figer des
affirmations non scientifiques → §D contraignante ; (d) proposer une architecture impossible → la
contrainte « `recommendation.py` non modifiable » est intégrée à la conception, pas ignorée.

## 4. Constats majeurs de l'audit

1. **`BodyZone`/`ExerciseMuscleMapping` ne sont pas la source de vérité** : **un unique chemin
   d'intégration DB, étroit** (le lecteur `body_map_descriptor`, emprunté depuis plusieurs points
   d'appel, ne servant que la body-map de séance) contre **12+** consommateurs lourds encore sur
   classification par sous-chaîne ou JSON. `Sb_32.4` est donc **retenue comme fondation bloquante**,
   conformément à la consigne conditionnelle.
2. **Deux défauts vivants et visibles par l'utilisateur, non listés au blueprint** :
   - `profile_metrics._zone_session_counts` mélange 6 axes macro et 11 zones détaillées → **seul
     `pecs` peut être compté** ; le coach (« zone travaillée / peu travaillée ») et le radar BI sont
     structurellement faux.
   - collision d'échelle `fatigue_score` **0-100 produit / 0-1 lu** → le message « fatigue élevée »
     est émis quasiment toujours et la branche inverse est inatteignable ; **les tests pinnent la
     mauvaise échelle**.
3. **Fragmentation prouvée** : 5 calculs, 6+ échelles, 3 sens du mot « disponibilité », 2 sens de
   « readiness » affichés sur la même page, et **une seule arête d'intégration, fail-open**.
4. **Cardio = île de données**, exclusion explicite en code.
5. **Moteur de morphologie orphelin** ; `wingspan_cm` inexistant hors du module pur.
6. **Activation BI ambiguë** : flag par défaut `False`, aucun `.env` du repo ne l'active, absent du
   smoke, et **deux documents se contredisent** sur l'état prod → risque #1.

## 5. Écarts assumés par rapport à la file demandée

La mission autorise renommage/fusion/suppression/réordonnancement **uniquement si le repo prouve une
meilleure frontière**. Quatre écarts, tous justifiés par une preuve :

| Écart | Justification |
|---|---|
| **+ `Sb_ZONE_COUNT_TAXONOMY_FIX_01`** (P0, ajout) | Défaut vivant §C.0-A, visible utilisateur, isolé et peu coûteux. Le migrer tel quel dans `Sb_32.4` reviendrait à migrer une projection fausse. |
| **+ `Sb_FATIGUE_SCALE_FIX_01`** (P0, ajout) | Défaut vivant §C.0-B, visible utilisateur, et **les tests verrouillent l'erreur** — à corriger avant de normaliser quoi que ce soit. |
| **`Sb_03.1_SUBSTITUTION_REASON` → `Sb_SUBSTITUTION_REASON_01`** | `Sb_03.1` est un identifiant hérité d'une **autre lignée de spec** (consolidation Exercise System) → collision d'ID ambiguë. Contenu élargi au `rationale` manquant de N1/N3. |
| **`Sb_PHYSIQUE_BI_CONVERGENCE_01` reciblée** | La décision est **déjà prise et close** (`Sb_BI_01.next`, Option B : BI primaire, `/physique` déprécié progressivement, route conservée). La slice **exécute** cette décision ; la rouvrir violerait la règle anti-rebuild. |

Deux clarifications sans renommage : `Sb_BI_01.activation` existe déjà comme
`Sb_BI_01.activation-readiness` (**plan livré**) → la slice restante est l'**activation** elle-même,
qui doit **commencer par établir la vérité d'état prod**. `Sb_MORPHO_PROFILE_RUNTIME_01` est bien
**neuf** (`Sb_MORPHO_PROFILE_01` est le module **pur** déjà mergé).

## 6. Fichiers touchés

| Fichier | Changement |
|---|---|
| `docs/strategy/Sx_AUREN_ORCHESTRATOR_01_GAP_CONSOLIDATION_SPEC.md` (**neuf**) | la spec, sections A→I + périmètre interdit |
| `docs/SPRINT_Sx_AUREN_ORCHESTRATOR_01_GAP_CONSOLIDATION_REPORT.md` (**neuf**) | ce rapport |
| `docs/strategy/SPEC_REGISTRY.md` | nouvelle section `1duodecies` + entrée |
| `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` | pointeur vers la roadmap canonique |
| **code / migrations / tests** | **aucun** |

## 7. Interdits tenus

**0 code · 0 migration · 0 test applicatif · 0 UI.** Aucun cycle clos rouvert (liste nominative en
§Non-goals). Aucune modification de `recommendation.py` (contrainte intégrée à la conception).
Aucune roadmap antérieure réécrite. Aucune revendication médicale/composition/EMG/« % récupéré ».
Aucun build, merge, cleanup ni activation de flag autorisé par ce document.

## 8. Validation

`python scripts/check_scope.py` → **DOCS** · `python scripts/check_spec_protocol.py` → **PASS**
(la spec porte le marqueur littéral requis « Non-goals / Périmètre interdit ») ·
`python scripts/check_ruff_budget.py` → **543 ≤ 548** (inchangé, 0 code).

**Note CI** : diff 100 % `docs/**` → la CI push est **légitimement skippée** par `paths-ignore`
(`CLAUDE.md §2`). La CI de **PR** reste la source de vérité.

**Note de coordination** : cette PR et la PR **#68** (`Sb_MORPHO_DOGFOOD_01`) modifient toutes deux
`SPEC_REGISTRY.md` et `ROADMAP_AND_NEXT_STEPS.md`. La **seconde mergée** demandera un rebase trivial
sur ces deux fichiers ; aucune autre intersection.

## 11. Verdict

**Verdict :** ✅ **Sx_AUREN_ORCHESTRATOR_01_GAP_CONSOLIDATION_SPEC — MERGED.**
Roadmap canonique pilotée par les manques, adossée à un **audit du code actif** avec preuves
`fichier:ligne` : capability map, architecture cible, matrice de manques (**dont 2 défauts vivants
découverts**), garde-fous scientifiques contraignants, matrice de sources de vérité, graphe de
dépendances, file ordonnée P0→P2→E2E entièrement spécifiée par slice, différés/rejetés, et
définition de fin de programme. **SPEC ONLY : aucun build n'est autorisé par ce document.**

---

## Appendice post-merge (closeout)

- **Merge** : PR **#69 MERGED** 2026-08-10, build `7c36581` + fix Gitar cohérence `91a0252` +
  synchronisation canonique `09238c8`, merge commit **`d69a1a6`** via
  `--merge --match-head-commit 09238c8` — **sans squash, sans `--admin`, sans force** (gate `CLEAN`,
  `MERGEABLE`, **0 thread non résolu**, head épinglé).
- **Synchronisation sans réécriture d'historique** : la canonique `d447615` (incluant `Sb_MORPHO_DOGFOOD_01`
  et son closeout) a été **fusionnée DANS** la branche — **pas de rebase, pas de force-push**. Le
  conflit unique portait sur l'item 5 de la roadmap ; résolu en **préservant les deux apports** :
  statut final MERGED de `#68` + le pointeur de roadmap canonique de `#69`. Diff final vs canonique :
  **570 insertions, 0 suppression** — aucun contenu de `#68` perdu.
- **CI de PR** : **5 checks PASS** sur `09238c8` (pytest + QA · lint · Gitar · SonarCloud · gate
  externe SonarCloud Code Analysis) ; **gate Sonar OK** (0 bug/smell/vuln/SCA neufs).
- **CI canonique** : **légitimement SKIPPÉE** — le merge `d69a1a6` est **100 % `docs/**`**
  (5 fichiers, tous sous `docs/`), donc filtré par `paths-ignore` (`CLAUDE.md §2`). Ce n'est pas un
  `[skip ci]` manuel : la CI de PR reste la source de vérité et elle est verte.
- **Thread Gitar résolu par correction réelle** : le décompte « un seul consommateur DB » du résumé
  exécutif contredisait §C.1 qui énumérait deux fournisseurs. Reformulé partout en **« un unique
  chemin d'intégration DB étroit »** (lecteur `body_map_descriptor`, plusieurs points d'appel, une
  seule surface servie) contre **12+** consommateurs lourds. **Conclusion inchangée : `Sb_32.4`
  reste une fondation bloquante.**
- **Cleanup** : branches + worktrees de `#68` et `#69` supprimés (cleanup explicitement inclus).
- **Suite** : la file P0 effective démarre à **`Sb_ZONE_COUNT_TAXONOMY_FIX_01`**. **Aucun sprint
  produit n'est ouvert** — chacun reste sur GO explicite.
