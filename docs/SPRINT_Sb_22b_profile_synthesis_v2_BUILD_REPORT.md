# Sprint Sb_22b Build Report — Profile Synthesis v2

**Date :** 2026-05-31
**Type :** BUILD — implémente `SPIGNOS_PROFILE_SYNTHESIS_SPEC_v2.md` amendé v2.1.
**Prérequis :** Sb_22a + Sb_22a.next livrés et déployés (`63f78e9`).
**Successeur :** Sb_23 (Coach Report) — réutilisera `profile_metrics.py`.

---

## 1. Objectif

Élever la surface leaderboard/profile à une **synthèse à 3 niveaux** (ligne → preview card → page profil), avec score numérique unique par niveau, radar toujours silhouette (sans score central), et un pattern preview-vs-clic homogène desktop/mobile.

Ferme deux retours dogfooding :
- N2b — score dupliqué (centre radar + au-dessus) → score affiché 1 seule fois sous le radar en L3, absent en L2.
- N2a/N2c — hover trop minimal + clic vers historique brut → L2 carte preview riche (radar + 4 KPI), L3 vraie page de synthèse avec activité agrégée.

## 2. Contrats durs respectés (spec v2.1 §A.bis)

| Contrat | Niveau ciblé | Vérifié par |
|---|---|---|
| Score numérique au L3 uniquement (jamais L2, jamais centre radar) | L2/L3 | `test_preview_endpoint_returns_html_fragment` + radar.py B3 fix |
| Radar silhouette à L2 et L3 | L2/L3 | template inspection |
| Métadonnées (taille/poids/âge) à L3 uniquement | L3 | template inspection |
| Activité agrégée (top zone / pattern / dernière séance) à L3 uniquement | L3 | template inspection |
| Pattern preview-vs-clic mobile/desktop | L2 | preview.js (hover 200ms desktop, double-tap mobile) |

## 3. Fichiers créés / modifiés

| Fichier | Type | Nature |
|---|---|---|
| `app/services/profile_metrics.py` | New | 280 LoC — `streak_days`, `cardio_minutes_per_week`, `strength_volume_delta_pct`, `top_zone`, `neglected_zone`, `dominant_pattern`, `last_session_summary`, dataclasses `PreviewPayload`/`PagePayload`, orchestrateurs `build_preview`/`build_page`. Lit `data/exercise_properties.json` (réutilise Sb_22a) pour le pattern dominant. |
| `app/routers/leaderboard.py` | Modify | Imports `build_page`/`build_preview`. Le handler `/users/{username}` injecte `page` dans le contexte. Nouvel endpoint `/users/{username}/preview` qui rend le partial L2 (path validation Sb_20.3 répliquée, 404 ownership-safe). |
| `app/templates/user_profile.html` | Rewrite | Refonte complète L3 v2 : header avec badge grade, radar + score sous radar (1 seule fois), bloc KPI 4 colonnes, sections métadonnées / activité 30j / dernière séance — chacune conditionnelle, alignée spec §A.bis. |
| `app/templates/_partials/profile_preview.html` | New | Partial L2 — header + mini-radar + 4 KPI + CTA "Voir profil →". Aucun score numérique. |
| `app/templates/leaderboard.html` | Modify | `data-preview-user="{{ e.username }}"` sur les liens username + `<script src="js/preview.js" defer>` chargé en bas. |
| `app/static/js/preview.js` | New | ~120 LoC — hover desktop avec délai 200ms ; double-tap mobile (1er=preview, 2ème=navigation) ; Esc / click-outside / scroll → ferme ; fetch graceful avec fallback navigation native si erreur. Aucune dépendance. |
| `app/static/css/app.css` | Modify | +110 LoC : `.user-profile__score` / `.user-profile__kpi-row` / `.user-profile__section`/`__activity`/`__last`, `.profile-preview*` (carte 280px), `.preview-portal` (positionnement absolu), `.trend--up/down`. |
| `tests/test_profile_metrics.py` | New | 12 tests : streak / cardio / volume delta / zones / payloads structurés / contrat score-not-in-preview / endpoint smoke (200/404/422) / L3 page render. |
| `docs/SPRINT_Sb_22b_profile_synthesis_v2_BUILD_REPORT.md` | New | Ce rapport. |

**0 modification BD · 0 migration · 0 modèle touché.** Tous les KPI sont dérivés à la volée depuis les tables existantes.

## 4. Hiérarchie d'information livrée

| Bloc | L1 leaderboard | L2 preview card | L3 page profil |
|---|---|---|---|
| Badge grade | ✅ | ✅ | ✅ |
| Score numérique | ❌ (texte rang + pts seulement) | ❌ (badge fait foi) | ✅ une fois sous radar |
| Mini-radar | ❌ | ✅ silhouette 200×200 | — |
| Radar full | ❌ | ❌ | ✅ + score sous-titre |
| Sessions 30j | ✅ | ✅ | ✅ |
| Streak | ❌ | ✅ | ✅ |
| Cardio min/sem | ❌ | ✅ | ✅ |
| Volume Δ % | ❌ | ✅ avec couleur up/down | ❌ (déjà en L2) |
| Métadonnées (taille/poids) | ❌ | ❌ | ✅ |
| Top zone | ❌ | ❌ | ✅ |
| Zone négligée | ❌ | ❌ | ✅ |
| Pattern dominant | ❌ | ❌ | ✅ |
| Dernière séance | ❌ | ❌ | ✅ template+score+recency |

Score numérique = **1 emplacement par niveau, jamais en double, jamais au centre du radar**.

## 5. Comportement preview-vs-clic

| Geste | Desktop | Mobile (coarse pointer) |
|---|---|---|
| Hover sur lien username | preview affichée après 200ms | n/a |
| Tap court | navigation immédiate `/users/{X}` | 1er tap → preview ; 2ème tap → navigation |
| Esc / clic dehors / scroll | ferme la preview | ferme la preview |
| Fetch en erreur | preview disparaît, lien suit son href natif | idem |

Détection mobile via `window.matchMedia('(hover: none)')`. Aucun framework, aucune dépendance externe. ~120 lignes JS, chargées en `defer` uniquement sur `/leaderboard`.

## 6. État des tests

```
12 nouveaux tests profile_metrics — 12/12 verts
770 → 782 tests pass (+12, 0 régression attendue)
catalog_pattern_qa : OK exit 0
ruff/bandit : inchangés
```

## 7. Limites assumées

1. **Volume Δ % calculé sur sets work strength uniquement** — Pas de pondération par tonnage (poids × reps). Acceptable V1, un user qui passe de 100 sets légers à 80 sets lourds verrait −20 % alors qu'il a progressé. Documenté pour V2.
2. **Top zone / pattern dominant exigent du data 30j** — Comptes peu actifs voient "—" ou des compteurs faibles. Pas de fallback "élargir à 90j" V1.
3. **Préview JS dépend du JS browser activé** — Si JS off, le lien suit son href natif vers L3 directement. Pas de dégradation utilisateur (juste pas de preview).
4. **Cache 0 V1** — chaque hover refetch. Acceptable car le payload est ~3 ko et les calculs sont rapides. Sb_23 ajoutera un cache 5 min si besoin.
5. **Pas de PR-decoration mobile-only** — la double-tap convention peut surprendre. Mitigée par CTA "Voir profil →" toujours visible dans la preview, donc le user comprend qu'il peut cliquer.

## 8. Recommandation prochain sprint

**Sb_23 — Coach Report.** Justification :
- `profile_metrics.py` créé ici sera réutilisé tel quel par Coach Report (cf spec `SPIGNOS_COACH_REPORT_SPEC_v1.md` §F.1).
- Pas de refactor nécessaire — l'orchestration `build_page` peut être étendue avec `build_coach_report` consommant les mêmes primitives.
- Le verrou §B.bis Coach Report (étiquetage Mesuré/Inféré/Non déductible) reste à implémenter au build — la couche métriques de Sb_22b est neutre par construction.

## 9. Verdict

**Sb_22b livré, conforme spec v2.1.** Hiérarchie 3 niveaux verrouillée, score unique par niveau, mobile-first via double-tap. 0 régression, 12 tests neufs. Sb_23 peut s'ouvrir directement sur cette couche métriques.
