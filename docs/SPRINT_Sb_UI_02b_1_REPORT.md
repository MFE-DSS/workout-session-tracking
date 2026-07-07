# Sprint Report — Sb_UI_02b.1 Auren Terminal Tokens + Home Re-skin

**Sprint ID :** `Sb_UI_02b.1_AUREN_TERMINAL_TOKENS_AND_HOME_RESKIN`
**Type :** BUILD UI — tokens CSS + Home re-skin + tests + report
**Date :** 2026-07-07
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Verdict :** 🟢 **DELIVERED — pending CI + human review**

---

## 1. Objectif

Transformer le Home « teal-light / wellness » en **première surface Auren Terminal** — le « Palantir du bodybuilding » : **graphite dense + typographie tout-mono + accent ambre rare (`#C8A24B`)**. Premier build de la migration Sx_UI_02b. L'utilisateur doit ressentir densité, précision, contrôle, sobriété — aucun effet wellness/spa, aucun dashboard SaaS générique, aucun gaming cyberpunk.

## 2. Rappel Sx_UI_02b accepted

La spec `Sx_UI_02b_AUREN_TERMINAL_SPEC` a été acceptée en human review (commit `e08381b`) avec 8 OQ tranchées : accent ambre `#C8A24B`, tout-mono système, graphite neutre froid, migration review-gated Home → Focus → hardening, dark unique V1, teal retiré, densité intermédiaire, nav en `.3`. **Re-skin, pas re-architecture** — invariants Sx_UI_04 intacts.

## 3. Stash teal droppé (non réappliqué)

Le patch teal obsolète (`stash@{0}`) a été **droppé** (`git stash drop stash@{0}`, hash `eed3778`) **avant** le build, sur instruction. Le build part de HEAD propre (`add992f` = Home teal committé, CI verte). Aucun empilement graphite au-dessus du patch teal.

## 4. Fichiers changés (whitelist stricte respectée)

| Fichier | Nature |
|---|---|
| `app/static/css/home.css` | **re-skin complet** Auren Terminal (tokens graphite + mono + ambre, scoped `.today-home`) |
| `app/templates/index.html` | marqueur `today-home--terminal`, statut, action block, microcopy terminal ; hero/CTA/branches/dashboard préservés |
| `tests/test_home_decision_hero.py` | 6 nouveaux tests Auren Terminal + ajustements (34 tests) |

**`app.css` non touché**, `session_focus.css` non touché, Focus Mode non touché (re-skin réservé à `.2`).

## 5. Tokens Home appliqués (scoped `.today-home`)

**Surfaces graphite** (séparation par luminosité, pas d'ombre) :
`--t-void #0A0C0F` · `--t-base #0F1318` · `--t-surface #151A21` · `--t-raised #1B2029` · `--t-line #2A303A` · `--t-line-strong #3A4250`.

**Foreground gris froids** : `--t-fg #E8ECEF` · `--t-fg-2 #A7B0BA` · `--t-fg-muted #8A94A0` · `--t-fg-faint #5A6472`.

**Accent AMBRE unique** : `--t-amber #C8A24B` · hover `#D7B45C` · dim `#8A7538` · weak `rgba(200,162,75,0.12)` · on-amber `#0A0C0F`.

**Typo tout-mono système** (zéro webfont) : `ui-monospace, SFMono-Regular, "SF Mono", Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace`. Graisse ≤ 600, titre 24px (26 desktop), `tabular-nums`, letter-spacing négatif sur titres, uppercase sur eyebrows/CTA.

**Chrome** : radius 4–6px, **aucune ombre décorative**, cards = surface + 1px line.

## 6. Graphite surfaces

Le Home entier (`.today-home`) prend le fond graphite `--t-base`. Le hero est `--t-surface` (+ rail ambre 2px en tête), la carte active passe en `--t-raised` (dominance par luminosité + rail latéral ambre). Les cards legacy du dashboard sont **re-stylées graphite DANS la zone Home uniquement** (`.today-home .card`, `.readiness-widget`, `.insight`, `.tile`) — pour éviter un dashboard clair/dark qui jurerait avec le hero, **sans toucher app.css** ni les autres pages. L'ancien accent orange legacy est neutralisé (`.today-home .kpi--accent .kpi__value` → ambre).

## 7. Mono typography

Toute la surface Home est en monospace système. Les chiffres (KPI, durées, compteurs) sont `tabular-nums`, alignés. Titres mono à graisse 600, letter-spacing −0.02em. Eyebrows/CTA en uppercase mono avec letter-spacing léger. Phrases courtes (discipline §22 Sx_UI_04).

## 8. Amber accent (rare)

L'ambre `#C8A24B` n'apparaît QUE sur :
- la **CTA primaire** (seule surface ambre pleine) ;
- le **rail** en tête de hero + rail latéral de la carte active ;
- le **préfixe `▸`** des eyebrows (signal minimal) ;
- le **focus visible** (outline ambre) ;
- la **valeur KPI accent** legacy neutralisée en ambre.

Tout le reste est graphite / gris. La couleur reste un événement.

## 9. Accessibilité / contrast reasoning

Contrastes calculés sur `--t-base #0F1318` (vérifiés par script) :
- `fg #E8ECEF` → **15.7:1** ✅ AA
- `fg-2 #A7B0BA` → **8.5:1** ✅ AA
- `fg-muted #8A94A0` → **6.1:1** ✅ AA (choisi > `#6F7A86` qui était 4.26:1 borderline)
- `amber #C8A24B` → **7.7:1** ✅ AA
- `on-amber #0A0C0F` sur amber → **8.1:1** ✅ (texte CTA lisible)

Focus visible : outline ambre 2px partout. Tap targets ≥ 44px (CTA 52px, secondary 44px). `prefers-reduced-motion` inchangé. Body copy mono lisible mobile (font-size ≥ 13px, line-height 1.45). Le graphite dense + fort contraste est **meilleur en lumière variable** (salle) qu'un blanc éblouissant.

## 10. Home decision IA préservée

- `.today-home` wrapper + `today-home--terminal`.
- **Hero Decision Surface** conservée (eyebrow « Aujourd'hui » + statut + titre + **CTA primaire unique** + action block + teaser readiness).
- **Active session domine** (`--active`, « Reprendre » → `/sessions/{id}`, méta « En cours · depuis {durée} »).
- **No-active** (« Prêt à t'entraîner ? » + « Démarrer une séance » → launcher).
- **Readiness teaser** qualitatif self-report, non médical.
- **Dashboard legacy** conservé, dé-priorisé sous en-tête « Résumé ».
- Routes / links existants **inchangés**. No-JS.

## 11. Tests exécutés

| Commande | Résultat |
|---|---|
| `check_ruff_budget.py` | ✅ **542 ≤ 548** |
| `check_spec_protocol.py` | ✅ pass |
| `pytest tests/test_home_decision_hero.py` | ✅ **34 passed** (dont 6 Auren Terminal) |
| `pytest tests/test_mobile_polish.py tests/test_visual_baseline_*` | ✅ (inclus dans le sweep) |
| broad sweep home-route (library, board_behavioral, home_payload, session_flow, mobile_polish, visual, reco, telemetry, sb_10, leaderboard, register_profile, body_profile, security, exercise_history, science + hero) | ✅ **351 passed, 0 failed** |

Tests Auren Terminal : **aucun hex teal** (`#0F8A85`/`#0B7A75`/…) dans home.css · **ambre `#C8A24B` présent** · **surfaces graphite** (pas de `--home-surface: #FFFFFF`) · **stack monospace** · **aucun webfont/@import/@font-face** · **aucune ombre décorative sur le hero**. Plus : marqueur terminal, statut, action, en-tête Résumé, CTA unique, active dominance, dashboard secondaire, no medical, no-JS, app.css intact.

### Incidents résolus (pré-commit)
- `test_no_teal_in_home_css` trippait sur le mot « teal » dans un **commentaire** documentant le retrait → test resserré aux **hex** (le vrai risque de fuite visuelle).
- `test_home_resume_tile_shows_duration_since_start` (legacy) attendait « depuis » dans la méta active → **« depuis » restauré** dans la microcopy terminal (contrat de durée préservé, test non affaibli).

## 12. Screenshots after (locaux, non commités)

Capture P0 locale (uvicorn 127.0.0.1:8001, runtime CLI Sb_UI_11.2) :
- **Done. ok=16 failed=0** (`var/visual-after/Sb_UI_02b_1/`).
- **Anti-404 OK** : `home-authenticated/mobile-authenticated.png` = 132 735 B (page complète).
- **Delta teal → terminal** : home/mobile 126 896 B → 132 735 B ; desktop 141 789 B → 146 838 B. La taille byte est un proxy faible (une page graphite compresse différemment), mais la **transformation visuelle est totale** : palette blanc/teal → graphite/ambre, typo → tout-mono (vérifié CSS : aucun hex teal servi, graphite/mono/ambre servis).
- **Contrôle Focus Mode inchangé** : `session-detail-active/mobile` = 230 857 B (Focus non re-skinné en `.1` — réservé `.2`).
- Screenshots **gitignored**, non commités.

## 13. Invariants préservés

- ✅ Route `/` reste Home / Today.
- ✅ SSR + Jinja only — React/SPA/bundler interdits.
- ✅ Aucun changement route / service / model / migration / JS.
- ✅ `app.css` non touché · `session_focus.css` non touché · **Focus Mode non touché** · partials/macros non touchés.
- ✅ Une seule CTA primaire ; dashboard existant conservé/accessible.
- ✅ Aucun claim médical ; readiness = repère self-report.
- ✅ No-JS complet ; WCAG 44×44 ; focus visible ambre ; AA vérifié.
- ✅ Aucun webfont / asset / GIF / SVG externe (graphite/mono = CSS + stack système).
- ✅ Aucun rebrand SPIGNOS → Auren dans le code.
- ✅ Baseline P0 capturable : `ok=16`.

## 14. Limites

- Les cards legacy sont re-skinnées **au niveau Home** (scoped `.today-home`), pas globalement — cohérent mais léger « patch de scope » ; l'harmonisation globale viendra avec les autres écrans.
- Le **Focus Mode reste teal/clair** jusqu'à `Sb_UI_02b.2` — transition à deux mondes assumée **temporairement** (Home graphite, Session claire) sur une seule étape.
- Certains micro-composants legacy internes (badges readiness colorés) gardent leurs couleurs sémantiques dans le widget existant — nettoyage fin possible en hardening `.3`.

## 15. Risques

- **Faible.** Build additif, scoped, sans logique métier ; 351 tests home-route verts. Contrats legacy préservés (« depuis », « disponibilit », « Démarrer une séance », tiles nav).
- Risque de cohérence : Home graphite vs Focus clair pendant une étape — assumé, résolu en `.2`.
- Lisibilité mono à valider en revue humaine (phrases courtes respectées).

## 16. Prochaine étape

**`Sb_UI_02b.2 Focus Re-skin`** — migrer `session_focus.css` (Focus Mode / cockpit Sx_UI_04) vers Auren Terminal graphite/mono/ambre, invariants structurels intacts. Puis `.3` hardening + shell/nav + baseline re-capturée.

## 17. Références

- Spec : `docs/strategy/Sx_UI_02b_AUREN_TERMINAL_SPEC.md`
- Spec acceptance : `docs/SPRINT_Sx_UI_02b_HUMAN_REVIEW_REPORT.md`
- Home spec : `docs/strategy/Sx_UI_05_TODAY_READINESS_HOME_SPEC.md`
- Registry : `docs/strategy/SPEC_REGISTRY.md`
- Roadmap : `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`

## 18. Verdict

🟢 **Sb_UI_02b.1 DELIVERED — pending CI + human review.**

**Sb_UI_02b.2 Focus Re-skin : next candidate, not opened.**
**Sb_UI_05.2 : still deferred. Sx_UI_06 : future.**
**After-screenshots : captured locally 16/16, not committed. No release tag.**
