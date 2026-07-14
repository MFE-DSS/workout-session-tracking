# Sprint Sb_SESSION_UX_01.2 — Active Console Priority (F1) — BUILD

**Statut** : 🟢 DELIVERED LOCALEMENT — **NON commité, NON poussé, CI non lancée** (LOCAL BUILD MODE)
**Type** : CODE BUILD — carte séance active, template only, SSR/no-JS
**Date** : 2026-07-14
**Audit source** : `Sx_SESSION_UX_01` (`9925165`), friction **F1** (P1)
**HEAD de référence** : `73d309b` (rien commité par ce sprint)

---

## 0. Étape 0 — Brainstorming / Options / Choix retenu

### Constat F1 (audit)
Sur la carte active, l'action principale (saisir un set) arrivait **après** plusieurs blocs de
contexte. Ordre réel constaté : `intent → worked-area → cues → [machine] → alternatives → console`.
Le bloc **cues techniques est toujours déplié** → c'est lui qui repoussait le plus la saisie.

### Options
| Opt | Description | Verdict |
|---|---|---|
| **A** | Repriorisation légère : cues + alternatives sous la console | ✅ **RETENU (adapté)** |
| B | Console juste après Intention | ❌ trop brutal (worked-area perd son rôle de repère) |
| C | Lien « Saisir maintenant » | ❌ ajoute une action (anti-densité) |
| D | Rien avant dogfood 01.5 | ⚠️ différé (mais 01.5 reste pending — voir §Risques) |

### Découverte en cours de build (contrainte non anticipée par l'audit)
1. **La console est PARTAGÉE** : rendue sur la carte active (pleine) **et** sur les cartes
   non-actives (`--compact`). → **Interdit de la remonter dans le hero `{% if is_active %}`**
   (sinon les cartes non-actives perdent leur console). Donc **on descend les blocs de contexte**,
   on ne remonte pas la console.
2. **Cues dépend de `_machine`** (résolu dans le hero) → en descendant les cues, `_machine`
   n'est plus dans le scope. Re-résolu **localement** (`_cues_machine = atlas_data.get(se.id).machine`)
   — présentation, aucune logique métier.
3. **Alternatives = drawer `<details>` form-critical** (radios `substituted_name`, N1/N2/N3,
   `if/elif`). Le déplacer intégralement = **risque de régression form-critical disproportionné**,
   d'autant qu'il est **replié par défaut** (1 ligne de summary, faible gêne).

### Choix retenu (Option A adaptée — scope de sécurité)
- **Cues techniques déplacées APRÈS la console** (le vrai coupable F1, toujours visible).
- **Alternatives LAISSÉES en place** (repliées `<details>`, form-critical) — **écart assumé vs
  brief** au nom de la prudence (CLAUDE.md : en cas de doute, remonter d'un cran de prudence).
- `_machine` orphelin (hero) **nettoyé** (plus de consommateur là-haut).

**Ordre livré (carte active)** : `intent → worked-area → [machine] → alternatives (replié) →
**console** → **cues** → ressenti / note / up-next / CTA`.
**Gain F1 capturé** : la **console (saisie) passe avant les cues** (bloc toujours-visible).

---

## 1. Ordre avant / après (carte active)

| # | AVANT | APRÈS |
|---|---|---|
| 1 | Intention | Intention |
| 2 | Zone travaillée (silhouette) | Zone travaillée (silhouette) |
| 3 | **Cues techniques** | [machine panel] |
| 4 | [machine panel] | Alternatives (replié) |
| 5 | Alternatives (replié) | **Console sets (saisie)** ⬆ |
| 6 | **Console sets (saisie)** | **Cues techniques** ⬇ |
| 7 | Ressenti / note / up-next / CTA | Ressenti / note / up-next / CTA |

Gain : la saisie n'est plus repoussée par les cues dépliées.

---

## 2. Fichiers modifiés (périmètre autorisé strict)

| Fichier | Nature |
|---|---|
| `app/templates/_partials/exercise_card.html` | cues retirées du hero + ré-insérées après la console (`_cues_machine` re-résolu localement) ; `_machine` orphelin nettoyé |
| `tests/test_session_ux_console_priority.py` | **nouveau** — 11 tests |

**CSS non modifié** : le déplacement réutilise les classes existantes (`session-focus__cues`) —
aucun style nouveau nécessaire. **Non modifiés** : routers, services, models, data, migrations, JS,
`session_focus.css`. Aucune donnée/calcul changé (cues re-résolues depuis `atlas_data` déjà présent).

---

## 3. Invariants préservés

- **Mêmes formulaires POST** (`update_exercise_card`) · **mêmes inputs** `set_{id}_weight_kg`/`_reps`
  (`test_set_inputs_present`).
- **`value=""` strict** · **completion dérivée serveur** (inchangés — console non touchée dans son contenu).
- **Placeholders overload inchangés** · **rappel « dernière »** (01.3) sur set actif **inchangé**.
- **Bloc « Référence précédente »** conservé.
- **Silhouette BodyMap** conservée (`test_bodymap_silhouette_preserved`).
- **Alternatives** fonctionnelles, mécanisme radios `substituted_name` intact (`test_alternatives_still_in_form`).
- **Machine panel** intact · **sticky CTA** (`test_sticky_cta_present`) · **rest timer** (`test_rest_timer_rendered`).
- **No-JS** (`test_no_js_added`) · **cues rendues 1 seule fois** (`test_cues_rendered_once`, pas de doublon).

---

## 4. Tests locaux

| Suite | Résultat |
|---|---|
| `test_session_ux_console_priority.py` (dédiés) | **11/11** |
| Non-régression (worked_area/console/ui06/bodymap/prev_load) | **98 passed** |
| Sweep large (session_focus/console/exercise_card/prev_load/bodymap/substitution/overload/rest_timer/sticky/session_flow/accessibility/…) | **516 passed / 0 échec** (159 s) |
| ruff (test neuf) | clean |
| `check_ruff_budget` | **543 ≤ 548** |
| `check_spec_protocol` | PASS |

**Assertions d'ordre** : `test_console_before_cues` (console < cues), `test_worked_area_before_console`
(worked-area < console). Test asservi existant `body-slot..cues` (parsing élargi) reste vert (pas d'asset).

> `check_scope` = **ISOLATED** (2 fichiers) → **promu manuellement SHARED_CODE** : `exercise_card.html`
> pilote la carte de **toutes** les séances. Sweep 516 couvre les consommateurs ; **CI réelle = source de vérité**.

> **Note test** : `test_alternatives_still_in_form` vérifie le **template source** (les exercices
> synthétiques n'ont pas de substitutions calculées → drawer non rendu ; le mécanisme reste présent).

---

## 5. Risques

| Risque | État |
|---|---|
| **Dogfood 01.5 (qui valide 01.3) encore PENDING** | ⚠️ on construit F1 avant confirmation terrain de F2. Ce build **doit** aussi être dogfoodé. |
| **Écart vs brief** : alternatives non déplacées | assumé (form-critical, replié) — à rouvrir si le dogfood juge la position gênante. |
| Casser l'ordre HTML asservi | mitigé : seul `body-slot..cues` parse l'ordre → vert. 98 non-régression verts. |
| Re-densification | non : aucun bloc ajouté, seulement réordonné ; cues re-résolues sans nouveau contenu. |

---

## 6. Chemins interdits vérifiés

✅ Aucun `app/routers/**`, `app/services/**`, `app/models/**`, `data/**`, `migrations/**`,
`schema_snapshot`, `app/static/js/**`, `.github/**`, `deploy/**`. ✅ `session_focus.css` non touché.
✅ overload / last_time / descriptor / ZONE_LABELS **intacts**. ✅ `Delt_lat` non traité.
✅ Body Intelligence OFF. ✅ Non commité / non poussé / CI non lancée.

---

## Verdict

**Verdict :** 🟢 **Sb_SESSION_UX_01.2 — DELIVERED LOCALEMENT (non commité).**

Sur la carte active, la **console de saisie passe désormais avant les cues techniques** (Option A
adaptée) : cues déplacées après la console, `_cues_machine` re-résolu localement, `_machine` orphelin
nettoyé. **Template only** (CSS inutile) : routers / services / models / data / migrations / JS
**intacts** ; POST / inputs / `value=""` / completion serveur / placeholders overload / rappel
« dernière » (01.3) / « Référence précédente » / silhouette BodyMap / sticky CTA / rest timer /
alternatives **préservés**. 11 tests dédiés + 98 non-régression + sweep 516 verts. check_scope
ISOLATED → **promu SHARED_CODE**.

**Écart assumé vs brief** : les **alternatives** (drawer replié, form-critical) **ne sont pas
déplacées** — prudence anti-régression ; le gain F1 principal (console avant cues) est capturé.

**Recommandation : GO COMMIT + CI complète** (surface partagée → CI réelle = source de vérité),
**puis dogfood** (idéalement groupé avec `01.5`) pour valider F1+F2 en salle. Alternative : si tu
veux les alternatives **aussi** sous la console, en faire un **`01.2b`** dédié (geste form-critical
isolé, testé à part). Ou STOP + dogfood d'abord si tu préfères confirmer avant d'empiler.
