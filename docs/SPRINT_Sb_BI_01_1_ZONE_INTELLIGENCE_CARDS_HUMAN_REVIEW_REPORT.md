# Human Review — Sb_BI_01.1 Zone Intelligence Cards

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED**
**Date** : 2026-07-11
**Type** : revue humaine — docs-only (aucun code touché par cette revue)
**Cycle** : Body Intelligence (reprise Sx_BI_01, Option A)
**Build report** : [`SPRINT_Sb_BI_01_1_ZONE_INTELLIGENCE_CARDS_REPORT.md`](SPRINT_Sb_BI_01_1_ZONE_INTELLIGENCE_CARDS_REPORT.md)

---

## 1. Décision

**Sb_BI_01.1 est accepté.** La surface `/body/intelligence` gagne une section
**« Lecture par zones »** sobre et traçable — cards par zone (volume récent,
tendance, contribution dérivée, confidence) en tête des blocs, état vide sobre si
données insuffisantes, mention non médicale. Le build **réutilise** les signaux
`muscle_scoring ZoneScore` (via `compute_physique_dashboard`, en lecture) **sans
créer de nouveau score** : le score opaque `.score`, le grade A/B/C et le radar
**ne sont jamais surfacés**. `/physique`, la Home, les modèles et le feature flag
restent inchangés — la surface reste **invisible en prod** (flag OFF).

---

## 2. Preuve CI (run réel)

| Item | Valeur |
|---|---|
| **Commit build** | `f0cc60bdbd9586736c10702b6be292277a578d16` |
| **Run** | [`29192711453`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29192711453) — ✅ **3/3 success** |
| `lint` | ✅ success |
| `pytest + QA scripts` | ✅ success (21:57, sous le timeout 35 min) |
| `SonarCloud` | ✅ success |
| Migration checks · Perf budget | ✅ success (dans le job pytest) |
| **Tests** | ✅ **1925 passed** (+12 = tests dédiés Sb_BI_01.1) |

Premier coup, aucune annulation infra — le fix timeout `25→35` (Sb_DOGFOOD_01.3) a tenu.

---

## 3. Éléments acceptés (checklist)

| Élément | Statut |
|---|---|
| Section « Lecture par zones » sur `/body/intelligence` | ✅ |
| Cards par zone : volume récent, tendance, contribution dérivée, confidence | ✅ |
| État vide sobre si données insuffisantes | ✅ |
| Mention « Estimation non médicale. » | ✅ |
| Réutilisation `muscle_scoring ZoneScore` via `compute_physique_dashboard` | ✅ |
| **Aucun nouveau score global** | ✅ |
| `ZoneScore.score` **non surfacé** | ✅ |
| Grade A/B/C **non surfacé** | ✅ |
| Radar **non surfacé** | ✅ |
| `/physique` intact | ✅ |
| Home intacte | ✅ |
| Flag `body_intelligence_enabled` conservé **OFF en prod** | ✅ |
| SSR/Jinja · no-JS fallback | ✅ |
| Auren Terminal sans nouvelle couleur | ✅ |
| Aucun modèle / migration / schema | ✅ |
| Aucun React / SPA / bundler | ✅ |
| Aucun deploy | ✅ |

---

## 4. Contribution = part dérivée, pas un score (acceptée)

La « contribution » affichée est `round(100 × hard_sets_zone / Σ hard_sets)` — une
**proportion arithmétique traçable** du volume, jamais une note. Le router ne lit
ni `.score` ni `.global_grade` dans les cards ; un test le verrouille
(`test_router_reuses_zonescore_no_new_score`) et un test extrait la section zones
pour prouver l'absence de `/100`, de grade et de radar
(`test_zone_cards_no_opaque_global_score_in_section`).

---

## 5. Tests (rappel)

12 tests dédiés (`test_bi01_zone_intelligence_cards.py`) : route/flag (404 off,
rendu on), contenu des cards (volume/confidence/contribution/non-médical), absence
de score opaque dans la section, état vide sur données insuffisantes, non-goals
(no JS, Home intacte, router sans `.score`/grade), régression (`/physique` non
référencé, limites non médicales conservées), wording interdit. Broad sweep
**284 passed** (BI/muscle_scoring/physique/progress/body_map/body_profile/
leaderboard) — 0 régression. CI réelle **1925 passed**.

---

## 6. Note scope-guard (promotion manuelle acceptée)

`check_scope` a classé **ISOLATED**, mais l'opérateur a **promu manuellement en
SHARED_CODE** parce que `body_intelligence.py` est un router monté dans `main.py`
via un import groupé que le classifier ne reconnaît pas (angle mort connu, même que
les templates). Un broad sweep élargi a été exécuté et **la CI GitHub complète a été
la source de vérité** → 3/3 verte. Bonne décision de prudence, pas une anomalie.

---

## 7. Flag & production

Le flag **`body_intelligence_enabled` reste OFF en prod** (défaut inchangé) : la
surface `/body/intelligence` et donc les zone cards restent **invisibles** en
production. L'activation du flag est **deferred until explicit GO**. Aucune config
prod modifiée, aucun deploy.

---

## 8. Suite

| Piste | État |
|---|---|
| **Sb_BI_01.2** drill zone → détail (top exercices, historique volume) | 🟡 **READY TO BE PROPOSED, not opened** |
| **Sb_BI_01.next** décision score `/physique` (garder / encadrer / déprécier) | 🟡 **not opened** |
| Activation `body_intelligence_enabled` | ⏸️ **deferred until explicit GO** |
| Dogfooding terrain Sx_DOGFOOD_01 | 🗓️ **pending** |
| Deploy | ⏸️ deferred |
| Release tag | ⏸️ deferred |

---

## 9. Verdict

**Verdict :** ✅ **Sb_BI_01.1 Zone Intelligence Cards — HUMAN REVIEW ACCEPTED.**

La reprise Body Intelligence livre une **lecture par zones traçable, sobre et non
médicale** sur la surface existante `/body/intelligence` : cards par zone (volume,
tendance, contribution dérivée, confidence), état vide sobre, mention non médicale.
Réutilise `muscle_scoring ZoneScore` en lecture — **aucun nouveau score**, score
opaque/A-B-C/radar jamais surfacés ; `/physique`, Home, modèles et flag inchangés ;
Auren Terminal sans nouvelle couleur ; SSR/Jinja, no-JS. CI réelle verte 3/3
(1925 passed). Le flag reste OFF en prod (surface invisible). Aucun code touché par
cette revue. Next proposed : `Sb_BI_01.2` (drill zone) ou décision d'activation du
flag, sur GO séparé.
