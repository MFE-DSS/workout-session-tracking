# Sprint Sb_11a Build Report — Pre-Session Briefing

**Date :** 2026-04-21
**Type :** Build chirurgical — implémente §G/§I de `SPIGNOS_PRE_SESSION_BRIEFING_SPEC_v1.md`
**Prérequis :** Session System V1 clos, Sx_11a spec validée
**Périmètre livré :** Variant E1 (chip cartes future) + Variant E2 (peek bas de carte active). E3 et E4 explicitement exclus.

---

## 1. Objectif

Donner à l'utilisateur, au bon moment et au bon endroit, un signal anticipé sur la prochaine action : combien de reps, qu'est-ce que j'ai fait la dernière fois, un rappel d'exécution. Sans transformer la carte en documentation. Sans dupliquer le delta, le machine-panel ou les hints déjà en place.

---

## 2. Fichiers modifiés

| Fichier | Type | Nature |
|---------|------|--------|
| `app/services/briefing.py` | **New** | Service pur — `build_chip` + `build_peek` + helpers format (~130 lignes) |
| `app/routers/sessions.py` | Modify | Contexte `briefing_chips` (dict par `se.id`) + `peek_for_active` (dict ou None) |
| `app/templates/session_detail.html` | Modify | Chip dans `<summary>` (2 endroits + `{% if %}`), peek `<aside>` entre la note et le footer CTA |
| `app/static/css/app.css` | Modify | 2 blocs BEM : `.exercise-card__chip*` et `.card-peek*` |
| `tests/test_briefing_service.py` | **New** | 17 tests unitaires (format scheme, last_time, build_chip, build_peek) |
| `tests/test_briefing_surface.py` | **New** | 8 tests d'intégration (rendu conditionnel chip + peek) |
| `docs/SPRINT_Sb_11a_pre_session_briefing_BUILD_REPORT.md` | **New** | Ce rapport |

**Zéro migration. Zéro JS. Zéro nouveau endpoint. Zéro nouvelle dépendance.**

---

## 3. Décisions d'implémentation

### D1 — Service pur, pas de I/O

`app/services/briefing.py` ne lit ni la DB ni le système de fichiers. Il compose des dicts à partir de :
- un `TemplateExercise` (pour les `rep_targets`) ;
- un `prior_summary` dict (déjà produit par `_summarise_prior` côté router) ;
- un `atlas_entry` dict (déjà produit par `machine_atlas.get_for_template_exercise`).

Les trois briques sont déjà hydratées quand `session_detail` tourne — le service ne ré-interroge rien.

### D2 — Chip limitée à `future` et `partial`

Dans le router, l'itération sur `ordered` filtre `jump_states[se.id] in ("future", "partial")`. La carte active ne porte pas de chip (redondant avec le formulaire déjà ouvert), la carte done non plus (la `recap line` chiffrée existe déjà via `summarise_current_exercise`).

### D3 — Peek uniquement sur la carte active, avec next existant

`peek_for_active` n'est construit qu'une fois (pour la carte active) et seulement si un `SessionExercise` suivant existe par position. Sur le dernier exercice, la variable reste `None` et le template n'émet rien — pas de bloc « Prochain » vide.

### D4 — `rep_targets` compact

Règle de composition dans `_compact_scheme` :
- Tous les rep_targets même (min, max) → `{n}×{min}-{max}`.
- Si `min == max` (cas rare) → `{n}×{min}`.
- Sets hétérogènes → `{n}×var`.
- Techniques (RP, DS) concaténées en suffix.

Exemples rendus : `3×8-12`, `2×5`, `4×6-10 RP`, `2×var`.

### D5 — Cues cappés à 2 avant rendu

La spec §G2 impose 2 cues max. Cap appliqué dans `build_peek` (`list(...)[:2]`), pas dans le template — sécurité contre une future machine d'atlas enrichie de cues.

### D6 — Substitution préservée dans le peek

Si le prochain `SessionExercise` porte déjà un `substituted_name`, le peek affiche le nom substitué, pas le prévu. Cohérent avec le reste du flow (`substituted_name or exercise_name_snapshot`).

### D7 — Zéro JS, SSR pur

Tout rendu en Jinja. Le chip est statique, non-cliquable. Le peek est un `<aside>` décoratif sans interaction.

---

## 4. Construction côté service

```python
# build_chip — utilisé pour chaque carte future/partial
chip = build_chip(se.template_exercise, prior, template_kind)
# → {"scheme": "3×8-12", "last_time": "dernière fois 60 kg × 10", "kind": "strength"}
# → ou None si pas de rep_targets (omit chip)

# build_peek — utilisé une fois pour la carte active
peek = build_peek(
    next_se,                            # ordered[active_idx + 1]
    last_time.get(next_se.exercise_code_snapshot),
    atlas_data.get(next_se.id),         # depuis Sb_07 surface
    template_kind,
)
# → {"code": "E3", "name": "…", "scheme": "…", "last_time": "…", "cues": [...], "kind": "…"}
# → ou None si next_se est absent ou a pas de scheme
```

Les deux fonctions sont **pures** (aucun effet de bord, testées sans DB — voir §7.1).

---

## 5. Injection dans les templates

### 5.1 Chip dans `<summary>`

```html
<summary class="exercise-card__compact">
  <span class="exercise-card__code">…</span>
  <span class="exercise-card__name">…</span>
  <span class="exercise-card__progress">{{ done }}/{{ total }}</span>
  {% if done > 0 and summary %}
    <span class="exercise-card__recap">…</span>
  {% endif %}
  {% set briefing_chip = briefing_chips.get(se.id) %}
  {% if briefing_chip %}
    <span class="exercise-card__chip exercise-card__chip--{{ briefing_chip.kind }}">{{ briefing_chip.scheme }} · {{ briefing_chip.last_time }}</span>
  {% endif %}
</summary>
```

CSS force le retour à la ligne (`flex-basis: 100%; order: 99`) — la chip apparaît sur une nouvelle ligne sous code / nom / progress, avec truncate si trop long.

### 5.2 Peek au bas de la carte active

```html
{% if is_active and peek_for_active %}
  <aside class="card-peek" aria-label="Prochain exercice">
    <header class="card-peek__head">
      <span class="card-peek__label">Prochain</span>
      <span class="card-peek__code">{{ peek_for_active.code }}</span>
      <span class="card-peek__name">{{ peek_for_active.name }}</span>
    </header>
    <p class="card-peek__scheme">{{ peek_for_active.scheme }} · {{ peek_for_active.last_time }}</p>
    {% if peek_for_active.cues %}
      <ul class="card-peek__cues">
        {% for cue in peek_for_active.cues %}<li>{{ cue }}</li>{% endfor %}
      </ul>
    {% endif %}
  </aside>
{% endif %}
```

Position : **après** le `<details class="exercise-card__note">`, **avant** le `<div class="card__actions--exercise">` (footer prev/next). Chrononologie visuelle : remplir ses reps → noter son ressenti → se préparer pour E+1 → cliquer Suivant.

---

## 6. Comportement strength vs cardio

Le champ `kind` est propagé sur le chip et le peek, utilisé comme suffix de classe CSS (`.exercise-card__chip--strength`, `.exercise-card__chip--cardio`) pour colorer différemment si besoin. Pour V1 seul le variant cardio colore la chip en teal ; le reste reste neutre `--fg-dim`.

**Strength** — cas dominant :
- `scheme` dérivé des `rep_targets` (3×8-12 etc.).
- `last_time` chiffré en kg × reps (1ʳᵉ série complétée).
- Cues dans le peek lorsque la machine est liée à l'atlas.

**Cardio** — cas d'usage : `liss-abs` (session cardio avec exercices abs).
- Les exercices abs ont des `rep_targets` → chips strength normales.
- Le `template_kind = "cardio"` propagé dans le chip/peek permet une coloration dédiée si besoin.
- Pas de chip sur l'entête session cardio (pas une carte exercice).

**Pure LISS** (`liss-only`, 0 exercice) : aucune carte rendue, donc aucun chip ni peek — le briefing ne s'applique pas, le flow existant suffit.

---

## 7. Pseudo-capture du rendu

### 7.1 Carte future (E3 de Push A, non encore ouverte)

```
┌─────────────────────────────────────────────────┐
│  E3   Butterfly pec machine            0/3      │
│       3×10-15 · dernière fois 45 kg × 12        │
└─────────────────────────────────────────────────┘
```

### 7.2 Carte active (E1 de Push A) avec peek vers E2

```
┌─────────────────────────────────────────────────┐
│  E1   Incline Smith Press              0/3      │
│       (form ouvert — warmup + work sets,        │
│        last-time, delta, hints, note exo…)      │
│                                                  │
│  ┌──────────────────────────────────┐           │
│  │ PROCHAIN  [E2]  Chest Press machine│         │
│  │ 3×8-12 · dernière fois 60 kg × 10 │         │
│  │ • Dos plaqué au dossier…         │          │
│  │ • Pousser vers l'avant…          │          │
│  └──────────────────────────────────┘           │
│                                                  │
│  [← E0 disabled]   0/3   [Enregistrer → E2]    │
└─────────────────────────────────────────────────┘
```

### 7.3 Dernière carte active (E7 de Pull A)

Aucun bloc peek rendu — la carte affiche directement le footer `[Enregistrer et terminer]`.

---

## 8. Tests ajoutés

### 8.1 Tests unitaires — `tests/test_briefing_service.py` (17)

- `test_compact_scheme_uniform_rep_targets` → `3×8-12`
- `test_compact_scheme_collapses_when_min_equals_max` → `2×5`
- `test_compact_scheme_variable_uses_var_marker` → `2×var`
- `test_compact_scheme_appends_technique` → `2×8-10 RP`
- `test_compact_scheme_no_rep_targets_returns_none` → None pour `[]` et None
- `test_last_time_chip_formats_integer_weights_cleanly` → pas de `60.0`
- `test_last_time_chip_preserves_decimal_weights` → `52.5 kg × 8`
- `test_last_time_chip_falls_back_to_premiere_fois` → `première fois` sur 4 cas edge
- `test_build_chip_returns_none_when_no_scheme`
- `test_build_chip_strength_happy_path`
- `test_build_chip_passes_through_cardio_kind`
- `test_build_peek_returns_none_when_next_is_none`
- `test_build_peek_returns_none_when_no_scheme`
- `test_build_peek_without_atlas_has_empty_cues`
- `test_build_peek_caps_cues_at_two`
- `test_build_peek_shows_substituted_name_when_set`
- `test_build_peek_merges_prior_last_time`

### 8.2 Tests d'intégration — `tests/test_briefing_surface.py` (8)

- `test_chip_present_on_future_card_summary` — rendu sur `/sessions/{id}` d'une Push A fraîche
- `test_chip_absent_on_active_card` — isolation DOM du `<details open>`, pas de chip
- `test_chip_absent_on_completed_card` — E1 forcée en done par fixture DB, recap line présent, chip absent
- `test_peek_rendered_on_active_card_when_next_exists` — présence `.card-peek` + label `Prochain`
- `test_peek_carries_scheme_and_last_time` — présence regex `\d+×\d+`
- `test_peek_absent_on_last_card` — isolation du dernier `<details open>`, pas de peek
- `test_peek_includes_cues_when_next_has_atlas_link` — E2 Chest Press lié à l'atlas → `.card-peek__cues` rendu
- `test_peek_head_shows_next_code_and_name`

### 8.3 Régression

- Full suite : **666 passed** (vs 641 avant Sb_11a, +25).
- Aucune régression observée.
- Tests impactés indirectement (session flow, mobile polish, substitution, done, science-atlas) : verts.

---

## 9. État final de la suite

```
tests : 666 passed en 3m24s
catalog_qa.py : PASS (16 templates, 98 exercises)
machine_atlas_qa.py : PASS (8 familles, 29 machines)
alembic : head = a19c4e3b7f21 (inchangé, pas de nouvelle migration)
```

---

## 10. Limites assumées

1. **Pas de toggle utilisateur** pour masquer le briefing — si le peek s'avère intrusif en dogfooding, ajouter E4 dans un Sb_11a.1 ciblé (~30 min).
2. **Pas de briefing sur les cartes future expandables à la demande** (Variant E3 rejeté) — la chip statique couvre le besoin à 80% sans double-`<details>` piégeux.
3. **Aucune coloration distincte `--strength` en V1** — la classe `.exercise-card__chip--strength` existe mais n'a pas de règle CSS spécifique pour l'instant. Seul `--cardio` colore en teal. Si un retour produit demande une distinction plus forte, ajouter dans une passe CSS dédiée.
4. **Cap cues à 2** — volontaire. Si l'utilisateur veut les voir tous, il ouvre le `machine-panel` sur la carte active.
5. **Pas d'impact export/confidence** — le briefing est purement visuel, ne touche pas le modèle analytique.
6. **Pas de mention dans le sprint queue doc** — le cycle Sb_11a était ouvert depuis Sx_11a, à référencer manuellement si on ajoute une ligne au queue dans un sprint de gouvernance.

---

## 11. Recommandation du prochain sprint de spec

**Sx_11b — Programme-builder utilisateur** (recommandation primaire).

**Pourquoi :**
- Prochain saut de valeur utilisateur naturel : passer de « consommer un catalogue pré-défini » à « composer son propre programme ».
- Pré-requis techniques sont maintenant tous en place : snapshots immutables (Sx_02), atlas de machines (Sb_07), scoring dispatcher (Sb_06), briefing (Sb_11a).
- Bonne lisibilité du scope : nouveau modèle `UserTemplate`, nouvelle page `/programmes/new`, réutilisation du catalogue existant comme point de départ.

**Alternative :** Sx_11c — Squad / social v2 (4h spec, 8-12h build). Moins urgent, faible dépendance aux briques V1.

**Statut immédiat recommandé :**
- Passer en dogfooding Sb_11a (valider chip + peek en conditions réelles mobile 375px).
- Si OK → ouvrir Sx_11b.
- Si retour montre que le peek est intrusif → ouvrir Sb_11a.1 (ajout toggle `?briefing=on/off`) avant Sx_11b.

---

## 12. Synthèse exécutive

- Chip compacte (scheme + last-time chiffré) rendue sur chaque carte *future* / *partial*, invisible sur *active* et *done*.
- Peek discret (rep scheme + last-time + jusqu'à 2 cues atlas) rendu uniquement en bas de la carte active, absent sur la dernière carte.
- Service pur `briefing.py` testé sans DB, router consomme des briques déjà hydratées (last_time, atlas_data), zéro nouveau I/O.
- **25 nouveaux tests** (17 unit + 8 surface), full suite **666 passed**.
- Zéro migration, zéro JS, zéro touche au catalogue, zéro nouvelle route.
- Cycle Session V1 étendu d'une brique utile, prêt pour dogfooding puis Sx_11b.
