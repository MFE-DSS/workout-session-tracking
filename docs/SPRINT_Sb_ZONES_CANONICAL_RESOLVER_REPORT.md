# Sb_ZONES_CANONICAL_RESOLVER — l'app reçoit les zones d'un exercice par le contrat canonique

**Date :** 2026-10-29
**Branche :** `sb/zones-canonical-resolver` (base canonique `20d0581`)
**Verdict :** voir la fin du rapport.

## 0. Commande

L'opérateur, 2026-10-29 : « de manière agnostique, tu associes les images à des zones de travail. Ces zones de
travail sont après exploitées par des exercices comme muscles principaux ou secondaires […] Et après, les exercices
sont ajoutés dans les programmes. C'est vraiment cette approche qu'il faut avoir de manière agnostique pour résoudre
les zones. »

Constat de DA-04.2 à l'origine : le plan servi à l'app et le relevé de séance classaient chaque exercice par l'ancien
classifieur à sous-chaîne, **sans les corrections revues** de `body_zone_source` :

| Exercice | Ancien classifieur | Contrat canonique |
|---|---|---|
| Rear delt fly machine (pec deck inversé) — Pull A | `pecs` [`triceps`] | `delt_post` |
| Relevé de jambes suspendu — LISS cardio + abdos | `calves` | `core` |

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

| Option | Pour | Contre |
|---|---|---|
| A — corriger les deux noms dans le classifieur à sous-chaîne | minimal | casse la base d'invariance `classify_exercise_baseline.json` ; une seconde liste de corrections |
| B — brancher le plan mobile et le relevé sur `resolve_exercise_zones` | une seule autorité, corrections comprises ; donne aussi les zones secondaires | migre deux consommateurs : une décision, que la garde exige d'inscrire |
| C — tout migrer (plus `profile_metrics`, `coach_*`, `body_intelligence_inputs`) | cohérence totale | hors de la demande ; chaque consommateur a ses gardes d'invariance |

**Choix : B.** Le plan et le relevé alimentent tous les deux l'app : ils doivent nommer la même zone pour le même
exercice. Les autres consommateurs restent sur leur chemin actuel (§4).

**Risques** : changer une zone affichée (→ deux exercices seulement, ceux que la liste revue corrige ; 0 divergence
sur le reste du catalogue, mesurée par `build_parity_report`) ; casser la forme de la réponse (→ champ **ajouté**
`secondary_zones`, `zone` inchangé ; côté client, champ optionnel).

## 2. Changements

| Fichier | Changement |
|---|---|
| `app/services/mobile_read_models.py` | `_exercise` résout par `resolve_exercise_zones(db, nom exécuté)` ; ajoute `secondary_zones: [{zone, label}]` |
| `app/services/session_recap.py` | `_zones_touched` résout par `resolve_exercise_zones(None, nom)` (corrections revues, puis repli) |
| client mobile, `src/domain/types.ts` | `PlanExercise.secondary_zones?` (optionnel : une charge d'avant n'en a pas) |
| `tests/test_mobile_zones_canonical.py` | 5 tests : plan = résolution canonique (principale et secondaires), Rear delt fly en `delt_post` sur le téléphone, presse avec `triceps` en secondaire, relevé = même zone, aucun module de charge mobile ne retombe sur l'ancien classifieur |
| `tests/test_exercise_muscle_mapping.py` | les deux consommateurs **ajoutés sciemment** à la liste migrée, motif cité ; `mobile_read_models.py` ajouté à la liste surveillée (il n'y figurait pas) |

## 3. Vérification

- `check_scope` : `SHARED_CODE` → balayage ciblé obligatoire : 26 fichiers de tests (plan mobile, auth mobile,
  relevé, revue de séance, ontologie, migration des consommateurs, mapping, exposition de zones, descripteur
  BodyMap, taxonomie, scoring…) — 459 tests verts après inscription de la migration (la garde de migration avait
  rougi comme prévu, avant l'inscription).
- Les tests neufs **discriminent** : l'ancien classifieur rend `('pecs', ['triceps'])` et `('calves', [])` sur les
  deux noms, la garde attend `delt_post` et `core`.

## 4. Reste hors de cette tranche

`profile_metrics`, `coach_inference`, `coach_report`, `body_intelligence_inputs` lisent toujours l'ancien chemin.
Leur migration est une décision par consommateur (gardes d'invariance propres), à prendre si l'opérateur veut
l'unification complète.

**Verdict :** le plan servi à l'app et le relevé résolvent les zones par le contrat canonique — principale et
secondaires —, conformément à la règle agnostique de l'opérateur ; deux erreurs d'attribution visibles sur le
téléphone corrigées.
