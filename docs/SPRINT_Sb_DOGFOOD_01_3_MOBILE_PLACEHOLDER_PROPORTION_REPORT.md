# Sprint Sb_DOGFOOD_01.3 — Mobile Placeholder Proportion

**Statut** : 🟢 DELIVERED — pending GO commit + CI + human review
**Type** : UI / PRESENTATION BUILD — formatter de string + CSS mobile, **aucune logique métier**
**Date** : 2026-07-11
**Cycle** : Sx_DOGFOOD_01 Load Hint / Substitution Coherence (dernier volet)
**Précondition** : `Sb_DOGFOOD_01.2` HUMAN REVIEW ACCEPTED ✅ (vérifié dans le repo).

---

## 0. Feedback dogfood

Dans la console de saisie, les placeholders de **cible chiffrée** (poids / reps)
sont rendus **dans les inputs eux-mêmes** — il n'y a **pas de span unité séparé**.
Quand la cible est longue, exemple « ≈ 102.5 » ou « ≈ 6-10 », le texte peut
devenir trop gros / trop large dans les cases sur **mobile étroit** (≤ 380 px),
au point de déborder ou de peser visuellement plus que la saisie réelle.

Règle produit inchangée : **placeholder = indication légère**. Jamais `value=`,
jamais préremplissage, jamais contrainte automatique.

---

## 1. Étape 0 — Brainstorming / Options / Risques / Choix retenu

### Options comparées

| Option | Description | Verdict |
|---|---|---|
| **A** | CSS-only (réduire la typo placeholder mobile) | ❌ partiel — ne résout pas « ≈ 102.5 » qui reste large |
| **B** | **Formatter compact (retirer `≈`) + CSS mobile `::placeholder`** | ✅ **RETENU** |
| C | Séparer valeur / unité dans le markup (span unité) | ❌ différé — trop large pour ce sprint |
| D | Supprimer les placeholders chiffrés | ❌ rejeté — régressif produit |

### Sujets clivants tranchés

1. **Retirer « ≈ » ou le remplacer par « ~ » ?** → **retirer** (`102.5`, `6-10`). « ~ »
   ré-ajoute un caractère et un bruit visuel ; la valeur nue est la plus lisible.
2. **Signal « suggestion » via microcopy plutôt que placeholder ?** → non nécessaire :
   le placeholder EST déjà le signal (texte grisé `--color-fg-subtle`, jamais rempli)
   + le contexte de la console. Pas de nouvelle microcopy.
3. **Réduire uniquement la typo placeholder sur mobile ?** → **oui**, `@media (max-width: 380px)`,
   `::placeholder` de la ligne d'overload uniquement.
4. **Séparer valeur / unité dans le HTML ?** → **non** (Option C différée V1).
5. **« kg » / « reps » comme placeholder vide ?** → inchangé : fallback `kg` / `reps`
   quand pas de cible chiffrée (déjà en place, non touché).
6. **Toucher `_build_overload_placeholder` ou seulement CSS ?** → **les deux** :
   formatter (présentation string, autorisé) **+** CSS. C'est la seule façon de
   régler « ≈ 102.5 » **et** la taille mobile.
7. **Modifier `sessions.py` alors que c'est une string de présentation ?** → **oui**,
   uniquement le formatter `_build_overload_placeholder` (aucune logique overload,
   historique, substitution).
8. **Limiter au premier work set actif ?** → déjà le cas (`_is_active_set`), pas de
   changement de portée : le placeholder cible ne vit que sur la ligne active.
9. **Largeur mobile cible : 360 / 380 / 390 px ?** → **380 px** — breakpoint déjà
   utilisé partout dans `session_focus.css` (cohérence, pas de nouveau seuil).
10. **Tester sans screenshot fragile ?** → tests sur la **string du formatter** +
    présence de la **règle CSS** (regex sur le fichier) + rendu HTML du placeholder.
    Aucun screenshot.

### Choix retenu — Option B légère

- Formatter : `"≈ 102.5"` → `"102.5"`, `"≈ 6-10"` → `"6-10"`, `"≈ 6"` → `"6"`.
- CSS : règle `@media (max-width: 380px)` ciblant `::placeholder` des inputs de la
  ligne `.set-row--has-overload-placeholder` (classe **déjà existante**, aucun
  changement de structure HTML).
- **Aucun** `value=`, **aucun** span unité, **aucun** JS, **aucun** engine touché.

### Risques / parades

| Risque | Parade |
|---|---|
| Perte du signal « suggestion » en retirant `≈` | Le placeholder reste grisé + jamais rempli ; test wording non-autoritaire conservé |
| Réduire la typo casserait le tap target / l'anti-zoom iOS | On ne touche **que** `::placeholder` ; `font-size:16px` de l'input et `min-height:44px` intacts ; test dédié le verrouille |
| Tests stale référençant `≈` | `test_overload_placeholder.py` mis à jour vers le contrat compact |

---

## 2. Format retenu

| Cas | Avant | Après |
|---|---|---|
| Progress (range) | `≈ 102.5` / `≈ 6-10` | `102.5` / `6-10` |
| Deload (min==max) | `≈ 90` / `≈ 6` | `90` / `6` |
| Une seule borne | `≈ 8` | `8` |
| Pas de cible | `None` | `None` (inchangé) |

L'unité **kg** reste portée par le label existant à côté du champ (contexte
console). La valeur nue tient dans un input mobile étroit (`102.5` = 5 caractères).

---

## 3. Pourquoi pas d'unité séparée en V1

Séparer valeur / unité (Option C) impliquerait un **changement de structure HTML**
(ajout d'un `<span>` unité, re-layout du `.set-row__inputs`), avec un risque de
régression sur le flux de saisie et l'alignement. Le brief le classe explicitement
« trop large pour ce sprint · à différer ». La cible V1 — lisibilité mobile — est
atteinte sans toucher au markup : compacter la string suffit, et la règle CSS
mobile absorbe le reste. L'unité séparée reste une piste propre pour un sprint UI
dédié (Option C), non urgente.

---

## 4. Changements

| Fichier | Nature | Détail |
|---|---|---|
| `app/routers/sessions.py` | formatter string | `_build_overload_placeholder` : retrait du préfixe `≈ ` sur weight + reps ; docstring mise à jour |
| `app/static/css/session_focus.css` | CSS mobile | règle `@media (max-width: 380px)` ciblant `::placeholder` de `.set-row--has-overload-placeholder` (font-size `0.8125rem`, letter-spacing `-0.01em`) |
| `tests/test_overload_placeholder.py` | tests (contrat) | assertions alignées sur le format compact (sans `≈`) ; garde wording rendue robuste |
| `tests/test_dogfood01_mobile_placeholder.py` | **nouveau** | 9 tests dédiés (formatter compact, CSS mobile ciblée, placeholders ≠ values, garde `repère`) |

**HTML** : `exercise_card.html` **non modifié** — la classe `.set-row--has-overload-placeholder`
existait déjà (posée par Sb_30.next.placeholder). Aucun span unité ajouté.

---

## 5. Tests

### `tests/test_dogfood01_mobile_placeholder.py` (NOUVEAU, 9 tests)
- **formatter** : poids compact ne contient ni « kg » ni « ≈ » · reps compact ne
  contient ni « reps » ni « ≈ » · format long `102.5` couvert et court (≤ 6 chars) ·
  cible None → None (défensif) ;
- **CSS** : règle mobile `::placeholder` ciblée présente sous `@media (max-width: 380px)` ·
  la règle ne déclare **ni** `min-height` **ni** `height` (tap target préservé) et
  réduit bien `font-size` ;
- **HTML rendu** : la cible `102.5` / `6-10` apparaît **uniquement** en `placeholder=`,
  **jamais** en `value=` ; input actif reste `value=""` ; aucun `≈` résiduel ;
- **garde** : aucune occurrence « Repère »/« repère » dans `exercise_card.html`.

### `tests/test_overload_placeholder.py` (MIS À JOUR, 14 tests)
- contrat formatter aligné compact (`102.5`, `6-10`, `90`, `6`) ;
- rendu HTML `placeholder="102.5"` / `placeholder="6-10"` ; plus de `≈` ;
- input contracts, active-card-only, first-work-set-only, `value=""` : **inchangés, verts**.

### Résultats
- Ciblés : `test_overload_placeholder.py` **14/14**, `test_dogfood01_mobile_placeholder.py` **9/9**.
- **Broad sweep** (session_focus/logging_console/overload_hint/ui06/dogfood01/placeholder) :
  **310 passed, 0 failed**.
- **Broad sweep consommateurs** (sessions/delta/hints/briefing/substitution/last_time/exercise_card) :
  **173 passed, 0 failed** (couvre la promotion `shared_code`).
- `check_scope` = **ISOLATED** (classifier) → **promu manuellement SHARED_CODE** :
  `sessions.py` est le router principal monté dans `main.py` via l'import groupé
  `from app.routers import (…)` que le classifier ne reconnaît pas (même angle mort
  que les templates). Broad sweeps élargis en conséquence.
- `check_ruff_budget` : **543 ≤ 548** ✅ · `check_spec_protocol` : ✅.

---

## 6. Invariants

- **Aucune injection `value=`** — placeholders purement visuels ; set vide reste `value=""`.
- **Tap target WCAG 2.5.5** (`min-height:44px`) et **anti-zoom iOS** (`font-size:16px`
  input) **intacts** — la règle mobile ne touche que `::placeholder`.
- **Aucun** changement d'overload engine / historique / substitution / delta / hints.
- **Aucun** modèle / migration / schema / Body Intelligence / substitution graph / JS.
- **Aucun** span unité (Option C différée).
- Portée placeholder inchangée : ligne active de la carte active uniquement.

---

## 7. Limites

- La lisibilité mobile est réglée par **compaction string + réduction typo**, pas par
  une refonte structurelle (unité séparée = Option C, différée).
- Le breakpoint est fixé à **380 px** (cohérent avec l'existant) ; les écrans
  360 px bénéficient de la même règle (max-width englobe 360). 390 px+ gardent la
  typo normale (le placeholder tient déjà).
- Le classifier scope-guard sous-détecte l'import groupé du router → promotion
  manuelle (angle mort connu, non bloquant : la CI réelle reste la source de vérité).

---

## 8. Consignes dogfood de demain matin

1. **Séance sur mobile étroit** (≤ 380 px, ou DevTools iPhone SE 375 px) : ouvrir une
   session in-progress avec historique → vérifier que le placeholder cible du 1er set
   actif affiche `102.5` / `6-10` (sans `≈`) et **tient dans la case** sans déborder.
2. **Confirmer que rien n'est prérempli** : les inputs doivent rester **vides** (texte
   grisé = placeholder, pas une valeur). Taper puis effacer → le placeholder revient.
3. **Vérifier le tap** : taper dans le champ ne doit **pas** déclencher de zoom iOS, et
   la zone tactile reste confortable (≥ 44 px).
4. **Lisibilité** : le placeholder est-il désormais assez discret sans être illisible ?
   Si trop petit sur ton device, noter la largeur exacte pour un ajustement `font-size`.
5. **Signal suggestion** : la valeur nue `102.5` se lit-elle bien comme « suggestion »
   (grisée) et non comme une saisie ? Si ambiguë, envisager Option C (unité séparée)
   ou une microcopy, en sprint dédié.

---

## 9. Next step roadmap

- **Cycle Sx_DOGFOOD_01 complet** : audit → `.1` fix source → `.2` vérif consommateurs
  → **`.3` mobile placeholder** (ce sprint). Dernier volet du cycle.
- **Pistes ouvertes** (aucune ouverte sans GO) : `Sb_UI_06.4`, reprise **Body
  Intelligence**, `Sb_32.4`, Option C (unité séparée) en sprint UI dédié.
- **Deferred** : release tag, deploy, smokes UI auth prod.

---

## Verdict

**Verdict :** 🟢 **Sb_DOGFOOD_01.3 mobile placeholder proportion — DELIVERED, pending GO commit + CI + human review.**

Les placeholders cible chiffrés sont **compactés** (`102.5` / `6-10`, sans `≈`) et
leur typo est **réduite sur mobile étroit** via une règle `::placeholder` ciblée
`@media (max-width: 380px)` — sans toucher au tap target, à l'anti-zoom iOS, à la
structure HTML, ni au moindre `value=`. Formatter (string de présentation) + CSS
uniquement ; aucun engine / historique / substitution / modèle / migration / JS /
Body Intelligence. 23 tests (14 mis à jour + 9 nouveaux) ; broad sweeps 310 + 173
verts ; ruff 543 ≤ 548 ; spec protocol vert. Dernier volet du cycle Sx_DOGFOOD_01.
