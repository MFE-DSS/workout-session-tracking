# Sb_ASSET_03B.2R — BodyParts3D Source-Contract Reset & Proven P0 Source Mapping

**Type** : spécification corrective normative — **DOCS-ONLY** (aucune géométrie, aucun binaire).
**Statut à l'issue de ce lot** : `SOURCE DOCTRINE: RESET LOCALLY` · `P0 SOURCE COVERAGE: PROVEN` ·
`PLAN-A GEOMETRY: NOT STARTED` · `PRODUCT REVIEW: AWAITING PLATE PRODUCTION` ·
`QUALIFIED ANATOMICAL REVIEW: REQUIRED_PENDING` · `GLOBAL ACCEPTANCE: BLOCKED` · `RUNTIME: BLOCKED`.
**Non une conclusion juridique** : `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED` ·
`PROFESSIONAL ANATOMICAL REVIEW: NOT CLAIMED` · `AI GENERATION OF ANATOMY: FORBIDDEN` ·
`GLOBAL BODYMAP: UNCHANGED` · `ASSET INTEGRATION GATE: BLOCKED` · `§5bis: NOT ENACTED`.

Autorité : confirmation produit humaine de Martin Feldmann (`decision_status: CONFIRMED`,
`confirmation_scope: production-method-and-governance-only`, `confirmed_at_utc: 2026-07-29T11:44:19Z`) —
voir le workspace opérateur externe `05_review/human/BODYPARTS3D_P0_PRODUCT_DECISIONS.md`. Cette confirmation
**autorise la production de candidats**, pas leur acceptation ni le runtime.

---

## A. Pourquoi Servier est superseded pour le body-fitting

Servier Medical Art reste **licite et utile** (CC BY 4.0) mais **inadapté comme socle géométrique des Regional
Plates P0** :

- kits d'illustration **fragmentés** (planches isolées, non solidaires) ;
- **pas de système de coordonnées cohérent** à l'échelle du corps entier ;
- **fitting macro-anatomique insuffisant** pour poser héros + contexte osseux dans un même repère ;
- inadapté comme **fondation géométrique régionale** déterministe.

Statut précis — **pas** « invalide » ni « inutilisable en tout contexte » :

```
SERVIER MEDICAL ART: SUPERSEDED FOR BODY-FITTING GEOMETRY
```

Ses candidats muscle antérieurs (Sb_ASSET_03B.2) restent **preuve historique valide**, non réécrite.

## B. Pourquoi BodyParts3D est retenu (PRIMARY DERIVATION)

- **système de coordonnées partagé corps-entier** (meshes solidaires d'un même repère) ;
- structures **représentées individuellement** (par concept) ;
- mapping **représentation + FMA exact** (traçabilité par identifiant, pas par nom de fichier) ;
- source **officielle DBCLS** (distribution BodyParts3D 4.0, obj_99) ;
- **licence CC BY 4.0** avec **preuves enregistrées** (voir `SOURCE_LEDGER`) — dérivés autorisés sous attribution ;
- pipeline **déterministe OBJ-based** possible (Plan A) ;
- **attribution requise** dans le livrable final ;
- `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED`.

```
PRIMARY DERIVATION: BodyParts3D 4.0 — official DBCLS distribution — CC BY 4.0
```

## C. Limites du modèle

- **référence masculin adulte** ; **non universelle** ;
- **pas une vérité anatomique canonique** ; **peut contenir des erreurs** (avertissement DBCLS) ;
- la **traçabilité BodyParts3D ≠ approbation anatomique** ;
- **revue anatomique qualifiée obligatoire** avant acceptation globale.

## D. Doctrine de dérivation à trois niveaux

**PLAN A — dérivation déterministe BodyParts3D.** Projection + simplification déterministes des meshes source
sélectionnés. À utiliser quand le résultat est anatomiquement cohérent, lisible, esthétiquement acceptable,
exploitable à 360 px.

**PLAN B — sculpting humain contrôlé conditionnel** (sur un dérivé BodyParts3D uniquement) :
- **human-only** ; **jamais exécuté automatiquement par l'agent** (l'agent prépare au plus un handoff) ;
- **aucune invention anatomique libre** ; **aucune insertion/séparation inventée** ; latéralité inchangée ;
- **preuve avant/après** ; **change log** ; **traçabilité source exacte** ; **revue anatomique qualifiée**.

**PLAN C — Open3DModel conditionnel, branche CC BY-SA** :
- **provenance séparée** ; **sorties séparées** ; **implications ShareAlike préservées et visibles** ;
- **aucun blanchiment dans la chaîne BodyParts3D** ; **NON autorisé pour le build P0 courant**.

## E. Doctrine IA

- **anatomie générative interdite** ; l'anatomie source **ne peut pas** être fournie en entrée générative ;
- **géométrie générée interdite** dans les assets finaux ;
- l'exploration de **style** (moodboard/compo/lighting/visual-language) peut rester **séparée et non géométrique**.

## F. Gates de revue

- **Martin** : revue produit, UX et visuelle ;
- **expert qualifié** : revue anatomique ;
- **les deux requis** avant acceptation globale ; **runtime bloqué**.

---

## P0 SOURCE MAPPING (prouvé — résolution exact-FMA, pas sous-chaîne)

Résultats du **build catalogue opérateur** (workspace externe `02_catalog/`), **pas** des faits généraux sur
toute distribution BodyParts3D. Vérification d'intégrité par OBJ SHA-256 :
`02_catalog/bodyparts3d_p0_selected_mapping.json` (35 représentations, 0 erreur, **0 match artériel/erroné**).
Terminologie officielle exacte conservée ; les libellés fitness sont des étiquettes d'affichage.

### CHEST
| rôle | nom officiel | représentation | FMA | latéralité |
|---|---|---|---|---|
| hero | pectoralis major | BP9382 | FMA13374 | left |
| hero | pectoralis major | BP6969 | FMA13373 | right |
| context | sternum | BP9392 | FMA7485 | unpaired |
| context | clavicle | BP8841 / BP9271 | FMA13323 / FMA13322 | left / right |
| context | humerus | BP9191 / BP9206 | FMA23131 / FMA23130 | left / right |

### SHOULDERS
| rôle | nom officiel | représentation | FMA | latéralité |
|---|---|---|---|---|
| hero | clavicular part of deltoid | BP8259 / BP7573 | FMA34681 / FMA34680 | left / right |
| hero | acromial part of deltoid | BP9075 / BP7571 | FMA34683 / FMA34682 | left / right |
| hero | spinal part of deltoid | BP8151 / BP5607 | FMA34685 / FMA34684 | left / right |
| context | scapula | BP9121 / BP9101 | FMA13396 / FMA13395 | left / right |
| context | clavicle | BP8841 / BP9271 | FMA13323 / FMA13322 | left / right |
| context | humerus | BP9191 / BP9206 | FMA23131 / FMA23130 | left / right |

### POSTERIOR
| rôle | nom officiel | représentation | FMA | latéralité |
|---|---|---|---|---|
| hero | gluteus maximus | BP8401 / BP5065 | FMA22329 / FMA22328 | left / right |
| hero | semitendinosus | BP9066 / BP4991 | FMA22359 / FMA22358 | left / right |
| hero | semimembranosus | BP7829 / BP4989 | FMA22449 / FMA22448 | left / right |
| hero | long head of biceps femoris | BP8331 / BP5575 | FMA45889 / FMA45888 | left / right |
| hero | short head of biceps femoris | BP8616 / BP5573 | FMA45892 / FMA45891 | left / right |
| context | hip bone | BP8950 / BP8768 | FMA16587 / FMA16586 | left / right |
| context | femur | BP9042 / BP8920 | FMA24475 / FMA24474 | left / right |
| context | patella | BP8378 / BP8390 | FMA24487 / FMA24486 | left / right |

**Couverture** : chest `PASS` · shoulders `PASS` · posterior `PASS` · résolution `exact-FMA-curated` ·
conflits non résolus `0`. Archives : ISA `40665852…c7cd409e`, PART-OF `9fbc713f…3eb61c97`.

### Résumé catalogue (build opérateur)
```
ISA representations:               2905
PART-OF representations:           1368
Deduplicated representations:      3432
Representations present in both:    841
Unresolved conflicts:                 0
```
(Ces chiffres résultent du build opérateur ; ils ne sont pas des faits généraux sur toute distribution
BodyParts3D.) Le catalogue complet (3 432 entrées) **n'est pas versionné** — seul ce mapping P0 sélectionné + les
compteurs le sont.

---

## SEGMENTATION CONTRACT (nouveaux faits prouvés)

### Pectoralis major — `source_mesh_separately_segmented: false`
La source fournit le **pectoralis major gauche/droit entier**. Les parts contractuelles
`part-pecs-clavicular` / `part-pecs-sternocostal` restent `partition_kind: functional-visual-region`. Toute
partition future doit être **déterministe, réversible au masque source original, traçable, visiblement
divulguée, revue**, et **jamais présentée comme meshes source distincts**.

### Deltoid — `source_mesh_separately_segmented: true`
La source fournit des parts **distinctes** — clavicular / acromial / spinal — pour les deltoïdes gauche et droit.
Mapping vers les parts contractuelles :
```
clavicular part of deltoid → part-delt_lat-anterior   (libellé fitness : antérieur)
acromial part of deltoid   → part-delt_lat-lateral    (libellé fitness : latéral)
spinal part of deltoid     → part-delt_post-posterior (libellé fitness : postérieur)
```
Les libellés d'application sont des **étiquettes d'affichage fitness** ; la **terminologie officielle et les IDs
source restent l'autorité de provenance**. Ces parts **ne sont pas** une partition algorithmique — ce sont des
meshes source segmentés.

### Posterior
Représentations musculaires sourcées exactes. Le **groupe ischio-jambier** est composé de structures sourcées
(semitendinosus, semimembranosus, chefs long/court du biceps femoris) mais la plaque N2 **ne doit pas** impliquer
un mesh anatomique unifié non sourcé ni une précision d'activation non supportée.
```
N2 regional mode:  muscle-heads    (inchangé)
N3 posterior mode: grouped-honest  (inchangé)
```
Ces modes **ne sont pas inversés**.

---

## Verdict

**`SOURCE CONTRACT: RESET LOCALLY (BodyParts3D-primary) / UNCOMMITTED`** · **`P0 SOURCE COVERAGE: PROVEN`**
(exact-FMA, 35 reps, 0 conflit) · **`P0 GEOMETRY: NOT PRODUCED`** · revue anatomique qualifiée `REQUIRED_PENDING`
· acceptation produit `AWAITING PLATE PRODUCTION` · `ASSET INTEGRATION: BLOCKED` · `RUNTIME: BLOCKED` ·
`§5bis: NOT ENACTED`. Le lot géométrie futur consomme cette doctrine mais reste **revu indépendamment**.
