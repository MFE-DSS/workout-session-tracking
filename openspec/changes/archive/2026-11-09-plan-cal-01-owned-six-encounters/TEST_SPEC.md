# PCAL — tests consommateurs à implémenter après GO

Aucun test Python/TS nouveau écrit ou exécuté dans la préparation. Les scénarios
ci-dessous gouvernent le futur TDD, pas des résultats PASS anticipés.

| ID | Entrée réelle / consommateur | Attendu |
|---|---|---|
| T01 | Builder v2 dans root vide, app copiée hors checkout, worker -I | Vrais load/evaluate/validate pour sept profils ; imports attestés sous root, aucune factory/donnée synthétique sélectionnée |
| T02 | Bundle v1/pilote historique, inventaire2 absent/inconnu, six sans négociation | V1 préservé, nouveau client6refus406 ; pas downgrade ou labels APPROVED |
| T03 | Source/policy/digest/module/parent altéré ou génération retirée | Pas nouvelle consigne ; lectures/faits préservés ou pending explicite si forme fiable indisponible |
| T04 | Chaque six : zéro épisode puis faits réels de préparation/choix/contexte/fam exacte/essai/acceptation via HTTP authentifié | QUALIFIED provisoire depuis vrai SCI et ledger propriétaire, aucun essai de travail créé |
| T05 | FAM sans setting/autre setting/booléen seul, date tardive, nouveau setup/choix disponible différent | Pas INITIATE_TRIAL/ACCEPT/QUALIFIED ; snapshot ne sert pas ancienne qualification C3 brute |
| T06 | RDL préparation sans haltères, champ vide, kg par haltère ; cinq machines kg affichés | Pas0kg implicite, BODYWEIGHT, total calculé ou conversion ; mêmes unités au journal |
| T07 | Unknown/unavailable/concern inconnue, qualité/gêne/motif inconnus, échec, retrait | Guidage fermé ; pause distincte du retrait, pas nouvel ID ou sélection contournant ledger complet |
| T08 | Essai incomplet TIME_LIMIT/USER_STOPPED sans préoccupation puis retry humain | Observation non qualifiée, aucun motif causal inventé ; retry jamais automatique |
| T09 | Deux ouvertures/replay et sélection concurrente, contextes A/B, sélection inconnue ou étrangère | Même clé/corps→même reçu ; mismatch/CAS409, étranger404 indistinguable, aucune sélection implicite «latest» |
| T10 | Nouvelle sélection, contexte UNKNOWN ou lieu contradictoire | Ancien positif invalide ; faits historiques visibles ; V3 pas fabriqué depuis lieu de dernière ligne |
| T11 | Réponse source perdue avant/après commit, GET absent concurrent, app relancée SQLite fermée/réouverte | Même clé/corps et relecture serveur ; aucune observation/acceptation dupliquée ou nouvelle clé cachant UNKNOWN |
| T12 | Switch compte A→B, logout, changement de rencontre pendant lecture/verification/ack/start | Réponses tardives neutralisées ; état local/drafts/pending partitionnés, aucune valeur ou permission de A/B mélangée |
| T13 | Sept acquisitions guidées HTTP réelles dans scénario synthétique qualifié, snapshot propriétaire | Vrai V3/validateur ; temps UNKNOWN/BUDGET_UNCERTAIN, REQUIRES_TIME_ACK puis ack exact/ELIGIBLE |
| T14 | Un épisode absent/non qualifié, ack changé, version packaging/inventaire changée même sans incrément de génération | Refus précis, aucune requalification/snapshot réécrit, vieux pins V3 seuls insuffisants |
| T15 | Start perdu après commit, deux clés concurrentes, récupération handoff, exécution/sets V3 | Même owned session réelle, 7exercices/14séries de travail par première séance selon vrai plan, sans warmup inventé |
| T16 | Journal RDL PER_IMPLEMENT et machine, correction/CAS/retour/reprise/fin | Faits typés persistés, pas totalKG ni overload/score legacy inventés ; lecture après rollback conservée |
| T17 | UI chargement/absence/refus/inconnu/concern/reprise, clavier/grand texte/retour | Action unique utile, pas réglage par défaut/acceptation auto ; refs/pins/hashes restent techniques hors flux produit |
| T18 | Anciens SCI exports/pins, clients V1, v1bundle et anciennes séances | Byte/replay sans modification, pas de migration ou régression des domaines déjà livrés |

Revue code fraîche et frontière SCI distincte sur l'intégration ; pas nouvelle
admission biologique ou enquête anatomique. Broad futur : calibration/profile/
packaging/authority/snapshots/evaluations/commands/execution/journal + leurs HTTP
et anciens consommateurs PLAN ; contrats/replays SCI concernés ; Jest/TS et
stockage/controller réel. CI complète du HEAD est le filet global. Sur rendu
natif, prouver lecture/reprise/journal avec vrai serveur jetable et préciser les
limites de simulateur ; jamais preuve physique ou production depuis une capture.
