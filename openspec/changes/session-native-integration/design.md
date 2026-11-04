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
