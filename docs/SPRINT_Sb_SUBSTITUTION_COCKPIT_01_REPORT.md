# SPRINT Sb_SUBSTITUTION_COCKPIT_01 — borner la substitution, pas la construire (RAPPORT)

**Base canonique :** `aeba137` · **Branche :** `sb/substitution-cockpit-01`

---

## 1. Audit préalable — la capacité existait déjà, et elle était exposée

Le brief prévoyait un HARD STOP si la substitution n'existait pas côté backend,
et « continuer » si elle existait sans être exposée. **Ni l'un ni l'autre : elle
existait ET elle était exposée.** Le dire est la première obligation du sprint
(priorité 1 : ne pas mentir sur la capacité existante).

| capacité auditée | état |
|---|---|
| `can_substitute()` | **existe** — verrouille dès qu'une série de travail est validée |
| Candidats N1/N2/N3 | **existe** — `compute_suggestions()`, avec `name` / `badge` / `rationale` |
| Action / route | **existe** — `substituted_name` posté au **même** formulaire d'exercice |
| Persistance | **existe** — `se.substituted_name = sub_name` sous garde `can_substitute` |
| Prévu vs réalisé | **existe** — `exercise_name_snapshot` (prévu) ≠ `substituted_name` (réalisé) |
| Bloc cockpit | **existe** — `.substitute-picker`, sous la console depuis la tranche UI V2 |
| Passage au gabarit | **existe** — `substitution_data[se.id]` construit par le routeur |
| Gardes | **existe** — `substitution.py` gelé par `test_no_decision_engine_was_touched` |

**Rien de tout cela n'a été reconstruit.** Aucun moteur, aucune route, aucun
service touché.

---

## 2. Le défaut réel : la quantité

Ce qui manquait n'était pas la substitution, c'était sa **borne**. Mesuré sur
`push-a`, en **liste directe** (N1+N2, hors disclosure « élargies » qui existait
déjà) :

```
E1  6      E2  6      E3  5      E4  4
E5  5      E6  5      E7  5
```

Soit jusqu'à **six alternatives affichées d'un coup au milieu d'une série** —
et jusqu'à **dix candidats au total** sur E5/E6. C'est précisément le
« catalogue en pleine séance » que le brief refuse.

---

## 3. Le correctif — plafond de 4, surplus démis et non supprimé

```jinja
{% set _cap = 4 %}
{% set _vis_n1 = _n1_all[:_cap] %}
{% set _n2_room = _cap - (_vis_n1 | length) %}
{% set _vis_n2 = _n2_all[:_n2_room] if _n2_room > 0 else [] %}
{% set _overflow = _n1_all[(_vis_n1|length):] + _n2_all[(_vis_n2|length):] + _n3_all %}
```

**L'ordre de proximité du service est respecté** : N1 remplit d'abord, N2 prend
la place restante. Le surplus rejoint la disclosure « alternatives élargies »
**qui existait déjà** — donc :

* **aucun candidat ne disparaît** — tous restent dans le DOM, sélectionnables ;
* **aucune valeur postée ne change** — même `name="substituted_name"`, mêmes
  `value` ;
* **l'ordre N1 → N2 → N3 est conservé**, y compris dans la source, comme
  l'exige la garde héritée.

Résultat mesuré : **4 visibles sur les 7 cartes**, totaux inchangés
(6 · 6 · 5 · 9 · 10 · 10 · 5).

---

## 4. Un défaut trouvé en pilotant, pas en lisant

Le pilotage navigateur a buté : le clic sur le résumé « Adapter l'exercice »
était **intercepté par `session-focus__header-main`**. En défilant jusqu'au
résumé, celui-ci se calait **sous l'en-tête collant**.

Même famille que l'ancre de série corrigée au sprint précédent, même correctif :

```css
.substitute-picker,
.substitute-picker__summary { scroll-margin-top: 110px; }
```

Il a fallu la poser **aussi sur le `<summary>`** : `scroll-margin-top` sur le
parent ne gouverne pas le défilement vers l'enfant, et le `<summary>` est
l'élément **focusable**. C'est donc un cas réel de contrôle obscurci au
**focus clavier**, pas seulement un artefact de test.

Pas de JS, pas de z-index, pas de position absolue.

---

## 5. Un faux positif écarté avant de conclure

`check()` de Playwright échouait sur les radios. Ce n'est **pas** un défaut :
les radios sont **volontairement masqués visuellement** (motif `.a11y-input` :
clippés mais focusables) et l'utilisateur clique le **label** qui les enveloppe.

Le script pilote donc le label — le geste réel — ce qui vérifie **au passage**
que l'association label/input tient. `coché après clic : True`.

---

## 6. Preuves navigateur, 360×640

```
AVANT SUBSTITUTION
  cue exercice actif ... "Banc à 30° pour cibler le haut des pecs"
  options rendues ...... 7 (dont « prescrit »)  → 4 directes + 2 élargies
  choix ................ "Développé incliné haltères 30°"
  coché après clic ..... True

APRÈS SUBSTITUTION + nav=stay
  url .................. ?active=15&rest=1#set-61
  reste sur l'exercice.. oui
  « (substitué) » ...... présent
  « (prescrit) » ....... présent          ← l'identité prévue survit
  cue après substit. ... "Banc à 30° (pas plus)"   ← suit le RÉALISÉ
  action de série ...... CTA CTA CTA CTA CTA
  CTA d'exercice ....... CTA CTA CTA CTA CTA
  scrollWidth .......... 360
```

**A8 est satisfait par le câblage existant** : `get_for_session_exercise()`
suit `substituted_name` en priorité, donc le cue atlas a changé tout seul pour
l'exercice réellement exécuté.

---

## 7. Acceptation

| | critère | état |
|---|---|---|
| A1 | capacité existante auditée et rapportée | ✅ §1 |
| A2 | contrôle **local** à la carte, pas global | ✅ absent de `session_detail.html` |
| A3 | 2 à 4 alternatives maximum | ✅ 4 sur 7/7 cartes |
| A4 | aucun catalogue global | ✅ garde sur marqueurs de recherche |
| A5 | prévu vs réalisé préservé | ✅ champs séparés, `(prescrit)` visible |
| A6 | retour au flow, log via `nav=stay` | ✅ `?active=…&rest=1#set-…` |
| A7 | CTA non obstrués | ✅ 5/5 sur les deux |
| A8 | cue atlas suit l'exécuté | ✅ vérifié |
| A9 | sans JS | ✅ `details` natif, aucun script |
| A10 | nom accessible | ✅ `aria-label` sur le résumé |
| A11 | parité métier | ✅ diff **vide** sur `app/models`, `migrations`, `app/services`, `app/routers` |

**15 tests dédiés.** Plantation : plafond porté à 99 → **2 gardes tombent**.
**Sweep 4704, 0 échec**, lancé depuis le worktree. Ruff propre.

---

## 8. Limites volontaires

- **Le plafond est de 4, en dur dans le gabarit.** Ni configurable ni
  par-utilisateur : V1 assumée, et un test l'exige explicite plutôt
  qu'implicite.
- **Le compteur d'en-tête affiche le TOTAL disponible**, pas les 4 visibles.
  C'est cohérent — 4 + le compte de la disclosure = total — et cela évite de
  laisser croire que le reste n'existe pas.
- **Aucune raison de substitution n'est collectée.** Le brief l'interdisait si
  elle n'était pas déjà supportée ; elle ne l'est pas, et on ne l'invente pas.
- **`.sub-elargi` peut désormais contenir jusqu'à 6 entrées** sur E5/E6. Elle
  est repliée par défaut, donc hors du champ du plafond de séance — mais si
  elle devenait elle-même un catalogue, ce serait le prochain sujet.

## Verdict

La substitution n'a pas été construite : elle existait, complète et câblée.
Ce sprint l'a rendue **utilisable en séance** en supprimant ce qui en faisait
un catalogue, sans retirer un seul candidat.

Le travail utile a été l'audit — établir que six des huit capacités demandées
étaient déjà là, et que le vrai défaut tenait en un nombre.

---

## Closeout (post-merge)

| | |
|---|---|
| PR | **#119** — `--merge --match-head-commit ab4c855`, **sans** squash / `--admin` / force |
| Merge | **`4d4c40e`** |
| CI canonique | run `32027643640` — **succès 6/6** |
| Gate Sonar | **`OK`** — 0 bug, 0 smell, 0 vulnérabilité, 0 % duplication |
| Threads / Gitar | **0 / 0** |
| CI PR | **9 checks verts au premier passage, aucun aller-retour** |
| Parité métier | diff **vide** sur `app/models`, `migrations`, `app/services`, `app/routers` |

### Capacité CI — `HEALTHY`, partition parfaitement équilibrée

| Shard | Fichiers | min MemAvailable | min SwapFree |
|---|---|---|---|
| 1 | 85 | 6 895 Mo | 3 071 — intact |
| 2 | 85 | 7 321 Mo | 3 071 — intact |
| 3 | 85 | 7 689 Mo | 3 071 — intact |

`workers=2`, manifeste respecté, jamais `-n auto`. **85/85/85** — partition
parfaitement équilibrée, shard bas à **6 895 Mo**, très au-dessus du plancher
de 4 Go.

### Trois sprints d'affilée sans aller-retour

`Sb_ATLAS_COVERAGE_01`, puis celui-ci : PR verte du premier coup, gate
comprise. Le pré-scan AST avant commit est devenu systématique, et c'est
exactement la période où les cycles CI supplémentaires ont cessé.

### Ce que le bénéfice composé a donné

`A8` — le cue atlas suivant l'exercice **réellement exécuté** après
substitution — a été satisfait **sans écrire une ligne**. Il découle de
`get_for_session_exercise()` qui priorise `substituted_name`, et de la
couverture complétée à la tranche précédente. Trois sprints qui s'empilent
proprement plutôt que de se gêner.
