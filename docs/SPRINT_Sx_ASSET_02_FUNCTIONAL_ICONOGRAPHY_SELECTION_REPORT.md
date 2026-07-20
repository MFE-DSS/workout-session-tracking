# Sprint Sx_ASSET_02 — Functional Iconography Selection — SPEC REPORT

**Statut** : 🟢 **SPEC RÉDIGÉE / READY FOR GO COMMIT**
**Type** : SPEC / AUDIT / OFFICIAL-SOURCE RESEARCH — **DOCS-ONLY** (0 SVG/licence/dépendance/app)
**Date** : 2026-07-20 · **Baseline** : `c1ad76c` (closeout Sx_ASSET_01)
**Livrables** : spec + ce rapport + due diligence (`docs/research/AUREN_ICON_VENDOR_DUE_DILIGENCE.md`)

> **SEMANTICS BEFORE ICONS.** Cette session **sélectionne un vocabulaire** ; elle **n'importe rien**. `Sx_ASSET_01`
> et `Sx_UI` restent CLOSED. `ASSET INTEGRATION GATE` reste BLOCKED.

---

## 1-2. Baseline
HEAD local = origin = `c1ad76c`, clean. Aucune spec `Sx_ASSET_02` préexistante (idempotence OK). Worktree
isolé `work/sx-asset-02-iconography-selection-spec` sur `c1ad76c` ; anti-collision `origin` contrôlé.

## 3. Brainstorming (§7)
`SEMANTICS BEFORE ICONS · MINIMAL SUBSET · TEXT REMAINS PRIMARY · NO MEDICALIZATION · NO AI SPARKLES · ONE
CONCEPT / ONE METAPHOR · OFFICIAL SOURCES ONLY · VERSION AND COMMIT PINNED · NO RUNTIME LIBRARY · NO ASSET
INTAKE IN SPEC · CUSTOM GLYPHS ONLY FOR PROVEN GAPS`.

## 4-11. Sources officielles (relevé réel 2026-07-20)
- **Tabler v3.45.0** (2026-07-17) · commit **`975920ff99c12c4dc9e3fe61a03738330600f9b2`** · **MIT** (© Paweł
  Kuna) · **5112 outline** · format `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
  stroke-width="2">` = **contrat Auren exact**.
- **Health Icons** · repo `resolvetosavelives/healthicons` · **0 tag** → commit
  **`891ace7addf4deb7a8b1ce8292d5906064fab36a`** (2025-09-04) · **icônes CC0 / code MIT** (distinction
  critique enregistrée). **NOT REQUIRED FOR P0.**
- Sources primaires uniquement (API GitHub + `healthicons.org/about`) ; 0 agrégateur/CDN/blog juridique.
- État : **OFFICIAL LICENSE EVIDENCE RECORDED AT ACCESS DATE**, **PAS** `LEGAL CLEARANCE COMPLETE`.

## 12-13. Inventaire runtime & SVG existants
Audit réel : **8 SVG inline** (base.html : 4 bottom-nav + 4 rail identiques, `existing-runtime-keep`) +
glyphes/emoji non gouvernés (`✓ ⚠ 💡 ☰`, candidats remplacement). BodyMap/welcome/science = OUT OF SCOPE.
**Fait majeur** : l'app est déjà quasi sans icônes ; les concepts sont **portés par le texte** → besoin réel
faible et ciblé. Matrice complète dans la spec §6.

## 14-16. Catégories & décisions P0/P1/typographic
- **P0 (10 Tabler à vendorer)** : substitute (`arrows-exchange`), timer play/pause/reset (`player-play`/
  `player-pause`/`rotate`), expand/collapse (`chevron-down`/`chevron-up`), guidance (`bulb`), warning
  (`alert-triangle`), completed (`check`), menu (`menu-2`). **Les 17 noms (P0+P1) vérifiés existants** au tag
  `v3.45.0` (API git tree, 0 nom inventé).
- **P1 différé** : trends (`trending-up`/`minus`/`trending-down`), excluded (`ban`), substituted history,
  history (`history`), program (`list-details`).
- **Typographic-only** : kg/reps/série/cible/**RIR**/durée/score/pourcentage/zones/primary-secondary/
  **confidence score**.

## 17-20. Health Icons / gaps custom / rejets
- **HEALTH ICONS NOT REQUIRED FOR P0** (concepts corporels médicaliseraient ; zone = BodyMap `Sx_ASSET_03`).
- **CUSTOM GLYPH TRACK: NOT REQUIRED** — 8 concepts testés (Body Intelligence, confidence, zone worked,
  substitution pattern, overload, substituted/excluded, push/pull), **0 gap démontré** (texte/Tabler
  suffisent). `Sb_ASSET_02.2: NOT REQUIRED`.
- **Rejetés/interdits** : sparkles IA · robot/cerveau · stéthoscope/croix médicale/ECG · flamme/éclair ·
  trophée · cible reco · haltère générique · silhouette générique · **tout emoji**.

## 21-27. Accessibilité / surfaces / budgets / vendoring / provenance / versioning / migration / tests / review
- **A11y** : décorative (`aria-hidden`/`focusable=false`) · action+texte (label sur le contrôle) · icône seule
  (timer/menu : accessible name, ≥44 px, focus visible) · tendance jamais couleur seule.
- **Surfaces** : matrice 13 surfaces (§19 spec) ; bottom-nav/rail = 4 icônes + label obligatoire.
- **Budget** : **10 ≤ 20** ✅ (< 24, pas de SPEC BLOCKED) ; ≤ 2 Ko/icône ; 0 npm/webfont/CDN/JS.
- **Vendoring** : dossiers `design/auren/source/icons/vendor/tabler/v3.45.0/outline/` **préparés, non créés** ;
  `app/static/` ≠ autorisé (build `04.1`).
- **Provenance/versioning** : 17 champs préparés ; épinglage tag+commit ; blob SHA comparé à l'intake ;
  `latest`/`main` interdits.
- **Migration** : reco partials Jinja/macros `currentColor` (SSR/no-JS), non implémentée.
- **Tests `02.1`** : manifest/fichiers (allowlist, viewBox 24, 0 hex, ≤2 Ko)/licence (MIT + CC0)/sémantique
  (1 id→1 fichier)/scope (0 app) — **sans snapshot pixel**.
- **Human review** : lisibilité 16/20/24 px, non-médicalisation, Auren Terminal, mobile 360 px.

## 28-29. Gates & queue
`ASSET INTEGRATION GATE: BLOCKED` inchangé ; spec rend `ICON INTAKE GATE: READY FOR Sb_ASSET_02.1`.
Queue : `Sb_ASSET_02.1` (intake P0) → `Sb_ASSET_02.2` **NOT REQUIRED** → `Sx_ASSET_02` closeout.

## 30. Fichiers docs
Créés : `docs/strategy/Sx_ASSET_02_FUNCTIONAL_ICONOGRAPHY_SELECTION_SPEC.md` · ce rapport ·
`docs/research/AUREN_ICON_VENDOR_DUE_DILIGENCE.md`. Modifiés : `SPEC_REGISTRY.md` ·
`ROADMAP_AND_NEXT_STEPS.md` · `AUREN_ASSET_PROGRAM_ROADMAP.md`. **0** `design/**`/`tests/**`/`app/**`/SVG/
licence/dépendance/Custom.

## 31. Scope / spec protocol
100 % `docs/**`. `check_spec_protocol` PASS attendu (spec a une section Non-goals, rapport a un marqueur
Verdict). `AUREN_ICON_SEMANTIC_MAP.md` **non créé** (= build `02.1`).

---

## Verdict

**Verdict :** 🟢 **Sx_ASSET_02: SPEC READY FOR COMMIT.** Vocabulaire fonctionnel minimal défini sémantique
d'abord : **10 concepts P0** couverts par **Tabler v3.45.0** (commit `975920ff…`, MIT, 17 noms vérifiés
existants, format = contrat Auren), P1 différé, métriques/confidence **typographic-only**, **Health Icons NOT
REQUIRED FOR P0** (CC0 assets / MIT code distingués), **0 gap custom** → `Sb_ASSET_02.2 NOT REQUIRED`.
Versioning épinglé, provenance/tests/review préparés, budget 10 ≤ 20. `ICON INTAKE GATE: READY FOR
Sb_ASSET_02.1` ; `ASSET INTEGRATION GATE` reste **BLOCKED** ; `Sx_ASSET_01`/`Sx_UI` **CLOSED**. Aucune
conclusion juridique absolue (evidence at access date).

**Prochaine action** (séparée, non commencée) : `GO COMMIT SPEC — Sx_ASSET_02 Functional Iconography
Selection`.
