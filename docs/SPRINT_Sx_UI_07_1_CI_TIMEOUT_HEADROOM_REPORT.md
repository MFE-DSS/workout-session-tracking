# Sprint Sx_UI_07.1 — CI Timeout Headroom (infra fix)

**Statut** : 🟢 DELIVERED — pending push + CI validation
**Type** : CI INFRA FIX — patch minimal du timeout du job pytest
**Date** : 2026-07-13
**Build fonctionnel concerné** : `Sx_UI_07.1` Progress Surface Auren Readability (SHA `98d679d`, template-only)

---

## 0. Contexte

Le build `Sx_UI_07.1` (SHA `98d679d`) est fonctionnellement valide mais son run CI a
été **annulé par timeout de job** — pas par un échec de test.

| Item | Valeur |
|---|---|
| **Run problématique** | [`29239935779`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29239935779) |
| **SHA build** | `98d679d` |
| **lint** | ✅ success |
| **pytest + QA scripts** | ❌ **cancelled** (timeout de job) |
| **SonarCloud** | ⏭️ skipped (needs pytest) |
| **pytest** | ✅ **1978 passed** (2 warnings, 32:07 de tests) |

---

## 1. Symptôme

Le job `pytest + QA scripts` a `timeout-minutes: 35`. Détail du run :
- Job : `09:39:42 → 10:14:59` = **35:17** → **dépasse 35 min**.
- Step **`Run pytest with coverage`** : `09:40:09 → 10:14:55` = **34:46**, marqué **cancelled**.
- Steps QA suivants (catalog/atlas/drift/snapshot/migration/perf) : tous **skipped** (job tué).

Le log confirme **`1978 passed`** en `32:07` : les tests **ne sont pas rouges** — c'est
le run pytest+coverage (tests + génération coverage + finalisation) qui a franchi la
limite de 35 min sur un runner lent.

---

## 2. Conclusion : pas un test rouge

- **`1978 passed`** — aucun échec, aucune erreur.
- Build `Sx_UI_07.1` **template-only** (aucun calcul métier, aucun service touché) —
  ne peut pas causer un timeout structurel.
- Ni annulation infra aléatoire (le step pytest lui-même est `cancelled` à 34:46,
  contre le timeout), ni vrai hang.
- **Cause** : la suite grandit (1967 → **1978** tests) + variance runner ; le timeout
  `35` (déjà relevé depuis `25` en Sb_DOGFOOD_01.3) est redevenu **trop juste** sur
  runner lent. Runs récents : `20:15` → `22:06` → `22:57` → `23:07` → **`32:07`**
  (variance forte).

---

## 3. Choix : timeout 35 → 45

Patch minimal, **1 ligne** dans `.github/workflows/ci.yml` (job `test`) :

```
-    timeout-minutes: 35
+    # Sx_UI_07.1 CI headroom — full pytest+coverage can exceed 35 min on slow runners; gates unchanged.
+    timeout-minutes: 45
```

45 min donne une marge raisonnable (~10 min au-dessus du pire run observé 35:17)
sans masquer un vrai hang (un blocage réel dépasserait largement 45 min).

---

## 4. Non-goals (garde-fous)

**Aucune réduction de la couverture ou des gates** :
- pytest **inchangé** (tous les tests joués) ;
- **coverage inchangé** (non supprimé) ;
- **QA scripts inchangés** (catalog/atlas/drift/snapshot/migration/perf) ;
- **SonarCloud inchangé** (input non modifié) ;
- **migration checks inchangés** ;
- pas de `[skip ci]` ; pas de touche à app/tests/migrations/schema/scripts/
  requirements/deploy/production config.

Le fix **relève seulement la marge de temps** ; il ne réduit **rien**.

---

## 5. Next

- **CI complète = source de vérité** : après push, le run doit passer **3/3** (le
  timeout à 45 laisse la marge pour pytest+coverage + QA aval).
- Le build fonctionnel reste `98d679d` (inchangé) ; ce fix est **infra-only**.
- Si la suite continue de croître, une future optimisation (parallélisation pytest,
  coverage plus léger) serait un sprint dédié — hors de ce patch minimal.

---

## Verdict

**Verdict :** 🟢 **Sx_UI_07.1 CI Timeout Headroom — infra fix DELIVERED.**

Le job `pytest + QA scripts` passe de `timeout-minutes: 35` à `45` — patch **1 ligne**,
tier `ci_infra`. Le build `Sx_UI_07.1` (`98d679d`) était **valide** (1978 passed) ;
seul le job dépassait 35 min sur runner lent (35:17, step pytest cancelled à 34:46).
**Aucun test affaibli, aucun gate retiré** (coverage/QA/Sonar/migration checks
inchangés). CI complète attendue verte 3/3.
