# Sprint Sb_BODYMAP_01.1 — Inline Anatomical Worked-Area Body Map — BUILD

**Statut** : 🟢 DELIVERED LOCALEMENT — **NON commité, NON poussé, CI non lancée** (LOCAL BUILD MODE)
**Type** : CODE BUILD — surface partagée (carte séance active), SSR/Jinja/SVG inline, no-JS
**Date** : 2026-07-14
**Spec** : `Sx_BODYMAP_01` (`docs/strategy/SPRINT_Sx_BODYMAP_01_ANATOMICAL_WORKED_AREA_VISUAL_SPEC.md`, commit `9cbc787`)
**Origine terrain** : DOGFOOD_DEBRIEF_01 (`c21bd9c`), irritant #2 CONFIRMÉ
**HEAD de référence** : `9cbc787` (rien commité par ce sprint)

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

### Options & 15 sujets clivants (décisions)

| # | Sujet | Décision |
|---|---|---|
| 1 | Remplacer dans le même emplacement ou déplacer ? | **Même emplacement** (conteneur `.session-focus__body-map` conservé). |
| 2 | Partial dédié ou SVG dans exercise_card ? | **Partial dédié** `worked_area_body_map.html` (isolé, testable). |
| 3 | 6 régions macro ou 11 shapes ? | **6 macro-régions visuelles** (OQ-BM-A) ; **texte 11 zones** conservé. |
| 4 | Primary only ou primary + secondary ? | **Primary + secondary** — le descriptor expose déjà `secondary_zones` (0 complexité ajoutée). |
| 5 | Toujours face+dos ou conditionnel ? | **Face + dos TOUJOURS visibles** (OQ-BM-D) — lève l'ambiguïté dos/postérieur. |
| 6 | Classes CSS par zone ou `data-zone` ? | **Classes CSS par région** (`wa-region--chest` + `is-primary`/`is-secondary`). |
| 7 | aria-hidden ou aria-label ? | **`aria-hidden="true"`** (V1) — texte = source sémantique. |
| 8 | Microcopy non médicale nouvelle ou réutilisée ? | **Réutilisée** — « Estimation indicative, non médicale. » inchangée. |
| 9 | Unknown neutre ou masquer le visuel ? | **Silhouette neutre** (aucune région active) + « À qualifier » texte existant. |
| 10 | Garder l'ancien blob en fallback ? | **Non** — remplacement total (aucune classe blob orpheline). |
| 11 | CSS minimal ou refonte ? | **Ciblé** — remplace le bloc blob, réutilise vars existantes. |
| 12 | Risque mobile 360px ? | 2 silhouettes 34×58px + gap → largeur ~80px, compacte ; `min-height:64px`. |
| 13 | Risque SVG trop long dans Jinja ? | SVG schématique (6 formes/vue) inline < ~2 KB. |
| 14 | Tests HTML structure vs pixels ? | **Structure HTML + CSS source** (jamais pixels). |
| 15 | Commit immédiat ou batch local ? | **LOCAL BUILD MODE** — livré local, GO COMMIT séparé. |

### Risque critique & parade

| Risque | Parade |
|---|---|
| **Casser les tests asservis `body-map`** (`test_session_focus_worked_area.py` : `session-focus__body-map` + `…-shape` + parsing CSS) | **Conserver le conteneur** `.session-focus__body-map` (satisfait présence + aria-hidden + CSS l.269) ; **ré-orienter** le seul assert `…body-map-shape` vers la nouvelle vérité (`wa-silhouettes`) — pas un masquage. **44 tests worked-area verts.** |
| **Claim médical implicite** | silhouette **schématique** (rects/cercle), microcopy « non médicale » conservée, `aria-hidden`. |
| **Nouvelle couleur / budget** | strictement `var(--color-accent)` / `--color-accent-weak` / `--color-border-subtle` / `--color-surface-sunken`. **0 hex nouveau** (test dédié). |
| **Zone non mappée → région fausse** | `unknown` ⇒ **aucune** région active (test dédié). Jamais d'invention. |

**Choix retenu** : partial dédié, même emplacement, remplacement total, SVG inline face+dos, classes CSS par région, primary plein + secondary faible, `aria-hidden`, texte inchangé.

---

## 1. Mapping zone (11) → macro-région visuelle (6)

| Zone (texte, 11) | Région visuelle (6) | Vue(s) |
|---|---|---|
| `pecs` | `chest` | face |
| `delt_lat`, `delt_post` | `shoulders` | face + dos |
| `lats`, `upper_back` | `back` | dos |
| `biceps`, `triceps` | `arms` (macro « Bras », OQ-BM-B) | face + dos |
| `quads`, `posterior`, `calves` | `legs` | face + dos |
| `core` | `core` (tronc dessiné, OQ-BM-C) | face |
| `unknown` / None | *(aucune région active)* | silhouette neutre |

Le **texte** garde la finesse 11 zones (`Deltoïdes latéraux`, `Triceps`, etc.) via le descriptor inchangé — aucune perte d'information.

---

## 2. Fichiers modifiés (périmètre autorisé strict)

| Fichier | Nature |
|---|---|
| `app/templates/_partials/worked_area_body_map.html` | **nouveau** — silhouette SVG inline face+dos, mapping zone→région, macro `_wa_cls`, `aria-hidden` |
| `app/templates/_partials/exercise_card.html` | branché : `{% set wa_* %}` + `{% include %}` remplaçant le blob (conteneur `.session-focus__body-map` conservé) |
| `app/static/css/session_focus.css` | bloc blob (`…body-map-shape*`) remplacé par règles silhouette (`.wa-silhouettes/.wa-silhouette/.wa-body/.wa-region[.is-primary/.is-secondary]`), vars existantes |
| `tests/test_worked_area_body_map.py` | **nouveau** — 16 tests dédiés |
| `tests/test_session_focus_worked_area.py` | 1 assert ré-orienté (`…body-map-shape` → `wa-silhouettes`), commenté « new truth » |

**Non modifiés** : `body_map_descriptor.py`, `muscle_mapping.py`, `ZONE_LABELS`, routers, services, models, data, migrations, JS, CSS `app.css`. **Delt_lat non traité** (irritant #1, attente capture).

---

## 3. Preuves d'invariance

### 3.1 no-JS
`test_no_js_added` : `<script>` / `addEventListener` absents du partial ; aucun fichier JS bodymap. SVG statique, 100 % SSR.

### 3.2 no-service / no-data / no-migration
`check_scope` : 5 fichiers changés, aucun `app/services/**`, `app/models/**`, `data/**`, `migrations/**`. Le descriptor (`body_map_descriptor.py`) fournit déjà `primary_zone`/`secondary_zones` — **aucune** logique métier touchée. Garde-fou grep : 0 chemin interdit.

### 3.3 non médical
- Silhouette **schématique** (rectangles + cercle), jamais planche anatomique.
- Microcopy existante « Estimation indicative, non médicale. » **conservée** (`exercise_card.html:176`).
- `aria-hidden="true"` sur `.wa-silhouettes` (`test_silhouettes_are_aria_hidden`).

### 3.4 no external asset / no new colour
- `test_svg_inline_no_external_reference` : pas de `<img>`, pas de `src=`, pas de `http`.
- `test_body_map_css_no_external_asset` : pas de `url(` dans la région CSS body-map.
- `test_no_new_hex_colour_in_body_map_css` : **aucun `#hex`** dans la région body-map (vars only).

### 3.5 texte source de vérité préservé
- `test_primary_row_and_label_preserved` : ligne « Principal » + label humain (« Pectoraux »).
- `test_delt_lat_text_label_unchanged` : `delt_lat` → **« Deltoïdes latéraux »** (jamais `Delt_lat`/`delt_lat` brut).
- Rows `--primary` / `--secondary` / note inchangées ; Sx_UI_06 D3 respecté (info = un seul endroit, silhouette décorative).

---

## 4. Tests locaux

| Suite | Résultat |
|---|---|
| `test_worked_area_body_map.py` (dédiés) | **16/16** |
| `test_session_focus_worked_area.py` (asservi, 1 ré-orienté) | **28/28** |
| **combiné worked-area** | **44 passed** |
| Sweep ciblé (`session_focus or worked_area or body_map or exercise_card or accessibility or session_flow`) | **295 passed / 0 échec** (104 s) |
| ruff (test neuf) | clean |
| `check_ruff_budget` | 543 ≤ 548 |
| `check_spec_protocol` | PASS |

**Rendu Jinja vérifié** (unitaire hors pytest) : mapped pecs→chest primary + triceps→arms secondary ; delt_lat→shoulders primary ; lats→back primary ; unknown→0 région, 2 SVG neutres.

> `check_scope` = **ISOLATED** → **promu manuellement SHARED_CODE** : `exercise_card.html` +
> `session_focus.css` pilotent la carte de **toutes** les séances actives. Le broad sweep
> ciblé (295) couvre les consommateurs ; **la CI réelle 3/3 reste la source de vérité**.

---

## 5. Rendu avant / après

- **Avant** : `<div class="session-focus__body-map" aria-hidden>` → `<span class="…body-map-shape--{zone}">` : **blob abstrait** (dégradé rayé + ovale accent), ne transmet aucune localisation.
- **Après** : même conteneur → **2 silhouettes SVG inline (face + dos)**, région de la zone primaire en **accent plein**, secondaires en **accent faible** ; `unknown` → silhouette **neutre**. Texte « Principal / Secondaire » inchangé.

---

## 6. Limites

- **V1 = 6 macro-régions** (pas 11 shapes fines) : la finesse reste au texte (décision OQ-BM-A).
- **Silhouette schématique** volontairement grossière (anti-claim) — pas une illustration anatomique réaliste.
- **`arms`/`legs`/`shoulders`** surlignent face **et** dos simultanément (pas de latéralisation biceps-face/triceps-dos en V1 — OQ-BM-B « macro Bras »).
- **Densité mobile** : 2 silhouettes systématiques ; compactes (~34px chacune) mais à confirmer en dogfood réel 360px.

---

## 7. Chemins interdits vérifiés

✅ Aucun `app/routers/**`, `app/services/**`, `app/models/**`, `data/**`, `migrations/**`, `schema_snapshot`, `app/static/js/**`, `.github/**`, `deploy/**`, `requirements*`, `service-worker`. ✅ `body_map_descriptor.py` / `muscle_mapping.py` / `ZONE_LABELS` **non touchés**. ✅ Delt_lat non traité. ✅ Body Intelligence OFF. ✅ Non commité / non poussé / CI non lancée.

---

## Verdict

**Verdict :** 🟢 **Sb_BODYMAP_01.1 — DELIVERED LOCALEMENT (non commité).**

Le blob décoratif « Zone travaillée » est remplacé par une **silhouette SVG inline face+dos**,
6 macro-régions, **zone primaire en accent plein + secondaires en accent faible**, `unknown` →
silhouette **neutre**. **Template-only + CSS** : `body_map_descriptor`/`muscle_mapping`/`ZONE_LABELS`/
services/data/migrations **intacts** ; texte « Principal / Secondaire » (11 zones, labels humains)
**source de vérité inchangée** ; `delt_lat` → « Deltoïdes latéraux » préservé. **Non médical**
(schématique + microcopy conservée + `aria-hidden`), **no-JS**, **aucune nouvelle couleur/hex**,
**aucun asset externe**. 16 tests dédiés + 28 asservis (1 ré-orienté « new truth ») + sweep 295 verts.
`check_scope` ISOLATED → **promu SHARED_CODE** (carte séance active partagée).

**Recommandation : GO COMMIT + CI complète.** La surface est partagée (carte de séance active) →
la CI réelle 3/3 est la source de vérité de non-régression. Plan : **1 commit code** (2 templates +
CSS + 2 tests + ce rapport) → CI 3/3 ; puis docs registry/roadmap. Alternative : dogfood terrain
360px **avant** commit si tu veux valider la densité mobile d'abord.
