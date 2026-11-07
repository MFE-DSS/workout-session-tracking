# SCI-P02-INITIAL-POLICY-ADMISSION — tasks

## 1. Assessment and proposal

- [x] Lire CLAUDE.md et GOV-MERGE-01 ; vérifier baseline et séparation planning/build/deploy.
- [x] Auditer REQUIRED_FIELDS, statut, sélection, prescriptions, calibration, temps et READY v1 dans le vrai code.
- [x] Exécuter check_scope avant probes existants ; reproduire douze sorties sans réécrire de fixture.
- [x] Documenter C1..C6, sources/SHA, limites et verdict auteur NOT_ADMITTED.
- [x] Spécifier corrections pertinentes, contrat versionné proposé, tests, collecte temporelle et handoff.
- [x] Obtenir la revue fraîche builder et scientifique indépendante ; aucun Important résiduel, corrections de design inter-scopes consignées dans le reçu coordinateur.
- [x] Exécuter check_scope sur la préparation finale (ISOLATED avec métadonnée YAML), protocole/OpenSpec13/13, budget et broad ciblé70 ; résultats dans le reçu coordinateur, aucun sweep complet.

## 2. Approval boundary — blocked until explicit decisions

- [ ] Faire trancher contrat READY, limites de la procédure initiale et route temporelle ; désigner responsables scientifiques/collecte.
- [ ] Faire approuver proposal/spec/design et obtenir un GO BUILD distinct pour corrections, contrat/binding et tests bornés ; aucun apply avant cet accord.

## 3. Future implementation — not performed by this preparation

- [ ] Après GO, relire canonique/fetch effectif et confronter tous les pins sans les réécrire ; arrêter sur conflit de spec.
- [ ] Écrire le plan d'implémentation précis puis tests RED des corrections C3/intégrité/bornes et implémentation minimale.
- [ ] Réaliser le protocole temporel autorisé ou consigner son impossibilité exacte ; valider indépendamment l'applicabilité avant admission positive.
- [ ] Versionner la décision d'admission, contrat choisi et binding exact seulement si toutes gates acquises ; sinon conserver NOT_ADMITTED sans registre promu.
- [ ] Vérifier les oracles TEST_SPEC par vrai producteur ; fixture READY seulement avec autorité réelle, jamais autorité de test promue.
- [ ] Exécuter check_scope avant tests locaux ; suivre tier réel, ciblés/broad adaptés, aucun full sweep local pour isolated/docs/shared_code hors doute documenté admis par politique.
- [ ] Obtenir revue code et science indépendantes ; CI obligatoire du HEAD final, merge commit sous GOV-MERGE-01 si conditions acquises, contrôle canonique/closeout/cleanup.
- [ ] Remettre au PLAN le binding réellement admis ou le blocage exact ; aucune activation/API/UI/recette appareil dans ce change.

## 4. Completion rule

- [ ] Ne déclarer ce change implémenté/archivable qu'après son résultat scientifique versionné, vérifications et livraison réelles ; le parent global demeure ouvert tant que ses conditions propres ne sont pas livrées.
