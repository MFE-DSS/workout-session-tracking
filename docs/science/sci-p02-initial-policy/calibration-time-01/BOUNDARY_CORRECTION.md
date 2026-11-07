# Correction complémentaire — provenance temporelle imbriquée

7 novembre 2026. Correction dans le même périmètre de validation stricte autorisé, après #366 ; aucune nouvelle règle scientifique ou activation.

## Brainstorming / Options / Risques / Choix retenu

La correction CODE-1 avait normalisé l'épisode de calibration et la session temporelle. Une composante brute pouvait encore contenir un objet Provenance copié sans validation : un origin/acquisition hors enum contournait le modèle imbriqué. Option rejetée : supposer qu'un modèle Python déjà construit est forcément valide. Choix : appliquer le même normaliseur JSON récursif existant à chaque composante avant validation. Coût : sérialisation explicite, déjà prévue aux autres frontières ; aucune coercition d'unité ou d'admission.

Les deux classes invalides ont été reproduites en tests RED puis corrigées GREEN ; le producteur intégré v2 possédait déjà sa frontière JSON complète. Ce correctif complète la règle annoncée pour l'API de recherche autonome, sans faille d'authentification servie démontrée. Aucun schéma source, policy, fixture réelle, état READY, API/UI ou dépendance modifié.

La CI du nouveau HEAD et le contrôle canonique doivent être vérifiés avant sa clôture, distinctement des preuves de #366. Pas de full sweep local ISOLATED ; tests ciblés et broad scientifique, contrôles applicables et reproduction d'artefacts requis.

Preuves locales :433tests scientifiques ciblés/broad passants (14modules, deux avertissements de dépendances), Ruff/Bandit/budget264≤548/protocole/OpenSpec strict8/8/Gitleaks passants. Les12fixtures/deux schémas reproduisent les mêmes octets ; aucun changement d'interface valide ou de politique. Cette extension du correctif CODE-1 est vérifiée par les deux régressions ciblées, sans troisième audit général ou nouvelle admission.
