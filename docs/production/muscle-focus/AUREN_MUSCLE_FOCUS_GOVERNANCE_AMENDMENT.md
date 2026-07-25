# AUREN — Muscle Focus Governance Amendment (`Sb_ASSET_03B.1`)

**Type** : **amendement de gouvernance normatif** (spécifié, **enactment gaté**) — **DOCS-ONLY**. Fige la
**clause exacte** qui autorisera fibres/insertions/coupe **uniquement sur les surfaces plaque**, **sans modifier
le contrat du BodyMap global** et **sans produire aucune géométrie**. `ASSET INTEGRATION GATE: BLOCKED`.
**Cible** : `design/auren/AUREN_STYLE_RULES.md` §5 (Anatomie) — **relaxation additive bornée**.
**Références** : spec §15 · `AUREN_STYLE_RULES §4/§5/§9` · adversarial Axe E #5/#6.

---

## 1. Motif (contradiction doc-vs-doc à neutraliser)

`AUREN_STYLE_RULES §5` interdit **à plat** « veines/**fibres**/organes » et « **aucune activation mesurée** » sur
l'anatomie ; `§4` interdit « **texte dans un SVG** (hors marque) ». Or les N3 (spec §8/§16) affichent
**fibres**, **insertions**, un **schéma de raccourcissement** et une **vue `section` (coupe locale)**. Sans
amendement, **contradiction directe**. Le gabarit plaque spécifiant déjà `overlay-fiber`/`overlay-insertion`/
`section`, la contradiction est **déjà latente** dans les docs versés (`ff9541a`).

## 2. Clause exacte à enacter (bornée aux surfaces plaque)

> **§5bis — Surfaces Muscle Focus (N2/N3, `auren-plate-*`) — carve-out gouverné.**
> Par exception **strictement bornée aux surfaces Muscle Focus Plate** (Niveaux 2 et 3, IDs `auren-plate-*`),
> sont **autorisés, schématiques et non médicaux** : (a) la **direction de fibres** (vecteurs le long de l'axe
> réel, **jamais** histologie/veines) ; (b) les **marqueurs d'origine/insertion** ; (c) un **schéma de
> raccourcissement fonctionnel** (sens le long des fibres — **jamais** EMG/activation/%/recrutement) ; (d) une
> **vue `section` (coupe locale) schématique** — **sans viscère, sans organe, sans rendu médical** (ex. corset
> transverse, chefs empilés).
> **Restent interdits partout** : rendu médical réaliste, activation mesurée/EMG, viscères/organes, gradients/
> ombres, détails sexuels, visage détaillé.
> **Le contrat du BodyMap global (silhouette master) reste inchangé** : `§5` (vues orthographiques, non médical,
> pas de fibres/organes) **continue de lier** `auren-bodymap` et le compact global. Le carve-out **ne s'applique
> qu'aux plaques**.
> **Texte hors SVG** (`§4`) : la **caption** (module 9) vit dans le **HTML adjacent**, jamais dans le SVG de la
> plaque. La caption **reflète** tout fait rendu par un overlay (invariant `caption_mirrors_overlay`).

## 3. Bornes dures (ce que l'amendement N'autorise PAS)

- **N'autorise pas** de toucher le master global, ni une 12ᵉ zone, ni un code métier hors des 11.
- **N'autorise pas** l'activation mesurée, l'EMG, le %, le recrutement, la magnitude (jetons interdits — cf.
  Overlay Contract §2).
- **N'autorise pas** viscères/organes même en `section` (coupe **schématique** seulement).
- **N'autorise aucune géométrie** dans ce build : le carve-out **spécifie** une permission future ; il ne
  **produit** rien.

## 4. Guard test requis (co-écrit à l'enactment)

À l'enactment (§5), un test de gouvernance (frère de `test_auren_bodymap_master.py` /
`test_auren_asset_governance.py`) devra asserter :
1. le carve-out **nomme explicitement « plate/N2/N3 » / `auren-plate-*`** (portée bornée, pas de fuite globale) ;
2. `§5` du master **reste** un interdit à plat pour `auren-bodymap` (la relaxation ne le touche pas) ;
3. aucune caption/label/registre plaque ne contient un **jeton interdit** (`EMG`/`%`/`activation`/`recruitment`/
   `mesure`/`clinique`) — miroir de `test_registry_status_never_approved` ;
4. `caption_mirrors_overlay == true` et caption **hors SVG**.

## 5. Enactment — **gaté, déféré** (décision de scope)

**État : `AMENDMENT: SPECIFIED / NOT YET ENACTED`.** L'édition réelle de `design/auren/AUREN_STYLE_RULES.md` §5
est **différée au build géométrie `Sb_ASSET_03B.2`** (première plaque productible), pour deux raisons :

1. **Co-écriture avec le guard test** : enacter la relaxation **sans** son test serait la faiblesse « prose-only »
   (adversarial #6). On enacte la règle **au moment où** la surface qu'elle gouverne existe **et** où son test
   est écrit.
2. **Posture du build 03B.1** : ce build est **`docs/**` strict / 0 géométrie / gate BLOCKED**. Éditer
   `design/auren/` ferait sortir le commit du `paths-ignore: ['docs/**']` (CI 3 jobs au lieu du skip légitime).

**Neutralisation immédiate de la contradiction** (côté docs, sans enactment) : tant que l'amendement n'est pas
enacté, les overlays `fiber`/`insertion`/`shortening` et la vue `section` sont **NON PRODUCTIBLES** (cohérent
`ASSET INTEGRATION GATE: BLOCKED` / `0 géométrie`). Le gabarit, le View & Crop Contract et l'Overlay Contract
**pointent tous** vers cet amendement et marquent ces éléments « sous amendement §5 ». La contradiction ne
**ship** donc pas : elle est **explicitement gouvernée et gelée**.

> **Alternative disponible (décision opérateur)** : enacter le carve-out **dès maintenant** dans
> `design/auren/AUREN_STYLE_RULES.md` (édition additive `§5bis`, texte §2 ci-dessus). Effet : le commit touche
> `design/auren/` → **CI 3 jobs** (plus de skip docs), et le guard test resterait à écrire au build géométrie.
> **Défaut retenu : déféré** (docs-only préservé). À basculer sur simple GO.

---

## Verdict

**Verdict :** 🟢 **`MUSCLE FOCUS GOVERNANCE AMENDMENT: SPECIFIED / ENACTMENT GATED (DOCS-ONLY).`** La clause
`§5bis` est figée mot pour mot : carve-out **borné aux surfaces plaque** (fibres, insertions, raccourcissement
fonctionnel, **vue `section` schématique sans viscère**), **master global inchangé**, **texte hors SVG**, +
**guard test requis** co-écrit à l'enactment. Enactment **déféré à `Sb_ASSET_03B.2`** pour préserver la posture
`docs/**` et co-écrire l'enforcement ; contradiction **neutralisée** (éléments non productibles tant que gate
BLOCKED). `ASSET INTEGRATION GATE: BLOCKED`.
