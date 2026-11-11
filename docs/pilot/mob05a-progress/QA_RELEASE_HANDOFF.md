# MOB-05A → REL-03 : intégration au prochain candidat QA

11 novembre 2026. **Code en cours de gate visuel final ; aucun artefact de
distribution MOB-05A construit ou publié.** Ce document est une entrée de
coordination, pas un reçu `qa-release/1.0.0` exécutable ou une autorisation de
déploiement. Le SHA final sera celui du HEAD accepté/testé et du merge vérifié,
à reporter dans le reçu de livraison après intégration.

## Couplage réel client / serveur

Le client Progrès exige les quatre GET propriétaires sous
`/api/mobile/v1/me/training-history` : liste, détail de séance, index d'exercices
et occurrences d'un exercice. Contrats historiques stricts `training-history`,
`training-session-facts`, `training-exercise-index` et
`training-exercise-occurrences` en1.0.0. L'historique SCI consomme aussi la route
V3 d'exécution existante, puis retire les permissions/actions de la vue
historique. Le poids lit la route BodyMeasurement déjà livrée et son accord
applicable. Backend sans ces GET : indisponibilité honnête, pas de données
fabriquées ni de repli web présenté comme fonction native.

Le slice n'ajoute ni module natif, dépendance, migration serveur, schéma SQLite
local, writer, autorité SCI ou génération de politique. Les sept tables PLAN,
le journal canonique, les unités et les sources SCI restent inchangés. Une
absence de migration n'autorise pas à omettre la vérification du schéma et du
bundle effectifs dans le candidat REL-03.

## Construction et activation séparées

L'APK QA02 existant, source `5ed4e0e2ad8e8d80c43dc4049a30dad7f37f5c61`,
package `dev.auren.releaseqa02`, versionCode2, ne contient pas MOB-04/MOB-05A et
ne supporte pas le nouveau canal OTA. Il ne reçoit pas ce slice depuis Git.

Le prochain candidat doit utiliser le vrai SHA client/serveur intégré, un
backend QA explicitement autorisé et compatible, la version/code natif suivis,
le runtime/fingerprint recalculés et le certificat réellement observé. Les
valeurs EAS/build/artifact/update restent inconnues tant qu'aucune opération
autorisée ne les a produites. Ne pas modifier le template partagé REL-03 pour
simuler un candidat prêt.

Pour une future base REL-03 déjà installée et compatible, le code UI/JS de ce
slice peut être classé sans changement natif ; cela ne prouve pas qu'une OTA
est compatible. Le pipeline doit établir les empreintes réelles, la cible et
la décision de release avant toute publication. Pour QA02, une nouvelle APK
compatible reste nécessaire. La signature/package doivent préserver leur
continuité QA et rester distincts d'une future application production.

## Smoke à reprendre sur le build distribué

- Connexion/restauration, compteA→B : aucune séance ou mesure de l'autre compte.
- Onglet Progrès réel, liste et fréquence explicite ; empty distinct d'une
  lecture inconnue, faits précédents conservés après coupure puis refresh.
- Séance → détail → exercice exact → occurrence → retour, avec unités typées,
  provenance dépliable et état incomplet distinct d'une absence.
- Poids daté sous accord applicable, lecture sans écriture ni zéro inventé.
- Android Retour, grandes fontes, safe areas, TalkBack et focus ; relance,
  force-kill et reconnexion du build installé.

Rendus actuels : vrai ConnectedApp iOS et Host/présentateurs Android de
production dans banc synthétique. Ils ne ferment pas la recette de l'APK
installé ou du téléphone du testeur. Aucun nouvel APK/OTA, hébergement, cutover
de QA02, modification OVH/DNS, activation DATA ou déploiement par ce slice.

Rollback : ces lecteurs n'écrivent pas l'historique ; un retour de version ne
nécessite aucune suppression/requalification de faits. La remise d'un ancien
binaire ou update doit rester compatible avec auth/journal et suivre le reçu
de rollback REL-03, vérifié sur un client installé ; aucune preuve de rollback
distribué n'est revendiquée ici.
