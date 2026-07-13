# Sprint Sx_UI_07.3 — Library / Launcher Catalogue Readability

**Statut** : 🟢 DELIVERED LOCALEMENT — **NON commité, NON poussé, CI non lancée** (LOCAL BATCH MODE)
**Type** : CODE BUILD — template-only readability pass on `/library` + `/launcher`, SSR/Jinja, no-JS safe
**Date** : 2026-07-13
**Cycle** : batch local (à la suite de Sx_CAT_01 / FB_01 / SUB_01 / BATCH_CLOSEOUT_01, non commités — préservés)
**HEAD de référence** : `b60e749`

---

## 0. But produit

Améliorer la lecture des surfaces **catalogue** (`/library`) et **lancement** (`/launcher`)
— choisir un type/zone/programme, consulter le catalogue, démarrer — **sans toucher au
comportement métier** (programmes, routes, recommandations, télémétrie, création de
session).

---

## 1. Étape 0 — Brainstorming / Options / Choix retenu

### Options

| Option | Description | Verdict |
|---|---|---|
| **A** | Template-only, microcopy additive | ✅ **RETENU** |
| B | Template + CSS minimal | ❌ non nécessaire (classes existantes) |
| C | Refonte launcher flow | ❌ trop large |
| D | Changer catalogue/data | ❌ déjà fait en Sx_CAT_01 — ne pas mélanger |

### 15 sujets clivants tranchés

1. **`/library` ET `/launcher`.**
2. **Template-only** (`pages.py` non touché).
3. **Microcopy additive/enrichie**, textes asservis préservés.
4. « Voir tous les programmes » **conservé** (×3 sur launcher).
5. CTA « Démarrer » **conservés**.
6. `creation_source` **inchangé** (library/launcher).
7. Cartes template **conservées**.
8. **Pas de CSS** (classes existantes) → **Option A pure**.
9. Inline styles **conservés**.
10. **Pas de lien BI.**
11. **Pas de lien Progress.**
12. **Pas de JS.**
13. `sections`/catalog (data) **non touchés**.
14. **Textes asservis préservés** : « Programmes de séance », « Catalogue complet » (substring), « Démarrer » (count ≥6), `creation_source` ; **pas** de « Bibliothèque » (asservi `not in body`).
15. **Suite du batch** : recommandation en §11.

**Choix : Option A pure** — template-only, changements **additifs** sur les ledes.

### Risques / parades

| Risque | Parade |
|---|---|
| Casser un test asservi (`test_library`, `test_session_flow`, `test_recommendation_telemetry`) | changements **additifs** ; « Catalogue complet » conservé en **substring** ; pas de « Bibliothèque » ; CTA/creation_source intacts. **71 tests asservis re-joués verts.** |
| Toucher route/service | `pages.py`/`sessions.py` **non ouverts** ; tests sentinelles |
| Toucher la reco | `next_session_reco.html` **non touché** (inclus tel quel en step 1) |

---

## 2. Fichiers modifiés

| Fichier | Nature |
|---|---|
| `app/templates/library.html` | lede enrichi (additif) |
| `app/templates/launcher.html` | 3 ledes de flow explicites (step 1/2/3, additifs) |
| `tests/test_library_launcher_readability.py` | **nouveau** — 12 tests |

**Non modifiés** : `pages.py`, `sessions.py`, services, data (`reference_split.json` =
Sx_CAT_01 préservé), session/progress/history/index/BI/physique templates,
`next_session_reco.html`, models, migrations, static/js, app.css.

---

## 3. Microcopy avant / après (additif)

| Surface | Avant | Après |
|---|---|---|
| `/library` lede | « Catalogue complet. » | « **Catalogue complet des séances disponibles, classées par usage.** » (garde la sous-chaîne « Catalogue complet ») |
| `/launcher` step 1 lede | « Type de séance ? » | « **Choisis le format de séance à lancer.** » |
| `/launcher` step 2 lede | « Quelle zone ? » | « **Sélectionne la zone ou l'objectif du jour.** » |
| `/launcher` step 3 lede | « Choisis un programme. » | « **Choisis le programme à démarrer maintenant.** » |

**Conservés à l'identique** : titre « Programmes de séance », titre « Nouvelle séance »,
sections + cartes template, CTA « Démarrer », « Voir tous les programmes → » (×3),
liens retour, liens `template_detail`, `next_session_reco` (step 1).

---

## 4. Preuve — forms POST & creation_source inchangés

- **`/library`** : form `create_session` + `template_slug` (hidden) + `creation_source="library"` (hidden) + « Démarrer » — **intacts** (grep : 1 `creation_source=library`).
- **`/launcher` step 3** : form `create_session` + `template_slug` + `creation_source="launcher"` + « Démarrer » — **intacts** (grep : 1 `creation_source=launcher`).
- Test `test_creation_source_hidden_inputs_intact` verrouille les 2 hidden + `create_session` + `next_session_reco`.
- **Télémétrie** : `test_recommendation_telemetry` (valeurs `library`/`launcher`) **verte**.

---

## 5. Preuve — routes / services / data inchangés

- **Diff** limité à des `<p class="lede">` + commentaires (grep sur le diff : aucune ligne non-lede supprimée).
- **Routeurs** : `pages.py` + `sessions.py` **non ouverts** (tests sentinelles `test_pages_router_not_modified_by_readability`, `test_sessions_router_not_modified`).
- **Data** : `reference_split.json` = état Sx_CAT_01 **préservé** (non re-touché par ce sprint).

---

## 6. Tests locaux

### `tests/test_library_launcher_readability.py` (NOUVEAU, 12 tests)
1. `/library` : titre + lede enrichi + « classées par usage » + pas de « Bibliothèque » ; form start + creation_source=library + « Démarrer » + lien détail.
2. `/launcher` : step1 lede + reco + « Voir tous les programmes » ; step2 lede (type valide découvert dynamiquement) ; step3 lede + start form + creation_source=launcher ; liens retour.
3. Non-régression : `pages.py`/`sessions.py` non modifiés.
4. Non-goals : pas de JS · pas de lien BI/physique · hidden inputs intacts · wording interdit absent.

### Résultats locaux
- Dédiés : **12/12 verts**.
- **Tests asservis existants** (`test_library`, `test_session_flow`, `test_recommendation_telemetry`, `test_home_decision_hero`) : **71 passed** — 0 cassé.
- **Sweep ciblé** (library/launcher/template_detail/create_session) : **57 passed, 0 failed**.
- `check_scope` = **ISOLATED** (correct — pages uniques, `pages.py` non touché). ruff clean, budget 543 ≤ 548 ; spec vert.

> **LOCAL BATCH MODE** : rapide, pas de full suite, pas de CI. Aucun commit/push.

---

## 7. Limites

- **Readability pass seulement** : ledes enrichis, aucune nouvelle fonctionnalité, pas
  de tri/filtre interactif (no-JS).
- **Inline styles conservés** (les retirer toucherait app.css sans nécessité).
- **Pas de lien inter-surfaces** (BI/Progress) — hors périmètre.

---

## 8. Impact sur le batch

Ce sprint ajoute **1 changement de code** (2 templates + 1 test) au batch local. Le
batch contient désormais **2 changements de code réels** :
- **Sx_CAT_01** (`reference_split.json` + test catalogue) ;
- **Sx_UI_07.3** (`library.html` + `launcher.html` + test readability).
+ les vérifications docs (FB_01, SUB_01, CLOSEOUT).

Le plan de commit du closeout (§5) doit être **mis à jour** pour inclure `library.html`,
`launcher.html`, `test_library_launcher_readability.py` dans le **commit code** (ils
déclenchent la CI), le rapport + registry/roadmap dans le commit docs.

---

## 9. Chemins interdits vérifiés

✅ Aucun : `pages.py`, `sessions.py`, `services/**`, `models/**`, `migrations/**`,
`schema_snapshot.sql`, `static/js/**`, `app.css`, session/progress/history/index/BI/
physique templates, `next_session_reco.html`. `reference_split.json` (Sx_CAT_01) et
`test_catalog_integrity_cleanup.py` **préservés, non modifiés**.

---

## 10. Recommandation finale

**GO BATCH COMMIT + CI complète.** Le batch est cohérent (2 changements de code
template/data + vérifications) et vérifié localement. Alternative : continuer un dernier
sprint local. Ma préférence : **fermer le batch et commiter** — il commence à contenir
2 changements de code qu'il serait sain de sécuriser via la CI réelle.

---

## Verdict

**Verdict :** 🟢 **Sx_UI_07.3 Library / Launcher Catalogue Readability — DELIVERED LOCALEMENT (batch, non commité).**

`/library` et `/launcher` gagnent des **ledes plus clairs** (catalogue « classées par
usage » ; flow launcher « format → zone/objectif → programme ») via des ajouts
**strictement additifs** — aucun texte asservi cassé (71 tests verts), aucune section/
carte/CTA/`creation_source`/reco touchés. Template-only : `pages.py`/`sessions.py`/
services/data **inchangés** ; aucun JS / CSS / lien BI-physique / nouveau score / rebrand.
12 tests dédiés verts ; sweep ciblé 57 passed ; ruff clean ; spec vert. Batch préservé.
Recommandation : **GO BATCH COMMIT + CI**.
