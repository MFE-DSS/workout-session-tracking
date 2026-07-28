# Sb_ASSET_03B.2 — P0 Regional Plate Production Package — SPEC

**Type** : PACKAGE DE PRODUCTION + CONTRAT D'INTAKE — **DOCS-ONLY (ce lot)**. Rend la production des 3 plaques
P0 **exécutable** par le toolchain opérateur, et fige le **contrat d'intake** (SVG / descripteurs / guard /
preview) sans produire ni géométrie ni faux artefact. `ASSET INTEGRATION GATE: BLOCKED`.
**Date** : 2026-07-27 · **Base** : `c70bdb0` · **Worktree** : `work/sb-asset-03b-2-p0-regional-plates`.
**Amont** : `Sb_ASSET_03B.1` (blueprint & plate contract, `c70bdb0`) — ID Contract v0.1.0, Descriptor Schema
v0.1.0, View & Crop Contract, P0 Blueprints (7), Overlay/A11y/Mobile Contract, Source Ledger, Governance
Amendment `§5bis`.

> **`PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED`** · **`PROFESSIONAL ANATOMICAL REVIEW: NOT CLAIMED`** ·
> **`GLOBAL BODYMAP: UNCHANGED`** · **`AI GENERATION OF ANATOMY: FORBIDDEN`**.

---

## 0. Décision structurante — production géométrique par le toolchain opérateur

Le GO propose de « produire 3 géométries P0 ». Or la géométrie anatomique **ne peut pas** être produite par
l'assistant IA sans violer les règles dures du programme :

- **§6 interdit** « génération IA de l'anatomie » et « reconstruction algorithmique anatomique sans source
  humaine vérifiable » ;
- le **Descriptor Schema** impose `ai_usage: NONE` ;
- la géométrie doit être **redessinée à partir de figures Servier/OpenStax réellement acquises** (SHA-256 réel).

Des `<path>` tapés par l'IA seraient (a) de l'anatomie générée algorithmiquement (interdite), (b) incompatibles
avec `ai_usage: NONE` honnête, (c) sans provenance de source acquise, (d) presque certainement des formes
trompeuses (« pectoraux = poumons »). **Décision opérateur retenue** : **la géométrie est produite par le
toolchain opérateur** (Blender / Potrace / Inkscape sur figures licenciées), exactement comme le master BodyMap
en `Sb_ASSET_03.1`.

**Conséquence de séquençage (motif 03.1 → 03.2)** :

| Lot | Contenu | Producteur | Statut |
|---|---|---|---|
| **Ce lot (03B.2 — package)** | Ce brief exécutable + protocole de revue + contrat d'intake + docs directeurs | Assistant (docs) | **CE COMMIT** |
| **Production géométrique** | 3 SVG P0 + acquisition sources + hashes | **Opérateur (toolchain réel)** | HORS GIT / À LIVRER |
| **Intake atomique (03B.2 — intake)** | `§5bis` enactment + guard test + descripteurs/registry/manifest/preview à provenance réelle + intake | Assistant, sur GO, **sur la géométrie livrée** | GATED |

**`§5bis` n'est PAS enacté dans ce lot** : son enactment reste **couplé atomiquement** au guard test et à la
géométrie (principe figé en 03B.1 pour éviter une relaxation « prose-only »). Il sera enacté à l'intake.

## 1. Mission (périmètre de CE package)

Livrer le **brief de production exécutable** des 3 Regional Plates P0 et le **contrat d'intake** qui les
recevra :

- `auren-plate-region-chest` (front) · `auren-plate-region-shoulders` (front+back) ·
  `auren-plate-region-posterior` (back).

**Ce package NE livre PAS** (aval, gated) : la géométrie SVG · l'enactment `§5bis` · le guard test vert · les
descripteurs/registry/manifest à hash réel · la preview · les plaques N3 · les overlays fibres/insertion/
contraction · les vues lateral/section · toute intégration runtime · toute approbation anatomique/juridique ·
tout statut `approved`.

## 2. Étape 0 — brainstorming / arbitrage (5 axes, synthèse unique)

Axes cadrés : **A** Anatomie & sources · **B** Géométrie vectorielle & crops · **C** Contrats/IDs/gouvernance ·
**D** Mobile/a11y/surface de revue · **E** Adversarial (sécurité SVG, reproductibilité). Décisions :

- **Pectoraux ≠ poumons** : **éventail convergent** — bande claviculaire (fibres ~horizontales depuis la
  clavicule) + bande sterno-costale (fibres montant en éventail depuis le sternum) narrowing vers **un seul
  nœud d'insertion humérale latéral**. Sternum = axe vertical fin ; clavicule = repère diagonal fin. Le **nœud
  de convergence latéral unique** est le garde-fou anti-cliché.
- **Deltoïde 3 faisceaux** : chaque chef ancré à son os (antérieur→clavicule, latéral→acromion,
  postérieur→épine scapulaire), convergence commune → tubérosité deltoïdienne ; front = ant+lat, back =
  post+lat. L'**ancrage osseux** rend les 3 chefs lisibles comme **un** muscle sous plusieurs angles.
- **Postérieur** : crop bassin→cuisse ; bassin = contexte osseux fin, fessier = masse superficielle haute,
  ischios = groupe long vers un genou-repère fin. **Grouped-honest** (pas de localisation par faisceau).
- **Héros vs contexte sans couleur codée** : héros = forme **remplie** (classe / `currentColor`) ; contexte
  (os, voisin) = **trait seul / opacité réduite** ; distinction par remplissage + opacité + structure, jamais
  par hex métier.
- **BodyMap = repère seulement** (règle opérateur §5, ci-dessous) : posture neutre + échelle + cadre spatial
  réutilisés ; géométrie musculaire **redessinée localement** ; **jamais** d'agrandissement mécanique du master
  ni de recopie d'ID `zone-*`/`geom-*`.
- **360 px** : formes réductibles, trait constant, contraste graphite/ambre, ≤ 3 teintes, captions dans le HTML
  adjacent (hors SVG) ; test 360 px + zoom 200 %.
- **Repro sans binaire committé** : identité source + SHA-256 au registry, PPTX/ZIP **hors Git**, acquisition +
  transformations + versions d'outils documentées ; ne committer que SVG/JSON/HTML/docs.

**Options rejetées (risques)** : agrandissement mécanique de la géométrie BodyMap (rejetée par revue humaine ;
viole §5 opérateur) · tracing SA/NC (Z-Anatomy, OpenStax 2ᵉ = contamination) · IA-génération d'anatomie
(interdite §6 ; attaches hallucinées) · hex métier dans le SVG (viole contrat) · entrée manifest agrégée (§11
exige 3 entrées) · commit de binaires source (guards).

## 3. Clarification « crop du master » pour N2 (règle opérateur §5)

Le BodyMap actuel est **accepté comme design source**, **non approuvé anatomiquement**, **non autorisé runtime**,
**jugé visuellement insuffisant** → **pas** un master anatomiquement validé. Donc, pour N2 :

- il fournit **repère spatial, échelle, posture neutre, cadre** ;
- sa **géométrie musculaire n'est PAS agrandie mécaniquement** ;
- les formes musculaires P0 sont **redessinées localement** depuis les sources éligibles ;
- **aucun** ID `zone-*`/`geom-*` du master n'est recopié ; ré-émission sous `auren-plate-*` ;
- **aucune** correction rétro-propagée dans `auren_bodymap_master.svg` — **`GLOBAL BODYMAP: UNCHANGED`**.

Cette clarification **ne modifie pas** le contrat métier des 11 zones.

## 4. Sources & licences (Source Ledger canonique)

**Dérivation autorisée** : **Servier Medical Art** (images médicales seules, CC BY 4.0 ; logos/marque/UI/site
exclus ; attribution + description des modifications obligatoires) · **OpenStax A&P 1ʳᵉ éd.** (CC BY 4.0 ;
acquisition + sélection de figure explicites ; **jamais** injecté dans un système génératif ; **jamais** la
2ᵉ éd. CC BY-NC-SA).
**Validation seule (jamais dérivé)** : BodyParts3D · NLM Visible Human (selon ses T&C) · Z-Anatomy · atlas/
logiciels commerciaux = références non dérivées.
**Interdits** : OpenStax 2ᵉ éd. · tracing d'une source SA/NC/copyright · MuscleWiki/BioDigital/Muscle&Motion/
Complete Anatomy/BioRender comme géométrie · **IA-génération d'anatomie** · reconstruction algorithmique sans
source humaine vérifiable.

**À enregistrer par plaque (au registry, à l'intake)** : URL officielle · titre exact · édition/version · date
d'accès · licence · fichier/figure précis · **SHA-256 du fichier acquis** · éléments sélectionnés ·
transformations · auteur de l'adaptation · `ai_usage: NONE`. Archives brutes binaires **hors Git** (identité +
hash consignés).

## 5. Brief géométrique par plaque (cibles exactes du toolchain)

### 5.1 `auren-plate-region-chest` — front — crop demi-torse
**Montrer** : sternum (axe central) · clavicule (repère) · chef claviculaire · chef sterno-costal ·
convergence latérale vers **une** insertion humérale · distinction héros/contexte.
**Éviter** : deux ovales miroir · aspect poumons · plastron · rendu médical réaliste · faux faisceaux non
sourcés. **Parts** : `part-pecs-clavicular`, `part-pecs-sternocostal`.

### 5.2 `auren-plate-region-shoulders` — front + back — un SVG, groupes séparés namespacés
**Montrer** : clavicule · acromion · épine scapulaire · faisceau antérieur · latéral · postérieur · insertion
deltoïdienne commune · continuité du **même** deltoïde sous plusieurs angles.
**Éviter** : 3 muscles indépendants · faisceaux flottants sans os · épaule ronde générique · fusion du
postérieur dans le haut du dos. **Parts** : `part-delt_lat-anterior`, `part-delt_lat-lateral`,
`part-delt_post-posterior`.

### 5.3 `auren-plate-region-posterior` — back — crop bassin→cuisse — mode muscle-heads
**Montrer** : bassin (contexte) · fessier superficiel · groupe ischio-jambier · séparation hanche/cuisse ·
continuité de chaîne postérieure · genou-repère sans détail hors sujet.
**Éviter** : corps entier · « bas du corps générique » · fusion fessier/ischios · localisation par faisceau
prétendue. **Parts** : `part-posterior-gluteus`, `part-posterior-hamstring`. **Mode** : muscle-heads.

> **Clarification normative (mode N2)** : `muscle-heads` est le **mode contractuel N2** de cette plaque
> régionale ; les **parts restent `part-posterior-gluteus` + `part-posterior-hamstring`** ; la plaque **ne
> subdivise pas** le groupe ischio-jambier en chefs non sourcés ; cette **retenue visuelle n'est pas** le mode
> `grouped-honest` ; **`grouped-honest` reste réservé à `auren-plate-muscle-posterior` (N3)** — blueprint
> `Sb_ASSET_03B.1` inchangé.

## 6. Contrat SVG (intake — chaque plaque)

**Obligatoire** : `<svg>` valide · root ID exact · `viewBox` numérique local stable · IDs uniques · enfants
préfixés root + `--` en surface composée · paths/groups réguliers · classes ou `currentColor` · opacité/
structure héros↔contexte · 0 réseau · newline final · XML bien formé.
**Interdit** : `zone-*` · `auren-bodymap` · IDs master · `<script>` · handlers · `<foreignObject>` · `<image>` ·
`<text>`/`<tspan>` · `<use>` · gradient · filtre · ombre · animation · bitmap/base64 · URL externe · hex métier ·
attribut `score/value/activation/emg/recruitment` · texte anatomique dans le SVG. Captions/labels = HTML
adjacent.
**P0 = clean** : `markers: []` · aucun overlay fiber/insertion/contraction · aucune vue lateral/section · aucun
lien interactif runtime.

## 7. Contrat descripteurs / registry (intake)

3 descripteurs `design/auren/source/muscle-focus/descriptors/auren_plate_region_{chest,shoulders,posterior}.json`
(Descriptor Schema v0.1.0). Constantes : `level: 2-regional` · `schema_version: 0.1.0` · `markers: []` ·
`exercise_link_granularity: zone` · `exercise_link_mode: list` · `attribution_required: true` · `ai_usage: NONE`
· `non_medical: true` · `scored: false` · `caption_mirrors_overlay: true`. `region_key_kind` : chest/shoulders =
`macro` ; posterior = `zone`. Vues : chest `[front]` · shoulders `[front, back]` · posterior `[back]`.
**Mode (P0 Regional)** : `chest` = `muscle-heads` · `shoulders` = `muscle-heads` · `posterior` = `muscle-heads`
— **aucune** plaque Regional P0 n'est `grouped-honest` ; `grouped-honest` reste réservé au N3
`auren-plate-muscle-posterior` (blueprint `Sb_ASSET_03B.1`, inchangé).
Registry `design/auren/source/muscle-focus/auren_muscle_focus_p0_regional_source.json` : 3 plaques exactes,
path · SHA-256 · taille · viewBox · vues · parts · sources · licence · attribution · modifications · tooling ·
statut de revue · runtime authorization · anatomical/legal/mobile review · AI usage. **Statuts** :
`status: technical-intake-accepted-human-anatomical-review-required` (à l'intake) · `runtime_authorization:
blocked` · `professional_anatomical_review: not-claimed` · `legal_review: required` · `mobile_review: required`
· `integration_authorized: false`. **Aucun** `approved`/`legally-cleared`/`runtime-integrated`/
`professionally-anatomically-validated`.

## 8. Contrat guard test (intake) — `tests/test_auren_muscle_focus_p0_regional.py`

26 assertions positives (3 SVG exacts · 3 descripteurs · roots uniques · aucun `zone-*`/ID master · enfants
uniques · aucune balise/URI/comportement interdit · aucun hex métier · aucune caption dans le SVG · conformité
aux 3 blueprints · `markers==[]` · vues exactes par plaque · zone/macro/`region_key_kind` exacts · parts
exactes · `exercise_link_granularity==zone` · `exercise_link_mode==list` · `scored==false` · `non_medical==true`
· `caption_mirrors_overlay==true` · hashes registry↔fichiers · licence/provenance présentes · runtime bloquée ·
aucun statut gate-crossing · `§5bis` présent mot-pour-mot & borné · §5 master inchangé sémantiquement · preview
3 captions/attributions/360 px · budgets). **Cas négatifs** prouvant l'échec sur : duplicate ID · `zone-pecs`
injecté · script · URL externe · `#C8A24B` dans le SVG · `scored: true` · `exercise_link_granularity: part` ·
`markers` non vide N2 · vue `lateral` N2 · `approved` · caption-mirror désactivé · jeton `EMG`/`%` · suppression/
élargissement non borné de `§5bis`. Allowlists exactes (3 SVG + 4 JSON), **aucun wildcard permissif**. Le guard
est **fail-closed** tant que la géométrie n'existe pas.

## 9. Budgets (à figer à l'intake)

Chaque SVG P0 : cible **≤ 20 Ko** (à confirmer sur la géométrie réelle ; sinon justifier). Preview HTML
autonome, 0 CDN/webfont/JS-lib. Descripteurs/registry JSON compacts. Ces budgets sont **provisoires** et seront
arrêtés sur les fichiers réels à l'intake.

## 10. Enactment `§5bis` (à l'intake, atomique)

À l'intake, insérer **mot-pour-mot** la clause `§5bis` figée dans
[`../production/muscle-focus/AUREN_MUSCLE_FOCUS_GOVERNANCE_AMENDMENT.md`](../production/muscle-focus/AUREN_MUSCLE_FOCUS_GOVERNANCE_AMENDMENT.md)
**après §5** de `design/auren/AUREN_STYLE_RULES.md`, bornée (N2/N3 · `auren-plate-*` · fibres schématiques ·
marqueurs origine/insertion · raccourcissement non mesuré · section locale sans viscère · caption HTML hors SVG
· BodyMap global inchangé), **avec** le guard qui l'assert. Puis amendement → `AMENDMENT: ENACTED IN
Sb_ASSET_03B.2 / GUARD: IMPLEMENTED / GLOBAL BODYMAP: UNCHANGED`. **N'ouvre pas** l'intégration runtime.

## 11. Manifest / provenance / licences (intake)

`AUREN_VISUAL_ASSET_MANIFEST.md` : type gouverné **`anatomical-regional-plate`**, **3 entrées distinctes**
(jamais agrégées), version 0.1.0, `status: anatomical-review-required`, `source_file` réel, `runtime_file: NOT
APPLICABLE`, surfaces design/review seules, licence+attribution, review technique passée, revues humaine/
anatomique/juridique/mobile non passées, consumers `NOT YET INTEGRATED`. `AUREN_ASSET_PROVENANCE.md`,
`AUREN_ASSET_INTAKE_CHECKLIST.md`, `LICENSES/README.md` mis à jour ; `LICENSES/openstax-ap1-NOTICE.md` ajouté si
besoin (**ne pas** dupliquer `CC-BY-4.0.txt`). Entrées BodyMap/Tabler/PWA/shell **inchangées**.

## 12. Surface de revue (intake) — `design/auren/previews/muscle-focus/auren-muscle-focus-p0-regional-v0.1.0.html`
Autonome (0 serveur/CDN/webfont/JS-lib), fond graphite, héros ambre via CSS de preview, contexte graphite/gris,
3 plaques (shoulders front+back), cadres 360 px simulés + desktop, captions FR (§ ci-dessous), statut de revue,
attribution, fallback no-JS (toutes vues inspectables). Ne pas l'intégrer à l'app.

**Captions P0 (figées)** — Chest : « Pectoraux — chef claviculaire et chef sterno-costal convergeant vers
l'humérus. Rôle général : adduction et flexion de l'épaule. Représentation non médicale et non mesurée. » ·
Shoulders : « Épaules — deltoïde, faisceaux antérieur, latéral et postérieur en contexte claviculaire et
scapulaire. Représentation non médicale et non mesurée. » · Posterior : « Chaîne postérieure — fessiers et
ischio-jambiers représentés comme groupe fonctionnel. Rôle général : extension de hanche et flexion du genou.
Localisation par faisceau non prétendue. Représentation non médicale et non mesurée. »

## 13. Critères d'acceptation (intake)
Guard vert (positif+négatif) · `check_scope` conforme au tier réel · `check_spec_protocol` PASS · ruff clean ·
suite pytest verte · `§5bis` enacté & borné · §5 master inchangé · `GLOBAL BODYMAP: UNCHANGED` · 3 SVG conformes
au contrat · descripteurs conformes aux blueprints · registry hashes ↔ fichiers · preview 360 px/desktop/no-JS ·
aucun statut mensonger · **livraison par PR** (pas de push direct).

## 14. Non-goals / gates
Aucune plaque N3 · aucun overlay · aucune vue lateral/section · aucune intégration runtime/route/template/
composant · aucune approbation anatomique/juridique · aucun `approved`. `REGIONAL PLATE GEOMETRY: NOT PRODUCED
(this lot)` · `HUMAN ANATOMICAL REVIEW: REQUIRED / NOT STARTED` · `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED` ·
`ASSET INTEGRATION GATE: BLOCKED`.

## 15. Procédure de revue humaine
Décision **par plaque** (CHEST / SHOULDERS / POSTERIOR : ACCEPTED | REVISION REQUIRED | REJECTED), axes de revue
et règle « global ACCEPTED ⇔ 3/3 acceptées », détaillés dans
[`../production/muscle-focus/AUREN_MUSCLE_FOCUS_P0_REGIONAL_REVIEW_PROTOCOL.md`](../production/muscle-focus/AUREN_MUSCLE_FOCUS_P0_REGIONAL_REVIEW_PROTOCOL.md).

---

## Verdict

**Verdict :** 🟢 **`Sb_ASSET_03B.2: OPEN — PHASE 1 PRODUCTION PACKAGE READY / GEOMETRY PENDING (AWAITING OPERATOR TOOLCHAIN)`.** Le brief
exécutable des 3 Regional Plates P0 (chest/shoulders/posterior), le contrat SVG/descripteur/registry/guard/
preview, les budgets et la procédure de revue sont figés ; la clarification « crop du master » est documentée
sans toucher le contrat des 11 zones. **La géométrie est produite par le toolchain opérateur** (sources Servier/
OpenStax acquises) ; **`§5bis` enactment + guard test + descripteurs/registry/manifest/preview à provenance
réelle sont livrés atomiquement à l'intake**, sur GO, sur la géométrie livrée. **Aucune géométrie, aucun faux
`ai_usage: NONE`, aucune approbation, aucune intégration.** `REGIONAL PLATE GEOMETRY: NOT PRODUCED (this lot)` ·
`GOVERNANCE AMENDMENT: SPECIFIED / ENACTMENT SCHEDULED AT INTAKE (ATOMIC w/ GUARD + GEOMETRY)` · `GLOBAL BODYMAP:
UNCHANGED` · `PROFESSIONAL ANATOMICAL REVIEW: NOT CLAIMED` · `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED` ·
`ASSET INTEGRATION GATE: BLOCKED`. **Prochaine action (sur GO)** : `GO OPERATOR` (production géométrie) puis
`GO INTAKE — Sb_ASSET_03B.2` (enactment + guard + intake atomique).
