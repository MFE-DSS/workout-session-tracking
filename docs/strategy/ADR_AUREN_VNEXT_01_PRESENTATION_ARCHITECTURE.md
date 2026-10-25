# ADR `AUREN_VNEXT_01` — architecture de la couche de présentation mobile

> **Statut : `ACCEPTED — C2`** — arbitrage opérateur du **2026-10-23** (§7). Le
> statut a été appliqué sur instruction écrite de l'opérateur ; les verdicts et
> amendements du §7 sont les siens, pas des recommandations.
> *(Avant l'arbitrage : `PROPOSED` — révision r2.)*
>
> **Historique :**
> * **r1 (2026-10-23)** — critère : expérience immédiate en minimisant une seconde
>   plateforme → **option B** (coquille web TypeScript même origine).
> * **r2 (2026-10-23)** — **l'opérateur change le critère** : *maximiser la qualité
>   de l'expérience d'application mobile, même s'il faut quitter la pile de
>   présentation historique* → **option C2** (React Native + Expo, backend FastAPI).
>   D1 et D4 sont amendés ; D2, D3, D5–D8 conservés ; D9–D11 ajoutés ; prérequis de
>   sécurité **A0** ajouté.
>
> **Spec porteuse :** `docs/strategy/Sx_AUREN_MOBILE_EXPERIENCE_VNEXT_SPEC.md`
> (r2 : `§0bis` ce qui change, `§0ter` A0, `§6.4` matrice, `§7` architecture,
> `§8.7–8.9` local d'abord / transitions / auth, `§9.3–9.4` plan de lab, `§12`
> capacités natives).
>
> **Canonique de référence :** `7d34fa237e7744f8d070c76454fe2447f25dd3eb`.
>
> Premier ADR du dépôt (ni `docs/adr/` ni convention ADR). Une décision **UI**
> tranchée sur rendu continue d'aller dans `DESIGN_DECISIONS_*` ; un ADR consigne
> une décision **d'architecture**.

---

## 1. Contexte

AUREN a un moteur mûr (recommandation V3 + mémoire de conseil, environnement
TRAIN A, état de console, surcharge, récupération) et une interface entièrement
rendue serveur où **chaque geste en salle est un POST de formulaire suivi d'une
redirection et d'un document complet**.

Mesuré le 2026-10-23 (in-process, 8 séances d'historique) : **27,8 ms** de coût
serveur médian entre VALIDER et le rendu du REPOS — le temps perçu est réseau et
document ; **sans réseau, rien ne se passe**. Après la dernière série d'un
exercice, le produit attend un geste (`exercise_complete`, 6 fois sur 6).

Produit cible : un **copilote silencieux** ; la séance active est un **mode**, avec
**zéro décision de navigation** pendant une séance normale.

**Prémisse r2, posée par l'opérateur :** le domaine et le backend sont un actif ;
**la pile de présentation existante n'est pas une contrainte**.

Contraintes versionnées que C2 lève (et qu'il faut lever explicitement) :
`Sx_UIV3_00A §9` (Jinja SSR KEEP, **React Native REJECT**, Capacitor FUTURE GATE V4) ·
`AUREN_VISUAL_BACKBONE §5bis` (SSR base fonctionnelle, « zéro framework ») ·
`Sx_UIV3_02 §4` (libellés figés) · doctrine `UI-CP8R` (heure serveur seule).

## 2. Moteurs de la décision — pondération r2

| Moteur | Poids r1 | Poids r2 |
|---|---|---|
| plafond UX, capacités natives (haptique, écran verrouillé, notification locale) | moyen | **dominant (×3)** |
| fiabilité hors-ligne, cycle de vie de l'app, risque de re-plateforme | moyen | **fort (×2)** |
| conservation de pile, coût d'une seconde plateforme | **dominant** | faible (×1) |
| aucune logique de domaine dans le client | absolu | **absolu** |
| legacy en service et réversible pendant la migration | absolu | **absolu** |

## 3. Options considérées

| | A — reset Jinja | B — web TS | C1 — natif complet | **C2 — RN + Expo** |
|---|---|---|---|---|
| Définition | SSR + JS progressif | page TS même origine, Capacitor plus tard | Swift/SwiftUI + Kotlin/Compose, ou RN nu sans Expo | une base TS iOS + Android, modules Expo, Swift/Kotlin ciblés |
| VALIDER → REPOS sans réseau | non | oui | oui | **oui** |
| Série hors-ligne, survit au redémarrage | non | fragile (stockage web évinçable) | oui | **oui (SQLite)** |
| Haptique iOS | non | non | oui | **oui** |
| Notification locale de fin de repos | non | non sur iOS | oui | **oui** |
| Écran verrouillé / Live Activity | non | non | oui | **oui (module Swift ciblé)** |
| Bases de code UI | 1 (existante) | 1 + 1 | **2** | **1 + 1** |
| Auth existante réutilisée | oui | oui | non | non (D9) |
| Total pondéré r2 (/ 135) | 57 | 70 | 117 | **116,5** |

Notation critère par critère, et ses justifications : spec `§6.4`. Les notes sont
des jugements argumentés, pas des mesures.

## 4. Décision proposée — r2

**OPTION C2 — client mobile React Native + Expo + TypeScript, backend de domaine FastAPI.**

- `clients/mobile/` : **une** base TypeScript pour iOS et Android ; vues natives,
  feuilles natives, animations sur le fil UI.
- **FastAPI reste l'autorité** du domaine et de l'historique durable ; base et
  services canoniques inchangés.
- **Contrats de présentation explicites**, repris de r1 : `MISSION_READ_MODEL`,
  `EXECUTION_READ_MODEL`, commandes par fait (`START_SESSION`, `SET_COMPLETION`,
  `SET_CLEAR`, `REST_SKIP`, `SUBSTITUTE`) — plus, en r2, un **plan de séance avec
  table de transitions calculée par le serveur** (spec `§8.8`), pour exécuter une
  séance démarrée **hors-ligne sans que le client décide quoi que ce soit**.
- **Local d'abord pour l'exécution** : journal + outbox **Expo SQLite**, une
  transaction par geste ; la série est **sûre** dès le commit local, **synchronisée**
  à l'ACK, **refusée** de façon visible le cas échéant ; zéro perte silencieuse
  (spec `§8.7`).
- **Authentification mobile** : jeton d'accès court + rafraîchissement rotatif
  révocable, coffre de l'appareil ; identité `User` et propriété inchangées (D9) —
  **après A0**.
- Modules **Swift / Kotlin ciblés** seulement pour Live Activity / Dynamic Island,
  notification de séance continue Android, App Intents (extensions E1/E2).
- Le legacy Jinja reste en service, lit la même base, sert de **repli** et de
  référence de parité.
- Le premier travail après acceptation est le **labo de design natif N0** (cinq
  écrans, fixtures réelles, appareil réel), **avant** toute tranche backend.

**Pourquoi pas C1** : il égale C2 sur le total (117 contre 116,5) mais au prix de
deux bases de code et de deux pipelines pour un opérateur seul ; C2 garde C1 comme
**issue locale** (un module natif là où il paie), donc sans re-plateforme future.
**Pourquoi plus B** : son atout (pas de seconde plateforme) est ce que le critère
r2 a cessé de valoriser ; ses manques iOS sont des limites de plateforme.

## 5. Conséquences

**Positives**
- plafond UX natif, haptique, notification locale, maintien d'écran dès N0 ;
- **chemin nominal d'une séance déjà matérialisée exécutable hors-ligne**, sans
  logique de domaine côté client (table de transitions serveur) ; les mutations
  non nominales passent en `REQUIRES_SYNC` visible ;
- surfaces d'écran verrouillé (Live Activity, notification continue Android) et
  raccourcis comme **extensions** du même projet, pas comme re-plateforme ;
- frontière domaine / présentation écrite une fois, servant l'app et le legacy ;
- dette de routeur remboursée là où elle bloque (écriture, START, position) ;
  double START et nom de substitution non validé fermés dans l'adaptateur ;
- l'audit a fait sortir **A0**, une faille qui existe **aujourd'hui** en production.

**Négatives / coûts**
- une seconde plateforme (TS / React Native / outillage Expo) et sa CI native ;
- comptes et secrets externes (Apple, Google, service de build) — détenus par
  l'opérateur (D10) ;
- un adaptateur d'authentification par jeton et **une** migration additive (D9) ;
- revue des stores pour les binaires ; fragmentation des versions à gérer
  (contrats `/api/vnext/v1`, serveur N et N-1) ;
- les gardes HTML ne voient rien de l'app : gardes de **capacité** à écrire ;
- l'invariant « écriture récupérable si le JS échoue » est **reformulé** (D2) ;
- la doctrine `UI-CP8R` (heure serveur seule) est **amendée** pour l'API mobile (D11).

**Neutres**
- moteur inchangé ; durée de repos = repli de 90 s étiqueté (D7) ; aucune
  migration pour les contrats de présentation.

## 6. Ce que cet ADR ne décide pas

La forme visuelle (tranchée sur **rendu d'appareil**, `CLAUDE.md §5.1`) ; les
versions exactes de l'outillage (épinglées à l'ouverture de N0) ; l'ordre de bascule
au-delà de MISSION / EXECUTION ; une prescription de repos par exercice ; la
correction elle-même de A0 (tranche de sécurité séparée).

## 7. Décisions de l'opérateur — 2026-10-23

Chaque ligne acceptée autorise **l'amendement correspondant** listé dans la spec
`§16`, dans la tranche qui le rend nécessaire. Détail des amendements : spec `§0quater`.

| # | Décision soumise | Verdict opérateur (2026-10-23) |
|---|---|---|
| **A0** | tranche de sécurité sur le contrat de jeton de session | **ACCEPTED / P0** — piste indépendante (`Sx_SEC_A0_SESSION_TOKEN_INTEGRITY`) ; aucun jeton de rafraîchissement mobile avant sa clôture ; N0 avance sans auth mobile |
| D1 | OPTION C2 — React Native + Expo mobile client, FastAPI domain backend | **ACCEPTED** — C2 est l'architecture cible ; la pile Jinja n'est pas une contrainte du vNext |
| D2 | client mobile non SSR ; invariant reformulé | **ACCEPTED** — **aucune écriture d'entraînement ne peut être perdue en silence** ; le web legacy est le repli |
| D3 | écriture JSON par série | **ACCEPTED** — une commande par fait ; jamais la route d'enregistrement d'exercice entier |
| D4 | `clients/mobile/` = Expo / React Native / TypeScript + CI native | **ACCEPTED** |
| D5 | repos entre exercices, enchaînement automatique | **ACCEPTED** — aucun geste de navigation sur le chemin nominal |
| D6 | saisie pré-remplie, VALIDER confirme l'affiché | **ACCEPTED POUR LE LABO / PAS FIGÉ COMME PRODUIT** — le dogfood mesure la confirmation silencieuse avant d'en faire un invariant |
| D7 | 90 s par défaut, aucune prescription | **ACCEPTED** — pas de vocabulaire d'ingénierie à l'écran (« 90 s par défaut », pas « repli ») |
| D8 | `LEGACY_VISUAL_REFERENCE` par surface ; cadres → `VNEXT_INTERACTION_REFERENCE_FRAME` | **ACCEPTED** — les cadres gouvernent la hiérarchie et l'état, pas la forme native |
| D9 | auth mobile accès court + rafraîchissement rotatif révocable | **ACCEPTED APRÈS A0** — ne pas implémenter avant la clôture de A0 |
| D10 | comptes Apple / Google / service de build | **AMENDÉ** — pas prérequis du premier labo local ; requis avant distribution signée, TestFlight / test interne Play, stores, et capacités natives qui les exigent |
| D11 | `performed_at` client borné | **ACCEPTED AVEC AMENDEMENT D'INTÉGRITÉ** — jamais l'horloge murale brute seule : ancre serveur + temps monotone + validation bornée + invariants d'ordre ; aucune décision de sécurité sur une heure client |

**Amendements de portes portés par le même arbitrage :** G-NOTIF (± 2 s) retiré ;
minuteur in-app ≤ 1 s = contrat dur ; notification OS = distribution mesurée et
publiée, jamais bloquante ; pas de privilège d'alarme exacte. « Séance entière
hors-ligne » → **chemin nominal d'une séance déjà matérialisée** hors-ligne,
`REQUIRES_SYNC` pour le reste.

**Tranches ouvertes par l'arbitrage :** `Sb_VNEXT_NATIVE_N0_EXPERIENCE_LAB`
(autorisée) ; `Sx_SEC_A0_SESSION_TOKEN_INTEGRITY` (spec de piste séparée).

*(Avant l'arbitrage, ce tableau portait la colonne « Recommandé » et des cases à
cocher ; il est conservé dans l'historique git de ce fichier.)*

## 8. Décisions produit portées par le vNext — 2026-10-23, après le premier essai physique

L'architecture C2 ne change pas. Ces deux décisions fixent **ce que** le client mobile
doit rendre, et renversent des décisions produit antérieures. Détail, état du domaine et
points ouverts : spec `§0quinquies`.

| # | Décision | Verdict opérateur |
|---|---|---|
| **D12** | score de séance et gamification | **ACCEPTED** — séries scorées ; **un** score de séance qui explique ce qui a été fait et substitué ; mécanique de récompense assumée, agent expressif. Superséde pour le vNext `AUREN_UI_BLUEPRINT` D7, `Sx_27`, `Sx_UI_05`, le « aucun score » de `session_done.html`. Le score de préparation reste interdit. **Amendé le même jour (moteur V2, ruling 11)** : plus de score unique /100 — performance par exercice, assiduité au programme et trace de décision restent séparées |
| **D13** | parcours de premier lancement | **ACCEPTED** — objectif + famille (haut / bas / corps entier, jamais un nom de gabarit) → séance proposée depuis le catalogue, adaptée au matériel → **profil d'entrée** (taille, poids, âge, sexe, activité, mesures connues ; chaque champ a un consommateur et dit pourquoi il est demandé ; tout est passable) → tutoriel court → séance ; puis le récit de la suite : le moteur prépare les séances suivantes, en rotation |

**Conséquences pour l'architecture :** D12 et D13 exigent des **tranches métier** côté
FastAPI (score calculé sur l'exercice réellement fait ; proposition d'une première séance
sans historique ; charges de départ ; colonnes de profil nouvelles par **migration
additive**). Le client mobile les **rend**, il ne les calcule pas : D3 et la règle « le
domaine reste au serveur » tiennent.
