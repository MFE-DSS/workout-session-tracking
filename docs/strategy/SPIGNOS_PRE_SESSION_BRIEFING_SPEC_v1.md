# SPIGNOS Pre-Session Briefing Spec v1

**Sprint ID :** Sx_11a_pre_session_briefing_spec
**Date :** 2026-04-21
**Statut :** SPEC ONLY — pas de code engagé par ce document
**Prérequis :** Session System V1 validé en dogfooding + branche mergée sur `main` (ou PR en cours), 0 FAIL critique/haute résiduel
**Successeur :** Sb_11a_pre_session_briefing_build (proposé en §L)

---

## A. Contexte

Le cycle V1 (Sb_05 → Sb_10 + catalog v12) a livré un flow carte-par-carte, un atlas machine consultable, une review `/done` enrichie, et un dispatcher strength vs cardio. La carte **active** est maintenant dense d'information utile au moment de l'exécution : machine-panel, last-time, delta, hints, drawer substitution, historique chiffré.

La **carte future** (les exercices pas encore faits) est au contraire presque muette : `<summary>` avec seulement `code | nom | progression 0/N`. L'utilisateur qui anticipe sa prochaine série n'a aucun signal chiffré avant d'ouvrir la carte suivante.

## B. Problème produit

En séance réelle, l'utilisateur a besoin de **décider vite** quelle charge mettre, quelle cadence viser, comment se positionner sur la machine, **avant** de commencer sa série. Aujourd'hui :

1. Il faut **ouvrir** la carte active pour voir les rep_targets, le last-time, les cues.
2. Le passage d'une carte à la suivante via `Enregistrer et passer à E3` est **instantané** — pas de temps pour « regarder avant » ; soit on est sur E2, soit sur E3.
3. L'utilisateur qui veut préparer E3 pendant qu'il repose après E2 doit **remonter manuellement** vers le `<summary>` de E3 pour lire le nom, puis ne voit rien d'utile (pas de cible, pas de last-time, pas de cue).

Résultat observé (intuitif, non mesuré) : charge mal choisie sur 1ʳᵉ série, coup d'œil rapide à l'atlas juste avant chaque set, friction évitable.

**Objectif produit :** réduire la charge cognitive en séance en rendant disponible, **au bon moment et au bon endroit**, un briefing court de la prochaine action. Sans transformer la page en documentation.

## C. Rôle exact du pre-session briefing

Un **signal anticipé** qui répond à trois questions dans un minimum d'espace :

1. **Combien de reps** dois-je viser ? → `rep_targets` du slot
2. **Qu'est-ce que j'ai fait la dernière fois ?** → `last_time.first_set` chiffré
3. **Un rappel d'exécution crucial** → 1-2 cues max depuis l'atlas, quand disponible

Tout ce qui n'est pas dans ces trois questions est **hors scope** du briefing (reste sur la carte active ou sur `/science/atlas`).

**Définition courte :** le briefing n'est pas une fiche. C'est un **pré-calibrage de l'intention** : « pour E3, je vise 8-12 reps, j'étais à 60 kg la dernière fois, et je n'oublie pas de garder les omoplates basses. »

## D. Surfaces existantes du repo à réutiliser

Toutes les briques de données nécessaires sont **déjà là**. Aucun nouveau service, aucune migration.

| Brique | Fichier | Nature |
|--------|---------|--------|
| rep_targets | `app/models/catalog.py` — `RepTarget` | min/max reps prescrits |
| last_time chiffré | `app/services/stats.py` — `last_time_by_exercise_code` → `first_set: {weight_kg, reps}` | déjà calculé dans `session_detail` |
| execution cues | `app/services/machine_atlas.py` — `get_for_template_exercise()` | retourne `{machine, family}` avec `execution_cues: [...]` |
| kind (strength/cardio) | `app/services/quality_score.py` — `session_kind(session)` | déjà alias public |
| cible cardio | `app/models/session.py` + `app/templates/session_detail.html` section cardio | durée + BPM zone |
| delta vs prior | `app/services/delta.py` | déjà calculé ; à NE PAS dupliquer (reste sur la carte active) |
| muscle_sensation, hints Sb_08, machine-panel | — | à NE PAS exposer dans le briefing |

## E. Variantes d'UX possibles

Quatre pistes évaluées, avec trade-offs :

### Variant E1 — Chip permanente sur `<summary>` des cartes future

Ajouter une ligne courte en dessous du `code + nom + progression` dans le `<summary>` de chaque carte `future` :

```
E3  Chest Press machine                   0/3
    3×8-12  ·  dernière fois 60 kg × 10
```

- **Avantages :** toujours visible, aucun clic, lisible d'un coup d'œil pendant le repos.
- **Risques :** densifie le DOM pour toutes les cartes non actives ; 7 future cards = 7 chips redondantes.
- **Mobile :** 1 ligne compacte, truncate si > 60 chars.

### Variant E2 — « Peek » en bas de la carte active

Ajouter, à la fin du formulaire de la carte active (après la zone feedback exercice, avant le footer CTA), un bloc compact annonçant la **prochaine** carte :

```
Prochain · E3 Chest Press machine
3×8-12  ·  dernière fois 60 kg × 10
Omoplates basses · pousser sans verrouiller
```

- **Avantages :** un seul briefing à la fois, celui du prochain exercice ; l'utilisateur qui est sur E2 voit E3 se préparer en contexte.
- **Risques :** rallonge la carte active ; ne bénéficie pas à l'utilisateur qui aurait sauté la carte intermédiaire.

### Variant E3 — `<details class="card-briefing">` sur chaque carte future

Un chevron cliquable sur le `<summary>` des cartes future qui déplie un mini-briefing **sans** ouvrir la carte complète.

- **Avantages :** sur demande, donc non intrusif.
- **Risques :** `<details>` nested dans `<details>` — syntaxiquement valide mais ergonomiquement piégeux (deux chevrons, deux interactions de clic) ; demande à l'utilisateur de savoir que le briefing existe.

### Variant E4 — Toggle global `?briefing=on/off`

Un bouton permanent en haut de la page qui active ou désactive toute la couche briefing. Utile comme complément d'une des variantes ci-dessus.

- **Avantages :** utilisateur en contrôle.
- **Risques :** énième toggle, friction cognitive si pas nécessaire.

## F. Arbitrage recommandé

**Combinaison E1 + E2, sans E3 ni E4.**

Raisonnement :

- **E1 (chip permanente sur le `<summary>`)** couvre le besoin de « vue d'ensemble » en scroll passif. Une ligne compacte ne densifie pas excessivement ; 7 chips de 1 ligne ≈ le coût visuel d'une carte Sb_05. Limité à **rep_targets + last-time chiffré**. Pas de cues ici.
- **E2 (peek au bas de la carte active)** ajoute les **cues** (jusqu'à 2) uniquement pour la prochaine carte. C'est le moment où l'utilisateur en a concrètement besoin : il finit E2, il lit « pour E3, voici les 2 points clés ». Inclut aussi rep_targets + last-time de la prochaine carte.
- **E3 rejeté :** double `<details>` est trop lourd pour un bénéfice marginal.
- **E4 rejeté :** pas de toggle global V1. Si l'utilisateur veut masquer, il peut de toute façon ignorer la chip et le peek (ils restent discrets).

**Conséquence :** la chip E1 est la couche « rapide » pour toutes les cartes future ; le peek E2 est la couche « détaillée » uniquement pour la carte immédiatement suivante.

## G. Modèle de contenu minimal viable

Deux composants, deux formats.

### G1 — Chip future (Variant E1)

**Format unique, une ligne, ≤ 60 chars desktop, truncate mobile :**

```
{scheme_compact}  ·  {last_time_chip}
```

Où :
- `scheme_compact` = forme lisible des rep_targets. Exemples : `3×8-12`, `2×12-15`, `4×6-10 RP`, `LISS 25min zone 115-135` (cardio, voir §H).
- `last_time_chip` = `dernière fois {weight} kg × {reps}` si prior first_set dispo, sinon `première fois` (pas de blabla).

Exemples rendus :

```
3×8-12  ·  dernière fois 60 kg × 10
2×12-15  ·  première fois
```

**Positionnement DOM :** à l'intérieur du `<summary>` existant, sur une deuxième ligne (CSS `flex-basis: 100%` pour forcer le retour à la ligne après le bloc code/nom/progression).

**Masquage conditionnel :**
- Chip rendue uniquement si la carte est **future** (ni active, ni done).
- Pour une carte `done`, le recap-line actuel `{weights} kg · {reps} reps` reste inchangé (c'est déjà un briefing rétrospectif).

### G2 — Peek bas de carte active (Variant E2)

**Bloc compact rendu après le feedback exercice, avant le footer CTA, uniquement si `next_code_by_exercise[se.id]` est non null :**

```html
<aside class="card-peek">
  <header class="card-peek__head">
    <span class="card-peek__label">Prochain</span>
    <span class="card-peek__code">{next_code}</span>
    <span class="card-peek__name">{next_name}</span>
  </header>
  <p class="card-peek__scheme">{scheme_compact} · {last_time_chip}</p>
  {% if next_cues %}
  <ul class="card-peek__cues">
    {% for cue in next_cues[:2] %}<li>{{ cue }}</li>{% endfor %}
  </ul>
  {% endif %}
</aside>
```

**Règles de contenu :**
- `next_code`, `next_name` tirés du `SessionExercise` suivant (par `position`).
- `scheme_compact`, `last_time_chip` : identiques à G1.
- `next_cues` : les **2 premières** `execution_cues` de l'atlas pour l'exercice suivant (pas plus). Si pas de machine liée → bloc cues omis silencieusement.
- Pas d'erreurs fréquentes ici (elles restent sur le machine-panel de la carte active quand elle sera ouverte).
- Pas de delta, pas de score — ce sont des signaux rétrospectifs, pas prospectifs.

**Cas sans next :** la carte active est la dernière → le peek est remplacé par `next = feedback section` (lien direct `#session-feedback`), ou simplement omis si on considère que le footer CTA `Terminer la séance` suffit.

### G3 — Récapitulatif du contenu autorisé

| Surface | rep_targets | last-time chiffré | execution cues | delta | erreurs fréquentes | muscle_sensation |
|---------|-------------|-------------------|----------------|-------|-------------------|------------------|
| Chip future (G1) | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Peek actif (G2) | ✓ | ✓ | ✓ (2 max) | ✗ | ✗ | ✗ |
| Carte active (existant) | ✓ (via scheme) | ✓ | ✓ (via machine-panel) | ✓ | ✓ | ✓ |

**Non-duplication garantie** : le delta et les erreurs fréquentes n'apparaissent **qu'une fois**, sur la carte active — là où l'utilisateur va exécuter.

## H. Différence strength / cardio

Deux formats de chip distincts, un seul format de peek :

### Strength

`scheme_compact` dérive de `rep_targets` :
- Tous les sets avec même min/max → `{n}×{min}-{max}`. Ex. `3×8-12`.
- Sets hétérogènes (rare) → `{n}×var` avec tooltip natif `<title>` sur le detail.
- Technique RP/DS ajoutée en suffix : `3×8-12 RP`.

`last_time_chip` : `dernière fois {weight} kg × {reps}` (1ʳᵉ série complétée).

### Cardio

Pas de `rep_targets` — template `liss-*` n'a pas d'exercices structurés de la même façon. `scheme_compact` dérive du template :

- Si template cardio-only (LISS pur) : `LISS {suggested_duration}min · zone {bpm_lo}-{bpm_hi}`.
  - Zone par défaut documentée : `115-135` bpm (cf. `science.html`).
- Si template cardio + abs (`liss-abs`) : la chip cardio sur le header + chips strength sur les abs. Les exercices d'abs suivent le schéma strength.

`last_time_chip` pour cardio :
- Si `cardio_duration_min` et `cardio_bpm_avg` présents sur la dernière séance : `dernière fois {duration}min · {bpm} bpm`.
- Sinon : `première fois`.

**Peek pour cardio** : pas d'`execution_cues` depuis l'atlas (machines cardio hors scope atlas V1) → bloc cues omis, chip seule.

## I. Impacts techniques

### I.1 Modèle / DB

**Zéro** changement. Tout est calculable depuis l'existant.

### I.2 Services

Un nouveau service léger proposé : `app/services/briefing.py`

```python
def build_chip(se, prior_summary) -> dict | None:
    """Retourne {scheme, last_time, kind} ou None si pas calculable."""

def build_peek(current_se, next_se, prior_map, atlas_for_next) -> dict | None:
    """Retourne le bloc peek pour la prochaine carte, ou None si pas de next."""
```

Responsabilités :
- Formatage `scheme_compact` à partir de `rep_targets` (strength) ou du template (cardio).
- Assemblage `last_time_chip` depuis `last_time_by_exercise_code`.
- Sélection des 2 premières `execution_cues` via `machine_atlas.get_for_template_exercise`.

Pas de nouvelle règle, pas de nouveau stockage, pas de nouvelle inférence.

### I.3 Router

Dans `sessions.py::session_detail` :
- Construire un `briefing_chips_by_exercise: dict[int, dict | None]` pour chaque `SessionExercise` en état `future`.
- Construire un `peek_by_active: dict | None` pour la carte active uniquement, dérivé de `next_code_by_exercise`.
- Passer les deux au template.

### I.4 Templates

Dans `session_detail.html` :
- `<summary class="exercise-card__compact">` — ajouter un bloc `{% if briefing_chip %}{{ chip markup }}{% endif %}` sur sa seconde ligne.
- Après le bloc feedback exercice et avant le footer CTA — ajouter `{% if is_active and peek %}{{ peek markup }}{% endif %}`.

### I.5 CSS

Deux nouveaux blocs BEM :
- `.exercise-card__chip` — monospace, taille 11-12px, couleur `--fg-dim`, `flex-basis: 100%`.
- `.card-peek` — cadre léger, bordure dashed, fond `--bg-soft`, padding-y réduit ; structure `header` + `scheme` + `cues` ul.

### I.6 Tests

- `test_briefing_service.py` : formats chip strength/cardio, edge cases (pas d'historique, rep_targets hétérogènes, atlas absent).
- `test_briefing_surface.py` : rendu chip sur carte future, pas sur carte active, pas sur carte done ; peek visible sur carte active ; peek absent sur le dernier exercice.
- Régression : `test_session_flow.py`, `test_mobile_polish.py`, `test_substitution.py` doivent rester verts sans modif.

### I.7 Zéro-JS

Tout en Jinja + CSS. Aucune interactivité requise (pas d'expand/collapse du briefing lui-même).

## J. Risques

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|-----------|
| Chip densifie trop le `<summary>` sur petit viewport (375px) | Moyen | Moyen | Format strict 1 ligne avec `truncate` CSS ; tests visuels dogfooding |
| Peek rend la carte active trop longue | Moyen | Moyen | Placement **après** les feedbacks exo, **avant** le footer CTA ; limité à 2 cues ; compact |
| Last-time chiffré mal extrait (prior sans first_set complet) | Faible | Faible | Cas géré dans `build_chip` → affiche `première fois` |
| Duplication perçue avec last-time déjà visible sur la carte active | Faible | Faible | Les deux coexistent par design — un sur le summary replié (pré-ouverture), un sur le form ouvert (exécution) |
| `execution_cues` atlas trop verbeux dans le peek | Moyen | Faible | Hard cap 2 cues, pas de wrapping multiligne ; règle éditoriale : « un cue = une phrase ≤ 60 chars » |
| Performances : chip calculée sur chaque `future` card, 7 fois | Faible | Nul | Calcul pur, pas de requête DB ajoutée (données déjà hydratées) |
| Utilisateur trouve le peek intrusif (« je veux juste finir E2 ») | Moyen | Faible | Peek discret, fond soft, typographie dim ; option E4 (toggle) **non-retenue V1** mais réservée si feedback le justifie |

## K. Acceptance criteria Sx_11a

| Critère | Statut |
|---------|--------|
| Problème produit articulé (§B) | ✓ |
| Rôle du briefing défini sans dérive (§C) | ✓ |
| Surfaces existantes réutilisées identifiées (§D) | ✓ |
| 4 variantes d'UX évaluées (§E) | ✓ |
| Arbitrage recommandé E1+E2, justifié (§F) | ✓ |
| Modèle de contenu minimal viable documenté chip + peek (§G) | ✓ |
| Différence strength/cardio explicite (§H) | ✓ |
| Impacts techniques cadrés (§I) — zéro DB, zéro migration, 1 service, 2 blocs template, 2 classes CSS | ✓ |
| Risques listés et mitigés (§J) | ✓ |
| Non-duplication avec delta / erreurs / atlas garantie (§G3) | ✓ |
| SSR-first, mobile-first, zéro JS | ✓ |
| Build suivant recommandé avec estimation (§L) | ✓ |

## L. Recommandation du build suivant

### Sb_11a — Pre-Session Briefing (build)

**Objectif :** implémenter E1 (chip) + E2 (peek) selon §G et §I.

**Périmètre :**
- New : `app/services/briefing.py` (~80 lignes, 2 fonctions publiques).
- Modify : `app/routers/sessions.py::session_detail` — enrichir le contexte template.
- Modify : `app/templates/session_detail.html` — bloc chip dans `<summary>`, bloc peek en bas du form actif.
- Modify : `app/static/css/app.css` — `.exercise-card__chip`, `.card-peek*`.
- New : `tests/test_briefing_service.py` (6-8 tests).
- New : `tests/test_briefing_surface.py` (4-6 tests).
- New : `docs/SPRINT_Sb_11a_pre_session_briefing_REPORT.md`.

**Hors scope :**
- Pas de toggle global (E4 différé si feedback le demande).
- Pas de mini-briefing expandable sur cartes future (E3 rejeté).
- Pas d'alerte si prior.weight > current saisi (déjà couvert par hints Sb_08).
- Pas de refonte de la carte active ou du `/done`.

**Effort estimé :** 5-7h (service 1h, router 30 min, templates 1h30, CSS 1h, tests 1h30, report 30 min).

**Critères d'acceptation Sb_11a :**
1. Chip visible sur chaque carte future ayant au moins un `rep_target` ou un `template.kind == 'cardio'`.
2. Chip affiche rep_targets compact + last-time chiffré, `première fois` si pas d'historique.
3. Peek rendu uniquement sur carte active si `next_code_by_exercise[se.id]` non null.
4. Peek limité à 2 cues (ou 0 cues si pas de lien atlas).
5. Strength et cardio formats distincts (voir §H).
6. Aucun bloc peek sur la dernière carte (next absent).
7. Full suite verte — aucune régression sur le flow V1.
8. Dogfooding visuel validé 375px + desktop.

**Prochain cycle après Sb_11a** : Sx_11b (programme-builder utilisateur) ou Sx_11c (squad v2), à arbitrer par l'utilisateur selon priorités produit.

---

## Annexe — Terminologie stricte (reprise Sx_10)

| Terme | Sens |
|-------|------|
| **briefing** | Pré-calibrage d'intention court et non-intrusif composé de chip + peek |
| **chip** | Ligne compacte sur `<summary>` d'une carte future : rep_targets + last-time chiffré |
| **peek** | Bloc compact rendu en bas de la carte active, préparant la prochaine carte |
| **carte future** | `<details>` sans `open`, position > active_position |
| **carte active** | `<details open>`, position == active_exercise_id |
| **carte done** | `<details>` sans `open`, tous work sets `completed` |
| **prévu** | `exercise_name_snapshot` sur `SessionExercise` — figé à la création de la séance |
| **réalisé** | `actual_exercise_name(se)` = `substituted_name or exercise_name_snapshot` |
| **last-time chiffré** | `last_time.first_set` = `{weight_kg, reps}` de la 1ʳᵉ série complétée de la séance précédente |
| **execution cues** | Liste `machine.execution_cues` depuis `data/machine_atlas.json`, max 2 dans le peek |
