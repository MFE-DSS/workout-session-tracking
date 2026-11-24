# UX11-C Implementation Plan

> Exécution inline via superpowers:executing-plans, tests via test-driven-development. Même worktree autorisé, sources antérieures préservées. Pas de commit par tâche avant pixels.

**Goal:** un objet de série numérique stable, référence secondaire visible à l’IME et commandes situées.
**Architecture:** modifier uniquement la présentation ContextualInstrument/ContextualPrimitives et ajouter des feuilles UI ciblées si nécessaires ; réutiliser referenceModel/read/hook et tous les callbacks sans réécriture. Aucun montage/contrôleur/API/SQLite nouveau.
**Tech Stack:** Expo58/RN0.88 existants, mêmes dépendances et client Android local de revue ; aucune installation/native build.
**Spec:** UX11_C_COMPOSITION.md et contrat source UX11 conservé.

## Task1 — objet de lecture/édition
- [x] RED : référence visible pendant IME ; identité et porteurs numériques stables avant/après soumission ; aucune préremplissage ; annulation et champ voisin préservés ; même appel unique au temps du clic.
- [x] GREEN : fenêtres existantes, valeurs dominantes, source compacte et disclosures ; commande située, reflow et action au-dessus IME.
- [x] Tests ciblés et consommateurs ; pas de changement des sélecteurs, contrats ou callbacks métiers.

## Task2 — preuve native et gate
- [x] Nouvelle copie synthétique, qualification canonique, même source avant/après (UX11 figé / UX11-C), aucun fait ancien réécrit.
- [x] 4 états natifs + contre-exemple grande fonte,360/480 dp et IME réel. Source mapping et gain fonctionnel observable, limites exactes.
- [x] check_scope, broad ciblé, mobile/TS, visuelLOCKED et sécurité pertinents ; une revue indépendante finale du diff, correctifs en scope.
- [x] Gate pixels distinct reçu le 24 novembre ; publication de code autorisée, aucune OTA implicite.
