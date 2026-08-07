# Sprint Report — Sb_ASSET_04.1-P0 · Muscle Focus Controlled Runtime Integration

## Outcome
`COMPLETE (P0 controlled runtime integration)`. The three owner-accepted P0 regional plates (merged in
Sb_ASSET_03B.2R-D1) are surfaced **SSR / no-JS** on the educational `/science` page. No geometry rewrite,
no score/model/migration change, fallback preserved. Delivered via PR under BOUNDED_DELIVERY; **merge is
a separate human GO.**

## Brainstorming / Options / Risks / Choice (CLAUDE.md §3)
- **Discovery**: the GO references "the accepted Sx_ASSET_04-P0 mapping", but **no such mapping spec exists**
  (`Sx_ASSET_04` is a roadmap title only; `Sb_ASSET_04.1` was BLOCKED BY ASSET INTEGRATION GATE). Implementing
  an "accepted mapping" that doesn't exist would mean inventing a product-design decision.
- **Options** (owner-decided): (A) educational section on science/atlas; (B) upgrade the exercise-card
  decorative silhouette; (C) author the mapping spec first.
- **Risk**: the plates are gate-BLOCKED design-source; a mobile-critical-flow integration is intrusive and
  the plates (2048²) don't fit a compact card.
- **Choice retained (owner)**: **(A)** — a new "Muscle Focus" section on `/science` (educational, outside the
  critical flow, minimal product risk). Fallback = the existing decorative worked-area silhouette, unchanged.

## Implementation (SSR / no-JS)
- 3 plate SVGs inlined **byte-exact** from design source as Jinja partials `_partials/muscle_focus_plate_*.svg`
  (freeze sha `7a4167ea` / `5eb7bedf` / `b84c8bce`; guarded — no geometry rewrite).
- `_partials/muscle_focus.html` — three figures with honest captions; **shoulders front/back no-JS accessible
  toggle** (radio + `:checked` CSS view-crop; front default, back via explicit control); posterior individual
  provenance named (semi-tendineux, semi-membraneux, biceps fémoral long/court); **BodyParts3D CC BY 4.0
  attribution visible**; non-medical + not-professionally-reviewed disclaimers.
- `science.html` — new `#section-muscle-focus`. Route unchanged (no data/model/score/migration change).
- `app.css` — scoped `.muscle-focus` block; colour from Auren Terminal tokens (plates carry no business
  colour); shoulders view-crop is absolutely-positioned so its 200% width never causes horizontal overflow at
  360 px; reduced-motion honoured by the existing global block.
- Plates are `aria-hidden` (decorative); the caption carries the accessible truth (STYLE_RULES §7 / §5bis).

## Constraints honoured
SSR/Jinja · no geometry rewrite · existing consumer (science) only · no horizontal overflow at 360 px ·
accessible shoulders toggle (no-JS) · **no chest partition** (whole-pectoralis plate) · posterior provenance
preserved · attribution visible · no score/model/migration change · fallback (worked-area silhouette) preserved.

## Governance / gate
The owner decision (C3) authorised **controlled P0 runtime integration** (C5/S/P5). This sprint adds that one
controlled educational surface. The design-source governance (`design/auren/…`, gate `BLOCKED` for *general*
integration) is **left unchanged** — the /science surface is the specific owner-authorised exception,
documented here, not a blanket gate flip. **Professional anatomical / legal / medical review: NOT PERFORMED /
NOT CLAIMED.** `ai_usage: NONE`.

## Validation
8 runtime SSR tests PASS (`test_auren_muscle_focus_runtime.py`) · existing `/science` tests unaffected ·
D1 asset guards unaffected · 360 px visual verified (no horizontal overflow; plates coloured; toggle) ·
ruff + gitleaks below · full CI + SonarCloud on the PR.

## Verdict
**COMPLETE (P0 controlled runtime integration).** The three frozen P0 plates render SSR/no-JS on `/science`
(educational), byte-exact (no geometry rewrite), with an accessible shoulders front/back toggle, visible
BodyParts3D CC BY 4.0 attribution, no chest partition, preserved posterior provenance, and no 360 px overflow.
Internal synthetic review only — **NOT a professional anatomical review**; design-source gate unchanged; no
model/score/migration change. Delivered via PR under BOUNDED_DELIVERY; **merge remains a separate human GO.**

---

## Appendice post-merge (closeout 2026-08-07)

- **PR #49 MERGED** — merge commit **`ae10737`** (via `--merge`, **no squash, no `--admin`** — gate
  `mergeStateStatus: CLEAN`, 0 thread non résolu ; garde `--match-head-commit 1adc0d1`). Base `49bacfa`
  (D1 intake).
- **CI recovery** : le head final n'avait aucun run GitHub Actions (outage ~12 h) → **close/reopen (×1)**
  a redispatché ; **5 checks verts** (run `31156308300`) — `pytest + QA scripts` (11m59) · `lint` ·
  `SonarCloud` · `SonarCloud Code Analysis` · `Gitar`.
- **CI canonique (push) : run `31161250110` sur `ae10737` → 3/3 GREEN** (lint · pytest+QA · SonarCloud).
  **Coverage `91.1 %`**, Sonar delta `issues total: 0`.
- **Comportement livré** : 3 plaques P0 Muscle Focus (chest / shoulders / posterior) surfacées
  **SSR / no-JS** sur `/science` ; **aucune réécriture de géométrie** ; attribution **BodyParts3D
  CC BY 4.0 visible** ; disclaimers **non médicaux** ; toggle épaules face/dos no-JS accessible ;
  **pas d'overflow 360 px** (vérifié par le flux antérieur) ; fallback silhouette décorative préservé ;
  zéro changement route/modèle/score/migration.
- **Nit Gitar (« front default » tautologique)** : **résolu / différé sans changement de code** (revue
  acceptée en dette de durcissement de test).

**Verdict post-merge :** ✅ **Sb_ASSET_04.1-P0 — MERGED + CANONICAL CI GREEN.** (Dogfood humain réel
Martin sur `/science` desktop + 360 px : relève d'un flux séparé, non couvert par ce closeout docs.)
