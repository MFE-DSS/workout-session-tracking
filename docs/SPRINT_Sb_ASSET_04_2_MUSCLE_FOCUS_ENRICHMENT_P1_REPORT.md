# SPRINT Sb_ASSET_04.2 — Muscle Focus Enrichment P1 (RAPPORT)

**Base canonique :** `831a38f` · **Branche :** `sb/asset-04-2-muscle-focus-enrichment-p1` · **Tier :** `ISOLATED`
**Spec :** [`Sb_ASSET_04_2_MUSCLE_FOCUS_ENRICHMENT_P1_SPEC.md`](strategy/Sb_ASSET_04_2_MUSCLE_FOCUS_ENRICHMENT_P1_SPEC.md)
**Livré sous le protocole agentique** (`CLAUDE.md §4`) : `GO BUILD` → autonome jusqu'à `PR GREEN / MERGE PENDING`.

## 1. Ce qui change

Le dogfood Martin a **accepté la fondation P0** mais demandé un **vrai upgrade visuel** (planches « pas assez grandes », micro-libellés illisibles), classé **enrichissement majeur**. P1 monte la **valeur perçue** de la surface Muscle Focus sur `/science` **sans toucher à l'anatomie** : layout en **cartes région**, **cartes de synthèse**, **divulgation progressive** et **lisibilité**. Les 3 plaques P0 sont conservées **byte-exact** ; aucune géométrie réécrite.

## 2. Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

| Option (spec §7) | Verdict |
|---|---|
| **A** captions/hiérarchie lisibles | **RETENU** (nécessaire, insuffisant seul) |
| **B** layout/cartes/rythme | **RETENU** (cœur du saut de valeur) |
| **C** cartes de synthèse par région | **RETENU** |
| **D** divulgation progressive « montre / ne montre pas » | **RETENU** |
| **E** nouvelles régions/plaques | **REJETÉ → P2+** (production anatomique gatée) |
| **F** illustrations générées / overlays médical-like | **INTERDIT** (garde-fous) |

**Choix : B+C+D+A**, sans E ni F. **Risques traités** :
1. **Présence des plaques sans toucher la géométrie** → obtenue par **layout** : carte `[plate-area | body]` (colonne en mobile, ligne en desktop, `plate-area` `clamp(220px, 32vw, 320px)`). `viewBox`/paths **inchangés**.
2. **Toggle épaules no-JS** (`:checked ~`) → les radios restent **siblings précédant** `.muscle-focus__toggle` + `.muscle-focus__frame--shoulders` **dans `plate-area`** → sélecteurs préservés.
3. **Claim « % activation »** → le P0 disait « aucune mesure d'**activation** » (négation honnête). Le garde-fou P1 interdit le substring → reformulé « **aucune mesure d'effort** » (même honnêteté, terme banni évité).
4. **Contraste AA** → texte dim en `--fg-dim` (≥ 5.31:1 sur `--surface`/`--surface-2`, guard `Sb_UI_09.3`) ; **zéro nouvelle couleur** (tokens Auren Terminal). IDE diagnostics : aucun warning sur les lignes neuves.

## 3. Fichiers touchés (3 + docs)

| Fichier | Changement |
|---|---|
| `app/templates/_partials/muscle_focus.html` | 3 `<figure>`/caption → **3 cartes région** (`<h3>` · « ce que ça représente » · limite honnête · 2 `<details>`) ; grille ; intro reformulée (« activation » → « effort ») ; **SVG includes, toggle, provenance ischio, attribution, disclaimers inchangés** |
| `app/static/css/app.css` | bloc `.muscle-focus` : ajout `__grid`/`__card`/`__plate-area`/`__body`/`__title`/`__represents`/`__limit`/`__label`/`__disclosure` + media ≥640px (row) ; **toggle + couleurs de plaque intacts** ; tokens seulement |
| `tests/test_auren_muscle_focus_runtime.py` | +4 tests P1 (cartes · disclosure · claims interdits · section rendue) ; **assertion tautologique du toggle corrigée** (parse front/back — résout le nit Gitar P0 différé) |
| docs | ce rapport + entrées registry/roadmap |

## 4. Interdits tenus

Zéro réécriture de géométrie / `viewBox` / path SVG · zéro nouvelle plaque/région · zéro génération/overlay · **non médical** · attribution **BodyParts3D CC BY 4.0** visible · `ai_usage: NONE` · **contrat additif** · SSR/no-JS (aucun JS) · **zéro** changement modèle/score/migration/EKB/`session_builder`/Publication · design source & SVG **non touchés** · `AGENTS.md` / `.spec-triage-policy.json` non touchés.

## 5. Tests

- `tests/test_auren_muscle_focus_runtime.py` — **12 passés** (8 P0 préservés + 4 P1 : 3 cartes région · 6 `<details>` « montre / ne montre pas » · claims interdits `%`/`activation`/`emg`/`recruitment`/`recrutement` absents de la surface rendue · provenance + non-médical conservés). Byte-intégrité des 3 SVG **intacte**, front par défaut coché / dos non coché prouvés sans tautologie.
- **Broad sweep ciblé** — governance + muscle focus + **contrast guard** + science page : **54 passés**. Le contrast guard valide le CSS neuf.

## 6. Validation

check_scope **ISOLATED** · `check_spec_protocol` PASS · `ruff check` (test) **clean** · budget **543 ≤ 548**. Full sweep local **non requis** (tier ISOLATED) — la CI PR parallélisée est le filet.

## Verdict

**Verdict :** 🟢 **Sb_ASSET_04.2 — PATCH COMPLETE / PR PENDING.** Enrichissement produit **template + CSS, no-JS** : cartes région + synthèse + divulgation progressive + lisibilité, **plaques byte-exact, zéro géométrie touchée, zéro claim d'activation/EMG/recrutement**, provenance BodyParts3D préservée. **Merge = GO humain.**
