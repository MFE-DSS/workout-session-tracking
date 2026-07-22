# Sx_ASSET_03 — BodyMap Human Production Package — SPEC

**Type** : SPEC / PRODUCTION PACKAGE / OFFICIAL-SOURCE RESEARCH — **DOCS-ONLY**, NO SVG, NO IMAGE, NO APP CHANGE
**Statut** : 🟢 **SPEC RÉDIGÉE / READY FOR GO COMMIT**
**Programme** : `Sx_ASSET` · **3ᵉ cycle** · **Date** : 2026-07-22 · **Baseline** : `cf41188` (closeout
Sx_ASSET_02) ; posé sur HEAD canonique réel `062ee92` (avance Custom EKB_03, indépendante).

> `Sx_ASSET_01` et `Sx_ASSET_02` restent **CLOSED**. `Sx_UI` reste **CLOSED**. Ce cycle transforme le **contrat
> sémantique BodyMap (déjà accepté, immuable)** en un **dossier de production humaine exécutable**. **Il ne
> produit pas le master SVG.** `ASSET INTEGRATION GATE: BLOCKED`. `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED`.

---

## 1. Mission
Produire la spec + le package opérateur pour la création humaine du master BodyMap : brief illustrateur,
contrat structurel SVG, exigences de livraison, registre de références, exigences PI/provenance, protocole de
revue anatomique/produit/mobile, grille, template de livraison. **Ne produit ni silhouette, ni image, ni
`auren_bodymap_master.svg`.** Package documentaire dans [`../production/bodymap/`](../production/bodymap/) +
due diligence dans [`../research/AUREN_BODYMAP_REFERENCE_DUE_DILIGENCE.md`](../research/AUREN_BODYMAP_REFERENCE_DUE_DILIGENCE.md).

## 2. Baseline & état
`Sx_ASSET_01 CLOSED` · `Sx_ASSET_02 CLOSED` · `Sx_ASSET_03` (cette spec) · `OPERATOR_ASSET_03.1 NOT STARTED` ·
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

## 10. Références & due diligence (§16 — recherche datée 2026-07-22)
- **BodyParts3D** (DBCLS) : **CC BY-SA 2.1 Japan** (ShareAlike), OBJ, attribution exacte requise. **RÉFÉRENCE
  SPATIALE uniquement** ; **dérivation directe écartée** (copyleft) ; `LEGAL CLASSIFICATION PENDING`.
- **AnatomyTOOL** : licence **par ressource** — qualifier chaque ressource (CC BY/CC0 éligibles ; NC/étudiant
  écartés).
- Le master doit être **original, redessiné**, non dérivé automatiquement. Détail + sources :
  [due diligence](../research/AUREN_BODYMAP_REFERENCE_DUE_DILIGENCE.md). **Aucune image committée.**

## 11. IA (§17)
Moodboard stylistique **uniquement** ; jamais source anatomique/géométrie/master/validation/provenance.
**Déclaration obligatoire** de tout usage ; géométrie générée non déclarée = **livraison bloquée**.

## 12. Exigences PI / provenance (§18)
Checklist d'exigences contractuelles (auteur, originalité, références, outils, tiers, IA, cession, droits,
correction/rejet, preuves) — **`PROCUREMENT / LEGAL REQUIREMENTS CHECKLIST`, pas un contrat**. Ne jamais
affirmer « Auren owns the master » avant contrat signé + sources + revue juridique. Statuts :
`contract-requirements-defined` → tout le reste PENDING. Détail : [exigences PI/provenance](../production/bodymap/AUREN_BODYMAP_IP_PROVENANCE_AND_SOURCE_DISCLOSURE_REQUIREMENTS.md).

## 13. Package illustrateur & manifeste de livraison (§19/§20)
Livrables : master SVG canonique + source native (hashée, non nécessairement commitée) + registre références +
déclarations (outils/tiers/IA) + previews + notes/changelog. Template de manifeste (17 champs, statuts initiaux
`not-started`/`professional-review-required`, **0 approved**) : [manifest template](../production/bodymap/AUREN_BODYMAP_DELIVERY_MANIFEST_TEMPLATE.md).

## 14. Protocole de revue anatomique / produit / mobile & previews (§21/§22/§23)
Relecteur à **compétence documentée** (anatomie/biomécanique/…) — revue de **cohérence de représentation**,
**pas** de validation médicale. Verdicts par zone (`PASS/ADJUST/BLOCKED/NOT APPLICABLE`) ; grille produit/mobile
360 + 60/80/120 px (non-régression logging) ; **32 previews bornées**. Détail : [protocole de revue](../production/bodymap/AUREN_BODYMAP_ANATOMICAL_PRODUCT_MOBILE_REVIEW_PROTOCOL.md).

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
Sx_ASSET_03: SPEC RÉDIGÉE / READY FOR GO COMMIT
BODYMAP SEMANTIC CONTRACT: ALREADY COMPLETE / IMMUTABLE
BODYMAP HUMAN PRODUCTION PACKAGE: DEFINED
BODYMAP MASTER: NOT YET PRODUCED
OPERATOR_ASSET_03.1: PACKAGE READY / NOT STARTED
Sb_ASSET_03.2: BLOCKED BY HUMAN MASTER DELIVERY
PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED · ANATOMICAL REVIEW: NOT STARTED
ASSET INTEGRATION GATE: BLOCKED · Sx_ASSET_01/02/Sx_UI: CLOSED
```
Queue : `OPERATOR_ASSET_03.1` (production humaine) → `Sb_ASSET_03.2` (intake) → [gate] → `Sx_ASSET_04`/`04.1`.
**Non ouverts** : `Sx_ASSET_04`, `Sb_ASSET_04.1`, runtime integration, BodyMap replacement.

---

## Verdict

**Verdict :** 🟢 **Sx_ASSET_03: SPEC RÉDIGÉE / READY FOR GO COMMIT.** Le package de production humaine du master
BodyMap est **défini et exécutable** : brief illustrateur (male_neutral_v1, biomécanique non médical, 11 zones,
agrégats honnêtes), **contrat SVG tranché** (viewBox `0 0 240 200`, 14 IDs stables figés, `<g>` unique/zone,
convention IDs enfants, 0 `zone-unknown`), exigences PI/provenance (`PROCUREMENT CHECKLIST`, pas un contrat),
protocole de revue anatomique/produit/mobile (compétence documentée ≠ validation médicale) + 32 previews
bornées, manifest template (0 approved), contrat `Sb_ASSET_03.2` préparé, budgets par artefact. **Due diligence
datée (2026-07-22)** : BodyParts3D **CC BY-SA** = référence spatiale uniquement (dérivation écartée),
AnatomyTOOL ressource-par-ressource. **Le master n'est PAS produit** ; `BODYMAP SEMANTIC CONTRACT` reste
immuable ; `ASSET INTEGRATION GATE: BLOCKED` ; `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED`. `Sx_ASSET_01/02`
restent CLOSED.

**Prochaine action** (séparée, non commencée) : `GO COMMIT SPEC — Sx_ASSET_03 BodyMap Human Production Package`.
