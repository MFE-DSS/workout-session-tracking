# MOB-04 — Today propriétaire, livraison contrôlée
10 novembre 2026. **Code et pixels contrôlés prêts ; PR/CI/merge encore à vérifier à cette publication.** GO BUILD/G1 puis réponse pixels « Valider ces pixels MOB-04 contrôlés » reçus avant commit UI. GOV-MERGE-01 applicable, aucun déploiement/APK/OTA ou acceptation physique.

## Fonctionnalité
Aujourd'hui privilégie une séance possédée ouverte ou une commande locale dont le résultat reste à vérifier. Le premier parcours PLAN existant est l'entrée par défaut ; l'historique n'est demandé que par choix explicite. Nouveau GET mission-action/1.0.0 propriétaire, négociation/echo stricts et projection sans DML. Client/resource annulent réponses périmées par owner/auth/source/interaction ; même contrôleur et journal existants, pas de moteur ni deuxième commande SCI.

Une réception perdue de start historique reste inconnue, y compris après restart ; GET sans séance ne prouve pas un refus. Marque et exclusion de reprise stockées dans le snapshot local existant, aucun nouveau schéma/outbox. Une séance locale contredite par le serveur ne reçoit plus de nouvelle permission jusqu'à confirmation ; faits conservés. Aucun rejeu automatique d'un POST historique non idempotent. Lecture capturée V3 séparée de permission active.

## Vérification réelle
105 tests backend ciblés et broad consommateurs, dont vrai router/SCI/GET sans DML, déjà passants sur les sources identiques au board accepté. Vérification finale mobile avant commit : **81 suites/1038 tests + TypeScript passants**. Inventaire routes + gardes spec/UI : **27 PASS** ; OpenSpec strict23/23 ; lint fichiers neufs, budget260≤548, Bandit et Gitleaks passants dans les preuves locales. Scope script ISOLATED relevé volontairement SHARED_CODE pour ConnectedApp/agrégateur. Pas de full backend local systématique ; CI réelle du HEAD final obligatoire, résultat pas anticipé ici.

Revue entière fraîche : cinq Important reproduits/corrigés RED→GREEN. Une re-review limitée a été lancée malgré la règle inline d'une seule passe ; elle a identifié deux résiduels A/B et reprise offline, corrigés RED→GREEN puis broad1038/TS vert. Pas d'avis indépendant inventé sur leur dernier patch. Détails, décisions et limites dans REVIEW_AND_VALIDATION.

## Pixels et consommation native
Quinze PNG (deux références intactes, treize nouvelles captures) et SHA256 de huit sources vérifiés identiques au board8136 accepté. [Receipt](../../../clients/mobile/visual-contract/review-receipts/mob04/receipt.json), [board](../../../clients/mobile/visual-contract/review-receipts/mob04/index.html).
Vrai ConnectedApp iOS sur comptes/base synthétiques : Today, reprise séance5, exécution existante, source historique et menu, entrée PLAN existante. Le start historique natif a créé séance6 ; la faute de perte de réponse n'a pas intercepté ce transport, donc aucune preuve native de réponse perdue prétendue. L'oracle de non-double-POST/restart est un test consommateur/SQLite.
Android360/480dp et texte130% : présentateur de production/AuthSession/SQLite/HTTP réels en banc hors produit ; ConnectedApp complet bloqué dans Expo Go par ExpoTopicSubscriptionModule, conservé. Témoin de réception incertaine : état local injecté, explicitement display-only. Pas de nouveau build ni appareil physique. VoiceOver/TalkBack complets restent à éprouver ; label Programmes existant tronqué à360dp/texte130%, aucune baseline globale changée.

## Limite différée et frontières
**M1 différé :** quitter PLAN après création peut laisser l'orientation Today antérieure jusqu'à refresh/foreground ; le contrôleur empêche une deuxième création. Ne pas transformer une CI verte ou l'acceptation du board en recette physique.
MISSION-SCREEN-V1, primitives/tokens/marque, SCI et hashes historiques, journal/outbox/schéma séance et source de calibrage conservés. Aucun catalogue/programme/MOB-06 réservé Maltin, nouvelle recommandation, charge, score ou permission offline. DATA, QA opérationnelle/OVH, diffusion et MOB03 complet restent ouverts.
