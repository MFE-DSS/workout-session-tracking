# Tasks

## 1. Revue de périmètre

- [x] 1.1 Obtenir la relecture opérateur de proposal/design avant apply ; consigner la décision et l'ordre CODX-00 → CI-01 → MOB-02 (demande de poursuite du 2026-11-03, rapport §Décisions d'exécution).
- [ ] 1.2 Mettre la branche sur la canonique incluant CODX-00 après sa livraison ; vérifier le diff limité à CI-01, le Python 3.11 installé depuis le lock et le bon `app.__file__`.

## 2. Job mobile et garde

- [x] 2.1 Écrire une garde ciblée du workflow, la voir échouer sur l'absence du job, puis ajouter le job décrit dans `design.md` ; vérifier qu'elle passe sans affaiblir les autres contrôles.
- [x] 2.2 Exécuter installation verrouillée, `npm test -- --ci --runInBand` et `npm run typecheck` dans `clients/mobile` ; relever les sorties réelles dans le rapport.
- [x] 2.3 Rédiger le rapport CI-01 avec Brainstorming / Options / Risques / Choix et mettre à jour le registre ; vérifier qu'aucun produit/lock/baseline n'a changé.

## 3. Contrôles locaux et CI réelle

- [x] 3.1 Exécuter `python scripts/check_scope.py` puis les contrôles exigés (`ci_infra` attendu), dont ruff/budget, spec protocol, garde ciblée et `bash scripts/run_local_sweep.sh` ; aucun `-n auto` ni script CI sur le poste (7147 tests, 378 fichiers, 95 lots, exit 0).
- [ ] 3.2 Après autorisation de livraison, ouvrir la PR et démontrer séparément qu'une assertion Jest fautive et une erreur de type rendent le job GitHub rouge ; relever les runs, restaurer les mutations et obtenir un dernier run vert sur le HEAD proposé.
- [ ] 3.3 Relever le nom exact du check et soumettre son ajout aux checks requis à l'opérateur ; ne pas changer la protection GitHub automatiquement.

## Workflow follow-up

- Merge humain puis closeout et archive ; une autre branche reprend MOB-02 après ces preuves.
