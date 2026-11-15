# MOB-07 — constructeur personnel natif minimal

15novembre2026. **PROPOSED / NO_GO_BUILD / G1_NOT_ACCEPTED**. Préparation demandée après livraisonMOB06 ; aucune source produit, migration, UI ou dépendance implémentée. Parent canonique préparé :59a28dc6db2554babc924701e11fe9f1a86bf613, après408/411 ; CI canonique finale43720672918 terminée avec succès ; revalider le parent courant avant apply.

## Why
Programmes sait lire les programmes possédés et lancer leurs séances admissibles, mais le pilote ne peut pas encore en construire un nativement. Livrer créer→composer→enregistrer→valider→publier→retrouver dans Programmes, sans déplacer le moteur de politique dans le client.

## What Changes
Un programme personnel contient des séances ordonnées ; chaque mouvement est sélectionné par identité canonique serveur, avec séries et plages de répétitions explicitement choisies par l’utilisateur. Brouillon, validation de structure et publication sont distincts ; VALIDATED ne devient pas lançable. Le départ reste celui de MOB06 et ses gates Legacy/V3. Correction d’un publié par cycle explicite, jamais mutation des templates historiques.

## Brainstorming / Options / Risques / Choix retenu
1. Copie du wizard web : rapide mais incompatible avec la DA et les contrats d’auth/reprise natifs.
2. Générateur scientifique client : hors mandat, ambiguïtés de prescription et duplication d’autorité.
3. Adaptateur natif borné des services canoniques, sélection explicite et reprise durable : proposition retenue par l’agent, pas décision opérateur acquise.
Risques : services historiques auto-commit, identité numérique séparée du nom EKB figé, concurrence web/natif et publication partiellement committée. Le design propose leur fermeture avant tout build.

## Non-goals
Aucun agenda, programme actif inventé, recommandation de volume/charge/nutrition, moteur scientifique nouveau, poids observé fabriqué, média généré, SDK ou APK. Aucun élargissement du GO MOB06.

## Impact
Un seul change/une PR de fonctionnalité ; migration additive de reçus techniques proposée, à recevoir avec son GO propre. G1 fonctionnel puis vrais pixels requis avant commit UI. GOV-MERGE-01 ensuite seulement, aucune activation/release implicite.
