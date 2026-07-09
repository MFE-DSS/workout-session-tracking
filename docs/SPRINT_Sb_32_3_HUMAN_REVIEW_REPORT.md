# Human Review — Sb_32.3 body_map_descriptor service contract

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED**
**Date** : 2026-07-09
**Type** : revue humaine — docs-only (aucun code touché)
**Cycle** : Sx_32 Deep Feature/Object Refactor (backend métier) — **in progress**
**Build report** : [`SPRINT_Sb_32_3_REPORT.md`](SPRINT_Sb_32_3_REPORT.md)

---

## 1. Décision

**Sb_32.3 est accepté.** Le contrat de représentation corporelle existe sous
forme d'un service **pur, non persistant, JSON-sérialisable** qui dérive un
descriptor stable (primary/secondary zones + labels + statut) des mappings Sx_32.
L'invariance historique — contrainte #1 — est **prouvée 91/91** sur les deux
chemins (name-only substring **et** DB lookup). Aucun consommateur n'est migré :
c'est exactement le périmètre attendu pour `.3`.

---

## 2. Preuve CI (run réel)

| Item | Valeur |
|---|---|
| **Commit** | `63a4e74fa4c5216c2daafeebbd64b9653db6e19f` |
| **Run** | [`29010584067`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29010584067) — ✅ **3/3 success** |
| **Tests** | ✅ **1843 passed** (20:48) |
| Migration checks | ✅ drift / snapshot / patterns / roundtrip OK (aucun modifié) |

---

## 3. Éléments acceptés (checklist)

| Élément | Statut |
|---|---|
| Service pur `body_map_descriptor` | ✅ accepté |
| `build_body_map_descriptor(name, *, exercise_code=None, db=None) -> dict` | ✅ accepté |
| Shape JSON stable (10 clés) | ✅ accepté |
| `resolution_path` honnête : `db_lookup` / `substring_fallback` / `unknown` | ✅ accepté |
| Unknown → `"À qualifier"` | ✅ accepté |
| Invariance **91/91** sur les deux chemins | ✅ accepté |
| **Aucun consommateur migré** | ✅ confirmé |
| **Aucune UI touchée** | ✅ confirmé |
| **Aucun modèle / migration / schema** | ✅ confirmé |
| **Aucun changement `classify_exercise`** | ✅ confirmé |
| Aucun scoring / coach / body intelligence / substitution / readiness touché | ✅ confirmé |

---

## 4. Note process — validation locale allégée (nouveau garde-fou)

Le full sweep **local** de ce sprint a été volontairement skippé (décision
opérateur), le tier `isolated` du nouveau garde-fou `Sb_OPS.scope-guard`
recommandant de laisser la CI réelle jouer ce rôle pour un service neuf non
importé. **La CI réelle a confirmé 1843 passed**, validant a posteriori ce
choix : un fichier isolé ne régresse pas la suite hors de sa surface, et le
broad sweep local (283, incluant tous les consommateurs) suffisait en pré-filtre.

---

## 5. Périmètre NON fait (par conception)

- Descriptor **non branché** en prod (aucun consommateur ne l'appelle).
- Pas de persistance (recalcul à la demande).
- `muscle_code` / stabilizer non exposés (aucune anatomie inventée).
- Aucune UI Worked Area.

---

## 6. Suite du cycle Sx_32

| Sprint | État après cette revue |
|---|---|
| **Sb_32.1** | ✅ HUMAN REVIEW ACCEPTED (2026-07-08) |
| **Sb_32.2** | ✅ HUMAN REVIEW ACCEPTED (2026-07-09) |
| **Sb_32.3** | ✅ **HUMAN REVIEW ACCEPTED** (2026-07-09) |
| **Sb_32.next.worked-area-descriptor-ui** | 🟡 **READY TO BE PROPOSED, not opened** — consommer le descriptor dans l'UI Worked Area (SSR), review-gated |
| **Sb_32.4** | ⏸️ **BLOCKED / DEFERRED** — migration consommateurs (coach/body_intel/scoring) vers lookup DB + descriptor |
| Release tag | ⏸️ deferred |

---

## 7. Verdict

**Verdict :** ✅ **Sb_32.3 body_map_descriptor — HUMAN REVIEW ACCEPTED.**

Contrat de représentation corporelle livré : service pur, JSON-sérialisable,
`resolution_path` honnête, unknown explicite "À qualifier", invariance **91/91**
sur les deux chemins, **aucun consommateur/UI/modèle/migration**. CI réelle verte
3/3. Le cycle Sx_32 est **in progress**. Aucun code touché par cette revue.
