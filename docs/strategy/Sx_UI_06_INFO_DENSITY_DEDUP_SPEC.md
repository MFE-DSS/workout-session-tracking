# Sx_UI_06 — Information Density / Dedup Spec (SPEC ONLY)

**Statut** : ✅ SPEC ONLY — décisions D1/D2 + OQ-A→E tranchées ; ready for `Sb_UI_06.1` build (sur GO)
**Date** : 2026-07-09
**Type** : spec de dé-densification UI (docs-only, aucun code)
**Origine** : point d'attention opérateur — surcharge informationnelle : mêmes
données (poids/reps cible, charge dernière séance) affichées à plusieurs endroits
sur le même écran (surtout la carte d'exercice en séance).

---

## 1. Objectif

Réduire la **redondance informationnelle** de l'UI SSR : quand une même donnée
est affichée à ≥2 endroits sur le même écran, n'en garder **qu'un seul** —
**le plus proche de l'action**. But produit : lisibilité en salle, moins de bruit,
décision plus rapide. **Aucun changement métier** (scoring / classification /
données) ; réduction **de présentation** uniquement.

---

## 2. Règle directrice

> **Une information = un seul endroit, le plus proche de l'action.**

Corollaires :
- Si une donnée sert à **saisir** (poids/reps), sa suggestion vit **dans/au plus
  près du champ de saisie** (placeholder / ligne de référence adjacente), pas en tête.
- Un « teaser » ne **réaffiche jamais** les mêmes valeurs qu'un bloc détaillé plus
  bas : il **pointe** (lien / résumé qualitatif), il ne duplique pas.
- Un fallback neutre (« À qualifier ») ne se répète pas ligne par ligne : une note
  unique suffit.
- La **densité n'est pas la valeur** : mieux vaut une surface claire que trois
  surfaces qui disent la même chose.

---

## 3. Contraintes dures (verrouillées)

- **Aucun changement du contrat de saisie** : les inputs `name=set_{id}_weight_kg`
  / `set_{id}_reps` restent identiques (name, form POST, route, dérivation
  `completed` serveur).
- **Aucun changement métier / service / modèle / migration / endpoint / JS.**
- **SSR / no-JS strict** ; classes Auren Terminal préservées (re-skin, pas re-archi).
- **Tests** : chaque surface retirée est asservie par des tests (logging console,
  exercise history, mobile polish, worked area…). Les tests concernés doivent être
  **ajustés à la nouvelle vérité**, jamais contournés ni affaiblis dans leur intention.
- Réduction **réversible** : on retire de l'affichage, on ne supprime aucune donnée
  ni aucun calcul côté route (les variables de contexte restent disponibles).

---

## 4. Décisions déjà tranchées (opérateur, 2026-07-09)

### D1 — Charge de la dernière séance (carte d'exercice active)
Aujourd'hui affichée jusqu'à **3-4×** : `.exercise-card__recap` (aperçu compact,
L50) · `.exercise-card__chip` briefing (L54) · `.last-time__values` bloc « Dernière
fois » en tête (L356) · `.session-focus__console-ref--prev` « Référence précédente »
dans la console (L505).

**Décision** : **garder « Référence précédente » dans la console** (au plus près
des cases) ; **retirer le bloc « Dernière fois » en tête** (`.last-time__values`).
Le recap de l'aperçu **fermé** (`.exercise-card__recap`, L50) est conservé (surface
distincte : carte repliée). La date relative peut être fusionnée dans la référence
console.

### D2 — Cible / objectif (carte d'exercice active)
Aujourd'hui affichée jusqu'à **3×** : `.exercise-card__scheme` (set_scheme brut en
tête, L201) · `.session-focus__console-ref--target` « Cible » console (L510) ·
placeholder cible **dans la case** (Sb_30.next, L529+).

**Décision** : **garder uniquement le placeholder dans la case**. **Retirer** le
`.exercise-card__scheme` en tête **ET** la ligne « Cible » de la console-refs. La
suggestion cible ne vit plus que là où on saisit.

---

## 5. Inventaire priorisé des redondances (source : audit read-only 2026-07-09)

### 🔴 Critiques (même donnée ≥2× sur le même écran)

| # | Écran | Donnée | Emplacements | Proposition |
|---|---|---|---|---|
| R1 | exercise_card | charge dernière séance | recap (L50) · chip (L54) · `last-time` (L356) · console-ref-prev (L505) | **D1** : garder console-ref-prev ; retirer `last-time` tête |
| R2 | exercise_card | cible / set_scheme | scheme (L201) · console-ref-target (L510) · placeholder case | **D2** : garder placeholder case ; retirer scheme + console-target |
| R3 | exercise_card | zone travaillée primaire | body-zone-chip aria-hidden (L130) · worked-area-value primary (L147) | fusionner : le chip décoratif n'ajoute pas de sémantique → **OQ-A** |
| R4 | home (index) | readiness state | teaser `.today-home__readiness` (L59) · widget complet (L86+) | teaser → **pointeur** (lien + résumé qualitatif), pas les mêmes badges → **OQ-B** |

### 🟠 Hautes (redondance visuelle / fallback dense)

| # | Écran | Donnée | Proposition |
|---|---|---|---|
| R5 | exercise_card | « À qualifier » ×3 (Assistants L156 · Stabilisation L161 · Pattern L170) | une seule note « à qualifier » quand tout est vide, ou masquer les rows vides → **OQ-C** |
| R6 | progress vs home | KPI (sessions 30j, score, complétion) | home = sous-ensemble strict + lien ; ne pas recopier tout /progress → **OQ-D** |

### 🟡 Modérées (à évaluer, pas forcément à retirer)

| # | Écran | Donnée | Note |
|---|---|---|---|
| R7 | session_done | zones (synthèse) vs zones par exercice | synthèse + détail = légitime ; à réduire seulement si trop dense |
| R8 | coach_report | zones (section 4) vs body intelligence snapshot | 2 moteurs distincts ; garder mais clarifier les libellés |
| R9 | body_intelligence | headline + bullets + priorities | 3 couches d'interprétation — UX à valider, hors scope V1 |
| R10 | cues techniques | `.session-focus__cues` vs machine-panel cues | même contenu à 2 endroits (l'un replié) — à dédupliquer si confirmé |

---

## 6. Découpage build proposé (review-gated, séquentiel)

- **Sb_UI_06.1 — Carte d'exercice (R1 + R2)** : appliquer D1 + D2 sur
  `exercise_card.html`. Retirer bloc « Dernière fois » tête + `.exercise-card__scheme`
  + ligne « Cible » console. Ajuster les tests asservis. **Le plus fort ROI, le plus
  demandé.**
- **Sb_UI_06.2 — Worked Area (R3 + R5)** : dé-dupliquer zone primaire (chip vs value)
  + condenser les « à qualifier ». (Sous garde de non-régression Sx_32 : ne pas
  changer la sémantique du descriptor, juste sa présentation.)
- **Sb_UI_06.3 — Home (R4 + R6)** : teaser readiness → pointeur ; KPI home = sous-
  ensemble strict.
- **Sb_UI_06.4 — Écrans secondaires (R7–R10)** : session done / coach report / body
  intelligence / cues — au cas par cas, seulement ce qui est tranché.

Chaque sous-sprint : docs-only impossible (touche templates) → tier `shared_code`
probable (template partagé) → **full sweep local requis** selon `check_scope`.

---

## 7. Non-goals (hors périmètre Sx_UI_06)

- Aucun changement de **donnée**, **calcul**, **scoring**, **classification**,
  **service**, **modèle**, **migration**, **endpoint**, **JS**.
- Aucun **rebrand**, aucune nouvelle **couleur/token**, aucune **ré-architecture**
  de layout (on retire des surfaces, on ne refait pas la grille).
- Aucun retrait de **donnée persistée** ou de **variable de contexte** côté route
  (uniquement de l'affichage).
- Body Intelligence 3-couches (R9) : **non traité** en V1 (UX dédiée requise).
- Pas de refonte de la navigation home (tiles) au-delà de la dé-duplication stricte.

---

## 8. Open Questions — TRANCHÉES (opérateur, 2026-07-09)

- **OQ-A** (R3) — zone travaillée : le `body-zone-chip` (code brut « pecs »,
  aria-hidden) vs le label « Pectoraux ».
  ✅ **DÉCIDÉ : retirer le chip** (décoratif, redondant avec le label sémantique
  `.worked-area-value`). Une seule surface pour la zone primaire.
- **OQ-B** (R4) — teaser readiness home.
  ✅ **DÉCIDÉ : résumé qualitatif court + lien** (ex. « Prêt · fatigue modérée →
  détails »), **sans réafficher les badges** du widget plein. Le teaser pointe, ne duplique pas.
- **OQ-C** (R5) — les 3 « à qualifier » (Assistants / Stabilisation / Pattern).
  ✅ **DÉCIDÉ : masquer les rows vides** quand aucune donnée réelle ; **garder
  Principal toujours** (+ la note prudente unique en bas conservée). Pas de fallback
  répété ligne par ligne.
- **OQ-D** (R6) — KPI home vs /progress.
  ✅ **DÉCIDÉ : home = sous-ensemble strict décisionnel** (séances cette semaine +
  streak) **+ lien /progress**. Ne pas recopier l'ensemble des KPI de /progress.
- **OQ-E** — ordre de build.
  ✅ **DÉCIDÉ : commencer par `Sb_UI_06.1`** (carte d'exercice, D1 + D2, point
  d'origine du signalement, ROI max).

---

## 9. Critères d'acceptation de la spec

- [x] Règle directrice « une info = un endroit » validée.
- [x] D1 (charge → console) + D2 (cible → case) confirmées.
- [x] OQ-A→E tranchées (§8).
- [x] Ordre de build confirmé (`Sb_UI_06.1` en premier).

---

## Verdict

**Verdict :** ✅ **SPEC ACCEPTED — ready for `Sb_UI_06.1` build (sur GO).**

L'audit confirme que la surcharge informationnelle est **systémique** (carte
d'exercice surtout, mais aussi home et progress) : la charge « dernière séance »
est affichée jusqu'à 3-4× et la cible jusqu'à 3× sur la même carte active. La règle
« une information = un seul endroit, le plus proche de l'action », les décisions D1
(charge → console) / D2 (cible → case), et les OQ-A→E tranchées (chip retiré ·
teaser readiness = pointeur qualitatif · rows vides masquées · KPI home = sous-
ensemble strict · ordre = carte exercice d'abord) définissent le build. Premier
sous-sprint à fort ROI : **`Sb_UI_06.1`** (carte d'exercice, D1 + D2). Aucun code
touché par cette spec.
