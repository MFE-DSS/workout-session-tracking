# Proposal — session-native-integration (MOB-02)

## Why

La roadmap de l'opérateur (2026-10-31) : « MOB-02 Session — passer les écrans de séance déjà validés des bancs vers la
vraie app », en cinq volets : reprise, saisie des séries, repos, substitution, fin de séance. L'inventaire du 2026-11-03
montre que les trois écrans verrouillés (`EXECUTION-SCREEN-V1`, `MISSION-SCREEN-V1`, `COMPLETE-SCREEN-V1`) tournent
**déjà** sur les vraies données dans le chemin heureux. Ce qui manque est **hors du chemin heureux**, et la passe PLAT-01
l'a mesuré : après une relance, une série acceptée par le serveur s'affiche « enregistrée sur l'appareil » ; « Démarrer »
ne montre aucune attente et peut être touché deux fois ; « 1 séries faites » ; l'écran de démarrage est vide pendant la
restauration du jeton ; le bilan affiche une fréquence « (par défaut) » et aucune comparaison, faute de lecture serveur ;
le refus d'une substitution par le serveur n'a pas d'état décidé. Un utilisateur qui relance l'app au milieu d'une séance
voit donc des faits faux sur ce qu'AUREN a reçu. Cette tranche rend la séance native vraie dans tous ses états.

## What Changes

- **Saisie — la vérité de synchronisation survit à la relance.** L'état serveur de chaque série (acceptée / refusée) est
  relu du journal local (outbox), pas seulement gardé en mémoire : une série acceptée reste « reçue par AUREN » après
  une relance, dans l'exécution comme dans le bilan.
- **Démarrer / Reprendre — un état d'attente, un seul envoi.** Pendant la requête, le bouton montre l'attente et ne
  relance pas une seconde séance.
- **Reprise — le texte juste.** Accord du pluriel (« 1 série faite ») ; la reprise serveur dit, comme la reprise locale,
  ce qui se passe hors ligne.
- **Démarrage — jamais d'écran vide.** Pendant la restauration du jeton, un écran de démarrage (la marque) au lieu du vide.
- **Substitution — hors chemin heureux.** Un refus du serveur et une demande restée hors ligne ont chacun un état
  explicite et réversible ; la série suivante n'est jamais bloquée sans explication.
- **Fin de séance — de vraies valeurs, ou rien.** La fréquence hebdomadaire vient de la préférence déclarée de
  l'utilisateur ; la comparaison « à toi-même » vient de l'historique serveur. Chaque valeur absente reste absente,
  jamais une valeur par défaut présentée comme la sienne. *(voir D-MOB02-1)*
- **Repos** : déjà porté par l'écran verrouillé ; vérifié sur appareil (anneau, ±15 s, notification), aucun changement
  prévu sauf défaut mesuré.

## Capabilities

### New Capabilities
- `mobile/session-integration` : ce que la séance native garantit hors du chemin heureux — vérité de synchronisation
  par série, envoi unique, reprise, démarrage, substitution refusée ou en attente, valeurs du bilan.

### Modified Capabilities
- (aucune spec vivante de séance n'existe ; `mobile/navigation-shell` n'est pas modifiée)

## Non-goals (hors périmètre)

- **L'instrument de charge** (`SESSION-CARD-R1`, `INSTRUMENT-SURFACE-B1/B2`, `INSTRUMENT-CONTROLS-B3`, ligne de
  calibration) reste sur le banc : il attend les bornes de zone du moteur (E7). Aucune borne n'est inventée.
- Aucune recomposition d'un écran verrouillé ; aucune baseline modifiée sans approbation.
- Pas de MISSION (MOB-04 : la raison « déjà bien servi » sur un compte neuf), pas d'onboarding (MOB-03), pas de
  journal / progrès (MOB-05).
- Pas de nouvelle migration de base de données.

## Décisions de l'opérateur demandées

- **D-MOB02-1 — le bilan.** (a) ajouter deux lectures serveur **en lecture seule, sans migration** (fréquence déclarée,
  historique des séances de l'utilisateur) et les afficher ; ou (b) les reporter à MOB-05 et retirer du bilan la
  fréquence « (par défaut) » d'ici là. *Recommandation : (a)* — les données existent déjà côté serveur
  (`training_preferences`, historique des séances) ; seul le chemin mobile manque.
- **D-MOB02-2 — l'écran de démarrage.** La marque seule sur le fond, ou rien de plus que l'écran de lancement natif
  prolongé. *Recommandation : la marque seule (dessin primaire), sans texte.*

## Dépendances bloquantes

- MOB-01 (`native-navigation-shell`) mergée — la séance est la pile plein écran de cette coque.
- Pour (a) : relecture du contrat de données mobile (aucun champ inventé) ; déploiement du canonique en production
  (workflow existant) avant la passe appareil.

## Impact

- `clients/mobile` : `ConnectedApp.tsx` (relecture des états serveur, envoi unique, démarrage), `ResumeScreen.tsx`
  (pluriel, texte hors ligne), états de substitution (sans recomposition de l'écran verrouillé), `CompleteScreen`
  alimenté ; tests jest des fonctions pures ajoutées.
- `app/routers/mobile_api.py` (si D-MOB02-1 = a) : deux routes GET en lecture seule + leurs tests ; aucune écriture.
- Passe appareil : émulateur Android (production) et iPhone ; captures des états hors chemin heureux.

## Décisions opérateur acceptées — 2026-11-03

L'artefact « AUREN — CODEX REPRISE / MOB-02 » transmis dans la session Codex accepte :

- **D-MOB02-1 = A** : deux lectures GET mobiles pour la fréquence déclarée et l'historique requis par le bilan,
  depuis les services/données canoniques, isolées par `user_id` authentifié ; aucune migration, aucune vérité
  dupliquée ; une source absente est omise, sans valeur par défaut présentée comme déclarée ou mesurée.
- **D-MOB02-2** : AUREN-MARK-V1 seule pendant la restauration de l'authentification ; aucun texte, nouveau logo,
  redesign décoratif ni animation supplémentaire.

Ces décisions lèvent les alternatives du bloc historique ci-dessus. La roadmap est désormais CODX-00 → CI-01
→ MOB-02, avec STORE-00 et les assets en parallèle. Aucun code produit n'est ouvert par la remise à niveau Git.
Preuves de build requises : restaurer les succès depuis `restore().outbox` (pas seulement `outboxRows()`),
consommation par le vrai chemin `ConnectedApp`, états dégradés Android puis passe iPhone connectée avec l'opérateur.
