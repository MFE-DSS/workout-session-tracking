# Sx_NN — Amendment §`<N>bis` — `<TOPIC>`

> Un amendement modifie une spec **déjà validée**. Il ne réécrit jamais la section originale : il ajoute une section `§N` bis qui prime, et marque la section originale comme `✅ TRANCHÉE <date>` pointant vers `§Nbis`. Voir `docs/strategy/SPEC_DRIVEN_ENGINEERING_PROTOCOL_v1.md §amendments`.

**Spec parente :** `docs/strategy/Sx_NN_<...>.md`
**Section amendée :** §`<N>` (`<titre>`)
**Date :** `YYYY-MM-DD`
**Sprint déclencheur :** `<Sb_NN.k ou OQ-N>`

---

## 1. Pourquoi l'amendement

Quel signal a déclenché l'amendement (mesure réelle ≠ estimée, OQ-N à trancher, retour terrain d'un sprint précédent, etc.).

## 2. Décision tranchée

Une à trois phrases. Ce qui est figé maintenant.

## 3. Modèle retenu / nouvelles valeurs / contraintes ajoutées

Détails techniques de la décision.

## 4. Justification / divergence de la spec originale

Si la décision diverge d'une valeur ou d'une intention de la spec originale, le dire **honnêtement** ici. Pas d'invention rétroactive.

## 5. Impact sur les Sb_NN.k existants et futurs

| Sprint | Avant | Après |
|---|---|---|
| Sb_NN.k déjà livré | | |
| Sb_NN.k+1 à venir | | |

## 6. Nouveaux hard contracts (si applicable)

Format verbatim citable. Préfixe `HC-<DOMAIN>-<N>` pour traçabilité.

## 7. Backlog post-amendement

Items créés par l'amendement (`Sb_NN.next.<topic>-<n>` par exemple).

## 8. Statut

- [ ] Section originale marquée `✅ TRANCHÉE <date>`
- [ ] Section `§Nbis` complète
- [ ] Hard contracts versionnés
- [ ] Si applicable : impact sur `docs/strategy/SPEC_REGISTRY.md` reflété

**Statut final :** `<DRAFT | READY FOR HUMAN REVIEW | APPLIED>`
