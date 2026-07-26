# AUREN — Muscle Focus Descriptor Schema (`Sb_ASSET_03B.1`)

**Type** : schéma normatif du **descripteur de plaque** — **DOCS-ONLY**. Fige les **champs, types et invariants**
qu'un descripteur de Muscle Focus Plate doit porter, **sans produire aucune plaque**. `ASSET INTEGRATION GATE:
BLOCKED` · `PLATE GEOMETRY: NOT PRODUCED`.
**Références normatives** : [`AUREN_MUSCLE_FOCUS_ID_CONTRACT.md`](AUREN_MUSCLE_FOCUS_ID_CONTRACT.md) ·
[`../../strategy/Sx_ASSET_03B_MUSCLE_FOCUS_TECHNICAL_SURFACE_SYSTEM_SPEC.md`](../../strategy/Sx_ASSET_03B_MUSCLE_FOCUS_TECHNICAL_SURFACE_SYSTEM_SPEC.md) §7-§10.
**`SCHEMA VERSION: 0.1.0`** (aligné sur `CONTRACT VERSION` de l'ID Contract ; bump conjoint).

> Ce schéma **succède au gabarit** de `AUREN_MUSCLE_FOCUS_PLATE_TEMPLATE.md` : il en **fige** la forme et
> **ajoute** les garde-fous issus de la revue adversariale (exercise-link zone-only, caption-miroir de
> l'overlay, typage `region_key_kind`, jeton non-médical). Le gabarit reste la vue pédagogique ; **ce schéma
> est la vérité contractuelle**.

---

## 1. Schéma (champs, types, obligation)

```yaml
# ── identité ────────────────────────────────────────────────────────────────
plate_id:            <string>     # REQUIS · ∈ les 19 racines figées (ID Contract §3)
level:               <enum>       # REQUIS · "2-regional" | "3-muscle"
mode:                <enum>       # REQUIS · "muscle-heads" | "grouped-honest"
schema_version:      <semver>     # REQUIS · == "0.1.0" en v0.1.0 (== CONTRACT VERSION)

# ── ancrage taxonomie (Layer A, jamais étendu) ──────────────────────────────
zone_codes:          [<code>...]  # REQUIS · sous-ensemble NON VIDE des 11 codes figés ; JAMAIS un nouveau code
macro:               <enum>       # REQUIS · "chest"|"shoulders"|"back"|"arms"|"legs"|"core"
region_key_kind:     <enum|null>  # REQUIS si level=2-regional : "macro" | "zone" ; null si level=3-muscle

# ── géométrie / vues (Layer B) ──────────────────────────────────────────────
views:               [<enum>...]  # REQUIS · sous-ensemble de [front, back, lateral, section] ; N2 ⊆ {front,back}
viewbox_local:       <string>     # REQUIS · figé par famille (cf. View & Crop Contract) ; crop master (N2) ou neuf (N3)
parts:               [<part-id>]  # OPTIONNEL · ⊆ registre part-* (ID Contract §4) ; [] autorisé (ex. lats)
markers:             [<mark-id>]  # OPTIONNEL · mark-<zone>-origin|insertion-<i> ; N2 = [] (overlay N3 only)

# ── liens produit ───────────────────────────────────────────────────────────
exercise_link_granularity: <enum> # REQUIS · "zone" (SEULE valeur licite en v0.1.0) — jamais "part"/"head"
exercise_link_mode:  <enum>       # REQUIS · "list" (N2 + P0) | "interactive-overlay" (N3, P1+)

# ── provenance / licence ────────────────────────────────────────────────────
source_refs:         [<ref>...]   # REQUIS · clés du Source Ledger (source · rôle · url_licence · access_date)
attribution_required:<bool>       # REQUIS · true dès qu'une géométrie CC BY est dérivée (perpétuel)
ai_usage:            <NONE|obj>    # REQUIS · "NONE" | {role: "style"|"composition", declared: true} — JAMAIS géométrie

# ── invariants produit ──────────────────────────────────────────────────────
non_medical:         true         # CONSTANT · true (littéral) — vecteurs/ROM, jamais EMG/activation/%
scored:              false        # CONSTANT · false (littéral) — une plaque n'introduit AUCUN score/donnée
caption_mirrors_overlay: true     # CONSTANT · true — la caption porte le texte-équivalent de tout fait de l'overlay
```

---

## 2. Invariants durs (à faire respecter par le futur guard)

1. **`plate_id` ∈ 19 racines** (ID Contract §3) ; `level`/`mode` cohérents (les 2 `grouped-honest` sont
   `upper_back` et `posterior`, toutes deux `level: 3-muscle`).
2. **`zone_codes ⊆ 11`, non vide, aucun code inventé.** `scored == false` et `non_medical == true` **littéraux**
   (rejet si absents ou modifiés).
3. **`region_key_kind`** REQUIS ⇔ `level == 2-regional` ; valeur cohérente avec ID Contract §3 (chest/shoulders/
   back/arms/core = `macro` ; quads/posterior/calves = `zone`). `null` si `level == 3-muscle`.
4. **`views` :** N2 ⊆ `{front, back}` ; `lateral`/`section` **réservés N3** (Layer B licite au niveau plaque,
   cf. amendement de gouvernance).
5. **`parts ⊆` registre §4** ; un `part-*` hors table = rejet. `markers` non vides ⇒ `level == 3-muscle`.
6. **`exercise_link_granularity == "zone"`** — toute autre valeur (`part`, `head`, `fascicle`) = **rejet dur**
   (anti sous-zone implicite / anti fausse-précision, adversarial #3).
7. **`caption_mirrors_overlay == true`** — condition d'a11y : tout fait anatomique rendu **visuellement** dans
   un overlay (origine, insertion, direction de fibre, rôle mécanique) a une **forme textuelle** dans la
   caption (module 9). L'overlay décoratif peut alors être `aria-hidden` **parce que** la vérité est au texte
   (adversarial #4 ; cohérent `AUREN_STYLE_RULES §7`).
8. **`ai_usage` ≠ géométrie** : `role ∈ {style, composition}` uniquement ; `declared: true` obligatoire si objet.
   `attribution_required` vrai dès qu'une source CC BY est dérivée (Servier, OpenStax 1ʳᵉ éd.).
9. **Aucun jeton mensonger** dans un descripteur ou une caption : `approved`, `legally-cleared`,
   `anatomically-validated-professionally`, `runtime-ready`, `integration-authorized` **interdits en
   affirmation**. Aucun jeton de mesure : `EMG`, `%`, `activation`, `recruitment`, `mesure`, `clinique`.

---

## 3. Exemple (gabarit rempli — **illustratif, non produit**)

```yaml
# ILLUSTRATIF — aucune géométrie n'existe ; viewbox_local à figer au build géométrique
plate_id: auren-plate-muscle-pecs
level: 3-muscle
mode: muscle-heads
schema_version: "0.1.0"
zone_codes: [pecs]
macro: chest
region_key_kind: null
views: [front, lateral]
viewbox_local: "<figé par la famille chest — cf. View & Crop Contract>"
parts: [part-pecs-clavicular, part-pecs-sternocostal]
markers: [mark-pecs-insertion-01]        # insertion humérale unique (spec §16 : éventail convergent)
exercise_link_granularity: zone           # « exercices — Pectoraux », jamais « — chef claviculaire »
exercise_link_mode: interactive-overlay
source_refs: [servier-smart, openstax-ap1-2013]   # clés Source Ledger
attribution_required: true
ai_usage: NONE
non_medical: true
scored: false
caption_mirrors_overlay: true
```

---

## Verdict

**Verdict :** 🟢 **`MUSCLE FOCUS DESCRIPTOR SCHEMA v0.1.0: LOCKED (DOCS-ONLY).`** Champs/types/obligation figés
avec **9 invariants durs** dont les 4 garde-fous adversariaux : `exercise_link_granularity: zone` (anti
sous-zone), `caption_mirrors_overlay: true` (a11y), `region_key_kind` typé (macro/zone), jeton non-médical
banni. `scored:false`/`non_medical:true` littéraux. **Aucune plaque produite.** `PLATE GEOMETRY: NOT PRODUCED`
· `ASSET INTEGRATION GATE: BLOCKED`.
