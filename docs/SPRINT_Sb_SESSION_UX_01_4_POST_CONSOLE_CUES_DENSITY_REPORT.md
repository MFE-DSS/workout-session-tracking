# Sprint Sb_SESSION_UX_01.4 — Post-Console Cues Density (F3) — BUILD

**Statut** : 🟢 **SAFE BUILD — DELIVERED LOCALEMENT** (LOCAL BATCH MODE, non commité)
**Type** : CODE BUILD — carte séance active, template + CSS minimal, SSR/no-JS
**Date** : 2026-07-14
**Origine** : friction **F3** (densité mobile) — audit `Sx_SESSION_UX_01`
**HEAD de référence** : `be499f7` — **batch local** (contient déjà `01.2b` SAFE BUILD non commité)

---

## 0. Étape 0 — Brainstorming / Options / Choix retenu

### Décision : **SAFE BUILD** (Option A)
Les cues post-console (toujours visibles depuis 01.2) sont **repliées dans un `<details>` natif**,
**replié par défaut** (pas d'attribut `open`). Contenu (liste + fallback) et classes **inchangés** ;
aucune information supprimée ; **no-JS** (`<details>` natif).

### Sujets clivants tranchés
| # | Sujet | Décision |
|---|---|---|
| 1 | Garder visibles ou replier | **Replier** (F3 = densité). |
| 2 | `<details>` natif ou CSS | **`<details>` natif** (no-JS, accessible). |
| 3 | Replié ou ouvert par défaut | **Replié** (pas d'`open`). |
| 4 | Déplacer encore plus bas | **Non** : garder après alternatives (ordre 01.2b conservé). |
| 5 | Préserver contenu cues | **Oui, exactement** (liste + item + fallback). |
| 6 | Garder fallback « Exécution contrôlée… » | **Oui** (inchangé). |
| 7 | Cacher une info utile | non : 1 tap révèle tout ; rien supprimé. |
| 8 | Tap de trop | accepté : la saisie est priorisée, les cues deviennent secondaires. |
| 9 | Casser tests d'ordre 01.2/01.2b | **non** : classes `session-focus__cues` / `cues-title` préservées → 115 tests verts. |
| 10 | Mobile 360px | gain (bloc replié) ; summary lisible. |
| 11 | CSS ou template | **template + CSS minimal** (affordance summary). |
| 12 | Microcopy | non (summary « Cues techniques » suffit). |
| 13 | Machine panel séparé | **inchangé** (hors périmètre). |
| 14 | Test HTML ou source | **les deux** (rendu + source). |
| 15 | Continuer ou fermer batch | **fermer** après ce sprint (voir §recommandation). |

### Options écartées
- **B (rester visible)** : F3 non traité.
- **C (supprimer cues)** : rejet (perte d'info immédiate).
- **D (fusionner dans machine panel)** : rejet (refactor large).

---

## 1. Ordre final de la carte active

`Intention → Zone travaillée → [machine panel] → **Console sets** → **Alternatives (replié)** →
**Cues techniques (repliées `<details>`)** → Ressenti / note / up-next / CTA`

Ordre source vérifié : `worked-area < console < alternatives < cues`. **F1 complet** (console avant
cues et alternatives) **+ F3** (cues repliées).

---

## 2. Fichiers modifiés (périmètre autorisé strict)

| Fichier | Nature |
|---|---|
| `app/templates/_partials/exercise_card.html` | cues `<div>` → **`<details class="session-focus__cues">`** (sans `open`) ; `<span cues-title>` → **`<summary cues-title>`** ; contenu (liste + fallback) inchangé |
| `app/static/css/session_focus.css` | + règle minimale summary : `cursor:pointer`, `display:list-item` (garde le marker repliable), `[open]` margin — **var only, aucun hex** |
| `tests/test_session_ux_cues_density.py` | **nouveau** — 17 tests |

**Non modifiés** : routers, services, models, data, migrations, JS. Console / previous-load hint (01.3) /
« Référence précédente » / BodyMap / substitutions (01.2b) / sticky CTA / rest timer **intacts**.

---

## 3. Preuve : cues gardent leur contenu

- **Liste** `session-focus__cues-list` + `session-focus__cues-item` (les 3 cues machine) : **conservée**.
- **Fallback** `session-focus__cues-empty` « Exécution contrôlée, amplitude complète, tempo maîtrisé. » : **conservé** (test `test_cues_list_or_fallback_present`).
- Bloc rendu **1 seule fois** (`test_cues_rendered_once`).
- Seul le **wrapper** change (`<div>`→`<details>`, `<span>`→`<summary>`) — l'information est **repliée, pas retirée**.

## 4. Preuve no-JS
`<details>` est un élément HTML **natif** (repli/dépli sans JavaScript). `test_no_js_added` :
`addEventListener` absent, aucun fichier JS ajouté.

## 5. Preuve substitutions intactes
`test_substitutions_present` : `name="substituted_name"` + `sub-badge--n1` présents. Le bloc
alternatives (01.2b) n'est pas touché par ce sprint. 56 tests substitution restent verts (batch).

---

## 6. Tests locaux

| Suite | Résultat |
|---|---|
| `test_session_ux_cues_density.py` (dédiés) | **17/17** |
| Batch + asservis (`cues_density` + `alternatives_order` + `console_priority` + `prev_load` + `cockpit` + `worked_area`) | **115 passed** |
| Sweep large (session_focus/console/cues/alternatives/substitution/exercise_card/prev_load/bodymap/sticky/rest_timer/session_flow/accessibility) | **397 passed / 0 échec** (123 s) |
| ruff (test neuf) | clean |
| `check_ruff_budget` | **543 ≤ 548** |
| `check_spec_protocol` | PASS |

> `check_scope` = **ISOLATED** (7 fichiers batch) → **promu manuellement SHARED_CODE** (`exercise_card.html`
> + `session_focus.css` partagés). Sweep 397 couvre les consommateurs ; **CI réelle = source de vérité** (fin de batch).

---

## 7. Risques restants

| Risque | État |
|---|---|
| Marker repliable invisible (summary `display:block`) | **corrigé** : `display:list-item` force le chevron natif + `cursor:pointer`. |
| Casser l'ordre 01.2/01.2b | **non** : 115 tests verts, classes préservées. |
| Cacher une info utile | non : 1 tap révèle ; fallback toujours présent. |
| **Batch non dogfoodé** | ⚠️ 01.2 (mergé) + 01.3 (mergé) + 01.2b + 01.4 (locaux) empilés **sans confirmation salle**. |

---

## 8. Chemins interdits vérifiés

✅ Aucun `app/routers/**`, `app/services/**`, `app/models/**`, `data/**`, `migrations/**`,
`schema_snapshot`, `app/static/js/**`, `.github/**`, `deploy/**`. ✅ substitutions / console / previous-load /
BodyMap / overload / last_time / descriptor / ZONE_LABELS **intacts**. ✅ `Delt_lat` non traité.
✅ Body Intelligence OFF. ✅ Non commité / non poussé / CI non lancée.

---

## Verdict

**Verdict :** 🟢 **SAFE BUILD — Sb_SESSION_UX_01.4 DELIVERED LOCALEMENT (non commité).**

Les cues post-console sont **repliées dans un `<details>` natif** (replié par défaut, no-JS),
réduisant la densité mobile une fois la saisie priorisée. **Contenu et fallback inchangés**
(information repliée, pas supprimée) ; classes `session-focus__cues` / `cues-title` préservées.
**Template + CSS minimal** (affordance summary, var only, aucun hex) : routers / services / models /
data / migrations / JS **intacts** ; console / previous-load (01.3) / « Référence précédente » /
BodyMap / substitutions (01.2b) / sticky CTA / rest timer **préservés**. 17 tests dédiés + 115
batch/asservis + sweep 397 verts. check_scope ISOLATED → **promu SHARED_CODE**.

**Recommandation batch** : ce sprint **conclut le cycle de repriorisation de la carte active**
(F1 console-first + F2 previous-load + F3 densité cues). Le **batch local** contient maintenant
**`01.2b` + `01.4`** (non commités), en plus de `01.2`/`01.3` déjà mergés. Trois options :
1. **Dogfood F1+F2+F3 en salle AVANT de fermer** (recommandé) — 5 changements de la carte active
   empilés sans confirmation terrain ; un passage valide tout.
2. **Fermer le batch maintenant** : commit code (`01.2b` + `01.4`) → **CI complète 3/3** → puis revue.
3. Ajouter un dernier micro-sprint sûr avant fermeture.

Mon conseil : **(1) dogfood puis (2) fermeture CI** — pour ne pas merger 5 changements UX non éprouvés.
