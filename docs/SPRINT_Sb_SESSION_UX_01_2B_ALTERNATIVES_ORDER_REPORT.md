# Sprint Sb_SESSION_UX_01.2b — Alternatives Below Console — BUILD

**Statut** : 🟢 **SAFE BUILD — DELIVERED LOCALEMENT** (LOCAL BATCH MODE, non commité)
**Type** : CODE BUILD — carte séance active, template only, SSR/no-JS, **form-critical (prudence max)**
**Date** : 2026-07-14
**Origine** : dette optionnelle de `Sb_SESSION_UX_01.2` (F1) — audit `Sx_SESSION_UX_01`
**HEAD de référence** : `be499f7` (rien commité par ce sprint)

---

## 0. Étape 0 — Brainstorming / Options / Choix retenu

### Décision : **SAFE BUILD** (Option A)
Le déplacement du drawer « Adapter l'exercice » sous la console est **purement structurel** — vérifié
par diff : tous les `<input type="radio">`, `<label>`, summary, badges N1/N2/N3, fallback legacy et
`elif se.substituted_name` sont **byte-for-byte identiques** avant/après (seul le commentaire diffère).
Aucune condition (`can_sub`, `subs`, `grouped`, `total_grouped`, `se.substituted_name`), aucune value,
aucun name, aucune route touchés. → Les garde-fous form-critical passent → **Option A retenue**.

### Sujets clivants tranchés
| # | Sujet | Décision |
|---|---|---|
| 1 | Déplacer le drawer entier ou laisser | **Déplacer entier** (bloc auto-suffisant : ses `{% set %}` voyagent avec lui). |
| 2 | Même form POST | **Oui, identique** (`update_exercise_card`). |
| 3 | Radios `substituted_name` | **Tous préservés** (byte-identical). |
| 4 | N1/N2/N3 + legacy | **Préservés** (byte-identical). |
| 5 | Carte active seule ou toutes | **Toutes** (le bloc est hors `{% if is_active %}`, comme avant). |
| 6 | Risque `elif se.substituted_name` | **Préservé** (badge substitué inchangé). |
| 7 | Casser substitutions sélectionnées | **Non** : `checked` conditionnels inchangés. |
| 8 | Casser tests substitution | **Non** : 56 tests substitution verts. |
| 9 | Masquer une action utile avant 1re série | drawer **replié** ; désormais juste sous la console → toujours accessible. |
| 10 | Le drawer replié gêne-t-il assez ? | marginal, mais le geste est **sûr** → on capture la cohérence d'ordre. |
| 11 | Alternatives avant ou après cues | **avant cues** (cible : console → alternatives → cues). |
| 12 | Garder 01.2 tel quel + STOP | non : SAFE BUILD atteint. |
| 13 | Tester sans fixtures sub complexes | **assertions sur le template source** (ordre + invariance) + tests substitution existants. |
| 14 | Local batch ou commit | **LOCAL BATCH** (CI en fin de batch). |
| 15 | Dogfood avant CI | recommandé (voir §recommandation). |

### Options écartées
- **B (STOP)** : non nécessaire — le diff est purement structurel.
- **C (déplacer summary seul)** : rejet (sépare summary/body, HTML fragile).
- **D (lien secondaire)** : rejet (nouveau comportement, hors micro-sprint).

---

## 1. Ordre avant / après (carte active)

| # | AVANT (après 01.2) | APRÈS (01.2b) |
|---|---|---|
| 1 | Intention | Intention |
| 2 | Zone travaillée | Zone travaillée |
| 3 | [machine panel] | [machine panel] |
| 4 | **Alternatives (replié)** | **Console sets (saisie)** ⬆ |
| 5 | **Console sets (saisie)** | **Alternatives (replié)** ⬇ |
| 6 | Cues techniques | Cues techniques |
| 7 | Ressenti / note / up-next / CTA | Ressenti / note / up-next / CTA |

Ordre source vérifié : `worked-area < console < alternatives < cues`. Cible du brief atteinte.

---

## 2. Fichiers modifiés (périmètre autorisé strict)

| Fichier | Nature |
|---|---|
| `app/templates/_partials/exercise_card.html` | bloc alternatives (commentaire + `{% set %}` + `if/elif`) **déplacé** de avant-console à après-console (entre console et cues) — contenu **byte-identical** |
| `tests/test_session_ux_alternatives_order.py` | **nouveau** — 17 tests |

**Non modifiés** : routers, services, models, data, migrations, JS, **CSS** (`session_focus.css` intact —
déplacement réutilise les classes existantes). Aucune donnée/calcul/condition changé.

---

## 3. Invariants substitution préservés (preuve)

Diff `git HEAD` vs working tree, hors commentaires :
- **`<input type="radio">`** : **identiques byte-for-byte** (diff vide).
- **Contenu drawer** (`<label>`, `substitute-picker__*`, `sub-badge--n1/n2/n3`, `substitute-badge`) : **identique**.
- `{% if can_sub and (subs or total_grouped > 0) %}` · `{% elif se.substituted_name %}` · `{% set sub_data %}`… : **présents, inchangés** (tests dédiés).
- Bloc rendu **1 seule fois** (pas de doublon, `sub_data` non dupliqué).
- Même `<form ... action=update_exercise_card>` (form POST unique de la carte).

---

## 4. Tests locaux

| Suite | Résultat |
|---|---|
| `test_session_ux_alternatives_order.py` (dédiés) | **17/17** |
| Tests **substitution** existants (form-critical) | **56 passed / 0 cassé** |
| Adjacents (console_priority/prev_load/worked_area/ui06) | **63 passed** |
| Sweep large (session_focus/console/alternatives/substitution/exercise_card/prev_load/bodymap/sticky/rest_timer/session_flow/accessibility) | **371 passed / 0 échec** (126 s) |
| ruff (test neuf) | clean |
| `check_ruff_budget` | **543 ≤ 548** |
| `check_spec_protocol` | PASS |

> `check_scope` = **ISOLATED** (2 fichiers) → **promu manuellement SHARED_CODE** (carte séance active
> partagée). Sweep 371 + 56 substitution couvrent les consommateurs ; **CI réelle = source de vérité**.

---

## 5. Risques restants

| Risque | État |
|---|---|
| Sélection de substitution cassée | **écarté** : radios/`checked`/values byte-identical ; 56 tests substitution verts. |
| Ordre HTML asservi | mitigé : `body-slot..cues` (test worked_area) reste vert (région élargie, sans asset). |
| Dogfood F1+F2 encore pending | ⚠️ 01.2 + 01.3 + maintenant 01.2b **non confirmés terrain** — batch à dogfooder. |
| Re-densification | non : bloc déplacé, contenu inchangé, aucun ajout. |

---

## 6. Chemins interdits vérifiés

✅ Aucun `app/routers/**`, `app/services/**`, `app/models/**`, `data/**`, `migrations/**`,
`schema_snapshot`, `app/static/js/**`, **`app/static/css/**`**, `.github/**`, `deploy/**`. ✅ substitution
logic / overload / last_time / descriptor / ZONE_LABELS **intacts**. ✅ `Delt_lat` non traité.
✅ Body Intelligence OFF. ✅ Non commité / non poussé / CI non lancée.

---

## Verdict

**Verdict :** 🟢 **SAFE BUILD — Sb_SESSION_UX_01.2b DELIVERED LOCALEMENT (non commité).**

Le drawer « Adapter l'exercice » est **déplacé sous la console** (ordre carte active : worked-area →
console → alternatives → cues). **Purement structurel** : contenu du drawer (radios
`substituted_name`, N1/N2/N3, legacy, `elif se.substituted_name`, form POST) **byte-for-byte
identique** — prouvé par diff. **Template only** (aucun CSS) : routers / services / models / data /
migrations / JS **intacts** ; substitution logic préservée (56 tests verts). 17 tests dédiés + 63
adjacents + sweep 371 verts. check_scope ISOLATED → **promu SHARED_CODE**.

**Recommandation — prochain micro-sprint du batch** : ce build **conclut la repriorisation de la
carte active** (F1 complet : console avant cues **et** avant alternatives ; F2 déjà livré). **Avant
d'ouvrir F3 (`01.4` scroll)** ou de fermer le batch en CI, je recommande **un dogfood terrain F1+F2**
(fiche prête) — trois changements de la carte active sont empilés localement/mergés sans confirmation
salle. Option : fermer le batch (CI complète sur 01.2b) puis dogfood, ou dogfood d'abord.
