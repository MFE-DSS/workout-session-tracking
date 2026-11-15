# BODY-01 après MOB-05A — première écriture native à cadrer

11 novembre 2026. Base réconciliée par avance rapide au merge MOB-05A
`18e04bd25ae424e97ac9f810321972e1b101dcae` ; CI canonique encore suivie au
moment de cet ajout. Les24 fichiers préparatoires BODY/NUT antérieurs ont été
sauvegardés et comparés par hash avant toute révision. **Préparation seulement ;
NO_GO_BUILD / BLOCKED_SPEC_RECONCILIATION / G1_PENDING / NOT_SERVED.**

## Ce qui existe désormais et ne doit pas être refait

Progrès lit les mesures datées depuis BodyMeasurement, via le client/ressource
poids et l'accord existants. Il n'écrit aucune mesure, ne stocke pas de seconde
série et ne remplace pas une absence par le poids du profil. Les dates/qualités,
plusieurs IDs à la même date et les valeurs inconnues restent distingués.
Le lecteur invalide ses réponses tardives par compte/période et n'effectue les
lectures que depuis la surface focalisée. Les historiques séance/SCI ne sont
pas des producteurs de mesure corporelle.

## Premier consommateur d'écriture proposé

Une mesure de poids réellement saisie et datée, sous propriétaire et accord
applicables, vers le writer canonique BodyMeasurement. L'aperçu explicite valeur,
unité, date et source humaine ; ni poids initial, jour ou consentement ne sont
déduits d'une lecture. Après reçu serveur confirmé, rafraîchir les lecteurs
canoniques ; une réponse perdue reste à réconcilier sous la même identité de
commande. Les unités, booléens/nonfinis, occurrence/enregistrement, stale revision,
kill/reprise, compteA/B et absence de permission sont des tests de consommateur.

Les tours de ruban, corrections et historique appartiennent au design BODY
existant ; ils ne sont ni implémentés ni intégrés à MOB-05A. La première preuve
doit rendre une mesure créée visible par le vrai lecteur Progrès, sans nouveau
modèle, cache de tendance ou moyenne scientifique ajoutée par commodité.

## Décision qui précède tout apply

[CONTRACT_RECONCILIATION](CONTRACT_RECONCILIATION.md) reste l'autorité de ce
blocage : capture append-only versus correction manuelle propriétaire. Le merge
MOB-05A n'a modifié aucune des deux sources contradictoires et n'accorde aucune
exception. L'optionA proposée doit être expressément choisie et amendée dans le
contrat canonique avant le GO BUILD ; B ouC exige le scope révisé correspondant.
Un « GO BUILD » générique, l'ancien GO Progrès ou la présence du writer web ne
résolvent pas cette contradiction.

Après décision : revue du delta normatif et de la forme additive du sidecar,
garde commune des writers, dates/id/concurrence/replay/copies locales ; GO/G1
propres puis vrais pixels et tests. DATA réelle et distribution gardent leurs
gates. Aucun writer, migration, moyenne, traitement photo, correction destructive,
appel fournisseur, nouvelle PR ou modification du banc QA par cette préparation.

## Leases de composition

Reprendre le BUILD_SCOPE sur le canonique frais après closeout MOB-05A, puis
réserver ConnectedApp/ShellContext/Progrès seulement pour la porte vers le même
consommateur BODY. Conserver TrainingHistoryHost et ses clients read-only ; ne
pas insérer les commandes BODY dans le journal des séries. NUT reste séquencé
sur les fichiers partagés ; MOB-06/Maltin demeure hors périmètre.
