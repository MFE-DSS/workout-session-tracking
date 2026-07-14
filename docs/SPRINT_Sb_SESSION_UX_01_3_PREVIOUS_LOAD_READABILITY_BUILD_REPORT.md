# Sprint Sb_SESSION_UX_01.3 — Previous Load Readability (F2) — BUILD

**Statut** : 🟢 DELIVERED LOCALEMENT — **NON commité, NON poussé, CI non lancée** (LOCAL BUILD MODE)
**Type** : CODE BUILD — carte séance active, template/CSS only, SSR/no-JS
**Date** : 2026-07-14
**Audit source** : `Sx_SESSION_UX_01` (`9925165`), friction **F2** (P1)
**HEAD de référence** : `9925165` (rien commité par ce sprint)

---

## 0. Étape 0 — Brainstorming / Options / Choix retenu

### Constat F2 (audit)
« Référence précédente » (charge dernière séance) existe déjà en **tête de console**
(`exercise_card.html:520-529`), mais elle est **séparée de la ligne de saisie active** par les
sets déjà faits → au moment de saisir, l'utilisateur n'a pas la référence sous les yeux.

### Options

| Opt | Description | Verdict |
|---|---|---|
| **A** | **Rappel discret in-row** sur la ligne du set ACTIF (additif), bloc console-ref conservé | ✅ **RETENU** — minimal, sûr, zéro casse |
| B | Déplacer le bloc console-ref vers le set actif | ❌ casse les tests asservis d'ordre/position |
| C | Dupliquer la référence sur chaque set | ❌ re-densification (interdit) |
| D | Rien (attendre dogfood) | ⚠️ écarté ici (build minimal validé par 01.5 ensuite) |

### Sujets clivants tranchés
1. **Additif** (in-row hint) vs déplacement → **additif** (préserve `console-ref--prev`).
2. **Set actif seul** → oui (jamais sur completed/upcoming ; 1 occurrence max).
3. **Silence si pas de donnée** → `_ref.has_data` requis ; sinon rien (jamais de faux poids).
4. **Décoratif** → `aria-hidden="true"` (le bloc console-ref porte la référence accessible).
5. **Couleur** → `--fg-dim` (var existante) ; **aucune nouvelle couleur/hex**.
6. **No-JS** → SSR pur.
7. **Format** → « dernière : X kg · Y reps » (mono, tabular-nums), cohérent avec le bloc console-ref.

### Risque / parade
| Risque | Parade |
|---|---|
| Casser tests asservis `console-ref--prev` / « Référence précédente » / « Non disponible » | **Bloc console-ref intact** ; hint = élément **additif** séparé. 358 sweep verts. |
| Re-densification | 1 ligne discrète, muted, sur le set actif seul. |
| Faux poids | `has_data` requis → silence sinon. |

**Choix : Option A** — rappel in-row discret sur le set actif, additif, `aria-hidden`, `--fg-dim`.

---

## 1. Fichiers modifiés (périmètre autorisé strict)

| Fichier | Nature |
|---|---|
| `app/templates/_partials/exercise_card.html` | + rappel `session-focus__console-row-prev` sur le set ACTIF (`_is_active_set and _ref.has_data`), `aria-hidden` |
| `app/static/css/session_focus.css` | + règle `.session-focus__console-row-prev` (muted, mono, tabular ; `var(--fg-dim)`) |
| `tests/test_session_ux_prev_load.py` | **nouveau** — 7 tests dédiés |

**Non modifiés** : le bloc « Référence précédente » (`console-ref--prev`) est **conservé
à l'identique** ; routers, services (`overload_*`, `last_time`), descriptor, ZONE_LABELS,
models, data, migrations, JS **intacts**. `_ref` réutilisé (déjà calculé, `last_time.get(...)`).

---

## 2. Comportement avant / après

- **Avant** : charge de référence uniquement en tête de console, loin de la ligne active.
- **Après** : sur le **set actif**, quand un historique existe, un rappel discret
  « dernière : X kg · Y reps » apparaît **au point de saisie** (sous le label du set actif).
  Le bloc « Référence précédente » reste en tête (référence accessible). **Silence** si pas
  d'historique.

---

## 3. Preuves d'invariance

- **no métier** : `check_scope` 3 fichiers, aucun `app/routers|services|models`, `data`,
  `migrations`. `_ref` = `last_time.get(...)` déjà présent — aucun calcul ajouté.
- **no-JS** : SSR pur (`test_no_js_added_for_prev_load`).
- **no new colour** : `test_no_new_hex_colour_in_prev_hint_css` — règle réutilise `var(--fg-dim)`,
  aucun `#hex`.
- **silence si pas de donnée** : `test_prev_load_hint_absent_when_no_data`.
- **décoratif** : `test_prev_load_hint_is_aria_hidden`.
- **non-régression console-ref** : `test_console_ref_block_preserved` (`console-ref--prev` +
  « Référence précédente » toujours présents).
- **une occurrence** : `test_prev_load_hint_only_on_active_row` (== 1).

---

## 4. Tests locaux

| Suite | Résultat |
|---|---|
| `test_session_ux_prev_load.py` (dédiés) | **7/7** |
| Sweep ciblé (`session_focus/console/last_time/ui06/accessibility/session_flow/prev_load/briefing/...`) | **358 passed / 0 échec** (122 s) |
| ruff (test neuf) | clean (UP017 corrigé : `datetime.UTC`) |
| `check_ruff_budget` | **543 ≤ 548** |
| `check_spec_protocol` | PASS |

> `check_scope` = **ISOLATED** → **promu manuellement SHARED_CODE** : `exercise_card.html` +
> `session_focus.css` = carte de **toutes** les séances actives. Sweep 358 couvre les
> consommateurs ; **CI réelle 3/3 = source de vérité**.

> **Note test** : le 1er jet ciblait E2 (non actif sur push-a) → hint absent (comportement
> **correct**). Tests corrigés vers **E1** (exercice actif). Correction de test légitime (mauvais
> ciblage), pas un masquage.

---

## 5. Limites

- Rappel **uniquement sur le set actif** (pas sur les sets à venir) — volontaire (anti-densité).
- Format = charge **agrégée** de la dernière séance (comme le bloc console-ref) — pas par-set.
- **À valider en dogfood réel `Sb_SESSION_UX_01.5`** : la friction F2 était *probable* (non
  confirmée factuellement en salle).

---

## 6. Chemins interdits vérifiés

✅ Aucun `app/routers/**`, `app/services/**`, `app/models/**`, `data/**`, `migrations/**`,
`schema_snapshot`, `app/static/js/**`, `.github/**`, `deploy/**`. ✅ `overload_*` / `last_time` /
descriptor / ZONE_LABELS **non touchés**. ✅ `Delt_lat` non traité. ✅ Body Intelligence OFF.
✅ Silhouette `Sb_BODYMAP_01.1` intacte. ✅ Non commité / non poussé / CI non lancée.

---

## Verdict

**Verdict :** 🟢 **Sb_SESSION_UX_01.3 — DELIVERED LOCALEMENT (non commité).**

La charge de la dernière séance est désormais rappelée **discrètement sur la ligne du set actif**,
au point de saisie (« dernière : X kg · Y reps »), **en plus** du bloc « Référence précédente »
conservé. **Template/CSS only** : `overload_*` / `last_time` / descriptor / services / data /
migrations **intacts** ; `_ref` réutilisé. **Additif** (bloc console-ref préservé), **décoratif**
(`aria-hidden`), **silence** si pas d'historique (jamais de faux poids), **no-JS**, **aucune
nouvelle couleur** (`--fg-dim`). 7 tests dédiés + sweep 358 verts. `check_scope` ISOLATED →
**promu SHARED_CODE**.

**Recommandation : GO COMMIT + CI** (surface partagée → CI réelle = source de vérité), **puis
dogfood `Sb_SESSION_UX_01.5`** pour confirmer le gain F2 en salle. Alternative : dogfood mobile
avant commit si tu veux valider le rendu d'abord.
