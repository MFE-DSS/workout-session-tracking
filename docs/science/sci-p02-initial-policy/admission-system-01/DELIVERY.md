# SCI admission étape1 — réalisation en cours

Périmètre autorisé par « Valider uniquement ce build SCI isolé », voir BUILD_AUTHORIZATION.md. Code successeur, registre vide et refus seulement ; politique non admise/non servie, aucun READY ni API/UI/activation. Ce fichier recevra les résultats réels avant livraison, sans anticiper CI/merge. Les sections de préparation des rapports voisins décrivent leur étape historique.

## Brainstorming / Options / Risques / Choix retenu

Corriger en place les modules historiques changerait leurs rejeux pinés. Copier un nouveau moteur complet créerait une divergence inutile. Choix retenu : wrappers successeurs explicites autour de la validation historique, comparaison stricte du résultat recomputé, puis diagnostics séparés et registre vide figé. Les fonctions nouvelles sont réellement consommées par le nouvel évaluateur ; elles ne sont pas présentées comme corrections rétroactives du producteur2.0.0. Contrat READY inchangé.
