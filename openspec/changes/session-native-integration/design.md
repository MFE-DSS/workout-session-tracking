# Design — session-native-integration (MOB-02)

## Context

Inventaire du 2026-11-03 (worktree MOB-01) : le chemin connecté monte déjà `ExecutionScreen`, `MissionScreen`,
`CompleteScreen` et `ResumeScreen` sur les vraies données. Les écarts mesurés sont hors du chemin heureux :

| Volet | Constat | Où |
|---|---|---|
| Saisie | `serverSets` vit en mémoire ; `onStatus` ne relit du journal que les séries **refusées** → après relance, une série acceptée retombe sur « enregistrée sur l'appareil » | `ConnectedApp.tsx` (`onStatus`, `serverStateOf`), `ExecutionScreen.tsx` |
| Démarrage | « Démarrer » sans état d'attente (1–2 s mesurées, PLAT-01 §5.3) | `ConnectedApp.tsx` `start` |
| Reprise | « 1 séries faites » ; reprise serveur `note={null}` | `ResumeScreen.tsx`, `ConnectedApp.tsx` |
| Lancement | `screen === 'BOOT'` rend `null` → écran vide pendant le rafraîchissement du jeton | `ConnectedApp.tsx` |
| Substitution | demande via l'outbox, plan relu à l'accusé ; refus et hors-ligne non décidés à l'écran | `ConnectedApp.tsx` `requestSubstitute` / `onAck` |
| Bilan | `history={null}`, `sessionsPerWeek={null}` → fréquence « (par défaut) », aucune comparaison | `ConnectedApp.tsx`, `CompleteScreen.tsx` |

L'API mobile (`app/routers/mobile_api.py`) n'expose ni historique ni préférence d'entraînement.

## Decisions (proposées)

- **Relecture des états serveur depuis le journal** : une fonction pure `serverStateFromOutbox(rows)` (acceptée /
  refusée / en attente par `set_id`), appliquée au démarrage et à chaque statut — testée en jest.
- **Envoi unique** : un drapeau « en cours » par action (démarrer, reprendre), porté par `ConnectedApp` ; les écrans
  verrouillés reçoivent un état `busy` déjà prévu par leurs boutons, ou rien si leur composition devrait changer
  (alors : planche avant / après à l'opérateur).
- **Écran de démarrage** : selon D-MOB02-2.
- **Bilan** : selon D-MOB02-1 ; en (a), deux routes `GET /api/mobile/v1/me/training-preferences` et
  `GET /api/mobile/v1/me/sessions?limit=…` en lecture seule, isolées par `user_id`, avec tests serveur ; le client
  n'affiche que ce qui arrive.

## Risks / Trade-offs

- [Un état `busy` change la composition d'un écran verrouillé] → si oui, planche avant / après et approbation (§5.1) ;
  sinon gate 77/77 inchangée.
- [Lecture serveur nouvelle] → lecture seule, sans migration, `user_id` imposé côté serveur ; tests d'isolement.
- [Écrire de vraies séances en production pendant la passe] → compte de test, séances abandonnées ensuite ; la
  fermeture du bilan est jouée une fois, sur le compte de test.

## Migration Plan

1. Décisions D-MOB02-1/2. 2. Fonctions pures + tests. 3. Câblage client. 4. Routes serveur (si a). 5. Passe émulateur
(états hors chemin heureux : relance, double appui, refus, hors ligne) + iPhone. 6. PR.

## Open Questions

- La réponse d'un refus de substitution par le serveur porte-t-elle une raison affichable ? À lire dans
  `mobile_api.py` avant d'écrire la phrase (aucune raison inventée).

## Décisions opérateur acceptées — 2026-11-03

D-MOB02-1=A et D-MOB02-2=AUREN-MARK-V1 seule, sans texte ni animation nouvelle, sont acceptées par l'artefact
de reprise. Les deux routes GET prévues en option (a) sont donc retenues, avec ownership serveur et données
absentes omises. Les paragraphes conditionnels précédents sont conservés comme historique de conception.

La restauration doit lire les commandes acquittées persistées via `restore().outbox` ; `outboxRows()` les exclut.
Les tests doivent traverser le consommateur réel `ConnectedApp` en plus des fonctions pures utiles.
Le build attend CODX-00 puis CI-01 ; aucun changement produit dans cette consignation.

## Suivi d’implémentation — inventaire des routes, 2026-11-04

La garde exhaustive MOB-00 exige de classer toute nouvelle route dans le même change.
Les deux lectures GET de MOB-02 sont ajoutées à `session-recap` dans l’inventaire vivant,
avec `KEEP_DOMAIN` conservé. Ce rattachement sert uniquement le bilan ; il ne migre
ni l’interface des préférences (MOB-03+) ni celle du journal (MOB-05). Aucune exclusion de garde.

## Arbitrage de finalisation — 2026-11-04

La directive opérateur impose de poursuivre ce change et la seule PR #352.
L’ordre applicable remplace le séquencement historique : implémentation mobile complète,
rendu réel et décision visuelle avant commit UI, contrôles du HEAD publié complet,
merge sous GO permanent si toutes les conditions sont réunies, autorisation de déploiement distincte,
déploiement du canonique vérifié, recettes Android puis iPhone connecté, closeout/archive après preuves.
Aucun déploiement ni résultat appareil n’est acquis par cette décision.

La directive proposait D-MOB02-3 : une ligne factuelle facultative avec période explicite,
source serveur seulement, sans transformer la fréquence déclarée en activité observée.
La réponse opérateur reçue ensuite est « Conserver zéro ajout sous le bloc ».
Le candidat conserve donc le bloc et n’ajoute aucune ligne dessous.
Le devenir de cette ligne et la représentation de la réception serveur dans le bilan
restent à arbitrer : la tâche 2.2 et son exigence de spec ne sont ni supprimées ni déclarées satisfaites.
Aucune nouvelle carte, baseline ou fonctionnalité MOB-03+ n’est introduite.

### Référence confirmée par l’opérateur

À la demande de validation de la planche, l’opérateur répond « réfère toi à ma dernière prompt injection ».
La directive MOB-02 FINALIZATION est donc appliquée : D-MOB02-3 accepte une ligne de contexte
optionnelle sous le bloc conservé. Le refus de l’ancien croquis de compteurs de synchronisation
ne sert pas à réintroduire ce croquis. Aucune validation finale du nouveau rendu n’est déduite.

Choix technique borné : nombre de séances terminées dans le GET complet de l’utilisateur,
du lundi UTC à la fin de la séance courante attestée par ce GET ; les deux bornes et UTC sont affichés.
La fréquence déclarée n’entre pas dans ce calcul. Ni séance locale ajoutée, ni comparaison, ni jugement.
Sans ligne courante attestée, complétude, dates valides et identifiants uniques, le contexte est omis.
La ligne de contexte historique ne prouve pas l’accusé de chaque série ; le rendu de réception
par série du bilan reste à résoudre pour 2.2, sans cocher cette tâche par simple transmission de props.

## LAST MILE — détail des séries du bilan

Inspection : aucune affordance de détail par exercice dans CompleteScreen ; les lignes sont de simples View.
Le bouton « … » existant est réutilisé pour une Sheet secondaire avec SheetRow, groupée par exercice
et limitée aux séries réalisées de cette séance. Le journal local préexistant reste accessible depuis cette feuille.
Le bilan fermé n’ajoute aucun compteur ni carte et sa composition ne change pas. La nouvelle géométrie
est soumise dans une seule revue finale, avant tout commit UI, selon le mandat opérateur.

L’unique sélecteur serverStateFromOutbox conserve les états du dernier envoi persisté par série :
acked → synced ; failed → refused ; pending/inflight → pending ; source absente/invérifiable → unknown.
L’exécution adapte pending/unknown à son contrat antérieur sans les transformer en confirmation.
Le bilan reçoit ce même modèle ; SessionSetDetails n’effectue aucune lecture et ne détient aucun cache.
Les lectures obsolètes sont ignorées ; une indisponibilité du dernier journal invalide l’état autoritatif.
La course identifiée en revue sur un ancien refus de substitution est corrigée par invalidation
des lectures avant la mutation et à la fin de sa persistance, et garde pendant les écritures concurrentes.
