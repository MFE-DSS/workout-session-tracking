# Sprint Report — Sb_UI_05.1 Home IA + Hero Decision Surface

**Sprint ID :** `Sb_UI_05.1_HOME_INFORMATION_ARCHITECTURE_AND_HERO_DECISION_SURFACE`
**Type :** BUILD UI — template structure + scoped CSS + tests + report
**Date :** 2026-07-07
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Verdict :** 🟢 **DELIVERED — pending CI + human review**

---

## 1. Objectif

Transformer l'accueil en **cockpit de décision quotidien** : l'utilisateur doit comprendre en 5 s s'il doit reprendre une séance active, en démarrer une, ou récupérer — via une **Hero Decision Surface** avec **une CTA principale unique**. Premier build du cycle Sx_UI_05 : IA + hero. Les blocs dashboard existants sont **conservés mais dé-priorisés** sous le hero.

## 2. Rappel Sx_UI_05 spec accepted

La spec `Sx_UI_05_TODAY_READINESS_HOME_SPEC` a été acceptée en human review (commit `b0ff372`) avec 10 OQ tranchées : Today reste root, readiness = bande qualitative self-report (non médicale), active session domine, repos non impératif, body léger, progress snapshot+lien, coach micro-note, nouvel utilisateur « Commencer », Home 100% no-JS, aucune nouvelle pref. Sb_UI_05.1 = premier build (IA + hero) ; le readiness/recovery complet est réservé à `.3`, la body continuity à `.4`.

## 3. Fichiers changés (whitelist stricte respectée)

| Fichier | Nature |
|---|---|
| `app/templates/index.html` | restructuration IA : `.today-home` wrapper + Hero Decision Surface + branches (active / no-active) + dashboard dé-priorisé |
| `app/static/css/home.css` | **nouveau** — CSS scoped `.today-home`, chargé via `extra_head` après `app.css` |
| `tests/test_home_decision_hero.py` | **nouveau** — 23 tests hero/IA/branches/invariants |

**`app.css` non touché** : un fichier dédié `home.css` a été créé (mécanisme `{% block extra_head %}` de `base.html`, identique à `session_focus.css`) — aucune fuite globale, aucun bloc scoped `.today-home` dans `app.css`.

## 4. Home IA

Le Home est enveloppé dans `.today-home` (flex column) :
1. **Hero Decision Surface** (`.today-home__hero`) en tête — voir §5.
2. **Secondary zone** (`.today-home__secondary-zone`) en dessous — tous les blocs existants conservés (coaching loop, next reco, readiness widget, disponibilité KPI, KPI-row + sparkline, tile-grid nav).

L'ancien titre `<h1>Cockpit</h1>` (non contractuel, aucun test) est remplacé par le hero décisionnel. Aucune information supprimée.

## 5. Hero Decision Surface

`.today-home__hero` (surface claire Auren, scoped) : eyebrow « **Aujourd'hui** » + titre décisionnel + **une CTA primaire unique** + lien secondaire discret + teaser readiness optionnel.
- Grammaire Auren appliquée au hero uniquement (blanc, teal `#0F8A85`, faible chrome, tap target ≥ 48px) — le dashboard legacy reste stylé par `app.css`.
- CTA = plain `<a href>` vers une route existante (no-JS).

## 6. Active session dominance

Résolution du Today Decision Model (§8 spec) :
- **Si `open_session`** : hero `--active` (bordure accent latérale), titre « **Séance en cours** », méta (nom + `open_since` déjà calculé), CTA « **Reprendre la séance** » → `/sessions/{id}` (route existante). Lien secondaire « Démarrer une autre séance ». La session active **domine**.

## 7. No active session / empty state

- **Sinon** : titre « **Prêt à t'entraîner ?** », CTA « **Démarrer une séance** » → `launcher` (route existante), lien secondaire « Voir les programmes ».
- Cette branche couvre aussi le **nouvel utilisateur** (OQ-05-H) : la CTA « Démarrer » / « Voir les programmes » oriente sans métriques vides ni marketing. (Un libellé « Commencer » dédié pourra être affiné en `.2` si une distinction new-user explicite est introduite — hors scope V1 sans nouvelle logique backend.)

## 8. CTA principale

**Une seule** CTA primaire dans le hero (`.today-home__cta`) — vérifié par test (`body.count("today-home__cta") == 1` dans les deux branches). Les autres actions (lien secondaire, tiles nav) sont visuellement subordonnées.

## 9. Readiness teaser / absence

- **Si `readiness_today`** : micro-teaser `.today-home__readiness` = « **Repère du jour** · état déclaré · voir plus bas » — **qualitatif, non médical**, renvoie au widget readiness existant (dé-priorisé plus bas). Aucun score numérique dans le hero.
- **Sinon** : teaser absent, hero non bloqué.
- Le **readiness/recovery complet** (bande qualitative agrégée, recovery cues) est réservé à **Sb_UI_05.3** — pas construit ici.

## 10. Dashboard de-prioritization

Tous les blocs existants (coaching loop, next reco, readiness widget, disponibilité KPI 0-100, KPI-row cette sem./score/complétion, sparkline 14j, tile-grid Historique/Progression/Programmes/Science) sont **conservés intégralement** dans la secondary zone, sous le hero. Aucune suppression : les contrats textuels legacy (« disponibilit », « Démarrer une séance », « Historique/Progression/Programmes ») sont préservés → les tests existants passent.

## 11. Tests exécutés

| Commande | Résultat |
|---|---|
| `check_ruff_budget.py` | ✅ **542 ≤ 548** |
| `check_spec_protocol.py` | ✅ pass |
| `pytest tests/test_mobile_polish.py tests/test_visual_baseline_*` | ✅ **159 passed** |
| tests home-route (library, board_behavioral, home_payload, session_flow, reco, telemetry, sb_10_polish, leaderboard, register_profile, body_profile, security, exercise_history, science) + hero | ✅ **182 passed, 0 failed** |
| `tests/test_home_decision_hero.py` (nouveau) | ✅ **23 passed** |

Tests hero couvrent : wrapper `.today-home` · hero + eyebrow · **CTA unique** (2 branches) · active dominance (`--active` + Reprendre + `/sessions/{id}`) · no-active « Démarrer une séance » · readiness teaser qualitatif (pas de claim médical) · dashboard préservé (disponibilité, tiles, KPIs, progress link) · hero avant secondary zone (DOM) · CTA plain `<a>` no-JS · no-React · pas de nouveau JS · home.css scoped + tap target ≥ 44px + chargé via extra_head.

## 12. Screenshots after (locaux, non commités)

Capture P0 locale (uvicorn 127.0.0.1:8001, runtime CLI Sb_UI_11.2) :
- **Done. ok=16 failed=0** (`var/visual-after/Sb_UI_05_1/`).
- **Anti-404 OK** : `home-authenticated/mobile-authenticated.png` = 126 896 B (page complète).
- **Delta home 04.5 → 05.1** : mobile 119 916 B → **126 896 B** (+7 KB), desktop 131 936 B → **141 789 B** (+9,9 KB) — le hero decision surface ajoute une structure visible.
- **Contrôle Focus Mode inchangé** : `session-detail-active/mobile` 230 934 B → 230 857 B (≈ identique, Sx_UI_04 non touché).
- Screenshots **gitignored** (`/var/`), non commités.

Note : `home-authenticated` et `home-no-active-session` rendent des tailles identiques (le fixture runtime ne distingue pas les deux états côté home) — artefact de fixture, déjà présent au 04.5, non causé par ce build.

## 13. Invariants préservés

- ✅ Route `/` reste Home / Today (aucun redirect).
- ✅ SSR + Jinja only — React/SPA/bundler interdits respectés.
- ✅ Aucun changement route / service / model / migration.
- ✅ Aucun JS ajouté (aucun fichier).
- ✅ `app.css` non touché · Focus Mode (`session_focus.css`, partials) non touché · macros non touchées.
- ✅ Une seule CTA primaire dans le hero.
- ✅ Données existantes conservées / accessibles ; métriques secondaires ne dominent pas.
- ✅ Aucun claim médical ; readiness = repère self-report qualitatif.
- ✅ No-JS fallback complet ; WCAG 44×44 ; focus visible.
- ✅ Mobile 360×640 + desktop 1440×900 utilisables.
- ✅ Aucun rebrand SPIGNOS → Auren dans le code.
- ✅ Baseline P0 capturable : `ok=16`.

## 14. Limites

- Le hero applique Auren **localement** (scoped `.today-home__hero`) ; le dashboard legacy sous le hero reste sur le thème dark app.css. L'harmonisation Auren du reste du Home relève de builds ultérieurs (ou d'un reskin global futur), hors scope .1.
- Distinction new-user explicite non implémentée (pas de nouvelle logique backend) — la branche no-active-session couvre les deux cas via « Démarrer / Programmes ».
- Readiness teaser = pointeur qualitatif, pas la bande agrégée (réservée .3).
- `home-authenticated` vs `home-no-active-session` non distingués par le fixture (artefact tooling, non bloquant).

## 15. Risques

- **Faible.** Build additif, scoped, sans logique métier ; 182 tests home-route verts, 23 nouveaux. Aucun contrat legacy cassé (labels préservés).
- Contraste hero clair vs dashboard dark : cohérence visuelle à valider en revue humaine (la hiérarchie « hero domine » est l'intention).

## 16. Prochaines étapes

- **Sb_UI_05.2 Active Session / Next Workout Cards** : enrichir les surfaces active/next sous le hero (méta séance, raison reco).
- **Sb_UI_05.3 Readiness / Recovery Snapshot** : bande qualitative readiness complète + recovery cues (self-report, non médical).
- Puis `.4` (progress + body continuity), `.5` (empty states + a11y + hardening).

## 17. Références

- Spec : `docs/strategy/Sx_UI_05_TODAY_READINESS_HOME_SPEC.md` (§7/§8/§9/§17)
- Spec acceptance : `docs/SPRINT_Sx_UI_05_HUMAN_REVIEW_REPORT.md`
- Baseline P0 : `docs/BASELINE_P0_CAPTURED_2026_07_04.md`
- Registry : `docs/strategy/SPEC_REGISTRY.md`
- Roadmap : `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`

## 18. Verdict

🟢 **Sb_UI_05.1 DELIVERED — pending CI + human review.**

**Sb_UI_05.2 : next candidate, not opened.**
**Sx_UI_06 : future, not opened.**
**After-screenshots : captured locally 16/16, not committed. No release tag.**
