# Sprint Sb_DOGFOOD_01.2 — Consumer Propagation Verification

**Statut** : 🟢 DELIVERED — pending GO commit + CI + human review
**Type** : **VERIFICATION-ONLY** — tests seulement, **aucun code applicatif changé**
**Date** : 2026-07-11
**Cycle** : Sx_DOGFOOD_01 Load Hint / Substitution Coherence
**Précondition** : `Sb_DOGFOOD_01.1` HUMAN REVIEW ACCEPTED ✅ (vérifié dans le repo).

---

## 0. Objectif

Prouver **noir sur blanc** que les consommateurs de `last_time` héritent du fix
source `.1` : quand `last_time_by_exercise_code` devient silencieux (S2/S3/S5),
aucune surface n'affiche la charge d'un **autre exercice**. Ce sprint ne refait
pas le fix ; il le **verrouille par des tests**.

---

## 1. Étape 0 — Brainstorming / Options / Risques / Choix retenu

### Constat (vérifié en étape 0)
Les consommateurs gèrent **déjà** `last_time.get(code) is None` :
- **delta** (`sessions.py:354-360`) : si `prior` None → `prior_w/r/score = None` →
  `compute_delta(...)` retourne **None** (vérifié unitairement).
- **hints Sx_08** : `compute_hints(se, None)` → **[]** (vérifié unitairement).
- **console « Référence précédente »** (`exercise_card.html:517-520`) : `_ref` absent
  → état vide existant « **Non disponible** ».
- **chip / peek** : `build_chip` / `build_peek` reçoivent un `prior` absent → état vide.

### Options
| Option | Description | Verdict |
|---|---|---|
| **A** | **Tests consommateurs uniquement** (le fix `.1` propage déjà) | ✅ **RETENU** |
| B | Patch léger consommateur | ❌ non requis (aucun test rouge) |
| C | Microcopy « historique non comparable » | ❌ différé (pas de nécessité UX ; brief le veut) |
| D | Service central `exercise_load_identity` | ❌ hors scope, futur |

### Décisions sujets clivants
1. Modifier ou tester ? → **tester seulement** (Option A).
2. `last_time` absent → surface = **état vide existant** (pas de nouvelle disparition).
3. Delta → **absent** (None) quand pas d'historique comparable.
4. Hints Sx_08 → **silencieux** ([]), pas de prudence générique.
5. Chip/peek → **état vide** cohérent, jamais une charge d'un autre exercice.
6. Microcopy « historique non comparable » → **non** (réutiliser l'existant).
7. Tests → **HTML rendu (bout-en-bout)** pour S1→S5 + **unitaire** pour delta/hints.
8. `last_time` absent = **unique signal de silence**.
9. Fixtures S1→S5 factorisées (helper `_seed`).
10. `.2` clos en **verification-only** (aucun code applicatif).

### Risque / parade
| Risque | Parade |
|---|---|
| Une surface afficherait encore une donnée fausse malgré `last_time` absent | Tests HTML S2/S3/S5 le prouveraient rouge → aucun rouge → aucun patch requis |

---

## 2. Surfaces testées

| Surface | Test | Résultat |
|---|---|---|
| Console « Référence précédente » | HTML S2/S3/S5 → « Non disponible » ; jamais la charge d'un autre exercice | ✅ |
| Console (référence comparable) | HTML S1/S4 → référence visible ; S3 → prescrit ancien (55), jamais substitution (80) | ✅ |
| Delta | unitaire : `compute_delta(prior=None)` → None | ✅ |
| Hints Sx_08 | unitaire : `compute_hints(se, None)` → [] | ✅ |
| Chip / peek | héritent de `last_time` absent (état vide) | ✅ (via le flux HTML) |
| Microcopy / wording | aucun nouveau texte ; aucun « Repère »/« repère » | ✅ |

---

## 3. Scénarios S2/S3/S5 (ce qui est silencieux / visible)

| Scénario | Silencieux | Visible |
|---|---|---|
| **S2** prescrit → substitué | Référence précédente (« Non disponible »), delta, hints | — |
| **S3** substitué → prescrit | la charge de la substitution (80) | le prescrit **plus ancien** (55) |
| **S5** substitué → autre substitut | la charge de l'autre substitut (90), Référence, delta, hints | — |
| **S1** prescrit → prescrit | — | référence (60) |
| **S4** substitué → même substitut | — | référence (80) |

---

## 4. Changements applicatifs

**NONE.** Aucun fichier applicatif modifié. Les consommateurs géraient déjà
l'absence de `last_time` ; ce sprint le **verrouille** par des tests. Option B
(patch consommateur) n'a pas été nécessaire (aucun test rouge).

---

## 5. Tests

### `tests/test_dogfood01_consumer_propagation.py` (NOUVEAU, 8 tests)
- unitaire : delta None sur prior absent · hints [] sur prior absent ;
- HTML bout-en-bout : S2 (console « Non disponible », pas 60) · S3 (55 oui, 80 non) ·
  S5 (« Non disponible », pas 90) · S1 (60 visible) · S4 (80 visible) ;
- garde wording : pas de « Repère »/« repère », « Non disponible » conservé.

### Résultats
- Nouveau fichier : **8/8 verts**.
- `check_scope` : **ISOLATED** (nouveau fichier test seul) → full sweep local skippé.
- ruff **543 ≤ 548** ; spec protocol vert.
- Broad sweep ciblé (last_time/delta/hints/briefing/session_focus/substitution/ui06) : voir §Verdict.

---

## 6. Invariants

- **Aucun code applicatif touché** (stats.py, overload, router, delta, hints,
  briefing, template, CSS **inchangés**).
- Contrat `last_time` (`.1`) intact ; consommateurs intacts.
- Aucun modèle / migration / schema / Body Intelligence / JS / `value=`.

---

## 7. Statut & next

- **`Sb_DOGFOOD_01.3`** mobile placeholder proportion (CSS-only) : 🟡 READY TO BE
  PROPOSED, not opened.
- **Body Intelligence** : deferred.

---

## Verdict

**Verdict :** 🟢 **Sb_DOGFOOD_01.2 verification-only — propagation prouvée, aucun code applicatif requis — pending GO commit + CI + human review.**

Les consommateurs de `last_time` (Référence précédente, delta, hints Sx_08,
chip/peek) héritent **automatiquement** du fix source `.1` : en S2/S3/S5 ils tombent
sur l'état vide existant (« Non disponible ») et n'affichent **jamais** la charge
d'un autre exercice ; en S1/S4 la référence comparable reste visible ; en S3 c'est
le prescrit plus ancien qui apparaît, jamais la substitution. **Aucun changement
applicatif** (Option A) — 8 tests le prouvent. `Sb_DOGFOOD_01.3` (mobile placeholder)
prêt à être proposé.
