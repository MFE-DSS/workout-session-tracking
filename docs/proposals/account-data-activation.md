# account-data-activation — proposition réservée, sans GO BUILD

5 novembre 2026. Suite distincte de MOB03, créée comme document de proposition par la scission opérateur GOV-MOB03-SPLIT-01. Aucun change/PR concurrent ouvert. Ancien scope et critères : `account-onboarding-native` au HEADd41eb2f, tasks1.1(D2/D3),4.1(unités corporelles),5.1(acquisitions non couvertes),5.2,5.3,5.4 ; données/privacy de6.4/6.5.

## But et périmètre

Rendre réellement disponibles consentement/retrait et éventuelles acquisitions corporelles, puis demandes d'effacement app/web et leur traitement authentifié. Réutiliser BodyMeasurement/body_profile et le service de demandes isolé livré par le socle. Aucun deuxième historique ni inventaire matériel.

## Critères hérités conservés — tous ouverts

- [ ] DATA-01 : décisions du contrôleur sur catégories/fondements/durées, copies/sauvegardes/restauration, faits locaux non envoyés/non attribués, reçus après effacement et responsable/juridiction/URL. Matrice23tables et tableau existants restent les entrées ; pas de durées arbitraires.
- [ ] DATA-02 : texte/version/finalité de consentement corporel et retrait, acquisitions/unités explicitement utiles et approuvées, héritage sans date exclu ; aucun photo/provider ou writer sans contrat/revue.
- [ ] DATA-03 : migration additive revue du workflow, schéma réellement déployé confronté au graphe, contraintes concurrentes et identité stable/tombstone contre réutilisation d'identifiant ; pas de traitement destructif pendant cette préparation.
- [ ] DATA-04 : routes app Bearer/web session-CSRF partagent le même service ; capacités privées/status après révocation et stockage secret côté client, expiration/récupération ; un autre appareil apprend l'identité canonique de demande active sans créer une seconde demande ni approuver un reçu au mauvais request_id.
- [ ] DATA-05 : mode manuel OU automatisé explicitement approuvé, opérateur/exécuteur réel et preuves de périmètre/révocation/effacement/protection de restauration. Aucun DELETED sur401/404, aucun faux formulaire ou faux traitement manuel.
- [ ] DATA-06 : exception destructive approuvée avant tests destructifs uniquement sur fixtures autorisées ; idempotence/reprise de chaque étape, après début irréversible pas de simple refus prétendant restaurer l'identité. Contrôles migration/drift/snapshot/roundtrip et sécurité requis.
- [ ] DATA-07 : revue visuelle des nouveaux parcours, SDK/consommateurs et accès externe réel, aucun nettoyage avant confirmation autoritaire ; tests A/B et appareil selon suite release.

## Frontières

Ne possède ni moteur/politique scientifique ni MISSION, ni le socle déjà livré. Ne remplace pas STORE00 par un lien inventé. Le futur OpenSpec sera proposé/revu avant application ; production et déploiement nécessitent leurs GO propres. Proposition uniquement : aucune case héritée n'est déclarée réussie.
