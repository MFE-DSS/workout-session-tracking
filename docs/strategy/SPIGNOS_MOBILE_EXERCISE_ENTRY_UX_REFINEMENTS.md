# SPIGNOS Mobile Exercise Entry UX — Refinements Spec (Sx_02.1)

**Sprint:** Sx_02_1_mobile_exercise_entry_ux_refinements
**Date:** 2026-04-14
**Status:** Spec ready, pending build (Sb_02.1)
**Relation:** Raffinement de `SPIGNOS_MOBILE_EXERCISE_ENTRY_UX.md` (Sx_02 — deja built sous Sb_02)
**Prerequisite:** Sx_01 decisions (feedback avance) integrees comme hypothese

---

## 1. Contexte

Le spec Sx_02 historique (`docs/strategy/SPIGNOS_MOBILE_EXERCISE_ENTRY_UX.md`) a ete **largement build** sous Sb_02. Le code actuel contient deja :

- `<details>` par carte exercice avec `{% if is_active %}open{% endif %}`
- Logique `active_exercise_id` dans `app/routers/sessions.py:242-256`
- Redirect post-save vers `?active={next_id}#exercise-{next_id}` (ligne 427)
- Summary compact (code + name + progress + recap) dans `<summary class="exercise-card__compact">`
- Session feedback positionne en bas (apres la boucle d'exercices)
- Jump bar sticky avec etats `done` et `partial`
- Ajustement Sx_01 : `execution_quality` et `reps_target` non rendus dans le formulaire par defaut

Le flux focus-exercice est operationnel. Ce qui reste a travailler est **du polish structurel** sur trois gaps observables : jump bar incomplete, CTA exercice ambigu, CTA exercice peu accessible au pouce en mobile.

---

## 2. Probleme

Trois frictions residuelles sur le flux mobile existant :

1. **Jump bar** — ne distingue que `done` et `partial`. `active` et `future` sont indifferencies. L'utilisateur n'a pas une lecture immediate de "ou j'en suis / ou je vais".
2. **CTA exercice** — le bouton "Enregistrer E1" n'indique pas que la soumission enchaine sur l'exercice suivant. Le user ne sait pas qu'il va etre emmene ailleurs.
3. **CTA accessibilite** — le bouton est en bas du formulaire. Avec 4-5 work sets + muscle_sensation deplie + note, le bouton sort du viewport mobile. Le user doit scroller pour valider.

---

## 3. Objectif

Transformer la jump bar en rail de progression lisible d'un coup d'oeil, clarifier la CTA de validation par contexte (intermediaire / dernier / deja complete), et reduire la friction de validation mobile sans introduire de JS lourd ni rompre la grammaire SSR.

---

## 4. Etat actuel (post Sx_01 + Sb_02)

### Feedback visible par defaut

| Niveau | Champ | Etat |
|--------|-------|------|
| Set | weight_kg | Visible |
| Set | reps | Visible |
| Set | completed | Visible |
| Set | execution_quality | Cache (Sx_01) |
| Set | reps_target | Cache (Sx_01) |
| Exercice | success_score | **Non rendu** dans le form — seulement affiche en recap (voir observation §8) |
| Exercice | muscle_sensation | Visible dans `<details>` optionnel |
| Exercice | free_note | Visible |

### Etats de carte exercice actuels

- `exercise-card--done` — all work sets completed
- (implicite) `partial` — au moins 1 work set fait, pas tous
- (implicite) `future` — aucun set fait et exercice non actif
- (implicite) `active` — carte ouverte (`open` attribute)

Aucune classe CSS explicite pour `active` ni `future`. L'etat `active` est exprime uniquement par le fait que le `<details>` est ouvert.

### Jump bar actuelle

```html
<a class="ex-jump__item
         {% if t > 0 and d == t %}ex-jump__item--done
         {% elif d > 0 %}ex-jump__item--partial{% endif %}">
```

Pas de classe pour `active` ni pour `future`.

### CTA actuel

```html
<button type="submit" class="btn btn--primary">
  Enregistrer {{ se.exercise_code_snapshot }}
</button>
```

Libelle fixe "Enregistrer E1" quel que soit le contexte (intermediaire, dernier, reedition d'un exercice deja fait).

---

## 5. Gaps reels a traiter

### Gap 1 — Jump bar states incomplets

**Constat :** la jump bar ne distingue que `done` et `partial`. Pas de distinction visuelle `active` (ou l'utilisateur est) ni `future` (les exercices a venir).

**Objectif :** 4 etats lisibles d'un coup d'oeil.

### Gap 2 — CTA de save trop implicite

**Constat :** "Enregistrer E1" ne dit pas que la soumission enchaine sur E2. User perdu : "est-ce que je reste sur E1 apres enregistrement ?".

**Objectif :** libelle contextuel qui annonce la transition.

### Gap 3 — CTA trop bas en mobile

**Constat :** le bouton peut sortir du viewport. L'utilisateur doit scroller verticalement pour valider apres avoir rempli ses sets.

**Objectif :** reduire la friction de validation sans introduire de JS lourd ni d'effet "app native simulee".

---

## 6. Decisions UX recommandees

### Decision 1 — Jump bar : 4 etats visuels explicites

**Regles d'attribution** (dans `session_detail.html`, calculees server-side) :

```
pour chaque session_exercise se:
  d, t = stats.per_exercise[se.id]
  is_active = (active_exercise_id == se.id)

  si is_active:                     etat = "active"
  sinon si t > 0 et d == t:         etat = "done"
  sinon si d > 0:                   etat = "partial"
  sinon:                            etat = "future"
```

**Priorite :** `active` ecrase `done`/`partial`/`future`. Un exercice actif reste visuellement "ici vous etes" meme s'il est deja complete (cas reouverture).

**Rendu visuel cible** — coherent avec le design system (couleurs semantiques existantes dans `app.css`) :

| Etat | Classe CSS | Bordure | Fond | Typo | Indicateur |
|------|-----------|---------|------|------|-----------|
| `future` | `ex-jump__item--future` | `var(--border)` | `var(--surface)` | `var(--fg-dim)` | Aucun |
| `active` | `ex-jump__item--active` | `var(--accent)` | `var(--accent-soft)` | `var(--accent)` | Dot gauche ou underline (a choisir au build) |
| `partial` | `ex-jump__item--partial` | `var(--warn)` | `var(--surface)` | defaut | Icone "en cours" implicite via couleur |
| `done` | `ex-jump__item--done` | `var(--ok)` | `var(--ok-soft)` | defaut | Implicite via fond/bordure |

**`future` remplace l'etat "neutre" implicite actuel** en lui donnant un nom. Cela force la hierarchie visuelle : future < partial < done, et active est transverse.

**Contrainte non negociable :** aucun JS. Le calcul est dans le template Jinja ou dans le routeur. Pas de data-attribute mute par JS.

**Contrainte DA :** rester sobre. Pas de badges, pas d'icones nouvelles. Couleur + bordure suffisent. Coherent avec le cockpit minimaliste de SPIGNOS (S2 dashboard, physique page).

### Decision 2 — CTA de save : libelle contextuel par position

**Regle de libelle** — calcule cote template via Jinja :

```
si se est le dernier exercice ordonne:
  libelle = "Enregistrer et aller au bilan"
sinon si se est deja done (tous work sets completes) ET pas la derniere position:
  libelle = "Enregistrer et passer au suivant"
sinon:
  libelle = "Enregistrer et passer a {next_code}"
```

Exemples concrets :
- E1 intermediaire : `Enregistrer et passer a E2`
- E6 avant-dernier : `Enregistrer et passer a E7`
- E7 dernier : `Enregistrer et aller au bilan`
- E3 reouvert (deja done), autres a faire : `Enregistrer et passer au suivant`
- Session avec 1 seul exercice : `Enregistrer et aller au bilan`

**Pourquoi ce phrasing :**
- `Enregistrer et passer a X` est explicite sur les deux actions (save + navigate)
- `aller au bilan` evite "Terminer" qui reste reserve au bouton session-feedback (action irreversible de clore la seance)
- Nommer le prochain code (`E2`) est plus specifique que "suivant" — le user voit ou il va avant de taper

**Bouton session-feedback** (bilan de seance) inchange : `Enregistrer` + `Terminer la seance` / `Rouvrir` — ce flux est separe et fonctionne deja.

**Options ecartees :**
- Libelle uniforme "Enregistrer" : ne resoud pas l'ambiguite
- "Continuer" seul : perd la semantique "save"
- Ajouter une fleche → : gadget visuel non necessaire, le texte suffit

### Decision 3 — CTA accessibilite : footer d'exercice renforce + compact actions sticky

**Analyse des options :**

| Option | Pour | Contre | Compatibilite SPIGNOS |
|--------|------|--------|----------------------|
| **A. Sticky bar bas-ecran pure JS** | Toujours accessible | JS requis, effet "app native simulee", sort de la grammaire SSR | **Non** — rejete |
| **B. `position: sticky` CSS pur sur footer du form** | Zero JS, toujours accessible dans le scroll du `<details>` ouvert | Peut chevaucher le contenu si mal dimensionne | **Oui** — faisable |
| **C. Footer d'exercice visuellement renforce (pas sticky)** | Zero friction, pas d'overlap, cohere avec le design | User doit quand meme scroller si carte tres longue | **Oui** — simple |
| **D. Repositionner le bouton en haut de la carte** | Toujours visible des l'ouverture | Le user remplit ses sets APRES, pas AVANT — ordre inverse pas naturel | **Non** — anti-pattern ergonomique |
| **E. Rappel inline entre les sets** | Visible tot | Pollue le flux de remplissage des sets | **Non** |

**Recommandation : Option C + Option B ciblee.**

Approche en 2 couches coherente avec SPIGNOS :

**Couche 1 — Footer d'exercice renforce (toujours)** :
- La `div.card__actions` du form exercice devient un footer visuel avec :
  - Padding vertical plus important
  - Bordure superieure subtile (separateur visuel)
  - Fond legerement distinct du card (`--surface-elevated` ou equivalent)
  - Bouton plus haut (touch target confortable, min 44px de hauteur)
  - Libelle pleine largeur
- Le recap "N/total work sets completes" s'affiche a cote du bouton pour rassurer avant validation

**Couche 2 — Sticky CSS sur le footer UNIQUEMENT quand le `<details>` est actif (open)** :
- Via selecteur CSS : `details.exercise-card[open] .card__actions { position: sticky; bottom: 0; }`
- Background opaque pour ne pas laisser transparaitre le contenu en dessous
- Padding et marges ajustes pour eviter tout chevauchement avec le dernier champ
- **Zero JS** — c'est du CSS natif
- L'effet ne s'applique que sur la carte ouverte (une seule a la fois par defaut) → pas de conflit entre 7 footers sticky

**Garde-fous pour le build :**
- Le sticky doit rester compatible avec le clavier virtuel mobile (ne pas masquer le champ actif)
- Tester sur iOS Safari (connu pour `position: sticky` capricieux dans les conteneurs scrollables)
- Si Safari iOS pose probleme dans un `<details>`, tomber en mode non-sticky sans JS (le footer renforce de la couche 1 suffit seul)
- Pas d'overlay, pas de shadow excessif, pas d'animation

**Pourquoi pas d'option pure sticky footer global :**
Un footer sticky global (qui persiste quand le user switch de carte) introduirait :
- Un etat "quelle carte je valide" ambigue
- Une necessite de JS pour pointer le bon form
- Une rupture avec le modele "chaque `<details>` a son form"

Rester dans la logique "chaque carte est autonome, son CTA vit dans sa carte" preserve la grammaire SSR existante.

---

## 7. Implications template / CSS / router

### Template `app/templates/session_detail.html`

**Changements :**

1. **Jump bar** — ajouter le calcul d'etat et les classes CSS :
   ```
   set state = "done" si ...
              "partial" si ...
              "future" sinon
   si is_active: state = "active"
   ```
   Et appliquer `ex-jump__item--{state}` sur chaque item.

2. **CTA exercice** — calculer `next_code` et `is_last` dans le template ou dans le routeur (recommande : routeur, pour garder le template propre). Libelle conditionnel :
   ```
   {% if is_last %}
     Enregistrer et aller au bilan
   {% else %}
     Enregistrer et passer a {{ next_code }}
   {% endif %}
   ```

3. **Footer renforce** — ajouter a `card__actions` dans le form exercice :
   - Recap compact "N / M work sets" a gauche du bouton
   - Structure pleine largeur coherente

### CSS `app/static/css/app.css`

**Ajouts :**

- `.ex-jump__item--future` : bordure `var(--border)`, typo `var(--fg-dim)` (explicite l'etat qui etait implicite)
- `.ex-jump__item--active` : bordure `var(--accent)`, fond `var(--accent-soft)`, typo `var(--accent)`
- `details.exercise-card[open] .card__actions` — sticky footer rules
- `.card__actions--exercise` (nouveau modifier) — styles du footer renforce (padding, bordure sup, recap inline)

**Ne pas toucher :**
- Classes `done` et `partial` existantes — garder la palette
- Structure de `.ex-jump` (flex, overflow-x) — inchangee
- Composants set-row — inchanges

### Routeur `app/routers/sessions.py`

**Changements :**

1. `session_detail` (GET) — enrichir le contexte template avec :
   - `next_code_by_exercise: dict[int, str | None]` — pour chaque session_exercise.id, le code du suivant (ou `None` si dernier)
   - Alternative plus simple : le template peut le calculer via la liste `session.session_exercises` qui est deja ordonnee

2. `update_exercise_card` (POST) — **inchange**. Le redirect vers `?active=next_id` est deja en place.

3. Aucun changement de modele, aucune migration.

---

## 8. Observations transverses (pas dans le perimetre mais a noter)

**A. `success_score` n'est plus rendu dans le formulaire exercice.**

Le template actuel n'affiche plus le `segmented` pour `success_score`. Seul le recap "score N" s'affiche en lecture (lignes 91-92 de `session_detail.html`, et dans `exercise_history.html`). Cela contredit la decision 2 de Sx_01 qui disait "`success_score` reste saisi manuellement, signal primaire, visible".

Deux lectures possibles :
- **Intentionnel mais non documente** : l'equipe a retire le champ du form mais garde la colonne en DB pour ne pas casser les consumers. Dans ce cas, Sx_01 doit etre amende (mentionner que success_score est "preserve en DB mais n'est plus saisi").
- **Oubli / regression** : le champ devrait etre reinjecte comme input.

**Ce n'est PAS le perimetre de Sx_02.1.** C'est un point a arbitrer dans Sx_01 ou dans un ticket separe. Sx_02.1 part de l'hypothese "visible par defaut : weight, reps, completed, muscle_sensation" (et success_score si re-introduit, sans impact sur ce spec).

**B. `muscle_sensation` est dans un `<details>` optionnel.**

Dans `session_detail.html:253-262`, `muscle_sensation` est deja wrappe dans un `<details>` avec label "Sensation musculaire (optionnel)". C'est un leger ecart vs Sx_01 decision 3 ("visible et saisi") mais coherent avec l'ergonomie : 1 tap pour deplier, 1 tap pour choisir. A documenter dans Sx_01 si desire mais hors perimetre Sx_02.1.

---

## 9. Risques

| Risque | Probabilite | Impact | Mitigation |
|--------|------------|--------|------------|
| Sticky footer chevauche le clavier virtuel iOS | Moyenne | Moyen | Tester iOS Safari, fallback non-sticky si probleme avere (footer renforce suffit) |
| 4 etats de jump bar saturent visuellement | Faible | Faible | Couleurs deja dans le design system, pas de nouvelle palette. Contraste teste sur mobile. |
| Libelle CTA long deborde sur petits ecrans | Moyenne | Faible | "Enregistrer et passer a E2" tient largement. Pour "Enregistrer et aller au bilan", tester sur 320px. Si trop long, tronquer en "Enregistrer → bilan". |
| `position: sticky` dans `<details>` capricieux Safari | Moyenne | Moyen | Fallback gracieux (footer renforce non-sticky). Documenter dans le build. |
| Ecart avec decisions Sx_01 sur success_score | Deja present | Traite hors perimetre | Documenter l'observation, ne pas reouvrir Sx_01 dans ce sprint |

---

## 10. Acceptance criteria — Spec (Sx_02.1)

- [x] Gaps Jump bar, CTA wording, CTA accessibility identifies et formalises
- [x] 4 etats de jump bar definis avec regles d'attribution + classes CSS + couleurs du design system
- [x] Logique de libelle CTA contextuelle definie avec exemples
- [x] Strategie CTA accessibility arbitree (footer renforce + sticky CSS cible)
- [x] Ajustement Sx_01 (execution_quality/reps_target caches) integre comme hypothese
- [x] Implications template / CSS / router cartographiees
- [x] Zero JS confirme
- [x] Observations transverses documentees sans polluer le perimetre

## 11. Acceptance criteria — Build (Sb_02.1)

- [ ] Jump bar affiche 4 etats visuellement distincts : future, active, partial, done
- [ ] L'exercice actif est toujours visible comme "active" dans la jump bar, meme s'il est done
- [ ] Le CTA d'un exercice intermediaire affiche le code du suivant (ex: "Enregistrer et passer a E2")
- [ ] Le CTA du dernier exercice affiche "Enregistrer et aller au bilan"
- [ ] Le CTA d'un exercice deja done mais pas dernier affiche "Enregistrer et passer au suivant"
- [ ] Le CTA session-feedback reste "Enregistrer" + "Terminer la seance" (inchange)
- [ ] Le footer d'exercice est visuellement renforce (padding, bordure, recap work sets a cote du bouton)
- [ ] Le footer est sticky via CSS sur la carte ouverte
- [ ] Sticky footer ne chevauche pas le clavier virtuel (test iOS + Android)
- [ ] Fallback gracieux si sticky CSS pose probleme sur Safari iOS (footer renforce seul suffit)
- [ ] Aucun JS ajoute
- [ ] Aucune regression sur les tests existants (`test_session_flow.py`, `test_mobile_polish.py`, `test_past_session_readability.py`)
- [ ] Aucun changement de modele ni de migration

---

## 12. Lotissement recommande

**Un seul sprint de build : Sb_02.1.**

Pas de decoupage. Les 3 gaps sont petits, coherents, et partagent les memes fichiers (`session_detail.html`, `app.css`, optionnellement `sessions.py`). Les traiter ensemble evite 3 allers-retours.

**Perimetre strict :**
- Jump bar : +2 classes CSS + calcul d'etat dans le template
- CTA libelle : logique conditionnelle Jinja
- Footer : CSS + legere restructuration de `card__actions`

**Hors perimetre Sb_02.1 :**
- Toute refonte du flow
- Toute modification de modele
- Tout JS
- Ajustement `success_score` / `muscle_sensation` (traites ailleurs)
- Substitution UX (reste Sx_03)

---

## 13. Marquage du spec Sx_02 historique

Le spec `SPIGNOS_MOBILE_EXERCISE_ENTRY_UX.md` doit etre marque :

**Statut recommande : `Built — refinements tracked in Sx_02.1`**

Ajouter un entete au document :

```
**Statut : BUILT (Sb_02).**
**Refinements UX : voir SPIGNOS_MOBILE_EXERCISE_ENTRY_UX_REFINEMENTS.md (Sx_02.1).**
```

Ne pas ecraser le contenu historique — il documente la decision originale et reste une reference pour comprendre pourquoi le flux focus-exercice existe.
