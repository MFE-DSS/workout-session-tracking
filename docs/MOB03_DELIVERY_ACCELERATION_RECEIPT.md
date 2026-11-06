# MOB-03 — reçu DELIVERY ACCELERATION

**Livraison du socle : #353 fusionnée au merge `db37b76` ; CI PR42126920199 et canonique42129145012 réussies.** [Closeout et archive du seul socle](MOB03_FOUNDATION_CLOSEOUT.md). MOB03 complet conserve DATA/PLAN/RELEASE ouverts, aucune activation ou recette physique déduite.

5 novembre 2026. PR unique #353 ; base `bf847c7`, précédent HEAD `d41eb2f`. Nouveau delta réalisé localement, publication/revue/CI finales à consigner dans la PR. **COMPLETE MOB03 non acquis**, aucun déploiement.

## Brainstorming / Options / Risques / Choix retenu

Conserver les ports seuls ne terminait pas les fondations. Activer une purge ou un plan de repli inventerait une politique. Choix : vrai service transactionnel non servi avec schéma de workflow isolé, et premier usage natif limité aux états prouvés. Service et croquis acceptés par l'opérateur ; pixels acceptés : « Valider ce rendu » avant commit UI.

## Réalisé / limites

- Service serveur partagé futur app/web : réauthentification canonique/CAS, demandes idempotentes et une demande active par propriétaire, persistance transactionnelle SQLAlchemy, lecture authentifiée, refus terminal et capacité de suivi limitée/rotative/expirante à condensat seul. Politique et vérificateur absents par défaut ; aucun import de démarrage, route, migration appliquée, worker, purge ou révocation irréversible. La table proposée ne change pas le graphe de 23 tables métier actuel ; sa migration future garde sa revue.
- Preuves de confirmation liées à propriétaire/demande/politique/portée/révocation/effacement/restauration ; aucun 401/404 ou disparition de compte n'est une preuve. Les preuves et politiques synthétiques ne vivent que dans les tests ; aucun workflow manuel réellement activé.
- Premier usage branché après résultat de création, accès aux préférences puis retour au parcours, sortie vers MISSION distincte d'un premier plan scientifique ; séance à reprendre prioritaire. SDK de préférences et FirstPlanClient réels, snapshot canonique absent par défaut, aucune fabrication de Blueprint/READY. Un résultat SCI sans contrat de démarrage reste indisponible.
- [Compatibilité, plan appareil et rollback](MOB03_RELEASE_RUNBOOK.md) prêts ; aucune recette physique prétendue effectuée. [Scission approuvée](strategy/MOB03_DELIVERY_SPLIT_AUTHORIZATION.md) : socle distinct de MOB03 complet ; tous les anciens critères transférés restent ouverts dans trois propositions réservées, sans nouveau change/PR actif.

## Croquis validé

Source : delivery-acceleration.md ; décisions reçues «Valider le service isolé proposé» et «Valider ce croquis ciblé». Une seule page après résultat compte créé : en-tête AccountFrame, titre «Ton premier entraînement», un message d'état, une action utile puis «Voir Aujourd'hui». Aucun nouveau formulaire ni cockpit chiffré.

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| Marque/en-tête | Identité AUREN | AccountFrame/AurenMark existants | non |
| Titre | Rôle du passage | Texte du croquis accepté | non |
| Message unique | Chargement/manque/consentement/absent/inconnu/indisponible | FirstUseController ; SDK canonique, snapshot futur et FirstPlanClient ; fixtures étiquetées sur banc seulement | non |
| Action | Modifier les préférences ou relire | Route native préférences existante / lecture controller.load | non |
| Sortie Aujourd'hui | Accès à la surface existante, pas preuve SCI | Coque ConnectedApp et MISSION existante | non |

## Comparaison avec la référence validée

| Référence validée | Tranche / date | Ce qui doit survivre | Survit ? |
|---|---|---|---|
| Compte V1 ajustée | MOB03  / 5 novembre | Entrée, résultat compte créé, logo, tokens et actions | oui |
| Préférences compactes sans inventaire | MOB03  / 5 novembre | Grille et déclarations conservées, retour et coque montée | oui |
| MISSION LOCKED | Contrat visuel | Aucune recomposition, aucun indicateur inventé | oui |

Rendu comparatif : http://127.0.0.1:8094/comparatif-premier-usage.html. Huit états rendus à 320/390/430 px, pas de débordement horizontal, erreur JS ou requête externe ; parcours de banc compte créé→premier usage→préférences. Ce banc web ne prouve pas VoiceOver/TalkBack ou force-kill natif.

## Changement unique de l'itération

- Demande : «Prepare the first-use native journey from the accepted account screen to the existing MISSION surface.»
- Changement : ajouter le seul passage d'état accepté, sans modifier entrée/résultat/préférences/MISSION.
- Avant : compte créé puis MISSION ; après : compte créé, état honnête, préférences facultatives puis MISSION. Comparaison ci-dessus, aucune baseline auto-approuvée.
- Relecture des décisions : entrée V1, signup/password, préférences compactes, priorités facultatives/no inventory et journal propriétaire respectés ; géométrie/token/instruments/BodyMap non concernés. Consentement/poids natifs, premier READY et effacement réels non livrés.

## Blocages véritables

Politique contrôleur et ses cinq arbitrages existants ; migration/routes/producteur et suivi après révocation non servis ; admission SCI dose/candidats/temps, snapshot et contrat de démarrage ; consentement/acquisitions natifs, compatibilité déployée et preuves physiques. Scission approuvée : ces critères restent les gates de MOB03 complet et de ses suites DATA/PLAN/RELEASE ; ils ne sont pas déclarés réussis par la livraison du socle. Le reçu exact HEAD/revue/CI/Sonar dans #353 reste l'autorité de publication distante.

## Décision de rendu reçue

L’opérateur accepte : **« Valider ce rendu »**. Les captures et leurs empreintes sont conservées dans `clients/mobile/visual-contract/review-receipts/mob03-first-use-v1/`, sans modifier une baseline LOCKED.

## Vérifications locales

Nouveau delta : **54 suites / 676 tests mobiles**, TypeScript ; service isolé **18 tests** passants sur SQLite réel, **248 tests backend ciblés/broad** passants après la dernière garde ; Ruff fichiers neufs et budget **264≤548**, Bandit ciblé, protocole documentaire et OpenSpec strict **7/7**. Nouvelle lecture du tier avant les checks ; pas de full sweep local sur ce code sans migration appliquée. Revue indépendante et CI exacte restent à consigner avant merge.

Revue indépendante du delta : un Important confirmé, correction du helper canonique de réauthentification sans réhydratation de l’objet principal avant validation. Deux régressions sur demande existante/tentatives répétées observées RED puis GREEN ; broad backend248, Jest676 et TypeScript repassés après correction. Aucun autre Important/Critical, aucune activation ou recette physique déduite. Tier final SHARED_CODE.
