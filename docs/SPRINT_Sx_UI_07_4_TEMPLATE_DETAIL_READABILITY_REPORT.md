# Sprint Sx_UI_07.4 — Template Detail Readability

**Statut** : 🟢 DELIVERED LOCALEMENT — **NON commité, NON poussé, CI non lancée** (LOCAL BATCH MODE)
**Type** : CODE BUILD — template-only readability pass on `/library/{slug}` (template_detail.html), SSR/Jinja, no-JS safe
**Date** : 2026-07-13
**Cycle** : batch local (à la suite de Sx_CAT_01 / FB_01 / SUB_01 / CLOSEOUT_01 / 07.3 — préservés)
**HEAD de référence** : `b60e749`

---

## 0. But produit

Quand l'utilisateur ouvre une fiche programme depuis `/library` ou `/launcher`, il doit
comprendre plus vite : l'objectif, le rôle du hint, la structure des exercices, les
séries/reps, et **qu'il consulte une fiche descriptive, pas une séance active**.
Réalisé **sans changer** le catalogue, les routes, les exercices, les rep_targets ni la
création de séance.

---

## 1. Étape 0 — Brainstorming / Options / Choix retenu

### Options

| Option | Description | Verdict |
|---|---|---|
| **A** | Template-only, microcopy additive | ✅ **RETENU** |
| B | Template + CSS minimal | ❌ non nécessaire |
| C | Ajouter CTA `create_session` depuis la fiche | ❌ comportement nouveau + telemetry à cadrer |
| D | Changer catalogue/data | ❌ hors sprint (Sx_CAT_01 existe) |

### 15 sujets clivants tranchés

1. **`template_detail.html` seul** (`pages.py` non touché).
2. Ajout d'une **note indicative** (pas seulement `template.focus`).
3. Noms d'exercices **préservés**.
4. `set_scheme`/`rep_targets` **préservés**.
5. **Pas de CTA « Démarrer »** (Option C rejetée).
6. Lien « ← Programmes » **conservé**.
7. **Pas de lien launcher.**
8. **Pas de CSS** (classes existantes `lede`/`section-header`/`kpi-note`) → **Option A pure**.
9. Inline styles **conservés**.
10. **Note « Fiche programme »** ajoutée.
11. Affichage cardio **inchangé**.
12. **Pas de lien BI/Progress.**
13. **Pas de JS.**
14. **Asservis préservés** : « ← Programmes », « Cardio : » absent sur strength, pas de fuite `suggested_label`, « Programmes ».
15. **Suite du batch** : recommandation §10.

**Choix : Option A pure** — template-only, 3 ajouts **additifs**.

### Risques / parades

| Risque | Parade |
|---|---|
| Casser `test_strength_template_hides_cardio_note` (push-a ne doit pas montrer « Cardio : ») | ma microcopy ne contient **pas** « Cardio : » ; la ligne cardio existante reste sous condition `kind=='cardio'` (non rendue sur strength). Test re-joué **vert**. |
| Fuite de la clé brute `suggested_label` | on rend `{{ template.suggested_label }}` (valeur), jamais la chaîne « suggested_label » |
| Toucher une donnée | diff = **8 insertions, 0 suppression** ; tous les champs data-bound préservés (test sentinelle) |
| Ajouter un POST/CTA | **aucun** form/`create_session`/« Démarrer » ajouté (test) |

---

## 2. Fichiers modifiés

| Fichier | Nature |
|---|---|
| `app/templates/template_detail.html` | 3 ajouts **additifs** (8 insertions / 0 suppression) |
| `tests/test_template_detail_readability.py` | **nouveau** — 11 tests |

**Non modifiés** : `pages.py`, `sessions.py`, services, data (`reference_split.json` =
Sx_CAT_01 préservé), `library.html`/`launcher.html` (Sx_UI_07.3 préservés), session/
progress/history/index/BI/physique templates, models, migrations, static/js, app.css.

---

## 3. Microcopy avant / après (additif)

| Emplacement | Ajout |
|---|---|
| après le hint | **+** « Fiche programme · structure prévue avant lancement. » |
| avant la liste d'exercices | **+** `<h2>` « Structure de séance » |
| après la liste | **+** « Les charges et reps réelles se saisissent dans la séance active. » |

**Conservés à l'identique** : « ← Programmes », titre `template.name`, lede
`template.focus`, cardio note (conditionnelle), `suggested_label` (hint), liste
d'exercices (code/name/set_scheme/notes/rep_targets), empty state cardio.

---

## 4. Preuve — données programme/exercices/rep_targets inchangées

Diff = **8 insertions, 0 suppression**. Tous les champs data-bound restent rendus —
test `test_detail_diff_is_additive_only` vérifie la présence de `template.name`,
`template.focus`, `template.cardio_note`, `template.suggested_label`, `ex.code`,
`ex.name`, `ex.set_scheme`, `ex.notes`, `ex.rep_targets`, `rt.min_reps`, `rt.max_reps`.
Aucune donnée retirée ni modifiée. `reference_split.json` (données) **non touché** par
ce sprint.

---

## 5. Preuve — aucun POST/route/service/data changé

- **Aucun form POST** : la fiche n'en avait pas, on n'en ajoute pas (test
  `test_no_post_form_added` : pas de `<form>`/`create_session`/« Démarrer »).
- **Routeurs** : `pages.py` + `sessions.py` **non ouverts** (tests sentinelles).
- **Data** : `reference_split.json` = état Sx_CAT_01, non re-touché.

---

## 6. Tests locaux

### `tests/test_template_detail_readability.py` (NOUVEAU, 11 tests)
1. Microcopy additive : « Fiche programme » + « structure prévue avant lancement » ; « Structure de séance » + note finale « Les charges et reps réelles… ».
2. Contrat préservé : « ← Programmes », exercise__code/scheme, exercise-list, sets__range, mot d'exercice réel.
3. Régression : `test_strength_detail_still_hides_cardio_prefix` (« Cardio : » absent + pas de fuite `suggested_label`).
4. Non-régression : aucun form POST · `pages.py`/`sessions.py` non modifiés.
5. Non-goals : pas de JS/lien BI-physique · diff additif (champs data-bound présents) · wording interdit absent.

### Résultats locaux
- Dédiés : **11/11 verts**.
- **Tests asservis existants** (`test_library` dont `test_strength_template_hides_cardio_note`, `test_science_page`) : **19 passed** — 0 cassé.
- **Sweep ciblé** (template_detail/library/launcher/create_session) : **68 passed, 0 failed**.
- `check_scope` = **ISOLATED** (correct — page unique, `pages.py` non touché). ruff clean, budget 543 ≤ 548 ; spec vert.

> **LOCAL BATCH MODE** : rapide, pas de full suite, pas de CI. Aucun commit/push.

---

## 6bis. Renversement ultérieur par Sx_TPL_01 (même batch)

> **Note (2026-07-13)** : `Sx_TPL_01` (sprint suivant du même batch local) **renverse la
> décision « pas de CTA »** de ce sprint : la fiche devient **actionnable** (ajout d'un
> CTA « Démarrer cette séance », POST `create_session`, `creation_source=library`). Le
> batch n'étant pas commité, ce changement se fait proprement : le test
> `test_no_post_form_added` de ce rapport est **ré-orienté** en
> `test_start_cta_form_present` (non affaibli). Cf. `SPRINT_Sx_TPL_01_TEMPLATE_DETAIL_START_CTA_REPORT.md`.
> La readability additive de `.4` (« Fiche programme », « Structure de séance », note
> charges/reps) est **conservée** ; seul le statut « pas de CTA » est levé.

## 7. Limites

- **Readability pass seulement** : microcopy indicative, aucune nouvelle fonctionnalité,
  pas de lien inter-surfaces. *(Le CTA « Démarrer » a été ajouté ensuite par Sx_TPL_01 —
  cf. §6bis.)*
- **Inline styles conservés** (les retirer toucherait app.css sans nécessité).

---

## 8. Impact sur le batch

Ce sprint ajoute **1 template + 1 test** au batch. Le batch contient désormais **3
changements de code** :
- **Sx_CAT_01** (`reference_split.json` + test catalogue) ;
- **Sx_UI_07.3** (`library.html` + `launcher.html` + test) ;
- **Sx_UI_07.4** (`template_detail.html` + test).
+ vérifications docs (FB_01, SUB_01) + closeout.

Le **plan de commit** (closeout §5) doit inclure `template_detail.html` +
`test_template_detail_readability.py` + ce rapport dans le **commit code**.

---

## 9. Chemins interdits vérifiés

✅ Aucun : `pages.py`, `sessions.py`, `services/**`, `models/**`, `migrations/**`,
`schema_snapshot.sql`, `static/js/**`, `app.css`, session/progress/history/index/BI/
physique templates. `reference_split.json` (CAT_01), `library.html`/`launcher.html`
(07.3), `test_catalog_integrity_cleanup.py` : **préservés, non modifiés** par ce sprint.

---

## 10. Recommandation finale

**GO BATCH COMMIT + CI complète.** Le batch contient **3 changements de code** (data +
3 templates) + vérifications. Plus le batch grossit en code sans CI, plus le risque
d'une régression non-testée-en-CI augmente. Ma préférence nette : **fermer le batch et
commiter** maintenant. Alternative : un dernier sprint local (mais le batch est déjà
substantiel).

---

## Verdict

**Verdict :** 🟢 **Sx_UI_07.4 Template Detail Readability — DELIVERED LOCALEMENT (batch, non commité).**

La fiche programme (`/library/{slug}`) gagne 3 repères **additifs** (« Fiche programme ·
structure prévue avant lancement », « Structure de séance », « Les charges et reps
réelles se saisissent dans la séance active ») clarifiant qu'il s'agit d'une fiche
descriptive — aucune donnée programme/exercice/rep_targets touchée (8 insertions,
0 suppression), aucun form POST/CTA/route/service/data changé, aucun test asservi cassé
(19 verts, dont le garde-fou cardio strength). Template-only ; aucun JS/CSS/lien
BI-physique/score/rebrand. 11 tests dédiés verts ; sweep ciblé 68 passed ; ruff clean ;
spec vert. Batch préservé. Recommandation : **GO BATCH COMMIT + CI**.
