# BODY-01 — livraison native contrôlée

15 novembre 2026. PR #407, parent canonique
`1462482a4e2bcd1fcde121d6f207a2131616e849`. Pixels BODY acceptés globalement
avec réserves de finition ; vérifications locales terminées, CI et livraison canonique en cours.
Aucune acceptation physique, activation réelle, nouvelle APK, OTA ou déploiement.

## Comportement livré par le changement

Profil et Progrès ouvrent le même workspace Mesures. Saisie datée kg/cm,
correction liée sans remplacement des nombres originaux, historique des versions
et effacement individuel confirmé de toutes les versions. BodyMeasurement reste
la seule source numérique ; le sidecar porte identité, révision, provenance et
reçus. Les lecteurs courants filtrent les têtes : ni double comptage ni retour
d'un champ explicitement effacé. Formules et autorités SCI conservées.

API propriétaire `body-measurements/1.0.0`, Bearer, no-store, onze routes
inventoriées ; contrat poids historique préservé, Progrès source-aware. Migration
additive `body_measurement_operations_01` après `plan_v3_20261107_01`, sans backfill
ni DDL startup. Downgrade peuplé refusé ; rollback applicatif conserve le schéma
et les lecteurs de têtes.

Commande exacte persistée SQLite avant HTTP, partition compte/backend, reçu
atomique vérifié, réponses tardives gardées. Réponse perdue : inconnu conservé,
vérification puis éventuel rejeu explicite de la même clé, aucun succès présumé.
Après retrait d'accord, gestion d'effacement sans nouvelle autorisation de
collecte et sans mesures numériques : identité/date/version minimales, relecture
courante, confirmation de toutes les versions et reçu exact après interruption.

## Autorisations et rendu

GO BODY/amendement/G1 conservé : call_106057b169a74bc9887b1fea9f527f5d.
Famille DA08 acceptée : DA08_FAMILY_ACCEPTANCE.json. Pixels natifs présentés
acceptés dans DA08_NATIVE_ACCEPTANCE.json. Réserves non bloquantes : icônes
Retour/Fermer, raccord clavier, légende, repérage de section et hiérarchie des
actions. POLISH_BACKLOG.md les conserve sans retouche non revue de la composition.

Vrai ConnectedApp iOS26.3, 390×844 pt, production presenter/API/SQLite, synthétique :
création, correction/original, versions, retrait, effacement, panne après commit,
kill/reprise et même reçu. Normal et Dynamic Type accessibility-medium, clavier
réel et safe areas. Rotation/focus/VoiceOver exhaustifs non certifiés. Après acceptation, seuls notre
banc et simulateur dédiés ont été arrêtés ; preuves et board restent conservés. Android
actuel sans cible ADB exploitable ; anciennes références Host explicitement
étiquetées, aucun nouveau PASS Android ou physique. SSR rendu séparément.

Board : http://127.0.0.1:8260/ ; ZIP public figé SHA256
`fb8bdae85ff957b41087e6198bfb2d9c78a02862d17ea3408863e0904f7a299e`.
Sources et reçus persistants :
`/Users/martinfeldmann/auren-review/body-da08-integration-20261114/`.
Aucun token, DB privée ou secret dans le paquet public. Primitives, tokens, D4,
MISSION, exécution, SDK/modules/lock et SCI inchangés. Relecture des décisions :
DESIGN_DECISION_REVIEW.md. Les anciens relevés du ledger gardent leur date ;
ils ne décrivent plus le statut courant des pixels.

## Vérification et livraison

Dernière campagne pré-gate : 100 suites /1215 tests mobiles et TypeScript PASS ;
179 backend ciblés et244 broad/SSR/migration PASS, campagnes pouvant se recouper.
Revue indépendante entière et addendum limité au portage correction sans
Critical/Important ; deux mineurs corrigés RED→GREEN. Pas de seconde revue des
correctifs finaux revendiquée.

Le diff entier relève du tier MIGRATION. Campagne finale sur sources immuables :
438 fichiers, 8597 PASS /1 ignoré. Arrêt initial du garde mémoire puis reprises
complètes de deux fichiers par leurs74 et97 cas collectés et des178 autres fichiers ;
ce n’est pas un unique run ininterrompu. Les quatre contrôles de migration passent.
Voir LOCAL_VERIFICATION_20261115.md. La CI du HEAD final reste requise avant merge. Les anciennes CI de checkpoint ou copies combinées ne les remplacent
pas. Sonar consultatif doit être relevé. Un résultat Gitleaks historique dans un
document canonique inchangé reste distinct du scan des sources modifiées et du
paquet public ; aucun seuil ou allowlist modifié.

## Intégration et limites

QA_RELEASE_HANDOFF.md définit API/schéma/reprise/rollback pour REL03. BODY doit
être livré avant la promotion de la migration NUT, puis MOB06 avec résolutions
partagées vérifiées. Les trois PR restent des scopes distincts ; BODY ne vaut pas
acceptation des pixels NUT/Programmes. Aucun APK par merge. QA02 ne contient pas
cette fonctionnalité. DATA, copies/sauvegardes, backend QA stable autorisé,
compatibilité runtime/signature, smoke installé et recette physique restent ouverts.
