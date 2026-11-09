## 1. Prepare
- [x] 1.1 Isoler au canonique fe9f6e9, préserver opérateur et UX en cours.
- [x] 1.2 Documenter scope de recette autorisé, sources et limites.
- [x] 1.3 Check_scope DOCS, spec_protocol PASS, OpenSpec strict global 17/17 et diff sans erreur sur le paquet documentaire ; aucun test/sweep local.

## 2. Controlled acceptance
- [x] 2.1 Monter bundle neuf/DB synthétique, config/flags/générations et schéma/bootstrap exacts ; pas de replay complet Alembic prétendu.
- [x] 2.2a Exécuter le vrai HTTP synthétique : sept rencontres, préparation/choix/familiarisation/qualification, snapshot/V3/ack altéré et exact, création idempotente, A/B et journal typé historique.
- [x] 2.2b Éprouver le retrait d'autorité 3→4 WITHDRAWN→5 ACTIVE de test, faits/lectures préservés et applicabilité BLOCKED ; distinguer flag configuré et autorité réelle.
- [ ] 2.2c Compléter la matrice live des entrées invalides/absentes, perte réseau/reprise en vol, nouvelles mutations sous retrait et coupure des flags ; ne pas déduire ces résultats du seul parcours positif ou des tests historiques.
- [x] 2.3 Inventorier builds/hôtes/appareils ; recette iOS ConnectedApp partielle et blocage Android ExpoTopicSubscriptionModule consignés avec niveau de preuve exact.
- [ ] 2.4 Recette native complète puis physique Android/iPhone sur artefacts compatibles réellement installés, SHA/backend attestés ; aucun APK QA produit et ancien build iPhone SHA/backend inconnus.
- [x] 2.5 Documenter B404/B603 sur appel réel, gardes et risques résiduels ; précisions D1/D2 relues indépendamment, aucune alerte globalement requalifiée ou fermée.

## 3. Closeout readiness
- [ ] 3.1 Revue indépendante du paquet documentaire final/preuves, corrections et matrice DATA/QA/devices/release/CI.
- [ ] 3.2 Publier seulement le périmètre documentaire/recette revu selon GOV-MERGE-01 ; garde HEAD/CI applicable, aucun skip manuel.
- [ ] 3.3 Préparer demande de déploiement seulement si cible/rollback/risques prêts ; aucune autorisation implicitement reçue.
- [ ] 3.4 Conserver preuves/processus attribués et préserver tous autres worktrees ; fin de cycle des seuls processus possédés à vérifier par le responsable de livraison.

RELEASE-01, MOB-03 complet et acceptation physique restent ouverts. Ce change
reste actif ; aucune archive ou fermeture anticipée depuis les preuves HTTP.
