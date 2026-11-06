# GOV-MOB03-SPLIT-01 — acceptation du socle distincte de MOB03 complet

5 novembre 2026. Décision opérateur reçue : **« Approuver cette scission traçable »**, après revue de delivery-split-decision.md. Autorise la redéfinition de #353 en socle compte/consommateurs non servis et le transfert explicite des critères restants vers trois propositions. N'autorise aucun déploiement, GO BUILD de suite ou suppression de gate sécurité/CI/visuelle du socle.

Ancien état immuable : commit `d41eb2f49257d233b8b0adac94af6299d4c0e3ad`, `openspec/changes/account-onboarding-native/{proposal,design,tasks}.md` et specs/mobile/{account-lifecycle,onboarding-profile}/spec.md. Les IDs ci-dessous permettent de retrouver chaque critère sans le marquer réussi.

| Ancienne tâche | Sort approuvé / propriétaire actuel | Preuve ou critère conservé |
|---|---|---|
|1.1| Décisions applicables au socle reçues ; solde D1/D2/D3/D4 transféré DATA01/02 et PLAN01/02 | GET kg/chronologie et visuels acceptés, aucune politique restante inventée |
|1.2,1.4| Socle | Identité/journal et tier/checks conservés |
|1.3| Socle pour lecteur actuel, DATA02/06 pour exposition future | Revue ciblée antérieure GET + nouvelle revue finale, aucune UI corporelle nouvelle |
|2.1–2.4| Socle | APIs compte, révocation, classification MOB00 et liens web existants |
|3.1| Socle pour compte/SDK/premier usage ; PLAN01–06 pour onboarding scientifique complet | Vrai ConnectedApp testé, pas de Blueprint inventé |
|3.2,3.3| Socle | Concurrence, réponse inconnue, récupération et retards |
|4.1| PLAN01 pour objectif/durée/expérience ; DATA02 pour unités/acquisitions corporelles | Vocabulaires et stockage à faire approuver, aucun LAB promu |
|4.2| Socle | Préférences compactes et déclarations historiques préservées |
|4.3| PLAN04| Contexte inconnu et substitutions sans inventaire, pas de compatibilité inventée |
|5.1| Socle pour GET kg/SDK/reader unique ; DATA02 pour nouvelles acquisitions/unités | Héritage sans date exclu, aucune seconde chronologie |
|5.2| DATA02/07| Consentement/retrait natifs à raccorder réellement, read gate actuel conservé |
|5.3| DATA01/03–07| Politique, exécuteur, preuve, locaux/copies et suppression réelle restent ouverts |
|5.4| DATA03/06| Toute migration future conserve ses checks ; aucune migration appliquée par le socle |
|6.1| Socle pour surfaces compte/préférences/premier état acceptées ; DATA07/PLAN07 pour les futures | Croquis puis pixels, aucune baseline auto-validée |
|6.2,6.3| Socle | Tests/revue/CI du HEAD final et merge sans bypass |
|6.4| Runbook préparé dans socle ; RELEASE01/06 pour compatibilité déployée/GO/rollback effectif | Aucun déploiement prétendu réalisé |
|6.5| RELEASE02–06| Recettes physiques, force-kill/clavier/accessibilité intégralement ouvertes |
|Rapports/itérations supplémentaires historiques| Socle pour code/preuves acquis ; mêmes DATA/PLAN/RELEASE pour leurs réserves | Les anciennes cases globales ouvertes ne sont pas converties en succès par scission |

Propositions réservées, sans nouveaux changes/PR actifs : [DATA](../../../../docs/proposals/account-data-activation.md), [PLAN](../../../../docs/proposals/blueprint-first-session-runtime.md), [RELEASE](../../../../docs/proposals/account-native-release-acceptance.md). Elles deviendront chacune un OpenSpec/revue/PR distinct avant leur futur apply. Leur stockage comme documents de proposition dans #353 conserve un seul change actif/PR de code, et ne fait pas chevaucher les implémentations.

## Statuts distincts

- **Socle account-onboarding-native** : clos après revue/CI finale, merge db37b76 et CI canonique42129145012 réussis ; seules les suites explicitement listées restent ouvertes.
- **MOB03 complet** : toujours ouvert sur DATA/PLAN/RELEASE ; aucune première séance personnalisée ou suppression réellement disponible déduite.
- **Release/Store/déploiement** : non autorisés/non acceptés par cette décision.
- **MOB04** : préparation de specs/fixtures après livraison autorisée du socle ; pas de GO BUILD implicite.
