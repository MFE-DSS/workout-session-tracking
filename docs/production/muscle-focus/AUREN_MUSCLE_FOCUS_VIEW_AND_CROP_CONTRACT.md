# AUREN — Muscle Focus View & Crop Contract (`Sb_ASSET_03B.1`)

**Type** : contrat normatif des **vues autorisées et des crops** — **DOCS-ONLY**. Fige *quelles* vues existent,
*où* elles sont licites, et l'**intention de crop** par famille — **sans figer aucun nombre de `viewBox` ni
produire de géométrie**. `ASSET INTEGRATION GATE: BLOCKED` · `PLATE GEOMETRY: NOT PRODUCED`.
**Références** : [`AUREN_MUSCLE_FOCUS_ID_CONTRACT.md`](AUREN_MUSCLE_FOCUS_ID_CONTRACT.md) ·
[`AUREN_MUSCLE_FOCUS_DESCRIPTOR_SCHEMA.md`](AUREN_MUSCLE_FOCUS_DESCRIPTOR_SCHEMA.md) · spec §5, §8-§9, §16.
**`CONTRACT VERSION: 0.1.0`**.

---

## 1. Les 4 vues (et où elles sont licites)

| Vue | Sens | N2 Regional | N3 Muscle | Contrainte |
|---|---|---|---|---|
| `front` | face orthographique locale | ✔ | ✔ | échelle cohérente face/dos (héritage `§5`) |
| `back` | dos orthographique local | ✔ | ✔ | requise pour `delt_post`, `posterior`, `upper_back` |
| `lateral` | vue 3/4 ou profil local | — | ✔ | requise `pecs` (convergence), `delt_lat` (3 faisceaux) |
| `section` | **coupe locale schématique** | — | ✔ | **sous amendement de gouvernance** (§4) — jamais viscères/organes |

- **`front`/`back`** héritent du contrat master : **orthographiques**, non médicales, échelle cohérente.
- **`lateral`/`section`** sont **nouvelles au niveau plaque** (Layer B). Licites **tant qu'elles ne touchent ni
  les 11 codes ni les 6 macros**. `section` **exige** l'amendement §5 (cf.
  [`AUREN_MUSCLE_FOCUS_GOVERNANCE_AMENDMENT.md`](AUREN_MUSCLE_FOCUS_GOVERNANCE_AMENDMENT.md)) : coupe
  **schématique** (corset transverse, chefs empilés) **sans organe, sans viscère, sans rendu médical**.
- **Règle P0** : les 7 blueprints P0 se limitent à `front`/`back` (clean + caption). `lateral`/`section` = P1.

## 2. Philosophie de crop — *le zoom est la valeur*

1. **Crop local, jamais corps entier.** Une plaque cadre une **région** (demi-corps, quadrant, zoom muscle).
   Le corps entier reste au **Niveau 1** (compact global). *« Pas de bas-du-corps générique »* (spec §16).
2. **N2 = crop documenté du master validé.** La Regional Plate **ré-émet** (jamais n'inline, ID Contract §Règle
   #4) un sous-cadre du master `240×200` sous son namespace plaque. Le `viewbox_local` est un **sous-rectangle**
   documenté du master.
3. **N3 = artefact neuf.** La Muscle Plate a son **propre `viewbox_local`** (repère local du muscle), non dérivé
   mécaniquement du master — exigeant package + intake technique au build géométrique.
4. **`viewbox_local` figé au build géométrique.** Ce contrat fige l'**intention** (§3) ; le **nombre exact**
   (`"minX minY W H"`) est arrêté quand la géométrie est produite et **bumpe le contrat** (semver). Aucun nombre
   n'est inventé ici (0 géométrie).
5. **Gouttière & safe-area** : héritées du master là où un crop bilatéral les traverse (gouttière médiane vide,
   marge de sécurité) ; re-figées par famille au build.
6. **Lisibilité mobile** : chaque crop doit rester lisible en **sheet plein écran 360px** (N3) ; formes
   réductibles, trait d'épaisseur constante, contraste fort (héritage `§5`/`§6`).

## 3. Intention de crop par famille (contrainte de contenu, pas de nombre)

Chaque crop **doit inclure** l'ancrage osseux et **exclure** le hors-sujet dicté par le cas d'exigence spec §16.

| Famille | Vues clés | Le crop **doit inclure** | Le crop **doit exclure** |
|---|---|---|---|
| **chest** (`pecs`) | front, lateral | éventail claviculaire + sterno-costal **convergeant** vers **une** insertion humérale ; sternum (axe `c`) | 2 blobs symétriques (« poumons ») ; corps entier |
| **shoulders** (`delt_lat`,`delt_post`) | front, lateral, back | 3 faisceaux **en contexte osseux** (clavicule / acromion / épine scapulaire), insertion deltoïdienne commune | faisceaux sans os (indistinguables) |
| **back** (`lats`,`upper_back`) | back | `lats` = nappe large en éventail vers l'humérus (V-taper) ; `upper_back` = empilement trapèze→rhomboïde | fusion largeur/épaisseur (le message est la distinction) |
| **arms** (`biceps`,`triceps`) | front, back | biceps (longue/courte) face ; triceps (3 chefs) dos ; ancrage huméral | avant-bras détaillé (hors zone) |
| **core** (`core`) | front, section | rectus = **sangle continue** à intersections tendineuses subtiles ; obliques en diagonale ; transverse en **corset** (idéalement `section`) | faux six-pack régulier bombé |
| **quads** (`quads`) | front | 4 chefs (rectus + 3 vastes) ; ancrage fémur/patella | postérieur (autre plaque) |
| **posterior** (`posterior`) | back | crop **bassin→cuisse** ; insertion ischiatique commune ; vecteur extension de hanche ; fessier (superficiel) vs 3 ischios | « bas du corps générique » |
| **calves** (`calves`) | back, lateral | gastrocnémien (2 chefs) sur soléaire ; tendon d'Achille | pied détaillé |

*(Les familles P1/P2 — arms, back, core, quads, calves — figurent ici pour compléter le contrat de vues ; seuls
chest/shoulders/posterior sont **blueprintés P0**.)*

## 4. Invariants (futur guard)

1. `views ⊆ {front, back, lateral, section}` ; `N2 ⇒ views ⊆ {front, back}`.
2. `section ∈ views ⇒ level == 3-muscle` **et** amendement §5 enacté (sinon la plaque est **non productible**).
3. `viewbox_local` : chaîne `"minX minY W H"` non vide au build ; **stable** par famille (changer = bump majeur).
4. N2 : `viewbox_local` est un **sous-rectangle** de `0 0 240 200` (crop master) — vérifiable géométriquement.
5. Aucune vue ne matérialise un `zone-<code>` ni ne réintroduit une 12ᵉ zone ; les faisceaux restent `part-*`.

---

## Verdict

**Verdict :** 🟢 **`MUSCLE FOCUS VIEW & CROP CONTRACT v0.1.0: LOCKED (DOCS-ONLY).`** 4 vues figées
(`front`/`back` partout, `lateral`/`section` N3-only, `section` sous amendement), philosophie de crop local
(N2 = crop du master ré-émis, N3 = artefact neuf), **intention de crop par 8 familles** ancrée sur les cas
d'exigence §16, `viewbox_local` figé au build géométrique (bump semver). **Aucun nombre de viewBox inventé,
aucune géométrie.** `PLATE GEOMETRY: NOT PRODUCED` · `ASSET INTEGRATION GATE: BLOCKED`.
