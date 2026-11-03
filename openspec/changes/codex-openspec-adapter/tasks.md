# Tasks

## 1. Base et préservation

- [x] 1.1 Actualiser origin et relever la canonique ; vérifier `fcfbcd7` et un worktree CODX-00 propre au départ.
- [x] 1.2 Sauvegarder `091110b`, rebaser MOB-02 et vérifier le diff du dossier de proposition vide avant consignation des décisions ; SHA résultant `8c0f4d7`, aucun conflit.

## 2. Adaptateur et pilotage

- [x] 2.1 Générer l'adaptateur officiel avec `openspec init --tools codex --no-animation` ; vérifier les six SKILL.md sous `.agents/skills`.
- [x] 2.2 Relire les nouveaux fichiers, comparer aux skills du générateur existantes et vérifier le diff vide de `CLAUDE.md`, `.claude/skills`, `openspec/config.yaml`, `openspec/specs`.
- [x] 2.3 Livrer la roadmap avec STORE-00 parallèle, le rapport CODX-00 et la ligne de registre ; vérifier les chemins et distinguer configuration locale de livraison.

## 3. Vérification et livraison

- [x] 3.1 Exécuter `python scripts/check_scope.py`, suivre ses contrôles applicables à cet outillage sans code produit ; OpenSpec strict et protocole documentaire doivent passer.
- [ ] 3.2 Soumettre le diff et le rapport pour revue de livraison ; relever l'autorisation avant commit/push/PR, puis vérifier la CI réelle avant toute clôture.

## Workflow follow-up

- Archiver après merge et contrôles de livraison ; ne pas archiver les autres changes aux tâches appareil restantes.
- CI-01 fait l'objet de sa propre proposition et de sa propre PR avant MOB-02.
