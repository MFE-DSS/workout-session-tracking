# Revue de construction de la proposition

6 novembre2026. Relecteur frais, distinct de l'auteur du design et de la recherche primaire ; lecture seule. Ce contrôle porte la possibilité de planifier le build, **pas** une admission scientifique ou revue de code d'une implémentation absente.

Trois questions importantes retournées, résolues dans le design comme **conventions proposées à l'opérateur**, sans les présenter comme choix déjà approuvés :

1. Reprise après préoccupation/échec : priorité au blocage de l'épisode ; aucune tentative ultérieure favorable ne le lève. Nouveau cycle lié et base/règle de revue applicable nécessaires ; sinon INSUFFICIENT_DATA. Aucun dispositif clinique inventé.
2. Effort inconnu/pending : modes OBSERVED_REFERENCE et BOOTSTRAP_PROTOCOL explicités. RIR inconnu ne bloque pas toute référence observée ; démarrage sans kg connu exige protocole et temps admis. Épisode actif/problème non résolu reste bloquant. Bundle actuel non admis → POLICY_UNAVAILABLE.
3. Familiarisation : confirmation sourcée nécessaire ; même tentative possible avec rôle explicite CALIBRATION_TRIAL, pas d'essai supplémentaire imposé ou série de travail créditée. Simple démarrage ne suffit pas.

Contrôle de la version clarifiée terminé : **« nothing important left »**. Aucun point important de construction restant selon ce contrôle ; les conventions restent proposées à l'opérateur et non scientifiquement admises. Aucun nouveau module, test fonctionnel ou fixture READY exécuté pour résoudre ces questions.
