# SPRINT Sb_UI_SESSION_CHOICES_DISCLOSURES_01 — le clavier rendu (RAPPORT)

**Train :** `AUREN_INTERACTION_REFINEMENT_01`, tranche 3/3 ·
**Base canonique :** `e8614bd` · **Branche :** `sb/ui-session-choices-disclosures-01`

---

## 1. Phase 0 — découverte dépôt entier (obligatoire)

Les tranches 1 et 2 ont échoué trois fois sur la découverte de périmètre. Cette
tranche commence donc par l'inventaire, avant toute édition.

### Inventaire COMPLET des consommateurs de `.segmented`

| Surface | Gabarit | Valeur de formulaire |
|---|---|---|
| Échelle de disponibilité (×5 champs) | `index.html:130` (inline) | `radio` 1..5 |
| Concentration | `session_detail.html:148` (macro) | `concentration` |
| Énergie générale | `session_detail.html:158` (macro) | `global_state` |
| Sensation musculaire | `exercise_card.html:626` (macro) | `muscle_sensation` |
| **Alternatives d'exercice** | `exercise_card.html:531` (inline `--stacked`) | `substituted_name` |

CSS : `app.css:1010–1035` et `2584–2589`.
Tests épinglant le composant : `test_session_focus_cockpit.py:298` uniquement.

**Faux positif écarté** : `_partials/muscle_focus.html` contient
« source-segmented deltoid » — terminologie des données de maillage, sans
rapport avec le composant. Le test d'inventaire cherche donc l'**usage de la
classe**, pas le mot.

### Décision : correction CENTRALE (option A du brief)

**Les cinq consommateurs sont des radios natifs interactifs ordinaires.** Aucun
n'a de comportement que la correction changerait. Le sélecteur fautif étant
global, la correction l'est aussi — elle répare **cinq** surfaces, pas
seulement celle qui apparaît sur la capture d'écran.

---

## 2. Le défaut P0, et sa correction

```css
/* avant, app.css */
.segmented__option input { display: none; }
```

`display: none` retire le contrôle natif **de la navigation clavier et de
l'arbre d'accessibilité**. Les radios de substitution en séance étaient donc
inatteignables au clavier en production.

**Corrigé sans seconde implémentation** : le sélecteur rejoint la déclaration
**unique** de `interaction.css` —

```css
.a11y-input,
.segmented__option input { position: absolute; …; clip-path: inset(50%); }
```

Une seule déclaration de masquage accessible existe dans le dépôt, et un test
l'exige.

**Le focus se voit là où l'utilisateur regarde** : l'input mesure 1 px, donc
l'indicateur est porté par la surface visible associée —
`.segmented__option input:focus-visible + span` avec l'ambre existant.

**L'état sélectionné cesse de dépendre de la couleur** : une coche `✓` textuelle
s'ajoute au libellé coché.

---

## 3. Alternatives — une seule liste groupée

Les options ne portent plus ni rayon ni ombre propres ; un filet les sépare et
la carte d'exercice reste le seul cadre. Cible tactile portée à 44 px, arête
`inset` de 2 px sur l'option retenue.

**Aucune métadonnée inventée** : le gabarit affiche ce que la substitution
fournissait déjà (nom, badge de palier, rationale quand elle existe).

---

## 4. Parité de substitution — gel produit respecté

Inchangés et testés : nom du champ `substituted_name` · valeur vide pour
l'exercice prescrit · `value="{{ s.name }}"` par candidat · ordre **N1 → N2 →
N3** · candidat coché = valeur persistée · repli plat hérité.

Un test vérifie par `git diff` qu'**aucun** module gelé n'est touché
(`substitution.py`, `sessions.py`, `recommendation.py`, `behavioral.py`).

**Aucun JS ajouté** : `details/summary` natif conservé, inventaire JS toujours
à trois fichiers.

---

## 5. Plantations — quatre, chacune sur la garde visée

| # | Plantation | Garde qui tombe |
|---|---|---|
| 1 | `display:none` restauré sur le radio natif | `test_the_segmented_radio_is_no_longer_display_none` |
| 2 | association label/input supprimée | `test_the_macro_still_renders_a_native_radio` |
| 3 | candidats réordonnés (N2 avant N1) | `test_the_tier_order_is_n1_then_n2_then_n3` |
| 4 | valeur soumise mutée | `test_every_candidate_still_posts_its_own_name` |

---

## 6. Deux tests de la tranche 1 mis à jour

`_rule()` n'acceptait qu'un sélecteur seul en début de ligne ; `.a11y-input` est
désormais **groupé** avec `.segmented__option input`, donc le motif accepte la
forme groupée. Et `test_the_family_stays_small` liste `segmented` comme
**composant historique réparé** — pas une primitive neuve — avec la raison
écrite.

---

## 7. Ce que cette tranche NE livre PAS

Énoncé franchement plutôt que passé sous silence :

- **Le panneau machine n'a pas été restylé.** La grammaire `.disclosure` existe
  et est testée, mais elle n'est pas appliquée au gabarit du panneau machine.
  Le brief le demandait ; je ne l'ai pas fait.
- **Aucune capture d'écran n'a été produite.** L'outillage canonique
  (`scripts/visual_baseline_capture.py`, Playwright) couvre des **routes**, pas
  des **états d'interaction** : la matrice n'a pas d'entrée pour « alternatives
  ouvertes » ou « disclosure machine ouverte », et piloter ces états demanderait
  d'étendre le harnais.
- **Aucun smoke clavier navigateur** n'a été exécuté. Les preuves d'accessibilité
  sont **structurelles** (CSS et balisage), pas comportementales dans un vrai
  navigateur.

## Verdict

Le défaut d'accessibilité rapporté est corrigé **à la racine** : une seule règle
globale, cinq surfaces réparées, une seule implémentation de masquage dans le
dépôt.

La présentation des alternatives cesse d'empiler des cadres. Mais la revue
visuelle humaine que le train prévoyait **ne peut pas s'appuyer sur des captures
produites ici** — c'est la limite honnête de cette livraison.
