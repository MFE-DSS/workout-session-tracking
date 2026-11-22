## Why

TIME-01 demande la qualification d'un écart historique de 28228,214 secondes,
sans lui attribuer une cause plausible. La restauration a été reproduite dans
l'APK signée dff03f3, sur copie AVD hors réseau : une ancre persistée est
réappariée à une horloge monotone neuve, puis une SET unique est enregistrée
avec un écart de 58915,472 secondes et estimated=false. Ce cas distinct prouve
un défaut A ; la cause de l'incident original reste F / preuves insuffisantes.

## What Changes

- Réparer uniquement la promotion d'un ancien server_now en ancre actuelle.
- Conserver l'ancre en mémoire du contrôleur, acquise sur une lecture
  d'exécution confirmée ; la perdre à restore/pause/échec de lecture.
- Prélever la date au clic, jamais dans un ancien rendu React.
- Conserver la sémantique D11 existante : estimation explicite sans liaison
  monotone fiable ; bornes et validation serveur inchangées.
- Consigner provenance, reproduction et limites de qualification séparément.

## Capabilities

### Modified Capabilities
- `mobile/blueprint-first-session-runtime`: fraîcheur de l'ancre native.

## Impact

FirstUseV3Controller, adaptateurs PlanV3Host/PlanV3ExecutionScreen et tests.
Aucune migration, dépendance native, politique SCI, nouvelle primitive ou
géométrie UI. Aucune réécriture d'opération, de date, de snapshot ou de reçu.
Le mandat opérateur TIME-01 §5 autorise la correction minimale après preuve ;
GOV-MERGE-01 reste conditionné aux contrôles du HEAD final. Aucune autorisation
OTA/APK/déploiement n'est déduite. La recette corrigée dans l'APK installée
nécessite sa publication contrôlée séparée ; aucun PASS natif après correctif
n'est déduit des tests React.
