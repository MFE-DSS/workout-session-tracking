# Proposal — CODX-00 / codex-openspec-adapter

## Why

La reprise Codex partait d'un checkout ancien sans OpenSpec ni client mobile récent. La canonique possède déjà
OpenSpec et ses skills Claude, mais pas l'adaptateur Codex. L'opérateur demande CODX-00 avant CI-01 puis MOB-02.

## What Changes

- Installer les six skills officielles par `openspec init --tools codex --no-animation` sous `.agents/skills`.
- Relire le diff généré, préserver les skills personnalisées et tous les contrats existants.
- Documenter la base de travail, la remise à niveau MOB-02 et le protocole de reprise depuis les bons contrats.
- Consigner la roadmap opérateur, avec STORE-00 en parallèle du chemin critique mobile.

## Capabilities

### New Capabilities

Aucune capacité produit. `skip_specs: true` : adaptation d'outillage et documentation seulement.

### Modified Capabilities

Aucune. Les specs historiques et les contrats visuels/de domaine ne sont pas modifiés.

## Non-goals

Pas de Spec Kit, de migration de specs historiques, d'AGENTS.md versionné, de changement à `CLAUDE.md` ou
`openspec/config.yaml`, de code produit, de pipeline CI, de baseline, de déploiement ni de compte Store.
CI-01 et MOB-02 restent des changes et branches distincts.

## Dependencies

Canonique `fcfbcd7` (PR #345 comprise), OpenSpec 1.14.3 déjà installé. La configuration locale de l'adaptateur est
explicitement demandée par l'artefact opérateur du 3 novembre ; sa livraison versionnée reste à relire.

## Impact

`.agents/skills/openspec-*`, ce change, rapport CODX-00, registre et roadmap datée. Aucun écran visible touché.
La remise à niveau de la branche MOB-02 est une préparation locale séparée ; aucun de ses fichiers n'entre dans
le diff CODX-00. Aucun push de branche rebasée n'est autorisé par cette préparation.
