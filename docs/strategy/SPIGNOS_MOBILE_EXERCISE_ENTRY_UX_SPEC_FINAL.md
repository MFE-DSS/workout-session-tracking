# SPIGNOS Mobile Exercise Entry UX — Final Spec

**Sprint:** Sx_02_mobile_exercise_entry_ux_spec (FINAL)
**Date:** 2026-04-14
**Status:** Final, aligne avec Sx_01 FINAL et la realite du code post Sb_02 + Sb_02.1
**Relation:** Consolide `SPIGNOS_MOBILE_EXERCISE_ENTRY_UX.md` (Sx_02 original BUILT sous Sb_02), `SPIGNOS_MOBILE_EXERCISE_ENTRY_UX_REFINEMENTS.md` (Sx_02.1 BUILT sous Sb_02.1), et le modele de signal Sx_01 FINAL.
**Builds de reference :** Sb_02 (structure focus-exercice) + Sb_02.1 (jump bar 4 etats, CTA contextuel, footer sticky)
**Next :** Sx_02 UX spec FINAL est le cahier des charges UI pour Sx_03 (substitution), ne doit PAS necessiter de rework du composant exercice pour Sx_03.

---

## 1. Contexte

Le flow mobile de session est en production apres :
- **Sb_02** : `<details>` par carte, `active_exercise_id`, redirect `?active={next_id}`, summary compact, session feedback en bas
- **Sb_02.1** : jump bar 4 etats (future/active/partial/done), CTA contextuel (`Enregistrer et passer a E2`), footer sticky CSS sur carte ouverte
- **Sb_01 / Sx_01 FINAL** : `success_score` derive, `execution_quality` + `reps_target` retires de l'UI, `muscle_sensation` dans un `<details>` optionnel

Ce document produit le **cahier des charges UI definitif** du bloc exercice mobile, consolide et fige. Il sert de :
- reference pour tout futur raffinement UX
- contrat d'interface pour Sx_03 (substitution locale)
- protection contre le rework

Aucun build n'est demande par ce spec. Tout ce qui est decrit est soit deja en prod, soit documente comme etat cible stable.

---

## 2. Audit du flow reel actuel

### 2.1 Routes FastAPI (app/routers/sessions.py)

| Route | Methode | Role |
|-------|---------|------|
| `POST /sessions` | Create | Instancie une session depuis un template (`instantiate_session`) |
| `GET /sessions/{id}` | Read editable | Si `status=completed` redirige vers `/done`. Sinon rend `session_detail.html` avec tout le contexte |
| `GET /sessions/{id}/done` | Read terminal | Rend `session_done.html` (Sb_R3). Redirige vers `/sessions/{id}` si status `in_progress` |
| `POST /sessions/{id}` | Update session-level | Save concentration / global_state / bodyweight / free_note. `action=end` bascule `completed` + redirige vers `/done`. `action=reopen` re-ouvre l'edition |
| `POST /sessions/{id}/exercises/{seId}` | Update exercise card | Parse sets (weight, reps, completed) + muscle_sensation + free_note + substituted_name. Derive success_score. Redirige vers `?active={next_id}#exercise-{next_id}` ou `#session-feedback` si dernier |

### 2.2 Contexte template (injecte par `session_detail` GET)

| Cle | Type | Source | Usage UI |
|-----|------|--------|----------|
| `session` | WorkoutSession | DB + snapshots | Header, meta |
| `stats.per_exercise` | dict[int, (done, total)] | `_session_stats()` | Jump bar progress + CTA recap |
| `stats.done` / `stats.total` | int | idem | Header progress global |
| `last_time` | dict par code | `last_time_by_exercise_code` | Bloc "Derniere fois" |
| `hints` | dict par code | `compute_progression_hint` | Bloc "Repere" |
| `exercise_summaries` | dict par id | `summarise_current_exercise` | Recap inline done-summary |
| `deltas` | dict par code | `compute_delta` + `format_delta` | Bloc "Delta" |
| `active_exercise_id` | int / None | Query `?active=` ou 1er non-complet | Ouverture `<details open>` |
| `substitution_data` | dict par id | `get_substitutes` + `can_substitute` | Picker substitution |
| `jump_states` | dict id→state | Sb_02.1 calcule future/active/partial/done | Classes jump bar |
| `next_code_by_exercise` | dict id→str/None | Sb_02.1 calcule next code | Libelle CTA contextuel |

### 2.3 Etat HTML actuel (session_detail.html, 411 lignes)

Structure par element (verifie par lecture) :
- Header session (titre, meta, progress global, note completed)
- Jump bar sticky horizontale (7 items exercices + FB)
- Boucle exercices : pour chacun, un `<details class="card exercise-card" id="exercise-{id}">`
  - `<summary>` : code + name (avec substituted fallback) + progress + recap inline si done > 0
  - Body : lien historique, set_scheme, done-summary si completed, substitute-picker conditionnel, last-time, delta, hint, set list warmup + set list work, muscle_sensation dans `<details>`, free_note, footer CTA contextuel
- Formulaire session-feedback (concentration + global_state + bodyweight + free_note + boutons Enregistrer / Terminer / Rouvrir)
- Aside method-reminder (regles techniques, collapsible)

### 2.4 CSS references (app.css)

Classes stables deployees :
- `.ex-jump`, `.ex-jump__item--future/active/partial/done/feedback` (Sb_02.1)
- `.exercise-card`, `.exercise-card--done` (Sb_02), `.exercise-card__compact`, `.exercise-card__recap`
- `.set-list`, `.set-row`, `.set-row--warmup`, `.set-row--work`, `.set-row__inputs`, `.set-row__done`
- `.card__actions--exercise`, `.card__actions__recap` (Sb_02.1)
- `details.exercise-card[open] .card__actions--exercise { position: sticky; }` (Sb_02.1)
- `.substitute-picker`, `.substitute-badge`

Ce CSS constitue le **design system du bloc exercice**. Toute evolution future doit s'y inscrire, pas le contourner.

---

## 3. Flow cible mobile d'une seance (synthese)

```
Entree session (1er GET /sessions/{id})
  ↓
  Jump bar rail : [E1:active] [E2:future] [E3:future] ... [FB:future]
  E1 card OPEN (others collapsed) — autofocus implicite via <details open>
  ↓
User saisit weight+reps+completed sur les sets de E1
User clique "Enregistrer et passer a E2"
  ↓
POST update_exercise_card
  ↓ server : parse sets, derive success_score via compute_success_score
  ↓ 303 → /sessions/{id}?active={E2.id}#exercise-{E2.id}
  ↓
GET /sessions/{id}?active={E2.id}
  ↓
  Jump bar : [E1:done] [E2:active] [E3:future] ...
  E2 card OPEN, E1 collapsed avec recap "60 / 60 / 60 kg · 10 / 10 / 10 reps"
  Scroll automatique vers E2 via #exercise-{id} anchor
  ↓
... repeter jusqu'a E7 ...
  ↓
User sur E7 (dernier), clique "Enregistrer et terminer"
  ↓
POST update_exercise_card → redirect vers #session-feedback (pas de next_se)
  ↓
User sur le bloc feedback session, saisit concentration/global_state/bodyweight/free_note
User clique "Terminer la seance"
  ↓
POST update_session action=end
  ↓ server : status=completed, ended_at=now
  ↓ 303 → /sessions/{id}/done
  ↓
GET /sessions/{id}/done (terminal state Sb_R3)
```

### Chemins alternatifs

- **Retour arriere depuis E3 vers E1** : user scrolle ou clique sur E1 dans la jump bar. E1 reste techniquement "done" (dans `jump_states`) mais un clic sur son `<details>` l'ouvre pour edition. Save de E1 re-ecrase son `success_score` et redirige vers le NEXT positionnellement (E2), meme s'il est deja done. Comportement accepte.

- **Reouverture d'une seance terminee** : depuis `/done`, bouton "Rouvrir pour editer" → POST action=reopen → status=in_progress → redirect `/sessions/{id}` → flow normal d'edition reprend.

- **Acces direct a `/sessions/{id}` sur seance completee** : redirect auto vers `/done` (Sb_R3 decision). Impossible de voir la page editable sans reouvrir explicitement.

- **Skip d'un exercice** : user ouvre E5 avant de finir E3. E3 reste `partial` dans jump_states (ou `future` s'il n'a rien coche). Pas de blocage. Le user est responsable.

---

## 4. Composant "bloc exercice" cible — cahier des charges UI

### 4.1 Header compact (toujours visible — `<summary>`)

**Contenu autorise :**
- Code (E1, E2...) — police mono, badge accent-soft
- Nom affichage : `substituted_name or exercise_name_snapshot`
- Progress `{done}/{total}` work sets
- **Recap inline** (si `done > 0`) : `weights_str kg · reps_str reps` — police dim, ligne unique

**Interdit :**
- Aucun bouton interactif (sauf le chevron natif du `<details>`)
- Aucun badge de success_score (il est derive apres save, pas prescriptif)
- Aucune icone decorative non-semantique
- Aucune animation

**Hauteur cible :** une ligne logique (wrap acceptable si nom long). Aucun scroll interne.

### 4.2 Body visible quand `<details open>`

**Ordre vertical fige :**

1. **Lien historique discret** : `Voir historique E2 →` — font-size 12px, `var(--fg-dim)`
2. **Set scheme du catalogue** (si present) : `3x 8-12` — texte simple, pas de box
3. **Done-summary** (uniquement si `session.status == 'completed'`) — bloc recap score/values
4. **Substitute picker** ou **substitute badge** (selon can_substitute / substituted_name) — zone reserve pour Sx_03
5. **Last-time** : `Derniere fois · il y a 3j · 60 kg · 10 reps` — ou "Aucune seance precedente"
6. **Delta** (conditionnel) : `+2.5 kg · +1 rep · score en hausse`
7. **Hint** (conditionnel) : `viser 12 reps avant d'augmenter la charge`
8. **Set list — Echauffement** (si warmup_sets) : sous-titre `Echauffement` + `<ul class="set-list">` avec set-row
9. **Set list — Travail** : sous-titre `Travail` + `<ul class="set-list">` avec set-row
10. **Zone "Ressenti exercice" — optionnel repli** :
    - `<details>` ferme par defaut, summary "Sensation musculaire (optionnel)"
    - Segmented `strong / partial / weak`
11. **Note libre** : `<textarea maxlength=140 rows=1>` avec label "Note (optionnel)"
12. **Footer d'action** (`.card__actions--exercise` sticky) :
    - Recap `Work : N/M` a gauche
    - Bouton primary a droite avec libelle contextuel (`Enregistrer et passer a E2` / `Enregistrer et terminer`)

**Interdit :**
- Aucun radio `success_score` (derive cote serveur)
- Aucun input `execution_quality` ou `reps_target` par set
- Aucun JS pour synchroniser des champs
- Aucun overlay, popover, modale

### 4.3 Set row (structure verticale compacte)

Chaque work set est **une ligne** avec 4 zones inline :

| Zone | Contenu | Input type |
|------|---------|-----------|
| Label | `Serie #N` + optionnel tag technique (RP, DS) | Texte |
| Weight | `kg` avec step 0.5, inputmode decimal | `<input type=number>` |
| Reps | placeholder "reps", inputmode numeric | `<input type=number>` |
| Done checkbox | Label "Fait" | `<input type=checkbox>` |

Warmup row suit la meme structure avec `Echauf.` au lieu de `Serie` et opacite 0.7.

**Regle d'alignement :** les 3 inputs (weight / reps / done) sont sur UNE SEULE LIGNE sur mobile. Si l'ecran est trop etroit (< 320px), la checkbox peut wrap sous les inputs — geree par le flex-wrap natif.

**Interdit :**
- Aucun champ secondaire par set (execution_quality / reps_target)
- Aucun bouton "ajouter set" (les sets sont prescrits par le catalogue au create)
- Aucun slider, stepper complexe — inputs number natifs uniquement

### 4.4 Emplacement des signaux Sx_01

| Signal | Ou ? | Visibilite par defaut |
|--------|------|----------------------|
| `weight_kg` (set) | Set row | **Visible** |
| `reps` (set) | Set row | **Visible** |
| `completed` (set) | Set row (checkbox "Fait") | **Visible** |
| `success_score` (exercice) | **Nowhere in input UI** (derive) | Visible seulement en recap post-save |
| `muscle_sensation` (exercice) | `<details>Sensation musculaire (optionnel)</details>` entre set list et free_note | **Collapsed** |
| `free_note` (exercice) | Textarea visible | **Visible** mais vide par defaut |
| `execution_quality` (set) | **Nowhere** | **Absent UI** |
| `reps_target` (set) | **Nowhere** | **Absent UI** |
| `substituted_name` (exercice) | Substitute picker conditionnel (top du body) | **Visible si sub disponibles ET aucun set complete** |
| `concentration` (session) | Bloc session-feedback (bas de page) | **Visible** |
| `global_state` (session) | Bloc session-feedback | **Visible** |
| `bodyweight_kg` (session) | Bloc session-feedback | **Visible** |

---

## 5. Regles de densite mobile

### Usage a une main

- Toutes les CTA primaires accessibles sans repositionner la main (bas d'ecran)
- Pouce droit : target min 44x44px sur tous les boutons / checkboxes
- Bouton footer sticky sur carte ouverte (Sb_02.1) — reachability garantie meme sur cartes longues

### Lisibilite rapide

- Couleur semantique :
  - `done` = ok vert (`var(--ok)`)
  - `partial` = warn (`var(--warn)`)
  - `active` = accent (`var(--accent)`)
  - `future` = dim neutre
- Police mono pour codes, weights, reps (lecture rapide)
- Pas de texte > 2 lignes dans le header compact

### Peu de texte

- Libelles d'input courts (`kg`, `reps`, `Fait`)
- Helpers minimaux sous les groupes session-feedback (ex: "Etais-tu focalise ?")
- Zero paragraphe explicatif dans le flow normal
- Regles techniques deportees dans `<aside class="method-reminder">` optionnelle

### CTA clairs

- Un seul bouton primary par carte (pas de "Save" + "Save and next" en parallele)
- Libelle inclut la consequence (`et passer a E2`, `et terminer`)
- Pas de bouton "Annuler" — le user peut toujours ne pas cliquer

### Pas de double validation

- Le save exercice fait en un POST : parse sets + muscle_sensation + free_note + derivation success_score. Pas de save set-level independant.
- Le save session feedback idem : tout en un POST avec optionnellement `action=end`.
- Zero patch partiel, zero JS de debounce.

### Pas d'empilement excessif

- Un seul `<details>` de profondeur 2 toleree (ex: carte exercice → `<details>` muscle_sensation, ou carte exercice → `<details>` substitute-picker). Pas de profondeur 3.
- Les blocs conditionnels (delta, hint, last-time) sont inline, pas dans des sous-containers.

---

## 6. Etats UX explicites

### Etats de carte exercice (compose de 2 dimensions)

**Dimension A — progress state** (dans `jump_states` + classe `exercise-card--{state}`) :

| State | Regle | Visuel jump bar | Visuel card |
|-------|-------|----------------|-------------|
| `future` | done == 0 ET non active | border `--border`, typo `--fg-dim` | defaut sobre |
| `partial` | 0 < done < total ET non active | border `--warn` | defaut |
| `done` | total > 0 ET done == total | border `--ok`, fond `--ok-soft` | `.exercise-card--done` (border verte, code vert) |
| `active` | se.id == active_exercise_id (ecrase les autres) | border `--accent`, fond `--accent-soft`, box-shadow, aria-current=step | rendu `<details open>` |

**Dimension B — open/collapsed state** (native HTML `<details>`) :

| State | Regle | Visuel |
|-------|-------|--------|
| `expanded` | `<details open>` (auto sur active, manuel sinon) | Body visible, footer sticky actif |
| `collapsed` | `<details>` sans `open` | Seul le `<summary>` visible |

**Composition** : active + expanded sont couples par defaut (si active alors open). Mais le user peut manuellement open un card non-active (ex: revisiter E1 deja done). Pas de lock-in.

### Etat validation error

**Non gere en UI cote session** (pas de validation stricte cote forme). Les champs sont tous tolerants :
- weight/reps vides → NULL accepte
- success_score derivation echoue gracieusement → None ou 80 defaut
- muscle_sensation vide → NULL accepte
- substituted_name invalide → ignore cote server (filtering par `can_substitute`)

Philosophie : le flow ne bloque jamais. Le user peut sauvegarder une carte a moitie remplie. Les consumers tolerent les NULL.

### Etat session completed

Pas un etat de la page editable — c'est une **redirection** vers `/sessions/{id}/done`. Aucun affichage "edit mode on completed" n'est autorise. Reversible via `action=reopen`.

---

## 7. Transitions documentees

### 7.1 Save set/exercice

```
[User coche set 1 "Fait", saisit weight=60, reps=10]
[User clique "Enregistrer et passer a E2"]
  ↓
POST /sessions/{id}/exercises/{E1.id}
  ↓
Server :
  1. Ownership check (session appartient a user)
  2. Parse form : muscle_sensation, free_note, substituted_name (si can_substitute)
  3. Pour chaque set : parse weight, reps, completed
  4. compute_success_score(se, te) → derive success_score
  5. db.commit()
  6. Resolve next_se par position (ordonne)
  7. 303 → /sessions/{id}?active={next_se.id}#exercise-{next_se.id}
     OU → /sessions/{id}#session-feedback si pas de next
  ↓
GET redirect
  ↓
Page re-rendue avec nouveau active_exercise_id.
Scroll auto via fragment ancre #exercise-{id}.
```

### 7.2 Next exercise

Same POST response. Le browser scroll auto vers `#exercise-{id}` car le `<details>` cible est `open` → navigateur le ramene au viewport.

### 7.3 Retour arriere

- **Clic sur un item jump bar** (passe ou futur) : navigation fragment `#exercise-{id}`. N'ouvre PAS automatiquement le `<details>` si le card cible n'est pas `active`. Le user doit cliquer sur le `<summary>` pour l'ouvrir.
- **Alternative** : navigation directe vers `/sessions/{id}?active={targetId}`. Re-rend avec ce card ouvert. Les autres restent collapsed.

### 7.4 Reouverture d'un exercice done

- Click sur `<summary>` d'un card `done` → le `<details>` s'ouvre (comportement HTML natif)
- Tous les champs redeviennent editables (les valeurs existantes sont renseignees)
- Save recalcule success_score et redirige vers le NEXT POSITIONNEL (peut etre deja done)
- Pas de warning, pas de confirmation

### 7.5 Compatibilite future substitution locale (Sx_03)

Le flow de substitution est deja **partiellement en place** :
- Picker `<details class="substitute-picker">` en haut du body quand `can_substitute == True`
- Badge `.substitute-badge` affiche apres lock

**Ce qui reste stable pour Sx_03** :
- Position (top du body, entre set_scheme et last-time)
- Mecanisme (radio group `name="substituted_name"`, parse cote server avec verification `can_substitute`)
- Lock mechanism (apres 1er set complete, le picker disparait et le badge reste)

**Ce que Sx_03 peut raffiner sans toucher au composant exercice** :
- Source des substitutes (JSON vs canonical entity — cf. Sx_03.1)
- Ajout de metadata (raison, niveau d'equivalence)
- Amelioration du wording ("Machine indisponible ? Substituer →")
- Validation structurelle (FK)

**Ce que Sx_03 NE DOIT PAS refaire** :
- La structure de la carte exercice
- Le placement du picker
- Le mecanisme de lock
- Le rendu de `substituted_name` dans le `<summary>`

---

## 8. Integration stricte avec Sx_01

### Ce qui reste visible dans l'UI standard

- Set-level : weight, reps, completed (3 inputs × N sets)
- Exercise-level : free_note (textarea visible)
- Session-level : concentration, global_state, bodyweight, free_note (4 inputs en bas de page)

### Ce qui devient secondaire (visible dans `<details>` optionnel)

- muscle_sensation — dans `<details>Sensation musculaire (optionnel)</details>` au niveau exercice
- Regles techniques / method reminders — dans `<aside>` method-reminder avec `<details>` par regle

### Ce qui ne doit plus apparaitre

- Radio `success_score` (derive, pas saisi)
- Radio `execution_quality` par set (orphelin)
- Radio `reps_target` par set (orphelin)
- Tout champ qui duplique un autre (pas de "comment etait ce set ?" si on a deja `completed`)

### Separation stricte set-level / exercise-level / session-level

| Niveau | Sauvegarde | Scope | Exemples de champs |
|--------|-----------|-------|-------------------|
| Set | Dans le POST exercise card | Une serie | weight, reps, completed |
| Exercise | Dans le POST exercise card | Un exercice (groupe de sets) | muscle_sensation, free_note, substituted_name, success_score (derive) |
| Session | Dans le POST session (feedback) | Toute la seance | concentration, global_state, bodyweight, free_note session |

Aucun champ ne deborde d'un niveau a un autre. Les formulaires sont distincts et ne partagent pas d'inputs.

---

## 9. Wireframes textuels mobile-first

### 9.1 Page `/sessions/{id}` (in_progress)

```
┌────────────────────────────────────────┐
│ ← Accueil                              │
│ Push A — Pecs epaisseur + Delts...     │
│ Lundi · 18:45 · En cours               │
│ 4 / 20 work sets                       │
├────────────────────────────────────────┤
│ [E1:done] [E2:active] [E3] [E4] ... FB │  ← sticky jump bar
├────────────────────────────────────────┤
│ ▶ E1 Incline Smith Press    3/3        │  ← <summary> compact
│    60/60/60 kg · 10/10/10 reps         │
├────────────────────────────────────────┤
│ ▼ E2 Chest Press machine    0/3 ●      │  ← <summary> active (accent)
│                                        │
│    Voir historique E2 →                │
│    3x 8-12                             │
│                                        │
│    [Machine indisponible ? Substituer ▶]  ← substitute picker Sx_03
│                                        │
│    Derniere fois · il y a 3j           │
│    55/55/55 kg · 10/10/10 reps         │
│                                        │
│    Delta : +5 kg · score en hausse     │
│    Repere : viser 12 reps...           │
│                                        │
│    Travail                             │
│    ┌──────────────────────────────┐    │
│    │ Serie #1   [60] [  ] [✓Fait] │    │
│    │ Serie #2   [  ] [  ] [ Fait] │    │
│    │ Serie #3   [  ] [  ] [ Fait] │    │
│    └──────────────────────────────┘    │
│                                        │
│    ▶ Sensation musculaire (optionnel)  │  ← <details> collapsed
│                                        │
│    Note (optionnel) : [            ]   │
│                                        │
│   ┌──────────────────────────────────┐ │  ← sticky footer (CSS)
│   │ Work: 0/3  [Enregistrer ... E3] │ │
│   └──────────────────────────────────┘ │
├────────────────────────────────────────┤
│ ▶ E3 ...   0/3                         │
│ ... (collapsed)                        │
├────────────────────────────────────────┤
│ Bilan de la seance                     │
│ Concentration : [Focalise][Correct]... │
│ Energie : [En forme][Moyen][Fatigue]   │
│ Poids : [    ]                         │
│ Note : [                            ]  │
│ [Enregistrer] [Terminer la seance]     │
├────────────────────────────────────────┤
│ Rappel methode (collapsible)           │
└────────────────────────────────────────┘
```

### 9.2 Page `/sessions/{id}/done` (terminal)

```
┌────────────────────────────────────────┐
│ ✓ Seance terminee                      │
│ Push A — Pecs epaisseur + Delts...     │
│ Lun 14/04 18:45 → 20:02 · 1h 17m       │
├────────────────────────────────────────┤
│ Resume                                 │
│ Work sets : 18/20 (90%)                │
│ Substitutions : 1                      │
│ Bodyweight : 78,5 kg                   │
│ Concentration : high                   │
│ Etat : good                            │
├────────────────────────────────────────┤
│ Par exercice                           │
│ E1  Incline Smith Press   3/3   100    │
│ E2  → Dev. couche halt.   3/3    80    │  ← substituted
│ E3  Dips pectoraux        3/3   100    │
│ ...                                    │
├────────────────────────────────────────┤
│ [Voir la synthese →]  [Historique →]   │
│                                        │
│              [Rouvrir pour editer]     │  ← discrete
└────────────────────────────────────────┘
```

### 9.3 Etats de carte exercice — recap visuel

```
FUTURE (collapsed, non-active, non-entame) :
┌────────────────────────────────────────┐
│ ▶ E3 Dips pectoraux         0/3        │  ← dim neutre
└────────────────────────────────────────┘

PARTIAL (collapsed, quelques sets faits) :
┌────────────────────────────────────────┐
│ ▶ E3 Dips pectoraux         1/3        │  ← border warn
│    60 kg · 10 reps                     │
└────────────────────────────────────────┘

DONE (collapsed, tous sets faits) :
┌────────────────────────────────────────┐
│ ▶ E3 Dips pectoraux         3/3 ✓      │  ← border ok, fond ok-soft
│    60/60/60 kg · 10/10/10 reps         │
└────────────────────────────────────────┘

ACTIVE (open, courant) :
┌────────────────────────────────────────┐
│ ▼ E3 Dips pectoraux         2/3 ●      │  ← border accent, fond accent-soft
│ ... (body visible) ...                 │
│ [Work: 2/3 | Enregistrer et ... a E4] │  ← footer sticky
└────────────────────────────────────────┘
```

---

## 10. Cartographie des ecrans / etats / transitions

### Ecrans (routes)

1. `GET /` Home — entree
2. `GET /library` — choix template
3. `GET /library/{slug}` — detail template
4. `POST /sessions` — create session
5. **`GET /sessions/{id}` — session edit (cible de ce spec)**
6. **`GET /sessions/{id}/done` — session terminal (Sb_R3)**
7. `GET /history` — historique des sessions
8. `GET /exercise-history/{template_slug}/{code}` — historique par slot

### Etats session

- `in_progress` → editable via /sessions/{id}
- `completed` → terminal via /sessions/{id}/done (redirect auto)

### Transitions critiques

| From | Action | To | Server side |
|------|--------|-----|-------------|
| Editable (E1 active) | Save E1 | Editable (E2 active) | parse, compute success_score, redirect 303 |
| Editable (E7 active) | Save E7 | Editable (feedback focus) | redirect 303 → #session-feedback |
| Editable (feedback) | action=end | Terminal | status=completed, ended_at=now, redirect 303 /done |
| Editable (any) | action=reopen (depuis /done) | Editable | status=in_progress, ended_at=NULL, redirect 303 /sessions/{id} |
| Terminal | Click Rouvrir | Editable | idem above |
| Terminal | Click Voir synthese | /dashboard | navigation |
| Terminal | Click Historique | /history | navigation |
| GET /sessions/{id} avec status=completed | — | Terminal (redirect 303) | redirect auto |

---

## 11. Preparation terrain pour Sx_03

### Ou vivra le bouton "Substituer"

**Deja en place** — position fige :
- Dans le body du `<details>` exercice, apres le set_scheme et avant le last-time
- Picker `<details class="substitute-picker">` avec radio group `name="substituted_name"`
- Badge `.substitute-badge` si deja substitue (remplace le picker apres lock)

### Contraintes du composant exercice que Sx_03 ne doit PAS changer

1. **Position du picker** : top du body, au-dessus du last-time (actuel). Si Sx_03 veut le deplacer, ca necessite un re-design de la structure du body — a eviter.
2. **Mecanisme de lock** : `can_substitute(se)` check (false si au moins 1 work set `completed`). Sx_03 peut raffiner le critere (ex: locker aussi en cas de blessure) mais pas la signature.
3. **Rendu du nom dans le summary** : `{{ se.substituted_name or se.exercise_name_snapshot }}`. Sx_03 peut enrichir via `actual_exercise_name()` mais le template doit continuer a utiliser un fallback simple.
4. **Parsing cote server** : `form.get("substituted_name")` avec check `can_substitute`. Sx_03 peut ajouter `substitution_reason` mais doit garder le champ `substituted_name` comme canonique.
5. **Structure data injectee** : `substitution_data[se.id] = {substitutes: [...], can_substitute: bool}`. Sx_03 peut enrichir avec `equivalence_levels` ou `reasons` mais les 2 cles existantes doivent rester.

### Ce que Sx_03 est libre de faire sans rework UX

- Changer la source des `substitutes` (JSON → canonical entity via Option 2 si triggers atteints)
- Ajouter `substitution_reason` comme nouveau champ optionnel (input ou radio dans le picker)
- Ajouter des metadata visuelles discretes (`exact / approx / fallback` badges sur les options du picker)
- Afficher le nom "prescrit" en fallback dans le badge post-substitution

### Points d'extension natifs dans le template actuel

- `substitute-picker` (lignes 105-119 du template) — inserer des attributs data-equivalence ou des labels d'aide la
- `substitute-badge` (ligne 120-123) — enrichir avec raison ou niveau
- Nouveau champ `substitution_reason` dans le form du body exercice — a ajouter apres le picker, avant muscle_sensation, en `<details>` optionnel comme muscle_sensation

---

## 12. Recommandations ordonnees pour le futur build

Aucun build obligatoire par ce spec. Le composant exercice est en production et stable. Recommandations priorisees pour les sprints futurs :

### P1 — Documentation figee comme contrat Sx_03

Ce spec FINAL devient la reference pour Sx_03. Toute evolution de la substitution doit s'inscrire dans les contraintes §11 — PAS de refactor du composant exercice.

### P2 — Test visuel cross-device

Audit manuel sur :
- iOS Safari (sticky footer dans `<details>` capricieux connu)
- Android Chrome (comportement natif `<details>`)
- Ecrans 320px (iPhone SE 1e gen)
- Ecrans 430px (iPhone Pro Max)

Rapport dans un nouveau doc si regressions visuelles detectees. **Aucune action tant que pas de remontee terrain.**

### P3 — Accessibilite approfondie

- Verifier que les `aria-current="step"` de la jump bar (Sb_02.1) sont lus correctement par VoiceOver / TalkBack
- Ajouter `aria-expanded` sur les `<summary>` si besoin (probablement natif deja)
- Verifier contrast WCAG AA sur les 4 couleurs d'etat de la jump bar

**A faire uniquement si un user utilisant un screen reader remonte un probleme.**

### P4 — Haptic feedback discret (si PWA devient iOS native-like)

Vibration sur save reussi, si la plateforme le permet. Pure enhancement, non-bloquant.

**Differer a V3.** Pas dans le scope SSR actuel.

### P5 — Persistence brouillon cote client

Si un user quitte la page au milieu d'une saisie, aucun storage local ne preserve les valeurs. Acceptable aujourd'hui (sessions courtes, connexion stable). Si un besoin explicite emerge, introduire un `localStorage` minimal serait possible. Pas de JS lourd.

**Differer. Pas de trigger actuel.**

---

## 13. Definition of Done (reponse aux criteres)

| Critere | Statut |
|---------|--------|
| Mode focus exercice defini clairement | ✓ (§3 flow cible + §4 composant + §9 wireframes) |
| Etats active / done / future documentes | ✓ (§6.1 table etats + §9.3 recap visuel) |
| Flow save → next specifie precisement | ✓ (§7.1 + §10 transitions table) |
| Champs visibles coherents avec Sx_01 | ✓ (§4.4 emplacement signaux + §8 integration stricte) |
| Composant reste SSR-friendly | ✓ (Zero JS, `<details>` natif, CSS pur, flex standard) |
| Place future substitution prevue | ✓ (§11 contraintes + points extension) |
| Aucun rework majeur laisse pour Sx_03 | ✓ (§11.2 contraintes explicites + §11.4 points extension natifs) |

---

## 14. Synthese executive

**Bloc exercice mobile SPIGNOS post-Sb_02.1 :**

- **Flow focus-exercice** : `<details>` par carte, un seul ouvert par defaut, save → next automatique
- **Jump bar 4 etats** : future / active / partial / done, lisibles d'un coup d'oeil
- **CTA contextuel** : `Enregistrer et passer a E2` / `Enregistrer et terminer` / fallback `Enregistrer`
- **Footer sticky CSS pur** sur carte ouverte, reachability au pouce garantie
- **17 inputs max** par exercice (Sx_01 FINAL) — 37% de gain UX vs pre-Sb_01
- **Taxonomie respectee** : performance mecanique visible, qualite technique derivee, ressenti optionnel
- **Substitution pre-cablee** : position et mecanisme deja en place, Sx_03 peut enrichir sans toucher au composant

Le composant est **stable, documente, et protege** contre le rework futur. Sx_03 peut commencer sur des bases propres.
