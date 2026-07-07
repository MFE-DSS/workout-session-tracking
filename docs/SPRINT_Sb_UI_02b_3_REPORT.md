# Sprint Report — Sb_UI_02b.3 Auren Terminal Hardening + Shell/Nav

**Sprint ID :** `Sb_UI_02b.3_AUREN_TERMINAL_HARDENING_SHELL_NAV`
**Type :** BUILD UI — global shell/nav hardening + Auren Terminal consistency + tests + report
**Date :** 2026-07-07
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Verdict :** 🟢 **DELIVERED — pending CI + human review**

---

## 1. Objectif

Harmoniser **la coque globale** (app.css tokens + shell/nav base.html) avec le monde Auren Terminal (graphite/mono/ambre), pour que **toute l'app** — pas seulement Home et Focus — donne une impression cohérente dès la navigation. Ce sprint **ferme la migration visuelle Auren Terminal V1** sans toucher aux moteurs métier.

## 2. Rappel Sb_UI_02b.1/.2 validés

- **Sb_UI_02b.1** : Home graphite/mono/ambre livré (CI verte).
- **Sb_UI_02b.2** : Focus Mode graphite/mono/ambre livré (CI verte, run `28875344109`).
- CI repo débloquée (SonarCloud Java 21 via `Sb_OPS.sonar-java21`).
- Restait : la coque (topbar, nav, pages non reskinnées) encore sur l'ancien thème dark/orange.

## 3. Fichiers changés (whitelist stricte respectée)

| Fichier | Nature |
|---|---|
| `app/static/css/app.css` | **migration des tokens `:root`** (graphite + mono + ambre) + bloc de hardening shell (focus ambre, nav active, active-banner, CTA, cards) + fix du dot orange légende |
| `app/templates/base.html` | **retrait du lien webfont Google Fonts** (Auren Terminal = mono système, zéro webfont) |
| `tests/test_shell_terminal.py` | **nouveau** — 15 tests shell/tokens/nav/cohérence |

**Aucun autre fichier touché** : `home.css`, `session_focus.css`, `index.html`, `session_detail.html`, tous les partials — intacts. Aucun route/service/model/migration/JS.

## 4. Shell/nav re-skin (méthode)

`app.css` a un bloc `:root` que **toutes les pages** consomment via `var(--bg)`, `var(--accent)`, `var(--font)`… Le re-skin **redéfinit les valeurs** de ces tokens (noms inchangés) → chaque page hérite automatiquement du look terminal, sans réécrire les sélecteurs métier. C'est la méthode la moins invasive possible pour une coque de ~3000 lignes.

Ajouts de hardening (bloc scoped en fin de fichier) :
- **Focus visible ambre** universel (`:focus-visible → outline var(--accent)`).
- **Topbar brand** en mono ; **lien nav actif** (`aria-current`) en ambre (seul accent de la nav).
- **Active-banner** : rail ambre + surface raised.
- **CTA primaire** (`.btn--primary`) : ambre plein + texte graphite (`--on-accent`).
- **Cards** radius 6px.
- `body { font-variant-numeric: tabular-nums }`.

## 5. app.css tokens (valeurs migrées)

- **Surfaces** : `--bg #0f1115 → #0F1318`, `--surface → #151A21`, `--surface-2 → #1B2029`, `--border → #2A303A`, `+ --border-strong #3A4250`.
- **Foreground** : `--fg → #E8ECEF`, `--fg-muted → #A7B0BA`, `--fg-dim → #8A94A0`.
- **Accent** : `--accent #f25f3a (orange) → #C8A24B (ambre)`, `+ --accent-hover #D7B45C`, `--accent-soft rgba ambre`, `--on-accent #0A0C0F`.
- **États** : ok/warn/danger/info désaturés graphite-compatibles.
- **Typo** : `--font Inter → var(--font-mono)` (stack mono système) ; `--font-mono` = ui-monospace + fallbacks système.
- **Chrome** : `--radius 8px → 6px`.

## 6. Graphite surfaces

Toute la coque prend `--bg` graphite. Topbar, nav, cards génériques, forms héritent des tokens. L'ancien orange `#f25f3a` est **retiré des tokens** ; le seul usage hardcodé résiduel (dot « strength » de la légende timeline) a été repointé sur `var(--accent)` (ambre), le dot « cardio » sur `var(--fg-muted)`.

## 7. AA / contrast

Contrastes calculés sur `--bg #0F1318` (identiques Home/Focus) : `fg` 15.7:1 ✅ · `fg-muted` 8.5:1 ✅ · `fg-dim` 6.1:1 ✅ · `accent #C8A24B` 7.7:1 ✅ · `on-accent #0A0C0F` sur ambre 8.1:1 ✅. Focus visible ambre 2px universel. Tap targets préservés.

## 8. Nav links préservés

Vérifié par test : `Accueil`, `Programmes`, `Historique`, `Progression`, `Profil`, `Déconnexion` (form logout) tous présents. Topbar `<details>`/`<a>`/`<form>` — no-JS intact. La marque `SPIGNOS` (base.html) **non modifiée** (rebrand réservé Sx_UI_10).

## 9. Home/Focus cohérence

Home (`today-home--terminal`) et Focus (`session-focus--terminal`) restent terminal (leurs CSS dédiés non touchés). La coque graphite les enveloppe désormais dans le même monde. Les pages précédemment non-reskinnées (login, register, progression) rendent maintenant graphite/mono/ambre via la migration des tokens app.css (deltas after-capture confirmés).

## 10. Tests exécutés

| Commande | Résultat |
|---|---|
| `check_ruff_budget.py` | ✅ **542 ≤ 548** |
| `check_spec_protocol.py` | ✅ pass |
| `pytest home_decision_hero + session_focus_terminal + shell_terminal + mobile_polish + visual_baseline_*` | ✅ **226 passed** |
| broad sweep (home / session_focus / shell / mobile_polish / visual / auth / profile / progress / physique / board / library / leaderboard / squad / coach / register / security / timeline) | ✅ **818 passed, 0 failed** |
| `tests/test_shell_terminal.py` (nouveau) | ✅ **15 passed** |

Tests shell : app.css `--bg` graphite · `--accent` ambre · orange `#f25f3a` retiré des tokens/valeurs · `--font` remappé mono · aucun webfont app.css · focus ambre + CTA ambre · base.html charge app.css + **plus de Google Fonts** · nav links préservés · logout form · Home/Focus terminal · topbar présent · no-JS/no-React.

## 11. Screenshots after (locaux, non commités)

- **Done. ok=16 failed=0** (`var/visual-after/Sb_UI_02b_3/`).
- **Anti-404 OK** : home 132 612 B · session-detail-active 236 399 B · profile 4 006 B · login 15 887 B (tous rendus complets).
- **Pages coque migrées (delta 02b.2 → 02b.3)** : login +27 B, register +559 B, progression +3 957 B → ces pages précédemment non-reskinnées passent en graphite/mono/ambre.
- **Home/Focus** stables (132 KB / 236 KB — CSS dédiés intacts).
- Screenshots **gitignored**, non commités.

## 12. Invariants préservés

- ✅ SSR + Jinja only — React/SPA/bundler interdits.
- ✅ Aucun changement route / service / model / migration / JS.
- ✅ `home.css` · `session_focus.css` · `index.html` · `session_detail.html` · partials · macros — **non touchés**.
- ✅ Nav links + logout + routes existantes inchangés.
- ✅ Aucun webfont (retiré) · aucun asset / GIF · aucun rebrand code (`SPIGNOS` intact).
- ✅ Baseline P0 capturable : `ok=16`.

## 13. Limites

- **Sparkline SVG** : la couleur du trait (`stroke="#f25f3a"` orange) est **hardcodée dans `app/services/timeline.py`** (zone interdite `app/services/**`) — **résidu non traité** dans ce sprint. La ligne de la sparkline restera orange jusqu'à un futur sprint touchant le service (ou un OPS dédié). Élément mineur (un trait fin dans une carte). La **légende** (dot) est corrigée en ambre côté CSS.
- Certains micro-composants legacy internes peuvent garder des teintes propres app.css non couvertes par les tokens principaux — nettoyage fin possible ultérieurement.
- Byte-delta faible sur certaines pages (profile sparse, app.css déjà dark) — la vraie bascule est orange→ambre + Inter→mono, peu visible en poids PNG.

## 14. Risques

- **Faible.** Migration par tokens, sans logique métier ; **818 tests verts** sur le périmètre élargi (toutes les pages coque). La méthode "redéfinir les tokens" garantit qu'aucun sélecteur métier n'est cassé.
- Lisibilité mono globale à valider en revue humaine.

## 15. Prochaine action

**Migration Auren Terminal V1 prête pour closeout** (Home + Focus + Shell cohérents). Deux voies possibles après human review :
- **Closeout `Sx_UI_02b`** (bilan de migration : Home + Focus + Shell, résidu sparkline documenté).
- **Retour `Sb_UI_05.2`** (Active Session / Next Workout Cards, désormais sur la baseline terminal).

## 16. Références

- Spec : `docs/strategy/Sx_UI_02b_AUREN_TERMINAL_SPEC.md`
- Home : `docs/SPRINT_Sb_UI_02b_1_REPORT.md` · Focus : `docs/SPRINT_Sb_UI_02b_2_REPORT.md`
- Registry : `docs/strategy/SPEC_REGISTRY.md`
- Roadmap : `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`

## 17. Verdict

🟢 **Sb_UI_02b.3 DELIVERED — pending CI + human review.**

**Migration Auren Terminal V1 (Home + Focus + Shell) : ready for closeout after review.**
**Sb_UI_05.2 : next candidate after closeout. Sx_UI_06 : future. Release tag deferred.**
**After-screenshots : captured locally 16/16, not committed.**
