# Tasks — contrat v2 isolé autorisé, admission positive distincte
- [x] Vérifier canonique2cddf5d et livraisons #369/#370 ; ne pas refaire l'étape1.
- [x] Confronter représentation v1 aux vrais drafts et diagnostics v2.
- [x] Définir contrat v2 proposé, unions, invariants READY, ownership et limites.
- [x] Revue fraîche de faisabilité du dossier : aucune question importante restante, aucun conflit/pin ou READY relaxé détecté.
- [x] Choix/approbation opérateur du delta de contrat et GO BUILD borné : « Valider le contrat v2 et ce build isolé ».
- [x] Après ce GO : types/schémas/tests isolés v2 réalisés ; v1 préservé, aucune admission positive déduite.
- [ ] SCI-POS01/02/03 : décisions de population/dose/bootstrap/candidats réellement liées au bundle.
- [ ] SCI-POS04 : contrat définitif revu et convention de projection effectivement admise.
- [ ] SCI-POS05 : base temporelle positive et moyens/données/protocole admissibles, pas de durée inventée.
- [ ] SCI-POS06 : binding/producteur/version/fixture READY réels seulement si toutes gates acquises.
- [ ] SCI-POS07 : handoff compatible à PLAN, sans écrire son SDK/backend en parallèle.
- [x] Exécuter `python scripts/check_scope.py` avant contrôles du diff ; protocole/OpenSpec maintenant, ciblés/broad et CI selon tier après code, aucun full sweep local redondant.
- [x] Revues SCI/code, CI PR371 et merge permanent114312e du seul contrat autorisé ; contrôle canonique et closeout suivis dans le reçu, déploiement non autorisé.

Les cases SCI-POS ci-dessus restent ouvertes et correspondent intégralement à la proposition réservée et au parent. Ce ne sont pas des critères de COMPLETE du seul build de contrat autorisé. La revue code a trouvé deux Important, corrigés par cinq cas de régression ; revue SCI séparée sans Important. La CI PR finale42378325542 est verte (neuf jobs), merge114312e vérifié. La CI canonique42379843461 et les contrôles de la maintenance de clôture sont suivis séparément dans le reçu vivant ; leur succès n’est pas anticipé dans cette archive préparée.
