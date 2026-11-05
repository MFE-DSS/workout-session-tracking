# MOB-03 Native Account Delivery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** réaliser les consommateurs natifs du compte et la frontière propriétaire, puis une planche consolidée de premier usage fidèle aux capacités réellement servies.
**Architecture:** AuthSession possède les mutations et leur génération ; une garde de propriétaire choisit le journal avant restauration ou synchronisation. Le Blueprint ne persiste que les champs disposant d'un contrat approuvé ; les autres sont des UI_DATA_GAP explicites. Les nouvelles compositions restent candidates jusqu'à acceptation opérateur.
**Tech Stack:** Expo 58 / React Native / TypeScript, SecureStore existant, SQLite existant ; aucune dépendance ajoutée.
**Spec:** specs/mobile/account-lifecycle/spec.md et specs/mobile/onboarding-profile/spec.md dans ce change ; manifeste docs/strategy/AUREN_MANIFESTO_V1.md ; mandat opérateur PRODUCT DELIVERY du 5 novembre.

## Global Constraints

- Le nouveau mandat autorise la reprise de MOB-03 et la livraison selon ses gates, pas de déploiement.
- AurenMark et tokens/primitives canoniques ; aucune géométrie LOCKED changée ; croquis avant code de composition et rendu accepté avant commit UI.
- Aucun algorithme scientifique, champ LAB ONLY, photo ou nutrition ; suppression bloquée sur politique réelle.
- Poids daté existant uniquement, provenance et unité explicites, pas de date inventée pour l'héritage.
- Préserver l'ancien journal, vérifier toutes les identités de séance, ne jamais afficher/synchroniser sous un autre compte.
- check_scope avant vérifications ; pas de full sweep Python pour ce périmètre partagé.

## Review Focus

- Réponse auth tardive après logout ou connexion concurrente : n'adopte pas l'ancien compte.
- Écriture SecureStore lente : ne réinstalle pas un credential quitté.
- Réponse perdue d'une mutation : aucun retry automatique et aucun succès prétendu.
- Ancien journal mixte, malformé ou indisponible : conservation et aucun envoi.
- Refresh hors ligne après attribution prouvée : reprise permise pour ce propriétaire uniquement.

### Task 1: Consommateurs AuthSession

**Files:** src/auth/authSession.ts et src/auth/authSession.test.ts sous clients/mobile.
**Interfaces:** register({username,password,password_confirm,email?}, deviceLabel) et changePassword({current_password,new_password,new_password_confirm}) retournent AccountOutcome : confirmed / rejected(code) / unknown / cancelled. Login conserve AuthOutcome. Les mutations ne sont pas rejouées par authorized.
- [x] Tests rouges : double appui, refus, réseau/réponse perdue, nouvelle paire, logout/réponses tardives et stores lents.
- [x] Exécuter check_scope puis Jest ciblé ; constater les échecs attendus.
- [x] Implémenter mutations, génération et sérialisation des écritures ; garder refresh single-flight.
- [x] Vérifier Jest auth et TypeScript ; revue du sous-ensemble avant raccordement.

### Task 2: Frontière propriétaire du journal

**Files:** nouveaux storage/ownership.ts, ownershipStore.ts/.web.ts et tests ; journal.ts inspection SELECT-only, ConnectedApp.tsx et sync/connectedApp.test.ts.
**Interfaces:** métadonnées séparées (session d'appareil → user_id vérifié ; user_id → fichier journal), aucune copie des tokens dans SQLite. Une inconnue nécessite /auth/me puis vérification de toutes les séances du fichier historique avant attribution unique.
- [x] Tests rouges sur compte A/B, journal mixte/malformé, reprise hors ligne connue et absence de preuve.
- [x] Implémenter garde et adapter le boot avant toute lecture affichée ou moteur de sync ; conserver le journal non résolu.
- [x] Vérifier tests réels ConnectedApp et suites outbox/sync ; prouver zéro envoi étranger.

### Task 3: Planche et consommateurs visuels

**Files:** UI compte/Blueprint, banc de revue isolé, câblage ConnectedApp et tests consommateurs.
- [x] Présenter croquis consolidé puis réaliser les compositions acceptées avec logo/primitives.
- [ ] Produire entrée/inscription/résultat, quatre moments Blueprint et paramètres/reprise/propriétaire incertain, avec états applicables ; champs non supportés signalés sans fausse persistance.
- [ ] Relier login/register/password et premier handoff réel ; aucun bouton factice en produit.
- [ ] Rendu réel soumis avant commit UI ; distinguer preview web et preuve appareil iOS/Android.

### Task 4: Vérification et livraison autorisée

- [ ] Jest mobile complet + TypeScript ; protocol/scope/OpenSpec strict ; ciblés backend et broad selon diff final.
- [ ] Revue indépendante, corrections en tests rouges/verts ; acceptation visuelle et autres décisions nécessaires.
- [ ] Commit/push sur PR #353, checks du HEAD final et merge sous GO permanent seulement après readiness.
- [ ] Recettes/déploiement exacts, tâches restantes et préparation MOB-04 ; pas d'archive sans preuves.

## Brainstorming / Options / Risques / Choix retenu

Le mandat a fixé l'entrée unique et le premier parcours. Réutiliser les API compte et les adaptateurs natifs réduit le changement de domaine. Une attribution globale par username ou un journal ouvert avant preuve exposerait les faits ; choisir des partitions et un lien d'identité vérifié, sans purge. Les gaps Blueprint seront traités comme dépendances réelles plutôt que champs décoratifs. Aucun changement partagé du moteur scientifique.

### Task 5: Adaptateur des préférences déclarées existantes

Sous-ensemble indépendant des champs Blueprint non contractualisés. Aucune nouvelle règle scientifique.

**Interfaces :** GET/PUT `/me/training-preferences/declarations` ; version 1 ; `sessions_per_week: int|null`, `focus_priorities: string[]|null` ordonnées, `available_equipment: string[]|null` normalisées. PUT exige les trois champs, refuse les extras et ne touche pas `available_equipment_items`. GET retourne aussi les vocabulaires/libellés canoniques et les bornes structurelles existantes, sans recommandation. Réponse versionnée, no-store, propriétaire issu du Bearer uniquement.

- [x] Tests API rouges : lecture absente, null/[], ordre, validation stricte, ownership/cookie, requête partielle, non-effacement environnement concret et répétition sans doublon.
- [x] Implémenter un adaptateur étroit du service existant et classer les deux routes dans profile-training-preferences ; aucune écriture du service partagé.
- [x] Client `TrainingPreferencesClient.read/save` : résultat confirmé/refusé/inconnu/annulé ; lecture pour réconciliation explicite, PUT envoyé une fois, fence après changement de compte, double soumission refusée tant que la précédente est en cours.
- [x] Tests transport/auth réels et vérifications ciblées/broad ; contrat et gaps mis à jour avec preuves, sans prétendre le Blueprint branché.
