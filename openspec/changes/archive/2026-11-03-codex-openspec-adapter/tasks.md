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
- [x] 3.2 Soumettre le diff et le rapport pour revue de livraison ; relever l'autorisation avant commit/push/PR, puis vérifier la CI réelle avant toute clôture (GO PUSH explicite, PR #346, run 41668162468 : 8/8 jobs et checks externes verts ; merge non effectué).

## Workflow follow-up

- Archiver après merge et contrôles de livraison ; ne pas archiver les autres changes aux tâches appareil restantes.
- CI-01 fait l'objet de sa propre proposition et de sa propre PR avant MOB-02.

## Relevé final avant archive

PR #346 mergée `60bea5d`, CI canonique41691072708 :8/8 jobs Actions réussis. Gate Sonar ERROR réelle,
désormais consultative sous GOV-SONAR-01 #348 mergée `cc80ddd`. Aucun code produit/baseline modifié.

## Vérification canonique et protection finales

CI-01 canonique `edd7351`, run41711441173 : tous les contrôles obligatoires hors Sonar réussis.
Protection phase B appliquée puis relue : QA,lint,visuel et `mobile checks (Jest + TypeScript)` requis,
app_id15368,strict=false ; Sonar consultatif,aucun autre réglage changé.
