# Scopes et autorisations — aucune propagation implicite

| Voie | Autorité actuelle | Travail autorisé / gate restant |
|---|---|---|
| PILOT-PARITY-00 | Mandat reçu : créer matrice/audit/priorités et préparer les nouvelles tranches | Documentation préparée ; revue et publication distinctes du GO code ; aucune parité appareil depuis cette préparation |
| MOB04 | docs/proposals/mob04-mission.md explicite sans GO ; brouillon ARCH non fusionné idem | Préparation actuelle même change, source/action possédée ; GO BUILD/G1 manquent, variante d'entrée Aujourd'hui à trancher |
| MOB05 | Futur jalon dans roadmap/MOB00 seulement, aucun active change canonique | Nouveau delta mob05-owned-training-history préparé séparément : historique brut propriétaire, dispatch legacy/SCI et faits par exercice ; GO/G1 requis |
| BODY01 | Domaine BodyMeasurement existant + GET poids headless, pas scope natif CRUD approuvé | Delta body-01-owned-measurements en préparation séparée ; BLOCKED_SPEC_RECONCILIATION sur correction/suppression face aux contrats historiques ; décision explicite requise, pas de GO implicite |
| NUT01 | Vision manifeste, aucun runtime nutrition actuel | Delta nut-01-manual-daily-ledger en préparation séparée ; saisie totale journalière/objectifs déclarés, pas moteur ; GO/migration/G1 à obtenir |
| MOB06/07 | Bibliothèque et builder/versionnement web existent | Sélection native P0 encore manquante ; préparer leurs tranches quand ouvertes, pas copier Jinja ou déclarer terminé via lien web. **MOB06 réservée le 10 novembre 2026, gouvernée par Maltin** : aucune préparation hors Maltin ([réservation](../../strategy/AUREN_MOBILE_CRITICAL_PATH_2026_11_03.md#réservation-maltin--mob-06-bibliothèque-de-séances)) |
| DATA/RELEASE | Dossiers préparés390/392 ; politique et artefact/physique ouverts | Pas d'activation de données réelles, Store/OTA ou déploiement depuis un merge de code |
| Assets | Brief391, source mannequin non productible automatiquement | Aucun nouveau master/Smith/bibliothèque produit par ce mandat |

Base commune2b831411. Worktrees propres séparés pour les préparations ; aucun ancien worktree ARCH/opérateur remplacé. Le brouillon ARCH reste conservé et son statut proposé cité, pas automatiquement repris comme contrat approuvé. Une seule ligne d'apply pour MOB04 devra être retenue avant PR concurrente.

Les leases partagés (ConnectedApp, ShellProvider, mobile_api, inventaireMOB00, SPEC_REGISTRY) s'appliquent en ordre : merge/relecture de base avant le slice suivant. Pas de modification simultanée ou de mélange de changes dans une PR. GOV-MERGE-01 couvre livraison des scopes approuvés et leurs corrections/closeout ; jamais nouvelle autorisation de build.

P0/P1/P2 ici désignent la continuité du pilote proposée à partir du mandat, pas un remplacement silencieux de l'ordre scientifique du manifeste. La saisie nutritionnelle P0 n'ouvre aucune recommandation nutritionnelle ; MISSION, séance et historique demeurent le premier jalon d'apply proposé.

Prochain résultat proposé : faire approuver le scope/G1 MOB04, puis MOB05 ; poursuivre en parallèle les dossiers BODY/NUT et preuve de build compatible. Toute autorisation reçue sera consignée mot pour mot avant code. Les propriétés d'acquisition/qualification/temps/commande SCI déjà admises restent intactes.
