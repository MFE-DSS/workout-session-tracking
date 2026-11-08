# Traçabilité du closeout contrôlé

8 novembre2026. PR379 HEAD7f4bd3f7cd81461e2f74b5debb70e813e910e599,
merge31b89f98985044a9ee40d75610d387976ff26d7c. Maintenance préparée en draft
pendant CI canonique42526541847 ; aucune réussite de ce run anticipée.
L'archive proposée ne devient canonique qu'après les gates de merge de la
maintenance, dont réussite du code canonique et de son HEAD de closeout.

## Autorité de périmètre

BUILD_SCOPE, approuvé par «Autoriser le build PLAN contrôlé», distingue
explicitement COMPLETE contrôlé, DATA réelle, appareils physiques et déploiement.
Ce closeout applique cette frontière reçue, pas une nouvelle scission qui retire
des critères. G1 puis pixels acceptés séparément. Aucun GO d'activation réel.

| Ensemble | État acquis / conservé |
|---|---|
| Task1 | Pins des deux autorités, lease/18routes et SDK historiques préservés ; DATA réelle différée |
| Task2 | Sept tables, révision/provenance, sources/snapshot propriétaire et politique de test seulement |
| Task3 | Vrais loaders/producteurs/validateurs hors checkout, décisions et ack exact ; aucun nouveau SCI |
| Task4 | Commande atomique/unique, vraie concurrence SQLite, réponse perdue et cancel/handoff |
| Task5 | Séance canonique7×2, faits typés/CAS, retrait/journal/sortie et dispatch legacy |
| Task6 | Consommateur natif, vraie SQLite/outbox, reprise/historique/correction et preuve A→J ; pixels acceptés |
| Task7 | Contrôles locaux complets avec deux sentinelles expliquées, PR CI9/9 ; code canonique et closeout en suivi avant intégration de maintenance |

Les anciennes tâches de préparation et leur formulation sont relisibles au
commit83b547164a06fd9b18ebc83a567ff266f943d743 ; l'état des tâches exécutées
reste dans tasks.md. Aucun ancien scénario T01–T37 supprimé ou renuméroté.

## Critères externes toujours OPEN, jamais convertis en PASS

- DATA réelle : Task1/DATA, T05/T31 et [DATA01–07](../../../../docs/proposals/account-data-activation.md), D-POL01–05, finalités et copies/export/retrait/effacement/restauration.
- T25 / [RELEASE01–06](../../../../docs/proposals/account-native-release-acceptance.md) : Android+iPhone physiques, compatibilité déployée, rollback effectif et autorisations distinctes.
- Activation/déploiement : aucun environnement ou donnée réelle ouvert par ce build APP_ENV=test ; gates DATA/runtime/RELEASE maintenues.
- Six premières rencontres restantes : aucune extension SCI du pilote leg-extension déduite d'observations synthétiques de test.
- [PLAN01–07 globaux](../../../../docs/proposals/blueprint-first-session-runtime.md) et MOB03 complet : états distincts conservés, réalisation contrôlée seule ne les clôt pas.

Le code PostgreSQL ne vaut pas preuve de courses PostgreSQL. La restauration et
le CSV legacy refusent explicitement ce profil ; première séance scientifique
unique, replanification/substitutions futures hors scope. Ces limites sont dans
le runbook et la passation, sans nouveau chantier concurrent.
