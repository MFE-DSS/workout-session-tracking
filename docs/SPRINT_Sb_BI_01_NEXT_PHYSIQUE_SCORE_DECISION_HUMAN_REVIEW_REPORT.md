# Human Review — Sb_BI_01.next Physique Score Decision

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED**
**Date** : 2026-07-11
**Type** : revue humaine — docs-only (aucun code touché par cette revue)
**Cycle** : Body Intelligence (reprise Sx_BI_01)
**Spec** : [`strategy/Sb_BI_01_NEXT_PHYSIQUE_SCORE_DECISION_SPEC.md`](strategy/Sb_BI_01_NEXT_PHYSIQUE_SCORE_DECISION_SPEC.md)
**Audit** : [`SPRINT_Sb_BI_01_NEXT_PHYSIQUE_SCORE_DECISION_REPORT.md`](SPRINT_Sb_BI_01_NEXT_PHYSIQUE_SCORE_DECISION_REPORT.md)

---

## 1. Décision

**Sb_BI_01.next est accepté.** La place du **score global A/B/C opaque + radar** de
`/physique` est tranchée : **Option B prudente** — `/body/intelligence` (Zone Cards
+ Drill) devient la future surface principale « lecture corporelle » ; `/physique`
reste **transitoire**, déprécié **progressivement** (route + service **conservés**),
son score A/B/C **encadré, jamais renforcé**, **jamais supprimé brutalement**.
**Aucun code** dans ce sprint — décision + séquence future.

---

## 2. Preuve (commit docs-only)

| Item | Valeur |
|---|---|
| **Commit spec/audit** | `0404aca557c51ef51f1d877731c5688f3cbf1da2` |
| **Type** | décision/spec docs-only (4 fichiers) |
| **CI** | ⏭️ **skipped** (`paths-ignore: docs/**`) |
| **DoD** | check_scope=DOCS · spec_protocol ✅ · ruff 543 ≤ 548 ✅ · docs-only ✅ |

Aucun run CI pour `0404aca`. `app/` et `tests/` intacts.

---

## 3. Éléments acceptés (checklist)

| Élément | Statut |
|---|---|
| `/physique` live avec score A/B/C + radar | ✅ constat |
| `/body/intelligence` existe (Zone Cards + Drill), flag-off prod | ✅ constat |
| Les deux surfaces deviennent concurrentes si flag activé sans encadrement | ✅ constat |
| **Option B prudente** retenue | ✅ |
| `/body/intelligence` = future surface principale | ✅ |
| `/physique` = surface transitoire à déprécier progressivement | ✅ |
| Route `/physique` **conservée** | ✅ |
| Service `compute_physique_dashboard` **conservé** | ✅ |
| Score A/B/C **encadré, jamais renforcé** | ✅ |
| Aucune suppression brutale | ✅ |
| **Point critique** : `compute_physique_dashboard` alimente `leaderboard` + `user_profile` → encadrer la surface, ne pas casser le service | ✅ |
| Séquence : `Sb_BI_01.3` **AVANT** `Sb_BI_01.activation` | ✅ |
| Aucun code / template / CSS / tests / activation flag / deploy / release | ✅ |

---

## 4. Point critique validé — service partagé

L'audit a établi que le score/radar **n'est pas isolé à `/physique`** :
`compute_physique_dashboard` alimente aussi **`leaderboard`** (radar mini social,
`radar_svg`/`radar_axes`) et **`user_profile.html`** (`global_score` « X/100 »).
**Conséquence actée** : la dépréciation vise la **surface `/physique`** (microcopy,
priorité nav), **jamais le service** — sans quoi le leaderboard casserait. Le
service reste **intact**.

---

## 5. Séquence build future (validée)

| Ordre | Sprint | Rôle |
|---|---|---|
| 1 | **`Sb_BI_01.3` Physique Surface Guardrails** | microcopy d'encadrement du score + lien `/physique`→`/body/intelligence` (si flag actif) ; aucun nouveau score/radar/Home ; `compute_physique_dashboard` intact |
| 2 | **`Sb_BI_01.activation` Controlled BI Flag Activation** | rendre `/body/intelligence` visible en prod — **uniquement après `.3`** + deploy GO explicite |

**Principe d'ordre validé** : **encadrer `/physique` AVANT d'activer BI** — pas de
double lecture corporelle au moment de l'activation.

---

## 6. Suite

| Piste | État |
|---|---|
| **Sb_BI_01.3** Physique Surface Guardrails | 🟡 **READY TO BE PROPOSED, not opened** |
| **Sb_BI_01.activation** | ⏸️ **deferred until after .3 + explicit GO** |
| Activation flag `body_intelligence_enabled` | ⏸️ deferred |
| Deploy | ⏸️ deferred |
| Release tag | ⏸️ deferred |
| Dogfooding terrain Sx_DOGFOOD_01 | 🗓️ pending |

---

## 7. Verdict

**Verdict :** ✅ **Sb_BI_01.next Physique Score Decision — HUMAN REVIEW ACCEPTED.**

La direction est tranchée : **`/body/intelligence` = future surface principale**,
`/physique` déprécié **progressivement** (route + service conservés, score A/B/C
encadré jamais renforcé, jamais supprimé). Point critique validé :
`compute_physique_dashboard` alimente leaderboard + user_profile → **service intact**,
on encadre la surface pas le service. Séquence actée : **`Sb_BI_01.3` (encadrement)
AVANT `Sb_BI_01.activation` (flag)**. Aucun code, aucune activation, aucun deploy.
Aucun code touché par cette revue. Next proposed : **`Sb_BI_01.3` Physique Surface
Guardrails**, sur GO séparé.
