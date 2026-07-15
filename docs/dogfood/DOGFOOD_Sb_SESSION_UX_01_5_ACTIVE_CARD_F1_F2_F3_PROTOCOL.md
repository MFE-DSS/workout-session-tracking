# DOGFOOD — Sb_SESSION_UX_01.5 — Active Card F1 / F2 / F3 — PROTOCOLE TERRAIN

**Statut** : 🟡 **FIELD TEST READY / OPERATOR EVIDENCE PENDING**
**Type** : protocole de validation terrain — docs-only (aucun code/test/template/CSS/donnée)
**Date de préparation** : 2026-07-15
**Baseline auditée** : `7c00203`
**⚠️ Ne pas marquer PASS / ACCEPTED / CLOSED avant la séance réelle.** Les champs vides ci-dessous
sont à remplir **par l'opérateur pendant/après la séance** — ne rien préremplir ni inventer.

> **Objectif réel** : *La carte active permet-elle désormais de commencer, renseigner et enregistrer
> un exercice sans que les éléments de contexte ralentissent ou brouillent l'action principale ?*
> Verdict par friction : **PASS / PARTIAL / FAIL / NOT OBSERVED**.

---

## 0. Chaîne fonctionnelle validée (déjà livrée + CI 3/3 verte)

| Friction | Comportement attendu | Build | Sous-sprint | CI (SHA) |
|---|---|---|---|---|
| **F1** — console prioritaire | console **avant** les cues ; action principale plus proche ; POST/champs inchangés ; sticky CTA + timer préservés | `901143f` | `Sb_SESSION_UX_01.2` | `29335728163` ✅3/3 |
| **F2** — charge précédente au point de saisie | « dernière : X kg · Y reps » **près du set actif** ; absent si pas d'historique ; **aucune valeur préremplie** ; aucune fausse reco | `015cdfe` | `Sb_SESSION_UX_01.3` | `29329356785` ✅3/3 |
| **F1-compl** — alternatives sous la console | « Adapter l'exercice » **après** la console ; drawer **replié** par défaut ; substitutions intactes | `4fdcb71` | `Sb_SESSION_UX_01.2b` | `29344051281` ✅3/3 |
| **F3** — cues repliées | cues techniques **après** la console ; `<details>` **replié** par défaut ; contenu toujours accessible ; **aucun JS** | `4fdcb71` | `Sb_SESSION_UX_01.4` | `29344051281` ✅3/3 |

---

## A. Contexte (à remplir)

```
Date            :
Salle           :            (générique OK ; aucune donnée perso de tiers)
Appareil        :
OS              :
Navigateur/PWA  :            (mobile web / PWA installée ?)
Orientation     :            (portrait / paysage)
Programme       :
Séance          :
Nb d'exercices  :            (cible ≥ 4)
Nb de work sets :            (cible ≥ 12)
Réseau          :            (wifi / 4G-5G / offline)
```

## B. État global avant la séance (1–5, contexte seulement)

```
Fatigue                :  /5
Stress                 :  /5
Familiarité séance     :  /5
Contrainte de temps    :  /5
```

## Conditions minimales à couvrir (cocher pendant la séance)

```
[ ] ≥ 4 exercices           [ ] ≥ 12 work sets
[ ] ≥ 1 exercice AVEC historique   [ ] ≥ 1 exercice SANS historique (si naturel)
[ ] ≥ 1 ouverture drawer substitution
[ ] ≥ 1 ouverture cues techniques
[ ] ≥ 1 passage save → next  [ ] ≥ 1 usage jump bar   [ ] ≥ 1 usage sticky CTA
```
*Séance plus courte exploitable → les critères non couverts restent **NOT OBSERVED**.*

---

## 8. F1 — Console prioritaire (relever sur les 2 premiers exercices)

| Item | Ex.1 | Ex.2 |
|---|---|---|
| Console identifiable immédiatement ? (oui/non) | | |
| Scroll avant 1ʳᵉ saisie ? (0 / 1 / 2+) | | |
| Alternatives gênent l'accès à la saisie ? (oui/non) | | |
| Cues gênent l'accès à la saisie ? (oui/non) | | |
| 1ᵉʳ champ de charge atteint sans hésitation ? (oui/non) | | |

**Qualitatif** : *Ai-je cherché où saisir, ou l'action était-elle évidente ?*
```

```
**Verdict F1** : ☐ PASS ☐ PARTIAL ☐ FAIL
- PASS : action claire, aucun bloc secondaire ne ralentit la saisie
- PARTIAL : action trouvée mais scroll/hésitation notable
- FAIL : contexte toujours prioritaire perceptivement / saisie difficile à retrouver

## 9. F2 — Charge précédente au point de saisie

**Exercice AVEC historique** :
```
Rappel visible sur le set actif ?         oui/non :
Valeur comprise immédiatement ?           oui/non :
Besoin de remonter vers le bloc global ?  oui/non :
Rappel utile pour choisir la charge ?     oui/non :
Rappel trop présent / distrayant ?        oui/non :
Valeur cohérente avec séance précédente ? oui/non/non vérifié :
```
**Exercice SANS historique** (si ce cas se présente) :
```
Aucune fausse valeur affichée ?           oui/non :
Ligne compréhensible sans historique ?    oui/non :
```
**Qualitatif** : *Le rappel « dernière » m'évite-t-il un effort de mémoire ou un scroll ?*
```

```
**Verdict F2** : ☐ PASS ☐ PARTIAL ☐ FAIL ☐ NOT OBSERVED

## 10. F3 — Densité de la carte (sur toute la séance)

```
Nb ouvertures cues            :
Nb ouvertures alternatives    :
Ouvertures accidentelles      :
Fermetures nécessaires avant saisie :
Scroll jugé excessif sur un exercice ? (oui/non + lequel) :
Perte de contexte après ouverture d'un détail ? (oui/non) :
```
**Qualitatif** :
- La carte paraît-elle **calme** ou toujours chargée ?
- Les infos repliées restent-elles **faciles à retrouver** quand utiles ?
- Le passage console → alternatives → cues → feedback paraît-il **naturel** ?
```

```
**Verdict F3** : ☐ PASS ☐ PARTIAL ☐ FAIL

---

## 11. Non-régressions à surveiller (cocher ✅ / ⚠️)

```
[ ] saisie poids/reps fonctionnelle
[ ] aucune valeur perdue au save
[ ] save → next correct
[ ] jump bar correcte
[ ] sticky CTA accessible
[ ] timer de repos utilisable
[ ] substitution toujours fonctionnelle
[ ] cues toujours consultables
[ ] bloc « Référence précédente » toujours présent
[ ] rappel inline seulement sur le set actif
[ ] aucune duplication visuelle évidente
[ ] aucune erreur serveur/template
```
**Anomalie éventuelle** (une par bloc) :
```
Exercice           :
Étape              :
Action             :
Résultat observé   :
Résultat attendu   :
Reproductible      : oui/non
Sévérité           : P0 / P1 / P2 / P3
```

## 12. Mesures simples (facultatives — estimation humaine, PAS d'instrumentation)
```
Temps ouverture exercice → 1ʳᵉ saisie (approx) :
Nb scrolls avant 1ʳᵉ saisie                    :
Nb retours vers le haut de la carte            :
Nb ouvertures cues / alternatives              :
Nb erreurs / corrections de saisie             :
```
*Ne pas créer de score composite.*

## 13. Irritant Delt_lat (indépendant — ne pas reproduire artificiellement)
```
Statut : ☐ NOT OBSERVED  ☐ OBSERVED — EVIDENCE CAPTURED
Si observé naturellement : surface exacte + texte exact :
(ne pas proposer de correction ici ; ne pas toucher ZONE_LABELS / données)
```

## 14. Preuves (confidentialité)
Acceptées : notes horodatées · captures **de l'app** · description d'étape · nom programme + code
exercice · temps approx · reproduction à l'exercice suivant.
**Ne pas** committer de capture avec : nom complet · email · données sensibles · visage/corps de
tiers · infos de salle non nécessaires. **Captures brutes hors Git tant que non nettoyées.**
Ne pas photographier d'autres personnes.

---

## 15. Décision de fin de terrain (matrice à compléter)

| Friction | Verdict | Preuve principale | Sévérité résiduelle | Action |
|---|---|---|---|---|
| F1 Console prioritaire | | | | |
| F2 Rappel précédent | | | | |
| F3 Densité | | | | |

**Actions autorisées** : `CLOSE` (concluant, aucune correction) · `OBSERVE AGAIN` (preuve
insuffisante) · `OPEN MICRO-FIX` (friction précise reproduite) · `REJECT CURRENT UX` (régression
sérieuse). **Un micro-fix exige** : observation concrète + scénario reproductible + impact réel sur
le logging + périmètre minimal. **Pas de fix sur simple préférence esthétique.**

---

## Verdict (préparation)

**Verdict :** 🟡 **Sb_SESSION_UX_01.5 — FIELD TEST READY / OPERATOR EVIDENCE PENDING.** Le protocole
terrain est prêt : chaîne F1 (`901143f`/01.2) + F2 (`015cdfe`/01.3) + F1-compl+F3 (`4fdcb71`/01.2b+01.4)
auditée, tous builds **CI 3/3 verts** (SHA exacts vérifiés). Fiche mobile-first à une main, sections
contexte + F1/F2/F3 + non-régressions + Delt_lat + matrice de décision. **Aucune observation n'est
inventée** ; les champs sont vides, à remplir par l'opérateur en salle. **Prochaine action après la
séance réelle** : `GO RECORD & CLOSEOUT — Sb_SESSION_UX_01.5` (exclusivement sur les observations
fournies par l'opérateur).
