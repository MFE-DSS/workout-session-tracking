# Gabarit — tâche visuelle AUREN (`DA-GOV-01`)

À coller en tête de **tout** prompt d'agent qui touche une surface visible. Autorité :
`docs/strategy/AUREN_VISUAL_CONTRACT.md`. Les garde-fous d'itération (`CLAUDE.md §5.6–5.9`) s'appliquent en plus.

---

## AUTHORITY

- Spec verrouillée : `<AUREN_CALIBRATION_SYSTEM.md / AUREN_VISUAL_CONTRACT.md §…>`
- Visual ID(s) concernés : `<CALIBRATION-LINE-V1, FRAME-C-V1, …>`
- Baseline(s) qui font foi : `<calibration-line-390-push, …>` (`clients/mobile/visual-contract/baselines/manifest.json`)

## CHANGE ALLOWED

Propriétés visuelles et fichiers **exacts** qui peuvent changer :
- `<propriété>` dans `<fichier>`

## CHANGE FORBIDDEN

Tout ce qui doit rester intact. Au minimum, les **MUST PRESERVE** et **MUST NEVER** des Visual IDs concernés, plus :
- `<fichiers LOCKED : geometry.ts, CalibrationRail.tsx, frameGeometry.ts, …>`

## TARGET DELTA

Le problème visuel à résoudre, en **une phrase**, avec la citation de l'opérateur.

## FIXTURES

États et tailles exacts qui jugent le changement : `<TARGET / PUSH / HIGH COST × 320 / 390 …>`

## STOP CONDITIONS

Si le problème demandé exige de modifier un invariant **LOCKED** : **STOP**.
Ne rien improviser ; rapporter le conflit à l'opérateur (invariant en cause, pourquoi, options).

---

## PRE-FLIGHT — à rendre AVANT toute modification

1. baseline ID : `<…>`
2. fichiers LOCKED impliqués : `<…>`
3. invariants LOCKED en jeu : `<MUST PRESERVE / MUST NEVER cités>`
4. delta permis : `<…>`
5. fichiers prévus : `<…>`

**Aucune ligne de code avant que ce pré-vol soit rendu.**

## POST-FLIGHT — à rendre APRÈS

1. fichiers modifiés : `<…>`
2. tests structurels : `<commande, résultat>`
3. régression visuelle : `bash clients/mobile/visual-contract/run.sh test` → `<résultat par fixture>`
4. avant / après de **chaque** fixture LOCKED touchée : `<images>`
5. liste de **chaque** delta visuel voulu : `<…>`
6. confirmation que chaque invariant LOCKED est inchangé : `<un par un>`

**Ne jamais mettre à jour une baseline approuvée soi-même** : c'est une décision de l'opérateur (`run.sh approve` + manifeste).
