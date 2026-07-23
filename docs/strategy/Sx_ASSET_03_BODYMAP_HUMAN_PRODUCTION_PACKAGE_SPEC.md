# Sx_ASSET_03 — BodyMap Human Production Package — SPEC

**Type** : SPEC / PRODUCTION PACKAGE / OFFICIAL-SOURCE RESEARCH — **DOCS-ONLY**, NO SVG, NO IMAGE, NO APP CHANGE
**Statut** : 🟠 **AMENDED — SOURCE-REUSE-FIRST** (2026-07-23) — spec versée en `66d18d4`, **amendée** par
décision opérateur ; la production n'est plus commandée à un illustrateur en première intention.
**Programme** : `Sx_ASSET` · **3ᵉ cycle** · **Date** : 2026-07-22, **amendée 2026-07-23** · **Baseline** :
`cf41188` (closeout Sx_ASSET_02) ; posé sur HEAD canonique réel `062ee92` (avance Custom EKB_03, indépendante).

> `Sx_ASSET_01` et `Sx_ASSET_02` restent **CLOSED**. `Sx_UI` reste **CLOSED**. Ce cycle transforme le **contrat
> sémantique BodyMap (déjà accepté, immuable)** en un **dossier de production exécutable**. **Il ne
> produit pas le master SVG.** `ASSET INTEGRATION GATE: BLOCKED`. `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED`.

---

## 0. AMENDEMENT 2026-07-23 — SOURCE-REUSE-FIRST

**Décision opérateur** : le BodyMap **n'est plus commandé en première intention** à un illustrateur externe.
La stratégie devient **SOURCE-REUSE-FIRST** — dériver un master simplifié depuis des ressources anatomiques
existantes, créées par des humains, **ouvertes, traçables et compatibles commercial**.

**Fait déclencheur** : la due diligence du 2026-07-22 avait classé **BodyParts3D en CC BY-SA 2.1 Japan**
d'après un **miroir GitHub figé en 2011**, et en avait conclu que toute dérivation était écartée. La page de
licence **officielle DBCLS** (mise à jour **2025-02-27**) donne **CC BY 4.0 International** — **sans
ShareAlike**. La dérivation vers un master propriétaire est donc **licite sous attribution**.

| | Avant (2026-07-22) | Après amendement (2026-07-23) |
|---|---|---|
| Méthode de production | commande externe à un illustrateur nommé | **dérivation** depuis sources ouvertes |
| BodyParts3D | référence spatiale, dérivation **écartée** | **`PRIMARY DERIVATION SOURCE`** (CC BY 4.0) |
| Préalable humain | illustrateur + relecteur nommés **obligatoires** | **illustrateur nommé : plus un préalable** |
| Revue anatomique | professionnelle **obligatoire** | **cohérence multi-sources REQUISE** ; professionnelle **non revendiquée / optionnelle** |
| Nature du master | œuvre humaine **originale** | **œuvre dérivée** sous attribution CC BY 4.0 |
| Prochain pas | `OPERATOR_ASSET_03.1` | **`Sb_ASSET_03.1`** ; `OPERATOR_ASSET_03.1` = **repli** |

**Ce qui ne change pas** : le contrat sémantique (11 zones, 6 macros, `unknown` = état, 14 IDs stables,
séparation `RADAR_AXES`) · la grille `viewBox 0 0 240 200` · la direction artistique (instrument biomécanique,
non médical) · les agrégats honnêtes · les 5 états pilotés runtime · l'accessibilité décorative · les budgets ·
les 32 previews · `ASSET INTEGRATION GATE: BLOCKED`.

**Nouveaux documents opposables** :
[stratégie de réutilisation](../research/AUREN_BODYMAP_OPEN_SOURCE_REUSE_STRATEGY.md) ·
[spec `Sb_ASSET_03.1`](Sb_ASSET_03_1_OPEN_ANATOMY_SOURCE_DERIVATION_SPEC.md).

**Dette créée par l'amendement** : l'attribution CC BY 4.0 devra être portée par une **surface de crédits**
qui n'existe pas encore dans l'application → `ATTRIBUTION SURFACE: NOT YET IMPLEMENTED`, à traiter en
`Sb_ASSET_03.2` / `Sx_ASSET_04`.

---

## 1. Mission
Produire la spec + le package opérateur pour la création humaine du master BodyMap : brief illustrateur,
contrat structurel SVG, exigences de livraison, registre de références, exigences PI/provenance, protocole de
revue anatomique/produit/mobile, grille, template de livraison. **Ne produit ni silhouette, ni image, ni
`auren_bodymap_master.svg`.** Package documentaire dans [`../production/bodymap/`](../production/bodymap/) +
due diligence dans [`../research/AUREN_BODYMAP_REFERENCE_DUE_DILIGENCE.md`](../research/AUREN_BODYMAP_REFERENCE_DUE_DILIGENCE.md).

## 2. Baseline & état
`Sx_ASSET_01 CLOSED` · `Sx_ASSET_02 CLOSED` · `Sx_ASSET_03` (cette spec, **amendée**) ·
`Sb_ASSET_03.1 SPEC READY / BUILD NOT STARTED` · `OPERATOR_ASSET_03.1 FALLBACK / NOT STARTED` ·
`Sb_ASSET_03.2 NOT STARTED` · `Sx_UI CLOSED` · `ASSET INTEGRATION GATE: BLOCKED` · `RUNTIME INTEGRATION: NOT
STARTED`.

## 3. Brainstorming (§8 — conclusion)
```
SEMANTIC CONTRACT FIRST · ORIGINAL HUMAN MASTER · MALE_NEUTRAL_V1 P0 · FRONT + BACK ORTHOGRAPHIC
ELEVEN ZONE GROUPS · SIX COMPACT MACROS · NO ZONE-UNKNOWN · NO AI ANATOMICAL GROUND TRUTH
BODYPARTS3D REFERENCE — NOT AUTOMATIC DERIVATION · ANATOMYTOOL RESOURCE-BY-RESOURCE CONTROL
FULL SOURCE DISCLOSURE · PROFESSIONAL LEGAL REVIEW NOT CLAIMED · ANATOMICAL REVIEW REQUIRED
MOBILE 360 REVIEW REQUIRED · NO APP INTEGRATION · GATE REMAINS BLOCKED
```
Décisions clés (30 questions) : le master **localise** des régions selon la **donnée réelle** (11 zones), sans
prétendre une précision qu'elle n'a pas ; `upper_back`/`posterior` restent des **agrégats** ; **un ID stable
par zone** porté par un `<g>` unique (jamais dupliqué face/dos, jamais partagé entre zones) ; convention d'IDs
enfants **techniques** `geom-<zone>-<view>-<side>-<index>` (n'affecte pas le Layer A) ; variante **V1 =
male_neutral_v1** (P0), autres en P2 ; **IA = moodboard stylistique uniquement**, jamais vérité anatomique ;
**BodyParts3D = référence spatiale, pas dérivation** (ShareAlike) ; **AnatomyTOOL ressource-par-ressource** ;
revue anatomique **≠ validation médicale** ; previews **bornées à 32** ; point d'arrêt = package défini, master
non produit, gate bloqué.

## 4. Audit du système existant (§7)
- **Contrat métier** (immuable, `Sb_ASSET_01.2`) : 11 zones + labels FR · 6 macros compactes · `unknown` =
  état neutre (pas une zone) · 14 IDs SVG stables · 5 états · **`BODYMAP COMPACT MACROS ARE NOT RADAR_AXES`** ·
  surfaces bornées.
- **Prototype runtime** (`worked_area_body_map.html`, lecture seule) : vues face/dos, `viewBox 0 0 60 100` par
  silhouette, formes `circle`/`rect` rudimentaires, mapping `_WA_ZONE_TO_REGION` (11→6), classes
  `is-primary`/`is-secondary`, `aria-hidden`, no-JS, consommé par `exercise_card.html`. **Rôle : prototype à
  remplacer après gate.** Limites : non anatomique, densité minimale. **0 fichier runtime modifié.**
- **Garde actuel** : `test_auren_asset_governance.py` interdit tout SVG sous `design/auren/` hors allowlist ; la
  future évolution (autoriser `auren_bodymap_master.svg`) relève de **`Sb_ASSET_03.2`, pas de cette spec**.

## 5. Contrat 11 zones / 6 macros / unknown / séparation radar
- **11 zones** + labels FR (cf. taxonomie) ; **6 macros** (`chest/shoulders/back/arms/legs/core`) ; `unknown`
  = état, **0 `zone-unknown`**. **`RADAR_AXES`/`RADAR_AXIS_ORDER`/scores/Body Intelligence/catalogue/historique
  INCHANGÉS** — le master ne les touche pas. Détail géométrique : [contrat SVG](../production/bodymap/AUREN_BODYMAP_SVG_STRUCTURE_AND_DELIVERY_CONTRACT.md).

## 6. Variante V1 (§9)
`body_variant: male_neutral_v1` — **P0 PRODUCTION VARIANT** (adulte, athlétique non culturiste, neutre, non
médical, sans détails sexuels, **0 genre dans les codes**, **mêmes 14 IDs** pour toute variante future).
`female_neutral_v1` · `neutral_abstract_v1` · vue latérale = **P2, NON produits** en `OPERATOR_ASSET_03.1`.

## 7. Direction artistique (§10)
Instrument **biomécanique**, non médical/gamer/pseudo-IA. Détail normatif : [brief illustrateur](../production/bodymap/AUREN_BODYMAP_ILLUSTRATOR_BRIEF.md).
Lisible 60/80/120 px + côte-à-côte 360 px.

## 8. Grille & structure SVG (§11 — tranchés)
**viewBox master = `0 0 240 200`** (face x∈[10,110] centre 60 ; dos x∈[130,230] centre 180 ; gouttière
[110,130]) — choix justifié par rendu côte-à-côte 360 px + export compact + testabilité, **non laissé à
l'illustrateur**. 14 IDs stables figés · **1 `<g id="zone-*">` unique par zone** · convention IDs enfants
`geom-<zone>-<view>-<side>-<index>` (technique). Règles dures (0 ID dupliqué, 0 path partagé, symétries ≠
nouveaux codes). Détail : [contrat SVG](../production/bodymap/AUREN_BODYMAP_SVG_STRUCTURE_AND_DELIVERY_CONTRACT.md).

## 9. États & accessibilité (§14/§15)
5 états `neutral/primary/secondary/unknown/disabled`, **jamais distingués par la seule couleur**, couleur
**pilotée runtime** (0 couleur métier dans le master). BodyMap **décoratif** (`aria-hidden`/`focusable=false`),
**texte adjacent = vérité accessible**, 0 texte/interaction/focus dans le master.

## 10. Références & due diligence (§16 — **amendé, recherche datée 2026-07-23**)
- **BodyParts3D** (DBCLS) : **CC BY 4.0 International** (officiel, maj **2025-02-27**), OBJ, release **4.0**,
  attribution exacte obligatoire → **`PRIMARY DERIVATION SOURCE`**, dérivation **licite**.
  *(Le relevé « CC BY-SA 2.1 Japan » du 2026-07-22 provenait d'un miroir GitHub périmé — corrigé.)*
- **Servier Medical Art** : **CC BY 4.0** — contrôle 2D face/dos (PNG + pack PPT).
- **AnatomyTOOL** : licence **par ressource** — qualifier chaque ressource (CC BY/CC0 éligibles ; NC/étudiant
  écartés).
- **OpenStax** : **1ʳᵉ éd. CC BY 4.0** éligible · **2e éd. CC BY-NC-SA 4.0 EXCLUE**.
- **Z-Anatomy** (CC BY-SA 4.0 + composant NC) · **Wikimedia `Muscles front and back.svg`** (CC BY-SA 4.0) :
  **référence / prototype uniquement, exclus du master livré**.
- Le master peut être **dérivé** (plus « original redessiné »), sous attribution. Détail + sources :
  [stratégie de réutilisation](../research/AUREN_BODYMAP_OPEN_SOURCE_REUSE_STRATEGY.md) ·
  [due diligence amendée](../research/AUREN_BODYMAP_REFERENCE_DUE_DILIGENCE.md). **Aucune image committée.**

## 11. IA (§17 — **périmètre précisé 2026-07-23**)
**Autorisée** : exploration stylistique · **simplification visuelle** · proposition de silhouette **non
anatomique** · **variation de contours**.
**Interdite** : source anatomique **unique** · source des **frontières musculaires** · preuve de provenance ·
validation anatomique.
**Déclaration obligatoire** de tout usage ; géométrie générée non déclarée = **livraison bloquée**.

## 12. Exigences PI / provenance (§18)
Checklist d'exigences contractuelles (auteur, originalité, références, outils, tiers, IA, cession, droits,
correction/rejet, preuves) — **`PROCUREMENT / LEGAL REQUIREMENTS CHECKLIST`, pas un contrat**. Ne jamais
affirmer « Auren owns the master » avant contrat signé + sources + revue juridique. Statuts :
`contract-requirements-defined` → tout le reste PENDING. Détail : [exigences PI/provenance](../production/bodymap/AUREN_BODYMAP_IP_PROVENANCE_AND_SOURCE_DISCLOSURE_REQUIREMENTS.md).

## 13. Package illustrateur & manifeste de livraison (§19/§20)
Livrables : master SVG canonique + source native (hashée, non nécessairement commitée) + registre références +
déclarations (outils/tiers/IA) + previews + notes/changelog. Template de manifeste (26 champs, statuts initiaux
`not-started`/`professional-review-required`, **0 approved**) : [manifest template](../production/bodymap/AUREN_BODYMAP_DELIVERY_MANIFEST_TEMPLATE.md).

## 14. Protocole de revue (§21/§22/§23 — **gate humain révisé 2026-07-23**)
```
MULTI-SOURCE ANATOMICAL CONSISTENCY REVIEW: REQUIRED
PROFESSIONAL ANATOMICAL REVIEW: NOT CLAIMED / OPTIONAL BEFORE FINAL INTEGRATION DECISION
NAMED ILLUSTRATOR: NO LONGER A PRECONDITION
```
Pour un master dérivé, chaque zone est confrontée à **≥ 2 sources indépendantes** (Servier · AnatomyTOOL
qualifié · OpenStax 1ʳᵉ éd.) — le SVG Wikimedia et Z-Anatomy **ne comptent pas comme avis indépendants**
(dérivés respectivement d'OpenStax et de BodyParts3D). Verdicts par zone
(`PASS/ADJUST/BLOCKED/NOT APPLICABLE`) ; grille produit/mobile 360 + 60/80/120 px (non-régression logging) ;
**32 previews bornées** (inchangé). La revue professionnelle reste **possible et recommandée avant la décision
d'intégration finale**, et **n'est pas revendiquée**. Détail : [protocole de revue](../production/bodymap/AUREN_BODYMAP_ANATOMICAL_PRODUCT_MOBILE_REVIEW_PROTOCOL.md).

## 15. Contrat futur `Sb_ASSET_03.2` (§24 — préparé, non implémenté)
Validations d'intake préparées (XML/SVG root/viewBox exact/14 IDs/0 unknown/0 dupliqué/0 path partagé/0 script/
0 URL/0 raster/0 texte/0 filtre/0 gradient/groupes face-dos/manifest/provenance/droits/références/previews/
budget compact/status ≠ approved). Le futur intake pourra faire évoluer `test_auren_asset_governance.py` —
**cette spec ne modifie aucun test.**

## 16. Budgets (§25)
`export compact optimisé ≤ 12 Ko` (**bloquant**) · `requête réseau BodyMap actif = 0` (inline) · master SVG
canonique = **indicatif** · source native = **aucun budget** · preview raster = indicatif. Détail par artefact :
[contrat SVG §7](../production/bodymap/AUREN_BODYMAP_SVG_STRUCTURE_AND_DELIVERY_CONTRACT.md).

## 17. Gate (§26)
`ASSET INTEGRATION GATE: BLOCKED PENDING HUMAN / ANATOMICAL / LEGAL / MOBILE APPROVALS`. Même après livraison du
master, restent : intake technique · anatomique · produit · accessibilité · mobile · provenance · PI · licence ·
manifest · intégration séparée. **Aucun fichier dans `app/static/` pendant `Sx_ASSET_03` / `OPERATOR_ASSET_03.1`
/ `Sb_ASSET_03.2`.**

## 18. Note metadata iconographique (§31 — constat, sans rouvrir Sx_ASSET_02)
Certains fichiers d'intake iconographique peuvent encore porter `human-review-pending` / `NOT YET REVIEWED`
alors que le closeout `cf41188` constate `HUMAN REVIEW ACCEPTED`. **Ne pas rouvrir Sx_ASSET_02.**
`ICON REVIEW METADATA SYNCHRONIZATION: REQUIRED BEFORE Sx_ASSET_04 INTEGRATION SPEC`. Le statut légal reste
`legal-review-required`. **Cette note ne bloque pas `Sx_ASSET_03`.**

## 19. Non-goals
Aucune silhouette · image · référence importée · `auren_bodymap_master.svg` · modif `app/**`/`design/**`/
`tests/**` · intégration prototype · changement métier/taxonomie · ouverture de `Sb_ASSET_03.2` · contrat
juridique final · dépendance · binaire · font. Aucune réouverture `Sx_ASSET_01`/`Sx_ASSET_02`/`Sx_UI`. Aucun
fichier Custom.

## 20. Statut & queue
```
Sx_ASSET_03: AMENDED — SOURCE-REUSE-FIRST (spec versée 66d18d4, amendée 2026-07-23)
BODYMAP SEMANTIC CONTRACT: ALREADY COMPLETE / IMMUTABLE
BODYMAP HUMAN PRODUCTION PACKAGE: DEFINED
BODYMAP MASTER: NOT YET PRODUCED
PRIMARY DERIVATION SOURCE: BodyParts3D CC BY 4.0 (official DBCLS archive)
Sb_ASSET_03.1: SPEC READY / BUILD NOT STARTED
OPERATOR_ASSET_03.1: FALLBACK OPTION / NOT STARTED
MULTI-SOURCE ANATOMICAL CONSISTENCY REVIEW: REQUIRED
PROFESSIONAL ANATOMICAL REVIEW: NOT CLAIMED / OPTIONAL
ATTRIBUTION SURFACE: NOT YET IMPLEMENTED
Sb_ASSET_03.2: BLOCKED BY PROTOTYPE DELIVERY
PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED
ASSET INTEGRATION GATE: BLOCKED · Sx_ASSET_01/02/Sx_UI: CLOSED
```
Queue : **`Sb_ASSET_03.1`** (dérivation depuis sources ouvertes) → `Sb_ASSET_03.2` (intake) → [gate] →
`Sx_ASSET_04`/`04.1`. `OPERATOR_ASSET_03.1` reste défini comme **option de repli**.
**Non ouverts** : `Sx_ASSET_04`, `Sb_ASSET_04.1`, runtime integration, BodyMap replacement.

---

## Verdict

**Verdict :** 🟠 **Sx_ASSET_03: AMENDED — SOURCE-REUSE-FIRST** (spec versée `66d18d4`, amendée 2026-07-23)**.**
Le package de production reste **défini et exécutable** — brief (male_neutral_v1, biomécanique non médical,
11 zones, agrégats honnêtes), **contrat SVG tranché** (viewBox `0 0 240 200`, 14 IDs stables figés, `<g>`
unique/zone, convention IDs enfants, 0 `zone-unknown`), exigences PI/provenance (`PROCUREMENT CHECKLIST`, pas
un contrat), 32 previews bornées, manifest template (0 approved), budgets par artefact — mais la **méthode
d'obtention de la géométrie change** : **dérivation depuis sources ouvertes**, plus commande externe en
première intention. **Correction établie sur source officielle** : **BodyParts3D est CC BY 4.0** (DBCLS, maj
**2025-02-27**), et non CC BY-SA 2.1 Japan comme relevé le 2026-07-22 sur un **miroir GitHub figé en 2011** →
**dérivation licite sous attribution obligatoire**, BodyParts3D devient `PRIMARY DERIVATION SOURCE`. Gate
humain révisé : **cohérence multi-sources REQUISE**, **revue professionnelle NON revendiquée / optionnelle**,
**illustrateur nommé n'est plus un préalable**. Sources encadrées : Servier CC BY 4.0 (contrôle 2D),
OpenStax **1ʳᵉ éd. seulement** (la 2e est NC), Z-Anatomy et le SVG Wikimedia **exclus du master livré**
(ShareAlike, et non indépendants). **Le master n'est toujours PAS produit** ; `BODYMAP SEMANTIC CONTRACT`
reste immuable ; nouvelle dette explicite `ATTRIBUTION SURFACE: NOT YET IMPLEMENTED` ;
`ASSET INTEGRATION GATE: BLOCKED` ; `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED`. `Sx_ASSET_01/02` restent
CLOSED.

**Prochaine action** (séparée, non commencée) : `GO BUILD — Sb_ASSET_03.1 Open Anatomy Source Acquisition &
BodyMap Derivation Prototype`. `OPERATOR_ASSET_03.1` reste disponible en **repli**.
