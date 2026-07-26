# Sb_ASSET_03B.1 — Muscle Focus System Blueprint & Plate Contract — SPEC

**Type** : BLUEPRINT NORMATIF / PLATE CONTRACT — **DOCS-ONLY**. Transforme la vision `Sx_ASSET_03B` en un
**système de production exécutable sur le papier**, **sans produire aucune géométrie**.
**Date** : 2026-07-24 · **Base** : `ff9541a` · **Worktree** : `work/sb-asset-03b-1-muscle-focus-blueprint`.
**Statut** : 🟢 **`Sb_ASSET_03B.1: CLOSED — CANONICAL DELIVERY COMPLETE`** · **`BLUEPRINT: COMPLETE / PLATE
CONTRACT LOCKED`** · `ASSET INTEGRATION GATE: BLOCKED`.
**`CANONICAL MERGE: 805b8a9`** (PR #34, mergé 2026-07-26 ; blueprint commit `95f47b3` ; premier parent réel
`c48714b6` = closeout SCORING_03, cf. `docs/SPRINT_Sb_ASSET_03B_1_FINAL_CLOSEOUT_REPORT.md`). Les sections de
conception ci-dessous sont **historiques** (état au build) et **conservées telles quelles**.
**Ne rouvre PAS** : `Sx_UI` (CLOSED) · `Sx_ASSET_01/02` (CLOSED) · contrat sémantique BodyMap (**immuable**).
**Ne modifie aucun master.** `PLATE GEOMETRY: NOT PRODUCED` · `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED`.

> Ce document est la **synthèse arbitrée** d'un build à **5 axes parallèles** (§2). Il **fige le contrat de
> plaque** et **délègue** le détail à 7 documents de production normatifs (§4). Il **n'ouvre** aucun build
> géométrique.

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

| Décision | Options | Risque de l'option écartée | **Choix retenu** |
|---|---|---|---|
| Namespace d'IDs de plaque | réutiliser `geom-*`/`zone-*` du master · **namespace propre** | **collision DOM** (getElementById/`<use>`/aria cassés quand map+plaque coexistent) — BLOCKER adversarial #1 | **namespace propre `auren-plate-*`, disjoint de l'API `zone-*`** |
| Granularité du lien exercice | par faisceau (`part-*`) · **par zone** | **sous-zone implicite / fausse précision** (la donnée n'a pas de champ faisceau) — adversarial #3 | **zone uniquement** (« exercices — Pectoraux ») |
| Vérité accessible de l'overlay | overlay `aria-hidden` sans miroir · **caption-miroir** | payload N3 **inaccessible** au lecteur d'écran — adversarial #4 | **caption reflète tout fait d'overlay** (`caption_mirrors_overlay`) |
| Amendement §5 | ignorer · enacter tout de suite · **spécifier + gater** | contradiction qui **ship** · relaxation **prose-only** sans guard | **spécifier la clause `§5bis` + enactment gaté au build géométrie (avec guard test)** |
| Clé régionale (macro vs zone) | inférer du nom · **typer** | ambiguïté figée dans le contrat — adversarial #8 | **`region_key_kind: macro\|zone` typé** |
| Source NLM Visible Human | PD « zéro contrainte » · **terms-based** | **dérivation sans attribution** d'un mesh protégé — adversarial #2 | **reclassé terms-based, validation par défaut** |
| Séquencement P0 | clean+caption seul · **+ lien exercice N2 liste** | plaque = **cul-de-sac de connaissance** — adversarial #7 | **clean + caption + lien exercice zone-liste** |

## 1. Objet et périmètre

`Sb_ASSET_03B.1` fige, **sur le papier**, le système Muscle Focus : **inventaire** (8 Regional + 11 Muscle),
**namespace d'IDs** (v0.1.0), **schéma de descripteur**, **vues/crops autorisés**, **couches clean/overlay**,
**a11y/mobile/attribution**, **7 blueprints P0 exacts**, **stratégie de source par plaque (revalidée)**, et un
**amendement de gouvernance borné**. **Aucune géométrie** n'est produite ; **aucune gate** n'est franchie.

## 2. Usage réel des Superpowers — 5 axes parallèles + arbitrage

Conformément à la mission, **cinq axes** ont tourné en parallèle (sous-agents + recherche web réelle), suivis
d'une **synthèse arbitrée unique** :

- **Axe A — Contract & IDs** : namespace `auren-plate-*` disjoint de `zone-*`, grammaire `geom/part/mark/
  overlay/view`, registre `part-*`, unicité DOM par préfixe → [`ID_CONTRACT`](../production/muscle-focus/AUREN_MUSCLE_FOCUS_ID_CONTRACT.md) + [`DESCRIPTOR_SCHEMA`](../production/muscle-focus/AUREN_MUSCLE_FOCUS_DESCRIPTOR_SCHEMA.md).
- **Axe B — P0 Visual Blueprint** : vues/crops, cas d'exigence §16 en contraintes de forme, 7 descripteurs P0 →
  [`VIEW_AND_CROP_CONTRACT`](../production/muscle-focus/AUREN_MUSCLE_FOCUS_VIEW_AND_CROP_CONTRACT.md) + [`P0_PLATE_BLUEPRINTS`](../production/muscle-focus/AUREN_MUSCLE_FOCUS_P0_PLATE_BLUEPRINTS.md).
- **Axe C — Source & License Revalidation** (**web réelle**, pages officielles 2026-07-24) : Servier, OpenStax
  1ʳᵉ/2ᵉ + clause anti-IA, NLM Visible Human, Gray's/atlas → [`SOURCE_LEDGER`](../production/muscle-focus/AUREN_MUSCLE_FOCUS_SOURCE_LEDGER.md) (**4 corrections**).
- **Axe D — UX / Mobile / A11y** : couches clean/overlay, caption-miroir, mobile 360px, module 7 renommé →
  [`OVERLAY_ACCESSIBILITY_MOBILE_CONTRACT`](../production/muscle-focus/AUREN_MUSCLE_FOCUS_OVERLAY_ACCESSIBILITY_MOBILE_CONTRACT.md).
- **Axe E — Adversarial Review** : 8 findings sur ce que le contrat **figerait** ; tous résolus (§3) →
  amendement + garde-fous.

**Arbitrage** (méthode multi-voix) : l'Axe C a d'abord relevé BodyParts3D « CC BY-SA » (miroir GitHub 2011) —
**écarté** au profit de la page officielle DBCLS **CC BY 4.0** (piège déjà résolu au BodyMap, re-confirmé). Les
apports réels de C (clause anti-IA OpenStax, reclassification NLM, PD conditionnel) sont **conservés**. L'Axe E
a **confirmé** le design Axe A (namespace propre) et **corrigé** 3 fuites que le gabarit versé aurait figées.

## 3. Findings adversariaux (Axe E) → résolutions

| # | Sévérité | Finding | Résolution dans ce blueprint |
|---|---|---|---|
| 1 | BLOCKER | Le gabarit réutilisait `geom-*`/`zone-*`/`view-*`… du master → collision DOM | **Namespace `auren-plate-*` propre, disjoint, préfixe d'unicité, `l\|r\|c`+`lateral\|section` ≠ master** (ID Contract §1/§5/Règle #4) |
| 2 | HIGH | NLM Visible Human « PD zéro contrainte » ≠ recherche | **Reclassé terms-based / validation par défaut** (Source Ledger C1 ; SPEC §11 + Strategy corrigés) |
| 3 | HIGH | Exercice « par faisceau » = sous-zone implicite / fausse précision | **`exercise_link_granularity: zone` (seule valeur licite)** (ID Contract §6, Schema §2.6) |
| 4 | MED-HIGH | Overlay `aria-hidden` sans miroir → N3 inaccessible | **`caption_mirrors_overlay: true` obligatoire** (Overlay Contract §3, Schema §2.7) |
| 5 | MED | Amendement §5 sous-scopé (oublie `section`) et non écrit | **Clause `§5bis` figée, inclut la vue `section` schématique, enactment gaté + guard test** (Governance Amendment) |
| 6 | MED | « Non-médical » prose-only ; module 7 lisible comme mesure | **Module 7 → `overlay-shortening` ; jetons interdits pour futur guard** (Overlay Contract §2) |
| 7 | MED | P0 (clean+caption) = cul-de-sac de connaissance | **P0 = clean + caption + lien exercice N2 zone-liste** (P0 Blueprints) |
| 8 | LOW-MED | Clé régionale mélange macro/zone silencieusement | **`region_key_kind: macro\|zone` typé ; `legs` sans plaque régionale** (ID Contract §3, Schema §2.3) |

## 4. Contrat figé (délégation aux 7 documents de production)

| Document | Fige | Version |
|---|---|---|
| [`AUREN_MUSCLE_FOCUS_ID_CONTRACT.md`](../production/muscle-focus/AUREN_MUSCLE_FOCUS_ID_CONTRACT.md) | namespace, 19 racines, grammaire, `part-*`, unicité, 7 prédicats | `0.1.0` |
| [`AUREN_MUSCLE_FOCUS_DESCRIPTOR_SCHEMA.md`](../production/muscle-focus/AUREN_MUSCLE_FOCUS_DESCRIPTOR_SCHEMA.md) | champs/types/invariants du descripteur | `0.1.0` |
| [`AUREN_MUSCLE_FOCUS_VIEW_AND_CROP_CONTRACT.md`](../production/muscle-focus/AUREN_MUSCLE_FOCUS_VIEW_AND_CROP_CONTRACT.md) | 4 vues, crops par famille, `viewbox_local` gaté | `0.1.0` |
| [`AUREN_MUSCLE_FOCUS_P0_PLATE_BLUEPRINTS.md`](../production/muscle-focus/AUREN_MUSCLE_FOCUS_P0_PLATE_BLUEPRINTS.md) | **7 descripteurs P0 exacts** | — |
| [`AUREN_MUSCLE_FOCUS_OVERLAY_ACCESSIBILITY_MOBILE_CONTRACT.md`](../production/muscle-focus/AUREN_MUSCLE_FOCUS_OVERLAY_ACCESSIBILITY_MOBILE_CONTRACT.md) | couches, a11y, mobile 360px | `0.1.0` |
| [`AUREN_MUSCLE_FOCUS_SOURCE_LEDGER.md`](../production/muscle-focus/AUREN_MUSCLE_FOCUS_SOURCE_LEDGER.md) | classification par source (revalidée, 4 corrections) | — |
| [`AUREN_MUSCLE_FOCUS_GOVERNANCE_AMENDMENT.md`](../production/muscle-focus/AUREN_MUSCLE_FOCUS_GOVERNANCE_AMENDMENT.md) | clause `§5bis` bornée + guard test requis | — |

### 4.1 Inventaire figé
- **8 Regional Plates (N2)** : `chest`·`shoulders`·`back`·`arms`·`core` (macro) + `quads`·`posterior`·`calves`
  (zone). **`legs` sans plaque régionale.**
- **11 Muscle Plates (N3)** : 1:1 avec les 11 zones ; **9 muscle-heads** + **2 grouped-honest** (`upper_back`,
  `posterior`).
- **`part-*` normés** (registre ID Contract §4) : faisceaux = **Layer B**, jamais un code, jamais scorés.

### 4.2 Invariants transverses
`scored:false` · `non_medical:true` (littéraux) · `zone_codes ⊆ 11` · **aucune 12ᵉ zone** · **RADAR_AXES
inchangés** · couleur = tokens runtime · attribution CC BY perpétuelle · `ai_usage ≠ géométrie` · **aucun jeton
mensonger/mesure**.

## 5. Réconciliation métadonnées (spec/rapport 03B)

- `Sx_ASSET_03B_..._SPEC.md` : statut `SPEC DRAFT — BUILD NOT AUTHORIZED` → **`SPEC COMMITTED — ff9541a /
  Sb_ASSET_03B.1 AUTHORIZED / NOT YET COMPLETE`** ; `b1f0b63` = parent de cycle, `ff9541a` = HEAD.
- `SPRINT_Sx_ASSET_03B_..._REPORT.md` : « Créés (7) » → **« Créés (6) »** (6 créés + 3 modifiés = 9).
- Corrections NLM appliquées au SPEC §11 et à la Source Strategy (cohérence avec le Source Ledger).

## 6. Queue de builds (aucune ouverte ici)

| Build | Objet | Gate |
|---|---|---|
| `Sb_ASSET_03B.2` | Regional Plate production + intake (P0 chest/shoulders/posterior) + **enactment amendement §5 + guard test** | 03B.1 + master validé |
| `Sb_ASSET_03B.3` | Muscle Plate production + revue cohérence anatomique (overlays) | 03B.2 |
| `Sb_ASSET_03B.4` | Exercise Mechanics Overlay (couplage EKB, lecture seule) | 03B.3 |
| (intégration) | via `Sx_ASSET_04` — après gate | gate franchi |

## 7. Non-goals

Aucun asset graphique · aucun SVG/PNG/HTML · aucune maquette · aucun `viewBox` chiffré · aucun prompt d'image
exécuté · aucun prototype runtime · **aucune** réouverture `Sx_UI`/`Sx_ASSET_01/02/03` · aucune migration ·
aucune 12ᵉ zone · aucun code hors des 11 · aucune intégration `app/` · **aucun enactment de l'amendement §5 dans
ce build** (spécifié + gaté) · aucun franchissement de gate · aucune revendication `approved`/`legally cleared`/
`anatomically validated professionally`/`runtime ready`/`integration authorized`.

---

## Verdict

**Verdict :** 🟢 **`Sb_ASSET_03B.1: BLUEPRINT COMPLETE / PLATE CONTRACT LOCKED`.** Le système Muscle Focus est
**exécutable sur le papier** : inventaire (8+11) figé, **namespace d'IDs v0.1.0 propre et disjoint de l'API
`zone-*`**, schéma de descripteur, contrat de vues/crops, couches clean/overlay avec **caption-miroir**, a11y/
mobile/attribution, **7 blueprints P0 exacts**, **source-ledger revalidé (4 corrections)** et **amendement de
gouvernance borné (spécifié, gaté)**. Les **8 findings adversariaux sont résolus** ; les 5 axes sont synthétisés
en un seul arbitrage. **Aucune géométrie, aucune œuvre dupliquée, aucune intégration, aucune gate franchie.**
`PLATE GEOMETRY: NOT PRODUCED` · `MUSCLE FOCUS PLATES: BLUEPRINTED / NOT PRODUCED` · `SOURCE STRATEGY:
REVALIDATED` · `GOVERNANCE AMENDMENT: SPECIFIED / NOT YET ENACTED` · `RUNTIME INTEGRATION: NOT STARTED` ·
`PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED` · `ASSET INTEGRATION GATE: BLOCKED`.
