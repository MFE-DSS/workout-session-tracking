# Sprint Sb_BI_01.next — Physique Score Decision (Audit)

**Statut** : 🟢 AUDIT COMPLET — READY FOR HUMAN DECISION
**Type** : PRODUCT DECISION / AUDIT — docs-only, **aucun code**
**Date** : 2026-07-11
**Spec** : [`strategy/Sb_BI_01_NEXT_PHYSIQUE_SCORE_DECISION_SPEC.md`](strategy/Sb_BI_01_NEXT_PHYSIQUE_SCORE_DECISION_SPEC.md)

---

## 0. Méthode

Audit **read-only** (aucun fichier modifié) de `/physique` (score A/B/C + radar),
`/body/intelligence` (Zone Cards + Drill), et de tous les consommateurs de
`compute_physique_dashboard`, pour trancher la place du score opaque avant toute
activation BI.

---

## 1. État actuel — `/physique`

| Aspect | Constat |
|---|---|
| Route | `GET /physique` (`pages.py:478`), **LIVE** (pas de flag), sélecteur fenêtre 30/60/90 |
| Contenu | `physique.html` : **score global** (`{{ dashboard.global_score }}`), **grade A/B/C** (`grade-badge--{{ dashboard.global_grade|lower }}`), **radar SVG**, 11 zones (label/score/trend/confidence/hard_sets) |
| Service | `muscle_scoring.compute_physique_dashboard(db, user_id, window_days)` → `PhysiqueDashboard(global_score, global_grade, zone_scores, radar_axes, radar_svg)` |
| Nature du score | **Composite opaque** : `0.50·performance + 0.30·exposure + 0.20·anthropo` par zone, moyenné en radar puis en global ; grade A (≥75) / B (≥50) / C (<50) |
| Lien vers BI | **Aucun** (`/physique` ne pointe pas vers `/body/intelligence`) |

---

## 2. État actuel — `/body/intelligence`

| Aspect | Constat |
|---|---|
| Route | `GET /body/intelligence`, **flag-gated** (`body_intelligence_enabled=False` → 404 en prod) |
| Contenu | Composer Sb_31 (blocs, priorités, limits non médicaux) **+** section « Lecture par zones » (Sb_BI_01.1 : Zone Cards) **+** drill `<details>` no-JS (Sb_BI_01.2) |
| Score opaque | **Jamais surfacé** — réutilise `ZoneScore` (volume/tendance/contribution/confidence) mais **pas** `.score` ni `global_grade` ni radar |
| Lien depuis | `profile.html`, `coach_body_snapshot.html` |

---

## 3. Conflit produit

Une fois `/body/intelligence` activé, **deux lectures corporelles concurrentes**
coexisteraient :
- **`/physique`** : score A/B/C **opaque** + radar (lecture synthétique, note globale) ;
- **`/body/intelligence`** : lecture **par zones traçable**, confidence-aware, non médicale.

Le document maître **Sx_TRANSFORM_01** interdit un **nouveau** score opaque et
privilégie les zones traçables. Le score A/B/C de `/physique` **préexiste** (n'est
pas un nouveau score), mais **contredit la direction** : il faut le **relativiser**,
pas le renforcer, et éviter la double lecture au moment de l'activation BI.

---

## 4. Consommateurs de `compute_physique_dashboard` (couplage réel)

| Consommateur | Usage | Impact d'une dépréciation |
|---|---|---|
| **`pages.py` `/physique`** | score + grade + radar + zones | surface à encadrer/déprioriser |
| **`leaderboard.py` (router)** | `dashboard.radar_svg` (radar mini social) | **NE PAS CASSER** — service requis |
| **`leaderboard.py` (service)** | `dash.radar_axes` (radar mini) | **NE PAS CASSER** |
| **`user_profile.html`** | `dashboard.global_score` (« Score · X/100 ») | surface tierce dépendante du score |
| **`dashboard.py` / `dashboard.html`** | `global_score` / `global_grade` (route DEPRECATED Sb_27.6) | déjà dépréciée |
| **`body_intelligence.py` (Sb_BI_01.1/.2)** | `ZoneScore` **en lecture**, sans surfacer le score | OK — n'affiche pas le score opaque |

**Conclusion clé** : le score/radar **n'est pas isolé à `/physique`** — il alimente
**leaderboard** (comparaison sociale) et **user_profile**. Donc **déprécier ≠
supprimer le service** : `compute_physique_dashboard` doit rester **intact** ; seule
la **surface `/physique`** peut être encadrée/déprioritsée.

---

## 5. Risques

| Risque | Gravité | Mitigation |
|---|---|---|
| Double lecture corporelle si flag BI activé sans encadrer `/physique` | élevé | encadrer `/physique` **avant** l'activation |
| Casser leaderboard/user_profile/dashboard | élevé | ne pas toucher `compute_physique_dashboard` |
| Suppression brutale de `/physique` | élevé | interdite — dépréciation progressive, route conservée |
| Renforcer le score opaque | moyen | microcopy le relativise, aucun nouveau score |
| Perte de repère utilisateur | moyen | transition progressive + lien `/physique` → BI |

---

## 6. Options (résumé — détail dans la spec)

| Option | Verdict |
|---|---|
| A — garder `/physique`, encadrer plus tard | acceptable **seulement si activation BI différée** |
| **B — BI surface principale, déprécier progressivement `/physique`** | ✅ **RETENU (prudent)** |
| C — fusionner `/physique` dans BI | rejeté (trop large) |
| D — supprimer `/physique` | rejeté (brutal, casse leaderboard) |

---

## 7. Choix recommandé

**Option B prudente** : `/body/intelligence` = future surface principale ;
`/physique` reste live **temporairement**, déprécié **progressivement** (route +
service **conservés**) ; score A/B/C **encadré** puis déprioritsé, **jamais
renforcé** ; `compute_physique_dashboard` **intact** (leaderboard préservé).

---

## 8. Séquence build future (sur GO séparé)

1. **`Sb_BI_01.3` Physique Surface Guardrails** — microcopy d'encadrement + lien
   `/physique` → `/body/intelligence` (si flag actif) ; aucun nouveau score/radar/Home.
2. **`Sb_BI_01.activation` Controlled BI Flag Activation** — **après** `.3` (encadrer
   d'abord) + deploy GO explicite.
3. Futur : dépriorisation nav `/physique`, volume/exercice dans le drill.

---

## 9. Non-goals

Pas de code / template / CSS / tests / activation flag / deploy / release /
suppression `/physique` / changement leaderboard / nouveau score.

---

## Verdict

**Verdict :** 🟢 **Sb_BI_01.next Physique Score Decision — AUDIT COMPLET, READY FOR HUMAN DECISION.**

`/physique` (score A/B/C opaque + radar, LIVE) et `/body/intelligence` (zones
traçables, flag-off) sont deux lectures corporelles concurrentes. Le score opaque
**préexiste** mais contredit la direction Sx_TRANSFORM_01. Point critique : le score/
radar alimente aussi **leaderboard** et **user_profile** via
`compute_physique_dashboard` — le **service doit rester intact**. Choix recommandé :
**Option B prudente** — `/body/intelligence` surface principale, `/physique`
déprécié **progressivement** (route + service conservés, score encadré jamais
renforcé). Séquence : **`Sb_BI_01.3` encadrement AVANT `Sb_BI_01.activation` flag**.
Aucun code touché par ce sprint.
