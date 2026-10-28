# Sb_DA_04_0_BODYMAP_INTAKE_RESOLUTION — une seule vérité sur le master BodyMap

**Statut** : 🟡 PR ouverte — tier `isolated` · **Branche** : `sb/da-04-0-bodymap-intake-resolution`
**Base** : canonique `bb539f8` · **Commande** : opérateur, 2026-10-28, « DA-04.0 — BodyMap Intake Resolution »
**Nature** : micro-tranche de **gouvernance**. Aucune exploration graphique, aucune intégration produit, aucune géométrie touchée.
**Verdict** : **OUTCOME B — NOT AUTHORIZED FOR APP INTEGRATION**

---

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

| Question | Options | Choix |
|---|---|---|
| Que vaut la présence du master ? | une autorisation implicite · **rien d'autre qu'une présence** | **une présence** : aucune approbation n'est déduite d'un fichier (brief, §1) |
| L'anatomie est-elle approuvée ? | conclure d'après la conformité au contrat · **ne statuer que sur une preuve d'approbation** | **sur preuve** : le dépôt n'en contient aucune → **non résolu, STOP** sur ce point |
| Corriger le contrat de mapping (`geometry_status: NOT YET PRODUCED`) ? | le corriger ici · **le signaler et proposer l'amendement** | **proposer** : c'est une spec versionnée, épinglée par une garde (`test_auren_body_zone_contract`) ; l'amender en silence est interdit (`CLAUDE.md §4`) |
| Corriger la provenance des planches Muscle Focus ? | la corriger ici · **la signaler** | **la signaler** : hors du master, et la corriger statuerait sur l'autorisation des planches, ce qui revient à l'opérateur |
| Comment empêcher la contradiction de revenir ? | relire à la main · **une garde de cohérence entre les quatre documents** | **la garde**, avec ses cas négatifs, plantée aussi sur le README d'origine |

| Risque | Parade |
|---|---|
| promouvoir l'asset sans le dire | registre : valeurs existantes **inchangées**, champs **additifs** seulement ; garde « statuts jamais approved » conservée |
| changer un fait de provenance pour faire passer le gate | aucun fait modifié ; une ligne datée ajoutée |
| toucher la géométrie | master et compact identiques à l'octet (`dbb57db3…` / `8024fd4c…`, garde existante) |
| une garde qui ne mord pas | le README d'origine, rejoué contre la garde neuve → `readme-says-no-master` |

## 2. Inventaire réconcilié

| Fichier | Présent | Octets | sha256 |
|---|---|---|---|
| `design/auren/source/bodymap/auren_bodymap_master.svg` | oui | 59 620 | `dbb57db333863434442b476277170017db442d83e2eced6e7191266ee9ecfa73` |
| `design/auren/exports/svg/auren_bodymap_compact.svg` | oui | 8 615 (budget 12 288) | `8024fd4ced62ca2010808bf85f94c3eaca4d334dde2b7c3b7683c3e5a4676c9a` |
| `design/auren/source/bodymap/auren_bodymap_mapping.yaml` | oui | 11 984 | `b6ef2c09cf1ef9dbe02802dcc991b7a18e7d7988fa0364f7c7ce4fb4f7e7a54a` (inchangé) |
| `design/auren/source/bodymap/auren_bodymap_source.yaml` | oui | — | modifié (champs additifs) |
| `design/auren/LICENSES/CC-BY-4.0.txt` | oui | 18 657 | `9ba9550a…` |
| `design/auren/LICENSES/bodyparts3d-NOTICE.md` | oui | 1 706 | `54081908…` |
| `design/auren/LICENSES/servier-medical-art-NOTICE.md` | oui | 1 697 | `b8d058db…` |

**IDs** (14) : `auren-bodymap`, `body-front-base`, `body-back-base`, et 11 `zone-*` : `pecs`, `delt_lat`, `delt_post`, `lats`, `upper_back`, `biceps`, `triceps`, `quads`, `posterior`, `calves`, `core`.

**Faces par zone** (convention `geom-<zone>-<front|back>-…`) : face — `pecs`, `biceps`, `quads`, `core` ; dos — `delt_post`, `lats`, `upper_back`, `triceps`, `posterior` ; les deux — `delt_lat`, `calves`. Bases : 1 face, 1 dos.

**Constructions du master** : `svg` 1, `g` 13, `path` 28 ; attributs `id`, `viewBox`, `fill` (`currentColor`, une fois, à la racine), `d` ; commandes `M` 39, `C` 1460, `L` 62, `Z` 39.

**Attribution** : BodyParts3D (base + 9 zones) et Servier Medical Art (`lats`, `core`), CC BY 4.0 ; textes exacts dans la provenance ; `ai_usage: none`.

**Statut enregistré** (registre) : `technical-intake-accepted-human-review-pending` · `runtime_authorization: blocked` · `professional_anatomical_review: not-claimed` · `legal_review: required` · `attribution_surface: not-yet-implemented` · `multi_source_consistency_review: recorded`.

**Trois vérités contradictoires trouvées** :
1. le README du dossier : « Aucun master anatomique n'est présent », puis « Master BodyMap accepté » — **corrigé** ;
2. le contrat de mapping : `geometry_status: "NOT YET PRODUCED"` et `male_neutral_v1 available: false`, alors que le master `male_neutral_v1` existe en design source ; la garde `test_exactly_three_body_variants_none_available` **exige** cette valeur — **non corrigé, amendement proposé** (§7) ;
3. les planches Muscle Focus (BodyParts3D) : servies au runtime **web** sur décision du propriétaire (`ACCEPT_INTERNAL_P0_WITH_CONSTRAINTS`, « controlled runtime integration », attribution CC BY affichée), alors que leur provenance dit « design-source only — NOT AUTHORIZED FOR APP INTEGRATION » et leur registre `asset_integration_gate: BLOCKED` — **non corrigé, signalé** (§7).

## 3. Statut anatomique — **NON RÉSOLU**

Ce que l'agent peut constater, et constate :
- les 11 zones sont exactement celles du contrat (taxonomie immuable, 6 macros) ;
- aucune zone n'est affectée à une face invraisemblable (pectoraux, biceps, quadriceps, abdominaux de face ; deltoïdes postérieurs, dorsaux, haut du dos, triceps, ischios / fessiers de dos ; deltoïdes latéraux et mollets visibles des deux côtés) ;
- `lats` et `core` (Servier) sont des zones de la taxonomie, `functional-body-zone`, `medical_claim: false` ;
- l'asset ne porte aucune revendication d'activation : une seule encre, aucun pourcentage, aucun dégradé.

Ce que l'agent **ne peut pas** établir : qu'**aucune zone n'est matériellement mal placée**. C'est un jugement anatomique ; aucune revue ne l'a rendu (`not-claimed`, `NOT YET REVIEWED`). **STOP sur ce point.**

## 4. Statut juridique / provenance — **INCOMPLET**

| Point | État |
|---|---|
| sources et licences | ✅ CC BY 4.0, textes et notices conservés |
| statut d'œuvre dérivée | ✅ enregistré (`derived-open-source`, modifications listées) |
| texte d'attribution exact | ✅ enregistré pour les deux sources |
| `ai_usage` | ✅ `none` (Blender, Potrace, Inkscape, Python) |
| cohérence des hashes | ✅ fichiers = registre = provenance |
| revue juridique | ❌ `legal_review: required` |
| surface d'attribution | ❌ aucune dans l'app mobile (seul le web en affiche une, pour les planches) |

## 5. Statut technique mobile — **PASSE**

SVG valide · `viewBox` `0 0 240 200` stable · IDs stables et uniques · aucun raster, aucune police, aucune URL, aucun script, aucune transformation, aucun style · une couleur `currentColor` passée par l'appelant · commandes de chemin standard · compact sous budget. `react-native-svg` (`Svg`, `G`, `Path`) le rend **sans mutation de géométrie** ; un recadrage par `viewBox` est le mécanisme prévu pour DA-04.1. Garde neuve : `test_master_is_in_the_react_native_svg_subset` (et ses deux cas négatifs).

## 6. Décision du gate

```
OUTCOME B — NOT AUTHORIZED FOR APP INTEGRATION
```

Manquent, exactement :
1. **une revue anatomique** — professionnelle, ou une décision explicite du propriétaire qui en tient lieu, avec ses contraintes ;
2. **une revue juridique** de l'œuvre dérivée CC BY 4.0 ;
3. **une surface d'attribution** dans l'app mobile.

Enregistré dans : le registre (`gate_resolution`, `gate_resolution_date`, `gate_technical_review`, `missing_for_runtime`), le README du dossier, la checklist d'intake, la provenance. La garde `test_authorization_is_one_truth` tient les quatre ensemble.

## 7. Prochaine action exacte — **à l'opérateur**

DA-04.1 **n'est pas démarré**. Deux voies ouvrent le gate ; l'agent n'en choisit aucune :

- **(a) revues externes** : un relecteur anatomique qualifié, une revue juridique de l'œuvre dérivée ;
- **(b) le précédent Muscle Focus** : une décision du propriétaire `ACCEPT_INTERNAL_WITH_CONSTRAINTS` pour le master, aux contraintes déjà tenues par les planches web — attribution CC BY visible dans l'app, mention « visualisation non médicale ; revue anatomique professionnelle non réalisée », aucune revendication d'activation.

Avec (b), une micro-tranche enregistre l'autorisation (date, base, hashes, contraintes) aux quatre endroits gardés, ajoute la surface d'attribution, puis DA-04.1 commence.

Deux décisions à prendre au passage :
- **amender le contrat de mapping** : `geometry_status` → produit en design source (Sb_ASSET_03.2), runtime non autorisé ; `male_neutral_v1` disponible en design source ; avec la garde qui l'épingle ;
- **réconcilier la provenance des planches Muscle Focus** avec leur intégration web effective.

En attendant : des recadrages et galeries de **design** à partir du master, hors runtime, sont permis ; l'emplacement BodyMap de la carte de série reste un emplacement nommé.

## 8. Réalisation

| Fichier | Changement |
|---|---|
| `design/auren/source/bodymap/README.md` | un seul « État actuel » ; ce qui est permis ; l'ancien état en historique daté |
| `design/auren/source/bodymap/auren_bodymap_source.yaml` | champs additifs ; aucune valeur existante changée |
| `design/auren/AUREN_ASSET_INTAKE_CHECKLIST.md` | section « Gate runtime statué » |
| `design/auren/AUREN_ASSET_PROVENANCE.md` | une ligne datée DA-04.0 |
| `docs/strategy/AUREN_VISUAL_BACKBONE.md` | §8.4 : roadmap corrigée par l'opérateur (DA-04.0 → DA-04.1 → DA-05.0 → DA-05.1 → gate DA-01 final ; MISSION pas avant) |
| `docs/strategy/SPEC_REGISTRY.md` | une ligne |
| `tests/test_auren_bodymap_master.py` | gardes : une vérité d'autorisation, sous-ensemble `react-native-svg`, faces par zone ; cas négatifs |

## 9. Post-vol

| Point | Résultat |
|---|---|
| gardes BodyMap, gouvernance, taxonomie, cadres, planches, protocole UI | **195 / 195** |
| master et compact | identiques à l'octet (garde existante) |
| README d'origine rejoué contre la garde neuve | rejeté : `readme-says-no-master` |
| `check_scope` | `ISOLATED` |

**Verdict :** le master BodyMap n'a plus qu'un état écrit. Il est techniquement prêt pour l'app mobile et **n'y est pas autorisé** : il manque une revue anatomique, une revue juridique et une surface d'attribution. La décision revient à l'opérateur.
