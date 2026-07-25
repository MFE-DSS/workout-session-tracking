# Sx_ASSET_03B — Muscle Focus Technical Surface System — SPEC

**Type** : SPEC ONLY / SYSTEM DESIGN / VISUAL-ANATOMICAL DIRECTION — **DOCS-ONLY**
**Date** : 2026-07-24
**Cycle** : `Sx_ASSET` (programme visuel propriétaire, indépendant de `Sx_UI` clos). Ce document ouvre un
**sous-cycle additif et stratégique** : `Sx_ASSET_03B`.
**Statut** : 🟢 **SPEC COMMITTED — `ff9541a`** · **`Sb_ASSET_03B.1` AUTHORIZED / NOT YET COMPLETE**.
`ASSET INTEGRATION GATE: BLOCKED`.
**Parent du cycle** : `b1f0b63` (baseline historique) · **HEAD courant** : `ff9541a` (spec versée). **Ne rouvre
PAS** `Sx_UI` (CLOSED), ni `Sx_ASSET_01` (CLOSED), ni
`Sx_ASSET_02` (CLOSED), ni le contrat sémantique BodyMap (immuable). Ne modifie **aucun** master existant.

> `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED` · `MUSCLE FOCUS PLATES: CONCEPTUALLY DEFINED / NOT PRODUCED` ·
> `RUNTIME INTEGRATION: NOT STARTED`.

---

## 1. Contexte et motif du pivot

Le programme `Sx_ASSET` a livré un **BodyMap global** (silhouette face+dos, **11 zones** figées, 6 macros,
5 états, décoratif + texte adjacent) — utile pour **naviguer et synthétiser**. La revue produit révèle un
**écart de cible** : cette surface segmente bien mais n'est **ni assez qualitative, ni immersive, ni
anatomiquement pertinente** pour être la **surface héro technique** d'Auren.

Feedback produit intégré comme **vérité prioritaire** :
- le bodymap global est trop vague, trop « corps entier » ;
- certaines zones (pectoraux) paraissent imprécises ; les deltoïdes manquent de détail ; le postérieur mérite
  un **zoom régional**, pas une simple zone sur un corps complet ;
- **la vraie valeur n'est pas « où ça tape ? » mais « comment ce muscle existe, s'insère, se contracte, et
  quels exercices/mouvements le sollicitent le mieux »** ;
- la surface cible doit être **locale, zoomée, immersive, pédagogique, biomécanique** ;
- la carte globale doit **rester un outil de navigation/synthèse**, mais ne plus être la surface premium.

**`Sx_ASSET_03B` ne remplace pas le bodymap global.** Il **redéfinit la couche visuelle premium** : un
système de **surfaces techniques zoomées par muscle / groupe musculaire** — les **« Muscle Focus Plates »**.

## 2. Diagnostic — limites du bodymap global

| Limite | Nature | Conséquence |
|---|---|---|
| Cadrage « corps entier » | le zoom est nul : tout est vu à la même distance | aucune lecture locale de faisceau/insertion |
| Granularité arrêtée à la **zone** | 11 codes métier, jamais les sous-structures | « pecs » ne peut montrer claviculaire vs sterno-costal |
| Silhouette **décorative** (contrat) | interdiction délibérée de fibres/veines/insertions (`AUREN_STYLE_RULES §5`) | crédibilité anatomique volontairement plafonnée |
| Rôle **synthèse** | répond « où / combien », jamais « comment » | la valeur pédagogique/biomécanique n'a pas de surface |
| Agrégats honnêtes (`upper_back`, `posterior`) | non subdivisibles au niveau global | la richesse fonctionnelle reste invisible |

Ces limites **ne sont pas des défauts** du bodymap global : ce sont les **choix qui le rendent stable et
lisible** en navigation. Le pivot ne les corrige pas — il **ajoute une couche** là où elles bornent la valeur.

## 3. Rôle révisé du bodymap global (reclassé **Niveau 1**)

Le BodyMap global **devient explicitement le Niveau 1 : index / navigation / synthèse / routeur**, forme
**inchangée** (aucune migration de contrat, aucune 12ᵉ zone).

- **Continue** : lecture d'ensemble et de couverture ; point d'entrée du score par zone ; rampe de lancement
  vers le Niveau 2 (chaque zone cliquable) ; surface « maison ».
- **Cesse** : porter la charge qualitative/immersive/anatomique ; être la surface héro ; « paraître précis ».
- **En une phrase** : le global map répond à **« où et combien ? »** — jamais à « comment ».

`GLOBAL BODYMAP: RETAINED AS NAVIGATION / SYNTHESIS LAYER.`

## 4. Vision cible — Muscle Focus Technical Surface System

Un système de **surfaces anatomiques locales, pédagogiques et biomécaniques**, orientées **compréhension
musculaire / exercice**, qui **complètent** le bodymap global. Une « surface technique musculaire » Auren
est une **plaque zoomée** qui :
- **localise** une région ou un muscle par un **crop local** (pas un corps entier) ;
- **explicite** faisceaux, insertions/origines, direction de fibres, rôle mécanique — **schématiquement**,
  jamais en rendu médical réaliste ;
- **relie** le muscle à des **exercices concrets** (le lien produit qui empêche la dérive vers l'atlas) ;
- reste **non médicale, non mesurée** (jamais d'EMG, jamais d'activation chiffrée) et **stylée Auren
  Terminal** (aplats sobres, trait clair, couleur pilotée runtime, **zéro gradient**, zéro rendu réaliste).

## 5. Principes de design — cadrage / profondeur / lisibilité

Grammaire « Auren Terminal » (extraite de principes, **aucune œuvre copiée** — cf. §11 et recherche) :

1. **Cadrage local** : crop sur la région (demi-corps, quadrant, zoom muscle), jamais le corps entier. *Le
   zoom est la valeur.*
2. **Hiérarchie à 3 rangs** : (1) muscle cible = aplat couleur runtime plein ; (2) synergistes = même teinte
   désaturée ; (3) structures adjacentes (os, tendon, muscle voisin) = **trait clair seul, sans remplissage**.
3. **Clean view + technical overlay** : *clean* par défaut (aplats + trait) ; *overlay* **activable** (fibres
   en hachures suivant l'axe réel + points origine/insertion + flèche vecteur de force le long des fibres).
4. **Profondeur par le trait, pas par l'ombre** : superficiel = aplat plein ; profond = même forme en
   **contour pointillé atténué** sous la couche superficielle. **Aucun gradient, aucune ombre portée.**
5. **Ancrage osseux minimal** : montrer l'os d'insertion (clavicule, acromion, humérus, bassin, épine
   scapulaire) en trait fin — ce qui distingue un **instrument biomécanique** d'un pictogramme.
6. **Lisibilité mobile** : formes réductibles, épaisseurs de trait constantes, contraste fort, **≤ 3 teintes
   actives** par plaque, texte de label **hors** de la surface anatomique.
7. **Anti-caricature = fidélité de forme** : la silhouette réelle du muscle, la direction des fibres et le
   point d'insertion réel sont le garde-fou contre le cliché (cf. §16 cas d'exigence).

## 6. Architecture en couches / niveaux

Système à **3 niveaux**, arbre strict **ancré sur les 11 codes** (aucune 12ᵉ zone) :

```
Niveau 1 — Global Map (existant, reclassé)   navigation · synthèse · score · localisation
   └─ Niveau 2 — Regional Focus Plate         zoom régional · lecture anatomique locale
        └─ Niveau 3 — Muscle Focus / Exercise Mechanics Plate
                                               faisceaux · fibres · insertions · fonctions ·
                                               exercices · patterns · angles · rôle mécanique
```

Réutilisation du **modèle 4-layers déjà figé** (`Sx_ASSET_01 §4` : A métier · B géométrie · C présentation ·
D surface). Les plaques sont des **surfaces géométriques dérivées** sous le **même régime** source-reuse /
attribution / non-médical que le master global. **Layer A (11 zones) reste intact** : les faisceaux/heads
sont de la géométrie **Layer B**, jamais des codes métier, jamais scorés.

## 7. Typologie des plates

**Regional Focus Plates = 8** — *une par macro*, sauf `legs` (zones dispersées) éclatée en 3 zones :
`chest` · `shoulders` · `back` · `arms` · `core` (5 macros) + `quads` · `posterior` · `calves` (3 zones de
`legs`). **Toutes clefées sur un code existant.**

**Muscle Focus Plates = 11** — une par zone figée (1:1 avec le descriptor), en **deux modes** :
- **9 plaques « muscle / heads »** : les faisceaux sont des **labels d'affichage intra-zone** (ex. `pecs` →
  claviculaire/sterno-costal ; `biceps` → longue/courte ; `triceps` → 3 chefs ; `quads` → 4 chefs ; `calves`
  → gastrocnémien/soléaire ; `delt_lat`/`delt_post` = même deltoïde sous son angle fonctionnel). Géométrie
  Layer B, **jamais** un code.
- **2 plaques « groupe honnête »** (`upper_back`, `posterior`) : mode **grouped** avec disclaimer explicite —
  traps/rhomboïdes ou ischios/fessiers **nommés sans localisation prétendue**. *La plaque ne gagne jamais une
  précision que la donnée ne porte pas* (héritage des agrégats honnêtes).

## 8. Modules d'une plate

Chaque plaque est une **pile de modules** (tous n'apparaissent pas à chaque niveau) :

| # | Module | Rôle |
|---|---|---|
| 1 | Clean anatomical view | la « géométrie master » de la plaque |
| 2 | View selector | `front` / `back` / `lateral` / `section` (coupe locale) |
| 3 | Depth / layer toggle | surface ↔ profond ; replie/déplie les overlays |
| 4 | Technical overlay layer | biomécanique : origines/insertions, lignes de traction |
| 5 | Insertion / origin markers | `mark-<zone>-origin|insertion-<i>` |
| 6 | Fiber-direction indicators | vecteurs **schématiques** (jamais histologiques) |
| 7 | Contraction / ROM indicator | schéma fonctionnel **non médical** (jamais EMG/activation) |
| 8 | Exercise link module | exercices + patterns depuis l'EKB ; ouvre l'Exercise Mechanics Overlay |
| 9 | Text caption module | **vérité accessible** (labels FR, fonction, disclaimer) — porte l'a11y |
| 10 | State / legend module | légende principal/synergiste/adjacent, indice **non-couleur** |
| 11 | Provenance micro-module | attribution CC BY (adresse la dette `ATTRIBUTION SURFACE`) |

| Module | N2 Regional | N3 Muscle |
|---|---|---|
| 1 · 2(front/back) · 9 · 10 · 11 | ✔ | ✔ |
| 2(lateral/section) · 3 · 4 · 5 · 6 · 7 | — | ✔ |
| 8 Exercise link | liste | interactif (overlay) |

## 9. Niveaux de détail et variantes mobile / desktop

**États d'affichage** (propres aux plaques) : `clean` · `overlay-on` · `exercise-highlighted`.

**Rôles d'exercice** (principal / synergiste / adjacent) — ils **ne créent aucun nouvel état runtime** : ils
**projettent** sur les **5 états figés** (Layer C) : principal → `primary`, synergiste → `secondary`,
adjacent → `neutral` + annotation. Contrainte conservée : **jamais distingués par la seule teinte**.

**Variantes de vue** : `front` · `back` · `lateral` · `section` (les deux dernières **nouvelles au niveau
plaque**, Layer B, licites tant qu'elles ne touchent ni les 11 codes ni les 6 macros).

**Mobile (360px) vs desktop** :
- **360px** : clean view + caption + **un seul accordéon** d'overlay ; **repliés par défaut** = overlay
  technique, fibres, contraction, coupe, comparative ; toggle de vue limité à `front`/`back` (`lateral`/
  `section` derrière un « plus ») ; exercices en **liste**, pas en overlay sur figure ; plaque N3 = **sheet
  plein écran** (le côte-à-côte 360px reste réservé au **compact global**).
- **Desktop** : overlays dépliables/juxtaposables, 4 vues exposées, comparative activée, Exercise Overlay
  interactif sur la figure. **Divulgation progressive stricte.**

## 10. Overlay biomécanique / exercise mechanics

- **Objet** : `Exercise Mechanics Overlay` — couche **projetée sur** une plaque (N3, éventuellement N2),
  **pas** une plaque autonome. Par exercice (clé EKB).
- **Contenu** : muscle principal / synergistes / structures adjacentes ; angle / prise / rôle mécanique ;
  pattern de mouvement. **Le vecteur de force suit toujours la direction des fibres** (principe biomécanique,
  §16).
- **Lien produit bidirectionnel** (Axe A) : plaque → « exercices qui sollicitent ce faisceau » → fiche
  exercice → **« ajouter à la séance »** ; fiche exercice → « ce que ça travaille » → plaque. *Chaque plaque
  débouche sur une action de training* — jamais un cul-de-sac de connaissance.
- **Dépendance donnée** (non gatée) : réutilise `app/services/muscle_mapping.py` +
  `data/exercise_knowledge_base.json` — **sans introduire de code hors des 11 zones**.

## 11. Stratégie de sources et de réutilisation (cohérente source-reuse-first)

Détail complet et vérifié dans [`../research/AUREN_MUSCLE_FOCUS_REFERENCE_RESEARCH.md`](../research/AUREN_MUSCLE_FOCUS_REFERENCE_RESEARCH.md).
Synthèse (relevés **2026-07-24**, `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED`) :

**4 rôles de source** *(revalidés 2026-07-24 — cf. [`../production/muscle-focus/AUREN_MUSCLE_FOCUS_SOURCE_LEDGER.md`](../production/muscle-focus/AUREN_MUSCLE_FOCUS_SOURCE_LEDGER.md))* :
- **Géométrie (dérivable, master propriétaire)** : **Servier Medical Art** (CC BY 4.0, **images seules** —
  marques/UI exclues) — socle et continuité avec le BodyMap · **OpenStax A&P 1ʳᵉ éd.** (CC BY 4.0, **+ clause
  anti-ingestion IA**) · **domaine public CONDITIONNEL** (Gray's 1918, atlas historiques — PD **par édition/
  scan/juridiction**, absence de couche moderne ; **pas** « zéro contrainte »).
- **Style** : Servier (trait vectoriel « maison ») + registre PD à **moderniser**, jamais décalquer.
- **Validation (lecture seule, jamais dérivé)** : **BodyParts3D / Anatomography** (FMA IDs) · **NLM Visible
  Human** (**terms-based** : attribution NLM + non-endossement + fraîcheur, mesh protégé — **reclassé** hors du
  PD « zéro contrainte », rôle validation par défaut) · **Z-Anatomy** — attaches/nommage/couches.
- **Inspiration (consulter, jamais dériver)** : MuscleWiki, BioDigital, Muscle&Motion, Complete Anatomy —
  conventions de cadrage/zoom UX.

**Règles de licence dures** (héritées du BodyMap) : CC BY = dérivation propriétaire **licite + attribution
irrévocable** · CC BY-SA = **copyleft, contamine** → validation/inspiration seulement · CC BY-NC = **exclu**
(OpenStax **2ᵉ éd.** est NC — ne jamais confondre avec la 1ʳᵉ) · CC0 / PD = liberté totale · copyright =
inutilisable (**MuscleWiki, BioDigital, BioRender**). **Agrégateurs = licence par fichier, jamais globale.**

**Continuité BodyMap** : **BodyParts3D est CC BY 4.0** (page officielle DBCLS, maj 2025-02-27) — un relevé
« CC BY-SA » provient invariablement du **miroir GitHub figé en 2011** (piège documenté et résolu au BodyMap,
re-confirmé ici par croisement adversarial ; cf. recherche §Arbitrage).

**Nuance juridique clé** (apport du croisement) : **les faits anatomiques ne sont pas protégeables, mais un
maillage 3D spécifique est une expression protégée**. On **redessine à partir du savoir anatomique** (multi-
sources, dont PD), on ne **trace/retopologise jamais** un mesh sous copyleft.

## 12. Politique IA (si utilisée plus tard)

**Last resort, plan B/C — jamais A.** Bornes impératives :
- **Jamais vérité anatomique** : toute sortie IA est **validée** contre BodyParts3D / Z-Anatomy / Gray's avant
  usage. Un générateur hallucine attaches, faisceaux, trajets.
- **Jamais géométrie finale livrée** : la géométrie livrable vient des sources CC BY / PD.
- **Périmètre autorisé** : moodboard, palette/ambiance, **composition non anatomique** (cadrage, fond, grille),
  variantes de rendu **sur une géométrie déjà validée et de source propre**.
- **Toujours déclarée** : registre par asset (rôle exact = style/compo, pas géométrie). **Ne jamais injecter
  une image propriétaire en entrée** pour « styliser ».

## 13. Priorisation P0 / P1 / P2

- **P0** : (a) **cette spec + un futur contrat d'IDs de plaque** (docs, 0 géométrie, analogue à `Sx_ASSET_01`) ;
  (b) les **3 zones les plus critiquées**, en paires Regional + Muscle : **`chest` / pecs**,
  **`shoulders` / delt_lat + delt_post**, **`legs` → `posterior` (chaîne postérieure)**. Vues `front`/`back`,
  mode clean + caption.
- **P1** : plaques `back`, `arms`, `quads`, `core`, `calves` ; **Exercise Mechanics Overlay** (couplé EKB) ;
  vues `lateral`/`section` des plaques P0 ; overlays insertion/fibres.
- **P2** : comparative views · contraction diagrams · variantes `female_neutral_v1` / `neutral_abstract_v1` ·
  micro-animations · coupe généralisée · cross-links synergistes.

## 14. Queue de builds future (aucune n'est ouverte par cette spec)

| Build | Objet | Gate |
|---|---|---|
| `Sb_ASSET_03B.1` | **Muscle Focus System Blueprint & Plate Template** (contrat d'IDs de plaque, templates, source strategy — docs, 0 géométrie) | 03B acceptée |
| `Sb_ASSET_03B.2` | Regional Plate production package + intake technique (P0 : chest/shoulders/posterior) | 03B.1 + master validé |
| `Sb_ASSET_03B.3` | Muscle Plate production + revue cohérence anatomique multi-sources (overlays fibres/insertions) | 03B.2 |
| `Sb_ASSET_03B.4` | Exercise Mechanics Overlay (couplage EKB, lecture seule) | 03B.3 |
| (intégration) | via `Sx_ASSET_04` / `Sb_ASSET_04.1` — **après gate** | gate franchi |

## 15. Gates et dépendances

- **`ASSET INTEGRATION GATE: BLOCKED`** — toute plaque géométrique est bloquée en amont ; aucun câblage `app/`.
- **`Sx_ASSET_03`** : la Regional Plate est un **crop documenté du master validé** (`Sb_ASSET_03.2 : ACCEPTED
  FOR DESIGN SOURCE / HUMAN REVIEW PENDING`) ; la Muscle Plate est un **artefact neuf** exigeant package +
  intake technique + revue de cohérence anatomique.
- **`Sx_ASSET_04` / `Sb_ASSET_04.1`** : les 3 nouvelles surfaces (`regional-plate`, `muscle-plate`,
  `exercise-mechanics`) doivent être **ajoutées au consumer/slot mapping** — après gate.
- **Amendement de gouvernance requis** (à acter au build 03B.1) : `AUREN_STYLE_RULES §5` interdit fibres/
  veines/insertions **sur la silhouette globale**. Les N3 les affichent → **autoriser explicitement ces
  détails uniquement sur la surface plaque dédiée, schématiques** (vecteurs, pas histologie ; ROM, pas EMG),
  caption non médicale. Sans cet amendement, contradiction directe avec `§5/§9`. **Le contrat du bodymap
  global reste inchangé.**

## 16. Cas d'exigence (spécifications anatomiques — contraintes de forme)

Ces cas sont des **exigences dures** : la fidélité de forme est le garde-fou anti-caricature.

- **Pectoraux — éviter les « poumons »** : dessiner l'**éventail convergent** (chef claviculaire, fibres
  inféro-latérales + chef sterno-costal, fibres horizontales) vers **un point d'insertion humérale unique** —
  jamais deux blobs symétriques. Le point de convergence latéral tue le cliché.
- **Deltoïdes — 3 faisceaux en contexte osseux** : antérieur (clavicule) · latéral (acromion) · postérieur
  (épine scapulaire), insertion commune (tubérosité deltoïdienne). **Ancrage osseux obligatoire** (sans lui
  les faisceaux sont indistinguables). Vue 3/4 pour antérieur+latéral ; **vue dos requise** pour le postérieur.
- **Postérieur — zoom bassin + fessiers + ischios** : crop bassin→cuisse ; insertion ischiatique commune ;
  vecteur d'extension de hanche ; distinguer fessier (superficiel, hanche) des trois ischios. **Pas de « bas
  du corps générique ».**
- **Lats vs upper_back — largeur vs épaisseur** : `lats` = grande nappe fine, fibres montant en éventail vers
  l'humérus, cadrage large (V-taper) ; `upper_back` = **pelage en couches** (trapèze superficiel → rhomboïde
  profond en pointillé) soulignant l'empilement. *La distinction largeur/épaisseur est le message de chaque
  plaque.*
- **Core — fonctionnel, pas de faux six-pack** : rectus = **sangle continue à intersections tendineuses
  subtiles** (pas une tablette régulière bombée) ; obliques en **diagonales** ; **transverse en corset**
  (idéalement via coupe transversale). Le message est **stabilité/fonction**, pas l'esthétique.

## 17. Risques / limites / non-goals

**Risques** : sur-complexité (effet labyrinthe) → *la profondeur se tire, ne se pousse jamais* ; logging
rallongé → **aucun drill-down obligatoire pendant la saisie** ; dérive vers l'atlas → **ancrage exercice
systématique** + budget de contenu ; dérive de positionnement (médical/mesure) → zéro claim EMG/activation,
langage fonctionnel simple ; poids des surfaces immersives → à cadrer en spec technique de build.

**Non-goals** : aucun asset graphique final · aucun SVG · aucune maquette · aucun prompt d'image exécuté ·
aucun prototype runtime · **aucune réouverture** de `Sx_UI` / `Sx_ASSET_01` / `02` / `03` (contrat sémantique
BodyMap immuable) · aucune migration · aucune 12ᵉ zone · aucun code métier hors des 11 · aucune intégration
`app/` · aucun franchissement de gate · aucune revendication `asset approved` / `legally cleared` /
`anatomically validated professionally` / `runtime ready` / `integration authorized`.

## 18. Prochaine action exacte (sans l'ouvrir)

`GO BUILD — Sb_ASSET_03B.1 Muscle Focus System Blueprint & Plate Template` (docs, contrat d'IDs de plaque +
templates + source strategy ; 0 géométrie). **Non ouvert par cette spec.**

---

## Verdict

**Verdict :** 🟢 **`Sx_ASSET_03B` — MUSCLE FOCUS TECHNICAL SURFACE SYSTEM: DEFINED (SPEC ONLY).** Le système
premium cible est cadré en **3 niveaux** ancrés sur les 11 zones immuables (Global Map niveau 1 conservé en
navigation/synthèse ; 8 Regional Plates ; 11 Muscle Plates), avec direction visuelle « clean view + technical
overlay », profondeur par le trait, ancrage osseux, cas d'exigence anatomiques durs (pectoraux/deltoïdes/
postérieur/lats-upper_back/core), stratégie de sources source-reuse-first (Servier + OpenStax 1ʳᵉ éd. + PD =
géométrie ; BodyParts3D/Z-Anatomy = validation seulement ; MuscleWiki/BioDigital = exclus ; IA = plan B/C
borné et déclaré), et queue de builds gatée. **Rien n'est produit.** `MUSCLE FOCUS PLATES: CONCEPTUALLY
DEFINED / NOT PRODUCED` · `GLOBAL BODYMAP: RETAINED AS NAVIGATION / SYNTHESIS LAYER` · `SOURCE STRATEGY:
DEFINED` · `RUNTIME INTEGRATION: NOT STARTED` · `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED` · `ASSET
INTEGRATION GATE: BLOCKED`.
