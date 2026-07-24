# Sprint Sx_ASSET_03B — Muscle Focus Technical Surface System — SPEC

**Statut** : 🟢 **SPEC COMMITTED (docs-only)** — cadrage/spec/recherche ; **aucun asset, aucun build**.
**Type** : SPEC ONLY / SYSTEM DESIGN — sous-cycle additif de `Sx_ASSET`.
**Date** : 2026-07-24
**Base canonique** : `b1f0b63` · **Worktree** : `work/sx-asset-03b-muscle-focus-system`.
**Ne rouvre pas** : `Sx_UI` (CLOSED) · `Sx_ASSET_01` (CLOSED) · `Sx_ASSET_02` (CLOSED) · contrat sémantique
BodyMap (immuable). `ASSET INTEGRATION GATE: BLOCKED`.

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

| Décision | Options | Choix retenu |
|---|---|---|
| Bodymap global | remplacé · conservé/reclassé | **conservé, reclassé Niveau 1** (navigation/synthèse) — le pivot est **additif** |
| Surface premium | enrichir le global · nouveau système zoomé | **nouveau système de plaques zoomées** (Muscle Focus Plates) |
| Granularité | nouvelles zones · sous-structures Layer B | **sous-heads = géométrie Layer B**, **aucune 12ᵉ zone**, les 11 codes restent l'API |
| Direction visuelle | rendu réaliste · clean view + technical overlay | **clean + overlay activable**, profondeur par le trait, ancrage osseux |
| Sources | commande illustrateur · source-reuse-first | **source-reuse-first** (cohérent BodyMap : Servier + OpenStax 1ʳᵉ éd. + PD ; validation BodyParts3D/Z-Anatomy) |
| Anti-atlas | savoir gratuit · ancrage exercice | **chaque plaque débouche sur une action de training** |

## 1. Usage réel des Superpowers (brainstorming / recherche / parallélisation / arbitrage)

- **Parallélisation — 4 sous-agents lancés simultanément** (Axes A/B/C/D), conformément à la mission :
  - **Axe A** — Product/UX framing (drill-down « se tire, ne se pousse jamais » ; ancrage exercice anti-atlas ;
    aucun drill pendant le logging ; texte adjacent a11y).
  - **Axe B** — Visual/anatomical direction (**recherche web** : 5 familles de références, principes extraits,
    grammaire clean-view/overlay, 5 cas d'exigence en contraintes de forme).
  - **Axe C** — Source/asset strategy (**recherche web** : matrice de licences vérifiées, 4 rôles de source,
    IA bornée).
  - **Axe D** — IA/system design (objets, typologie 8+11 plaques clefées sur les 11 codes, modules, états
    projetés sur les 5 états figés, mobile/desktop, contrat d'IDs de plaque, amendement de gouvernance §5).
- **Brainstorming structuré** : Étape 0 ci-dessus + les 3 niveaux tranchés.
- **Recherche** : web réelle (Axes B/C) + lecture des docs internes (roadmap ASSET, `AUREN_BODYMAP_OPEN_SOURCE_REUSE_STRATEGY.md`,
  contrat SVG, taxonomie 11 zones).
- **Synthèse contradictoire / arbitrage** : voir §2.

## 2. Arbitrage d'une contradiction (croisement adversarial)

L'**Axe C** a relevé BodyParts3D en **CC BY-SA 2.1 JP** (« risque #1 ») — mais depuis le **miroir GitHub figé
en 2011**. Le repo avait **déjà documenté et corrigé** ce piège : la page officielle DBCLS (maj **2025-02-27**)
porte **CC BY 4.0**. **Arbitrage : CC BY 4.0** ; l'erreur est écartée, mais les **apports réels** de l'Axe C
sont **conservés** (nuance « un mesh 3D est une expression protégée même si le fait ne l'est pas » ; sources PD
ajoutées Gray's 1918 / Visible Human ; exclusions MuscleWiki/BioDigital/OpenStax 2ᵉ éd. ; hygiène agrégateurs).
Documenté en §0 de la recherche. *C'est précisément la valeur d'un croisement à plusieurs voix.*

## 3. Diagnostic (limites du bodymap global)

Cadrage « corps entier » (zoom nul) · granularité arrêtée à la zone (11 codes) · silhouette **décorative** par
contrat (fibres/insertions interdites `§5`) · rôle synthèse (« où/combien », jamais « comment ») · agrégats
non subdivisibles. **Ce ne sont pas des défauts** mais les choix qui rendent le global stable — le pivot
**ajoute une couche** au lieu de les corriger.

## 4. Fichiers créés / modifiés

**Créés (7)** :
- `docs/strategy/Sx_ASSET_03B_MUSCLE_FOCUS_TECHNICAL_SURFACE_SYSTEM_SPEC.md` (spec, 18 sections + verdict)
- `docs/research/AUREN_MUSCLE_FOCUS_REFERENCE_RESEARCH.md` (recherche + arbitrage)
- `docs/production/muscle-focus/AUREN_MUSCLE_FOCUS_SYSTEM_OVERVIEW.md`
- `docs/production/muscle-focus/AUREN_MUSCLE_FOCUS_PLATE_TEMPLATE.md`
- `docs/production/muscle-focus/AUREN_MUSCLE_FOCUS_SOURCE_STRATEGY.md`
- ce rapport
**Modifiés (3)** :
- `docs/strategy/AUREN_ASSET_PROGRAM_ROADMAP.md` (ajout sous-cycle 03B)
- `docs/strategy/SPEC_REGISTRY.md` (ligne `Sx_ASSET_03B`)
- `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` (ligne `Sx_ASSET_03B`)

**Scope** : **100 % `docs/**`**. 0 `app/` · 0 `design/auren/` binaire · 0 SVG/PNG/HTML runtime · 0 tests · 0
scripts · 0 `data/` · 0 migrations · 0 `.github/` · 0 Custom/EKB/scoring · 0 intégration.

## 5. Contenu tranché par la spec (résumé)

Système à **3 niveaux** ancrés sur les 11 zones : Global Map (N1, conservé) → **8 Regional Plates** (une par
macro, `legs` éclatée en quads/posterior/calves) → **11 Muscle Plates** (1:1 zone, 9 muscle-heads + 2
grouped-honest). **11 modules** de plaque ; états `clean`/`overlay-on`/`exercise-highlighted` projetés sur les
**5 états figés** ; mobile (sheet, overlays repliés) vs desktop ; **contrat d'IDs de plaque** distinct de l'API
`zone-<code>`. Direction visuelle clean-view + technical-overlay, profondeur par le trait, ancrage osseux, ≤ 3
teintes. **5 cas d'exigence** (pectoraux/deltoïdes/postérieur/lats-upper_back/core) en contraintes de forme.
Stratégie de sources source-reuse-first. Queue de builds `Sb_ASSET_03B.1→4` gatée. **Amendement de gouvernance
requis** : autoriser fibres/insertions **uniquement sur la surface plaque dédiée** (le global reste régi par
`§5`).

## 6. Vérifications

`git diff --check` propre · `check_spec_protocol` PASS (spec = section non-goals §17 ; rapport = verdict) ·
`check_scope` DOCS · diff = **100 % `docs/**`** · aucune réouverture `Sx_UI`/`Sx_ASSET_01/02/03` · **aucun
terme mensonger** (`approved` / `legally cleared` / `anatomically validated professionally` / `runtime ready` /
`integration authorized` absents en affirmation).

## 7. Non-goals (rappel)

Aucun asset graphique · aucun SVG · aucune maquette · aucun prompt d'image exécuté · aucun prototype runtime ·
aucune migration · aucune 12ᵉ zone · aucune intégration `app/` · aucun franchissement de gate. `Sb_ASSET_03B.1`
et la suite **NOT OPENED**.

---

## Verdict

**Verdict :** 🟢 **`Sx_ASSET_03B` — SPEC COMMITTED / MUSCLE FOCUS SYSTEM: DEFINED.** Le cadrage du système
premium cible est complet et docs-only : bodymap global **conservé** comme couche de navigation/synthèse
(niveau 1), surfaces zoomées **conceptuellement définies** (8 Regional + 11 Muscle Plates, ancrées sur les 11
zones immuables), direction visuelle et cas d'exigence anatomiques tranchés, stratégie de sources
source-reuse-first établie (avec **arbitrage d'une contradiction de licence** par croisement adversarial), IA
bornée, queue de builds gatée. **Aucun asset produit, aucune œuvre dupliquée, aucune intégration.**
`MUSCLE FOCUS PLATES: CONCEPTUALLY DEFINED / NOT PRODUCED` · `GLOBAL BODYMAP: RETAINED AS NAVIGATION /
SYNTHESIS LAYER` · `SOURCE STRATEGY: DEFINED` · `RUNTIME INTEGRATION: NOT STARTED` · `PROFESSIONAL LEGAL
CLEARANCE: NOT CLAIMED` · `ASSET INTEGRATION GATE: BLOCKED`. **Prochaine action (non ouverte) :** `GO BUILD —
Sb_ASSET_03B.1 Muscle Focus System Blueprint & Plate Template`.
