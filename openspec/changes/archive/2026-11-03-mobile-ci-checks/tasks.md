# Tasks

## 1. Revue de périmètre

- [x] 1.1 Obtenir la relecture opérateur de proposal/design avant apply ; consigner la décision et l'ordre CODX-00 → CI-01 → MOB-02 (demande de poursuite du 2026-11-03, rapport §Décisions d'exécution).
- [x] 1.2 Mettre la branche sur la canonique incluant CODX-00 après sa livraison ; vérifier le diff limité à CI-01, le Python 3.11 installé depuis le lock et le bon `app.__file__`.

## 2. Job mobile et garde

- [x] 2.1 Écrire une garde ciblée du workflow, la voir échouer sur l'absence du job, puis ajouter le job décrit dans `design.md` ; vérifier qu'elle passe sans affaiblir les autres contrôles.
- [x] 2.2 Exécuter installation verrouillée, `npm test -- --ci --runInBand` et `npm run typecheck` dans `clients/mobile` ; relever les sorties réelles dans le rapport.
- [x] 2.3 Rédiger le rapport CI-01 avec Brainstorming / Options / Risques / Choix et mettre à jour le registre ; vérifier qu'aucun produit/lock/baseline n'a changé.

## 3. Contrôles locaux et CI réelle

- [x] 3.1 Exécuter `python scripts/check_scope.py` puis les contrôles exigés (`ci_infra` attendu), dont ruff/budget, spec protocol, garde ciblée et `bash scripts/run_local_sweep.sh` ; aucun `-n auto` ni script CI sur le poste (7147 tests, 378 fichiers, 95 lots, exit 0).
- [x] 3.2 Après autorisation de livraison, ouvrir la PR et démontrer séparément qu'une assertion Jest fautive et une erreur de type rendent le job GitHub rouge ; relever les runs, restaurer les mutations et obtenir un dernier run vert sur le HEAD proposé (négatif 41679982474 ; final 41680437230, 9/9 jobs réussis, HEAD 764b452).
- [x] 3.3 Relever le nom exact du check et soumettre son ajout aux checks requis à l'opérateur ; ne pas changer la protection GitHub automatiquement (`mobile checks (Jest + TypeScript)`, soumis dans le CR et le descriptif de PR ; décision opérateur en attente).

## Workflow follow-up

- Merge humain puis closeout et archive ; une autre branche reprend MOB-02 après ces preuves.

## Relevé final avant archive

PR #347 mergée `edd7351` ; candidat `8ff2808`, base `cc80ddd`. Sweep final complet : 7147 tests,
378 fichiers,149 lots,exit0 ; 2 adaptations mémoire,aucun fichier sauté. CI PR41707470720 :9/9 jobs verts,
77 tests visuels,422 tests mobiles,typecheck et étapes sécurité passants. CI canonique en cours ;
aucune archive déplacée avant sa vérification. Le check mobile requis sera relu après son application autorisée.

## Vérification canonique et protection finales

CI-01 canonique `edd7351`, run41711441173 : tous les contrôles obligatoires hors Sonar réussis.
Protection phase B appliquée puis relue : QA,lint,visuel et `mobile checks (Jest + TypeScript)` requis,
app_id15368,strict=false ; Sonar consultatif,aucun autre réglage changé.
