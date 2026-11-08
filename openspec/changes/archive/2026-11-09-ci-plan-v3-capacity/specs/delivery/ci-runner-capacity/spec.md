## ADDED Requirements

### Requirement: Capacity changes preserve the complete test set
La topologie SHALL utiliser cinq shards par fichiers, six seulement si les mesures réelles de cinq restent sous4096MiB de mémoire disponible minimale. L'algorithme round-robin, les deux workers par runner et l'exclusion unique test_v1_acceptance SHALL rester inchangés ; l'union SHALL couvrir exactement les fichiers canoniques et les intersections SHALL être vides.
#### Scenario: One matrix index is omitted
- WHEN la matrice ne correspond pas au compte canonique
- THEN le contrôle échoue, aucun résultat de suite complète n'est publié.

### Requirement: Complete coverage and protected checks remain authoritative
Le check pytest + QA scripts SHALL attendre chaque shard et le nombre d'artefacts SHALL être dérivé du compte canonique. Un artefact manquant SHALL échouer ; seule la couverture combinée complète SHALL être publiée. Les autres checks et l'attestation shadow SHALL rester inchangés.
#### Scenario: Last coverage artifact is missing
- WHEN le dernier artefact attendu manque malgré des jobs verts
- THEN l'agrégateur échoue avant de publier une couverture partielle.

### Requirement: Real measured capacity gates delivery
La livraison SHALL exiger CI PR et canonique réelles réussies, mêmes tests exécutables, échantillonsCI_RESOURCE non vides pour chaque shard et minMemAvailable>=4096MiB. Une annulation SHALL rester distincte d'un verdict passé. Six insuffisant SHALL produire un arrêt explicite sans extension implicite.
#### Scenario: Measurements are unavailable
- WHEN aucune série réelle n'est disponible pour un shard
- THEN aucune acceptance de capacité ni réutilisation de verdict n'est déduite d'un ensemble vide.
