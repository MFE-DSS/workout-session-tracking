# SCI-WORKER-EXIT-01 — terminaison contrôlée

## Why
Le correctif V3 est livré à54f68f65. Les campagnes natives précédentes ont admis Legacy5/5,Legacy1003/3,V3etmixte4/7 chacun. Un témoin retourne main et atteint atexit à1,867390sCPU puis meurt SIGXCPU à2,010212sCPU. Les refus restent des refus ; aucune causalité globale n’est supposée.

## What Changes
Seuls worker.py et son test : terminer explicitement après toutes les obligations requises, sans teardown général coûteux de l’interpréteur. Contrôler sortie, digest, fermeture et flush ; échouer sans succès partiel.

## Non-goals
Aucun autre module produit, SCI, writer, TIME-01, DTO, client, source scientifique ou budget. Aucun nouveau PREPARE_IMAGE, QA, modification d’infrastructure OVH, données réelles, APK ou OTA.
