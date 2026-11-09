# UX-CAL-02 — densité et hiérarchie du calibrage natif

9 novembre 2026. **PROPOSED / NO_GO_BUILD / G1_PENDING / NOT_ACTIVATED.**
Base canonique après fetch : `fe9f6e9beb585a271ae2c2726e338359057b9f58`.
Worktree `/private/tmp/auren-ux-cal-02`, branche `spec/ux-cal-02`.

## Why

PLAN-CAL-01/UX-CAL-01 sont livrés388/389 et CLOSED+CLEANED selon leurs reçus
finaux. Retour opérateur : « The calibration UI has too much text, oversized
CTAs and insufficient visual efficiency for a mobile device. » Le présentateur
partagé réutilise les grandes commandes du compte et juxtapose historique,
messages de procédure et actions secondaires. L'aide affiche le protocole
complet des six profils. Deux mineurs de décodage et d'aide sont à résoudre.

## What Changes

- Composition locale de l'entrée PLAN, du choix/reprise, du contexte et du
  calibrage partagé : une action dominante, titre court, réglage/unité uniques,
  contexte compact, historique et explications à la demande.
- Commandes compactes locales, cibles tactiles conservées, choix factuels groupés
  et progression de formulaire purement locale ; tous les faits obligatoires,
  UNKNOWN et permissions restent conservés.
- Liaison stricte du décodage client entre négociation, profils, intentions,
  réalisations et sémantiques des réglages. Ce contrôle ne réadmet pas la science.
- Aide disponible avant ouverture de rencontre ; projection déterministe des
  sections communes, de la seule réalisation concernée et des règles d'arrêt
  depuis les matériaux publiés existants, sans changer leur texte ni autorité.
- Preuves de consommateurs réels, d'équivalence des sept contextes, revue
  indépendante et board avant/après natif accepté avant commit UI.

## Non-goals

Aucun changement SCI, API/schéma partagé, inventaire négocié2, règle de
qualification/réessai/arrêt, moteur, snapshot/ack/commande de séance, migration,
nouvelle dépendance, asset, logo, palette ou design system. MISSION, compte,
préférences, proposition/ack temporel, exécution et journal ne sont pas
recomposés. Aucune baseline existante modifiée automatiquement. DATA, activation
réelle, appareils physiques et déploiement restent distincts.

## Review gates

Ce mandat exige scope et avant/après approuvés avant implementation. Les anciens
GO ne couvrent pas UX-CAL-02. [Design](design.md), [scope](BUILD_SCOPE.md),
[croquis G1 proposé](UX_CAL_BOARD.md), [tâches](tasks.md). Les primitives Frame C,
RecessedWindow, NumericReadout, AurenMark et tokens restent LOCKED dans leur
contrat. Aucun CalibrationRail/E7 ni incrément proposé. Après GO, livraison
autonome sous GOV-MERGE-01, avec pixels réels acceptés avant commit UI.
