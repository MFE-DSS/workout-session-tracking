# Human Review — Sb_32.next.worked-area-descriptor-ui

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED**
**Date** : 2026-07-09
**Type** : revue humaine — docs-only (aucun code touché)
**Cycle** : Sx_32 Deep Feature/Object Refactor — **premier consommateur visible** de `body_map_descriptor`
**Build report** : [`SPRINT_Sb_32_next_WORKED_AREA_DESCRIPTOR_UI_REPORT.md`](SPRINT_Sb_32_next_WORKED_AREA_DESCRIPTOR_UI_REPORT.md)

---

## 1. Décision

**Sb_32.next.worked-area-descriptor-ui est accepté.** Le Focus Mode / Worked Area
consomme désormais `body_map_descriptor` (Sb_32.3) et affiche la zone corporelle
**réellement résolue** par le mapping Sx_32 — primary + assistants réels, « À
qualifier » pour l'inconnu — en SSR strict, sans allégation médicale, sans toucher
au logging ni à aucun service métier. C'est le premier consommateur visible de la
fondation BodyZone/Muscle/Mapping/descriptor.

---

## 2. Preuve CI (run réel)

| Item | Valeur |
|---|---|
| **Build UI** | `9dd28a1` |
| **Fix CI** | `8559e8b0d7a4aebca94ad719ff33f74821e0a605` |
| **Run** | [`29029149976`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29029149976) — ✅ **3/3 success** |
| `lint (ruff budget + bandit + actionlint + shellcheck)` | ✅ success |
| `pytest + QA scripts` | ✅ success |
| `SonarCloud` | ✅ success |
| **Tests** | ✅ **1865 passed** (2 warnings, 21:43) |
| Migration checks | ✅ drift / snapshot / roundtrip OK |

---

## 3. Éléments acceptés — fonctionnel (checklist)

| Élément | Statut |
|---|---|
| `body_map_descriptor` consommé dans le Worked Area | ✅ |
| Rendering **SSR / no-JS** | ✅ |
| Zone principale réelle affichée (Chest Press → Pectoraux) | ✅ |
| Zones secondaires affichées si présentes (→ Triceps) | ✅ |
| Unknown → « À qualifier » | ✅ |
| `resolution_path` exposé **discrètement** en `data-*` | ✅ |
| Note prudente non médicale | ✅ |
| Carte active seulement : 1 Worked Area par page | ✅ |
| Contrats Focus Mode préservés (logging / forms / input names / rest timer / substitution / overload) | ✅ |
| Aucun endpoint API | ✅ |
| Aucun JS | ✅ |
| Aucun scoring / coach / body intelligence / substitution / readiness | ✅ |
| Aucun modèle / migration / schema | ✅ |
| Aucun rebrand | ✅ |

## 4. Éléments acceptés — fix CI (checklist)

| Élément | Statut |
|---|---|
| `test_scope_guard.py` ne dépend plus d'un fichier réel mouvant | ✅ |
| Fixture `isolated` désormais **synthétique** (`app/services/__scope_guard_new_leaf_fixture.py`) | ✅ |
| Classifieur, policy et code app **inchangés** | ✅ |
| Le fix **n'affaiblit pas** la couverture du garde-fou (9/9 tests verts) | ✅ |

---

## 5. Preuves détaillées

### 5.1 Descriptor consommé en SSR

La route `session_detail` (`app/routers/sessions.py`) construit, dans la boucle
existante, `body_map_data[se.id] = build_body_map_descriptor(actual_exercise_name(se),
exercise_code=…, db=db)` et le passe au template. Le partial
`exercise_card.html` (carte active) rend `primary_label` / `secondary_labels`
directement dans le HTML initial — **aucune donnée chargée en JS**. Un test
(`test_worked_area_present_in_initial_html_no_js`) vérifie que « Pectoraux » et
la classe `session-focus__worked-area` sont présents dans le HTML servi.

### 5.2 Unknown → « À qualifier »

`test_unknown_exercise_renders_a_qualifier` : un exercice sans mapping rend le
statut « À qualifier » sur Principal, aucune zone inventée, slot propre.

### 5.3 UI non médicale

`test_no_forbidden_medical_wording` : aucun terme affirmatif interdit (« muscle
activé », « activation musculaire », « corrige ta posture », « biomécanique
certifiée »). La note prudente « **Lecture indicative issue du mapping exercice —
repère d'entraînement, non diagnostic médical.** » est présente (disclaimer, non
une allégation).

### 5.4 Contrats Focus Mode intacts

`test_focus_mode_contracts_preserved` : console de logging, inputs (`weight_kg`/
`reps`), `worked-area-list`, rest timer préservés. Aucun partial de logging
touché ; substitution/overload inchangés.

### 5.5 Aucun consommateur métier lourd migré

Aucun changement `classify_exercise` / `body_map_descriptor` / `muscle_mapping` /
scoring / coach / body intelligence / substitution / readiness ; aucun modèle /
migration / schema. Le lookup DB existe mais n'est branché que dans l'UI Worked
Area (lecture), pas dans les consommateurs métier.

---

## 6. Point de leçon (capturé)

**Éviter les fixtures réels mouvants dans les tests du garde-fou.**

La CI initiale (`9dd28a1`) est passée rouge sur **1 test** :
`test_scope_guard.py::test_isolated_when_new_leaf_file_not_imported_anywhere`,
qui affirmait que `body_map_descriptor.py` était `isolated`. Or **ce sprint l'a
importé** dans la route → le classifieur l'a (correctement) reclassé `shared_code`.
Le classifieur avait raison ; **le test était caduc** — couplé à l'état d'import
réel du repo.

C'est la **deuxième occurrence** du même anti-pattern ce cycle (après les tests
d'isolation par git-diff de `test_body_map_descriptor.py`, déjà corrigés dans le
build). Fix (`8559e8b`, CI-only) : le test utilise désormais un **chemin
synthétique non importé**, rendant l'assertion **sémantique** (teste la logique
`isolated`) et non **historique** (ne parie plus qu'un fichier réel restera
isolé). Un durcissement optionnel du garde-fou (décourager les assertions sur des
fichiers réels dans ses propres tests) est noté comme candidat `Sb_OPS` séparé,
non ouvert.

Note process : ce cas est un exemple réel où le **full sweep local skippé** (tier
`isolated`) a laissé passer une régression — parce que `test_scope_guard.py`
n'était pas dans le broad sweep ciblé du build. La CI réelle l'a rattrapé, ce qui
valide le principe « la CI reste source de vérité ».

---

## 7. Suite du cycle Sx_32

| Sprint | État après cette revue |
|---|---|
| **Sb_32.1 / .2 / .3** | ✅ HUMAN REVIEW ACCEPTED |
| **Sb_OPS.scope-guard** | ✅ HUMAN REVIEW ACCEPTED |
| **Sb_32.next.worked-area-descriptor-ui** | ✅ **HUMAN REVIEW ACCEPTED** (2026-07-09) |
| **Sb_32.4** consumer migration | 🟡 **READY TO BE PROPOSED, not opened** — bascule coach/body_intel/scoring vers lookup DB + descriptor |
| **Sx_32 closeout** | 🟡 **READY TO BE PROPOSED, not opened** — acter la fondation + 1er consommateur UI, différer/planifier la bascule métier |
| Release tag | ⏸️ deferred |

**Next decision** : ouvrir `Sb_32.4` (bascule des consommateurs métier) **ou**
`Sx_32 closeout` (fondation + descriptor + 1er consommateur UI livrés, bascule
métier différée). Sur override explicite opérateur.

---

## 8. Verdict

**Verdict :** ✅ **Sb_32.next.worked-area-descriptor-ui — HUMAN REVIEW ACCEPTED.**

Premier consommateur visible du descriptor branché en SSR/no-JS, zones réelles +
« À qualifier », UI non médicale, contrats Focus Mode intacts, aucun consommateur
métier migré. CI réelle verte 3/3 (1865 passed) après un fix CI-only du test
garde-fou caduc. Cycle Sx_32 **in progress**. Aucun code touché par cette revue.
