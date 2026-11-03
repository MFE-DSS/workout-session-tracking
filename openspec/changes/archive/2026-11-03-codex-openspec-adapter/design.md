# Design — CODX-00

## Context

Voir la motivation et le périmètre dans `proposal.md`. Base observée : `fcfbcd7`.
Les skills Claude et la config AUREN existent ; `.agents/skills` n'existait pas.
Le checkout principal `61ca08c` est préservé. Le worktree MOB-02 était propre avant rebase.

## Goals / Non-Goals

**Goals:** adaptateur officiel, provenance vérifiable, bonne base et reprise courte par SHA.
**Non-Goals:** aucune nouvelle autorité documentaire, aucune modification d'écran, aucun effet iOS/Android.

## Decisions

- **Adaptateur officiel plutôt que copie manuelle** : `openspec init --tools codex --no-animation`, CLI 1.14.3.
  Les six skills générées restent intactes. Le chargement dans le catalogue Codex d'une prochaine session doit
  être distingué de leur présence sur disque ; lire leur SKILL.md permet de les utiliser dans cette session.
- **Autorités** : suivre le nouveau guide canonique `AGENT_ONBOARDING_SPEC_DRIVEN.md`. L'ancien AGENTS.md non
  versionné n'est ni commité ni recopié. Une skill de workflow ne peut pas modifier un contrat visuel verrouillé.
- **Base MOB-02** : sauvegarde `backup/mob-02-proposal-091110b`, puis rebase de la proposition sur la canonique.
  Alternative écartée : réécrire la proposition à la main. Le diff du dossier de proposition avant/après rebase
  doit être vide ; la consignation ultérieure des décisions opérateur est identifiée séparément.
- **Branches séparées** : CODX-00 et CI-01 ont chacun leur worktree ; aucun fichier MOB-02 dans CODX-00.
- **Roadmap datée** : document de pilotage opérateur, pas une réécriture des specs historiques. STORE-00 porte
  les décisions administratives en parallèle, avec dépendances vers les tranches d'implémentation.

## Risks / Trade-offs

- [Générateur réécrivant un contrat] → relire `git status` et comparer les fichiers protégés à HEAD.
- [Hooks Claude pris pour des hooks Codex] → RTK utilisé explicitement quand il conserve la preuve nécessaire.
- [Dépendances Python locales différentes] → signaler 3.14.7/FastAPI 0.135.3 contre 3.11/lock 0.141.1 ; aucun
  verdict backend produit à partir de cet environnement avant préparation dédiée.
- [Branche MOB-02 publiée puis rebasée] → aucun push forcé ; préserver l'ancienne référence et proposer une
  nouvelle branche de livraison lors de l'intégration de CODX-00 et CI-01, ou demander une décision explicite.

## Migration Plan

Configuration locale demandée par l'opérateur, revue du diff, contrôles documentaires/outillage puis revue
de livraison. Pas de PR ni d'archive avant autorisation. Rollback : retirer seulement les nouveaux fichiers
CODX-00 de sa branche après revue, sans toucher les skills Claude ni les worktrees tiers.
