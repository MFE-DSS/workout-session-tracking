# DATA-ACT-01 — audit read-only des fondations

Base `fe9f6e9`, 9 novembre 2026. Inspection statique seulement ; pas de nouveau
test produit exécuté et aucune garantie nouvelle d'intégration/production.

| Fondation déjà présente | Source examinée | Conclusion de réemploi |
|---|---|---|
| Identité/réauthentification, époques et sessions d'appareil | account_lifecycle, appelé par account_deletion_requests ; contrat MOB03 | Garder identité serveur et preuve du secret courant, mobile Bearer/web session-CSRF ; ne pas rouvrir choix par username |
| Workflow durable isolé | app/services/account_deletion_requests.py : metadata séparée, request/read/reject, unique owner/request et active_owner, version CAS | **Déjà écrit** ; pas demander de créer un second service de demandes ou une deuxième table générique |
| Admission de politique et vérification de preuve fermées par défaut | Policy(admitted=False), registry vide, verifier absent ; _policy exige scope/retention/controller refs et capacité positive | Garde existante, pas politique admise. Injecter une référence fictive ne serait pas une fondation sûre |
| Capacité de suivi isolée | issue_status_capability/read_status_capability, hash serveur, expiration, comparaison constante | **Déjà écrit** ; émission/adaptateurs/stockage client privé et récupération multi-appareils restent non intégrés. Ne pas mettre token en URL/log/outbox/reçu |
| Confirmation isolée | confirm exige IN_PROGRESS/CONFIRMED et preuves scope/owner/request/policy + verifier | Pas de méthode de début irréversible ; impossible d'en déduire un exécuteur livré ou un DELETED réel |
| Consentement corporel et chronologie | app/models/body_consent.py ; app/services/body_profile.py | body_measurements explicite/versionné/horodaté, retrait distinct de l'effacement, export et suppression unitaire existants. Ne pas créer deuxième historique ou importer le poids User sans date |
| Intention et retrait local | clients/mobile/src/storage/accountRequestStore.ts, ownershipStore.ts ; design MOB03 | Réutiliser les identités et gardes persistées ; une marque locale ne garantit pas non-réapparition serveur/restauration/réinstallation |
| PLAN contrôlé sept tables et journal | app/models/first_plan_runtime.py, snapshots.py, planV3Journal.ts | Réutiliser ledger, snapshots, évaluations, ack, commandes, bindings et observations ; aucune nouvelle table DATA pour les recopier |
| Export typé et refus de perte | export_builder.py, plan_v3/execution.py, restore.py | Réutiliser lecteur JSON et refus CSV/restore legacy. Ne pas décrire ces refus comme une restauration complète ou un export compte exhaustif |

## Fondations réellement manquantes, séquencées sans nouveau GO implicite

| Suite bornée proposée | Ce qui manque vraiment | Gate / prochain travail sûr |
|---|---|---|
| F01 — contrat d'admission DATA par finalité | Politique signée reliant catégories/traitements/version/retrait/retention/copies aux sources et assessment ; aujourd'hui UNAVAILABLE | **Maintenant : questionnaire et schéma documentaire seulement.** Après D01–D09 : design d'admission/propagation des retraits, revue de spec puis GO BUILD séparé pour code ; ne pas recycler le booléen BodyConsent comme accord PLAN |
| F02 — fermeture cohérente et identité stable | Design de transition irréversible, verrouillage commun des writers historiques/PLAN, idempotence/reprise par étape, non-réutilisation d'identité et registre de retrait/exclusion | **Maintenant : inventaire et dépendances**. Exécuteur, tombstone serveur, exception immutabilité/destruction et preuves ne partent qu'après D03/D07/D08, revue et autorisation explicite ; jamais DELETE users aveugle |
| F03 — adaptateurs et migration workflow | Route mobile/web commune au service existant, schéma de migration revue/confrontée au déployé, suivi privé après révocation/autre appareil | **Maintenant : réemploi identifié**, sans route ou migration. Après politique/mécanisme/URLs et GO approprié : compléter le service, ne pas le réécrire ; capacités existantes à intégrer avec identité canonique de demande active |
| F04 — export compte complet / copies PLAN | Contrat de couverture des sources/snapshots/évaluations/commandes en plus des séances exportées ; qualification des fichiers maîtrisés et limite téléchargée | **Maintenant : graphe et manque précis**, pas format/implémentation parallèle. Après D02/D05 : design/version/ownership à revue ; pas de promesse d'effacement à distance d'un export téléchargé |
| F05 — sauvegarde/restauration et exclusion | Inventaire déployé, stratégie typée PLAN complète, exclusion avant restauration, preuves vérifiables de non-réapparition | **Maintenant : questionnaire opérateur sans secrets**. Ne pas exécuter helper backup/restore ou prétendre que son défaut de 30 jours est admis. Après D06/D07 : procédure et tests synthétiques explicitement autorisés |
| F06 — purge locale propriétaire incluant V3 | Producteur/reçu autoritaire et politique de sort des faits non envoyés ; traitement coordonné sidecar/outbox/active_session/credentials et marque de retrait | **Maintenant : liste des surfaces**, pas câble de reset(). Après D04/D07 et producteur : design ciblé, reprise/échec et isolation A/B + faits inconnus, puis build/recette appareil autorisés |
| F07 — ressources publiques et exploitation réelle | Responsable/texte approuvés, URL privacy et demande web publiées/fonctionnelles, exécuteur vérificateur nommé, support et limites | **Maintenant : cases OPEN.** Aucun domaine/slug/formulaire inventé. Publication externe et traitement réel requièrent leurs autorisations et contrôles ; un lien existant de backend ne les remplace pas |

La préparation actuelle achève le travail documentaire sûr réellement manquant :
un paquet unique, une couverture explicite PLAN et une carte de réemploi. Elle
ne déclare aucune de F01–F07 implémentée. Les tests du socle, cités dans les
rapports historiques, ne sont pas relancés pour une modification documentaire.

## Arrêts qui demandent une décision du responsable

Absence de politique/finalité/identité/URL réelle, choix de conservation, exception
destructive et données opérateur non connues restent OPEN. Une réponse à une
ligne ne débloque pas les autres. Les techniques déjà contraintes (réauth,
idempotence, propriétaire, pas de purge unknown/pending, secrets hors URL) ne
sont pas renvoyées au responsable comme nouveaux choix de produit.
