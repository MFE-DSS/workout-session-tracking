# Amendement proposé — lectures répétées du snapshot SCI

28 novembre 2026, Europe/Paris. **PROPOSED / GO BUILD PENDING. Aucun code appliqué.**

## Déclencheur prouvé

L'image exacte de `1f81d5b82498f0a166e59b875e12db3dec56fceb` refuse deux fois la fixture structurelle `large100_v3` : 100 faits répartis sur 100 séances, construits en copie synthétique, sans prétendre à 100 START autorisés par le produit. Exit 1, réponse UNAVAILABLE, CPU 1,628–1,653 s. La sonde distincte attribue le refus au budget `statements=4096`, après 67 graphes/opérations. VM 58 000 ; entrée DB 283 754 octets ; catalogue parsé une fois. Ce n'est pas un nouveau diagnostic de dépassement CPU.

Sur ce même snapshot, `evaluation_for` relit la même évaluation et `runtime_authority` la même autorité pour chaque fait. Le témoin arrêté contient 68 recherches d'évaluation et 67 recherches d'autorité ; `has_table` recherche 69 fois la table des bindings. Les plafonds restent appliqués et la sortie n'est pas promue artificiellement.

## Brainstorming / Options / Risques / Choix retenu

Augmenter 4096 ou soustraire des lectures déjà réalisées affaiblirait le contrat : exclu. Un cache global entre captures ou propriétaires est également exclu. La solution proposée est la réutilisation bornée des seules lectures immuables dans **la même transaction SQLite read-only**, avec restitution indépendante des valeurs mutables. Son efficacité et ses limites restent à démontrer ; aucun PASS futur n'est présumé.

## Périmètre produit proposé, non autorisé

- `app/services/muscle_observed_load/sqlite_source.py` : réutilisation confinée à une instance `OwnedReadCapture` des présences de tables internes, évaluations par identité et autorité runtime ; caches détruits avec la capture, bornés par les identités déjà admises. Aucun changement de sélection, requête propriétaire, ordre, plafond ou comptabilisation des accès effectivement exécutés.
- `tests/test_muscle_observed_load_sqlite.py` : limites, copies indépendantes, propriétaires, captures et révisions concurrentes.
- `tests/test_muscle_observed_load_writer_readback.py` : parité du parcours canonique et témoin de volume explicitement synthétique, avec provenances exactes.
- Documents, autorisation et reçus du change correctif correspondant.

Ne pas modifier le reader HTTP, les writers, `provenance.py`, TIME-01, DTO, politiques SCI/P07, JSON sources, allocation V3 ou application mobile. Ne pas réduire les contrôles d'identité/digest faits pour chaque observation.

## RED → GREEN exigé

1. Préserver les refus exacts et recréer le témoin 100 V3 ; expliciter l'autorité réelle de sa fixture plutôt que présumer sa qualification scientifique.
2. Répétitions d'une identité dans une capture : même valeur, moins de lectures physiques, budget réel inchangé. Une mutation d'une valeur restituée ne modifie pas le résultat suivant.
3. Captures différentes et propriétaires A/B : aucune réutilisation croisée. L'ancienne capture garde son snapshot ; une nouvelle capture voit la révision suivante. Absence/contradiction reste UNKNOWN, PARTIAL ou UNAVAILABLE.
4. Sources/évaluations distinctes et ressources réellement dépassées : refus conservés, aucun raccourci d'autorité. Le nombre de faits seul ne garantit jamais une lecture complète de toute forme d'historique.
5. Digests normalisés, rôles, P07, réglages machine/PER_IMPLEMENT, read-only et reprise des slots inchangés. Rejouer 14 V3 canoniques, Legacy100, mixte100 et les scénarios adversariaux.

## Livraison et frontière opérationnelle

Après GO spécifique : check_scope, contrôles prescrits, tests ciblés/broad, revue indépendante et CI du HEAD exact ; livraison sous GOV-MERGE-01 sans GO MERGE routinier. Les preuves Linux doivent distinguer candidat de code et nouvelle image opérationnelle. Le présent amendement ne fournit aucun GO cloud, montage candidat supplémentaire, transfert, activation QA, données réelles, APK ou OTA. Les qualifications/opérations manquantes restent soumises à leur autorisation distincte.

Décision proposée : **autoriser ce seul correctif de lectures répétées et ses tests**, sans hausse de budgets. SCI-ACTIVATE-01 reste une étape ultérieure indépendante.
