# Human Review — Sb_UI_10.1 Visible Product Strings (SPIGNOS → Auren)

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED**
**Date** : 2026-07-15
**Type** : revue humaine — docs-only (aucun code touché par cette revue)
**Cycle** : Sx_UI_10 (Auren Visual Migration Closeout & Rebrand Readiness)
**Build report** : [`SPRINT_Sb_UI_10_1_VISIBLE_PRODUCT_STRINGS_REPORT.md`](SPRINT_Sb_UI_10_1_VISIBLE_PRODUCT_STRINGS_REPORT.md)

---

## 1. Décision

**Sb_UI_10.1 est accepté.** Le nom produit **visible** migre SPIGNOS → **Auren** sur
les 4 chaînes user-facing de `base.html` (apple-title, `<title>`, brand topbar,
footer) ; SPIGNOS reste le **nom interne** (documenté en commentaire Jinja non
rendu, 0 SPIGNOS visible dans le shell). **Template-only strings-only** : le diff
commité ne contient que les 4 swaps de chaînes + la mise à jour du commentaire —
routes, classes, `url_for`, nav 9 liens + `aria-current`, logout POST, manifest,
assets, pages auth standalone **tous intacts**.

> **Note de séquence** : le build report a été rédigé en LOCAL BUILD MODE
> (« non commité »). Le commit `e035259` + push + CI ont été exécutés ensuite sur
> GO opérateur ; cette revue valide le **commit poussé réel** (contenu re-vérifié
> au diff et au grep en session de validation, pas seulement le rapport).

---

## 2. Preuve CI (run réel)

| Item | Valeur |
|---|---|
| **Commit build** | `e035259` (base `49fa7d3`, conforme au plan `Sx_UI_10`) |
| **Run** | [`29403226554`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29403226554) — ✅ **3/3 success** |
| `lint` (ruff budget + bandit + actionlint + shellcheck) | ✅ success (41 s) |
| `pytest + QA scripts` | ✅ success — pytest **25:07**, marge confortable sous timeout 45 |
| `SonarCloud` | ✅ success |
| **Tests** | ✅ **2138 passed** (+14 = tests dédiés `test_auren_visible_product_strings.py`) |
| Timeout / annulation infra | **Aucun** — premier coup |

Annotations non bloquantes et **préexistantes** (hors périmètre du commit) :
warning shellcheck SC2046 via reviewdog sur `.github/workflows/ci.yml:190`
(fichier non touché) + dépréciation Node.js 20 des actions GitHub (informatif).

---

## 3. Vérifications de session de validation (2026-07-15)

| Vérification | Résultat |
|---|---|
| Diff `e035259` sur `base.html` = strings-only (4 swaps + commentaire) | ✅ prouvé au `git show` |
| Périmètre commit = 5 fichiers attendus exactement, 0 fichier de la liste STOP | ✅ |
| Auren en apple-title (l.14) / `<title>` (l.22) / brand (l.40) / footer (l.72) | ✅ grep |
| SPIGNOS uniquement en commentaire technique interne (l.11-13) | ✅ grep |
| Zéro occurrence Orion | ✅ grep |
| `pytest tests/test_auren_visible_product_strings.py -q` | ✅ **14/14** (4,1 s) |
| Sweep ciblé `-k "base or nav or shell or pwa or auth or visible_product or auren"` | ✅ **386 passed / 0 échec** (1 min 17) |
| `check_ruff_budget` | ✅ **543 ≤ 548** |
| `check_spec_protocol` | ✅ PASS |

---

## 4. Éléments acceptés (checklist)

| Élément | Statut |
|---|---|
| 4 chaînes visibles SPIGNOS → Auren dans `base.html` | ✅ |
| SPIGNOS conservé comme nom interne (commentaire non rendu) | ✅ |
| Zéro Orion (`test_no_orion_string_introduced`) | ✅ |
| Routes préservées (`test_brand_route_unchanged`, `url_for('home')`) | ✅ |
| Classes `topbar__brand`/`topbar__link`/footer inchangées | ✅ |
| Nav 9 liens + état actif `aria-current` (Sx_NAV_01) préservés | ✅ |
| Logout `<form method="post">` inchangé | ✅ |
| Manifest **non touché** (encore « Workout » — différé `Sb_UI_10.2`) | ✅ assumé |
| Pages auth standalone (welcome/login/register) non touchées (différé `10.3`) | ✅ assumé |
| Aucun asset / CSS / JS / service / model / migration | ✅ |
| check_scope ISOLATED → **promu SHARED_CODE** (base.html = shell de 37 pages) | ✅ bonne pratique |

---

## 5. Suite

| Piste | État |
|---|---|
| **`Sb_UI_10.2`** manifest + icons Auren (résorbe l'incohérence manifest « Workout ») | 🟡 READY TO BE PROPOSED — **nécessite les assets** |
| **`Sb_UI_10.3`** auth standalone (welcome/login/register) | 🟡 READY TO BE PROPOSED, not opened |
| **`Sb_UI_10.4`** docs/labels secondaires (science/atlas/coach_report) | ⏸️ après `10.2`/`10.3` |
| Due diligence nom/domaine Auren | ⏳ **PENDING** (gating public, hors builds) |

---

## 6. Verdict

**Verdict :** ✅ **Sb_UI_10.1 Visible Product Strings — HUMAN REVIEW ACCEPTED.**

Le shell authentifié (37 pages via `base.html`) affiche désormais **Auren** sur les
4 surfaces visibles ; SPIGNOS reste le nom interne. Diff strings-only prouvé,
invariants nav/routes/logout/manifest/assets préservés, zéro Orion. CI réelle
verte **3/3** (`e035259`, run `29403226554`, **2138 passed**, aucun timeout) +
gates locaux re-validés en session (14 dédiés, 386 sweep, ruff 543 ≤ 548).
Aucun code touché par cette revue. Next : `Sb_UI_10.2` (manifest + icons,
sous réserve d'assets) ou `Sb_UI_10.3` (auth standalone), au choix opérateur.
