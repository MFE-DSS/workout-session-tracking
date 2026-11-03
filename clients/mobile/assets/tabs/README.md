# Tab icons — MOB-01 · D4 « un ancrage propriétaire + trois utilitaires simples »

Template images for the native tab bar (`src/routes/_layout.tsx`): black on transparent, tinted by the system bar
(no colour is baked in). `<space>_<state>.png` at @1x / @2x / @3x (24 / 48 / 72 px), rendered from `source/*.svg`.
Default and selected differ only by fill vs outline or one structural closure — never by a new metaphor.

Operator decision: D3 « Famille C » rejected; D4 set A accepted on 2026-11-03 (board
https://claude.ai/artifact/HpJGvBW8azTfpmQgwPNyec).

| Space | Candidate | Construction reference | Licence |
|---|---|---|---|
| Aujourd'hui | c1 | AUREN-MARK-V1 (`design/auren/source/brand/mark/mark-primary.svg`), scaled 20/23, never redrawn | AUREN (LOCKED DA-03.2) |
| Programmes | p5 « pile décalée » | Lucide `file-stack`, lucide-static 1.66.0 — orthogonalised, square caps | ISC (`LICENSE-lucide.txt`) |
| Progrès | g3 « tendance » | Lucide `trending-up`, lucide-static 1.66.0 — square caps, selected closes the arrow head | ISC (`LICENSE-lucide.txt`) |
| Profil | h3 | AUREN drawing: the training-profile octagon + one off-centre core | AUREN |

The Lucide geometry is vendored and normalised here; no icon package is imported at runtime. Below 20 px the mark's
compact drawing applies (rule 12–15 / 16–19 / 20+ of AUREN-MARK-V1) — the tab bar renders at 24 pt.
