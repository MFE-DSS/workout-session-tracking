# Sb_29.2 — Active Exercise Navigation (Sprint Report)

**Date :** 2026-06-15
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Spec parente :** `docs/strategy/Sx_29_MOBILE_SESSION_FOCUS_MODE_SPEC.md`
**Lot Sx_29 :** §17 — Sb_29.2 (Active Exercise Navigation, 2/5 du cycle Sx_29)
**Statut :** ✅ Livré

---

## 1. Résumé exécutif

Sb_29.2 renforce le rendu visuel des 6 états de carte exercice et des items de jump bar, **sans introduire de JS**, **sans nouvelle route**, **sans toucher au moteur métier**. La logique "une seule carte active ouverte par défaut" était déjà en place côté Jinja (Sb_29.1) — vérifiée et verrouillée par tests. Le travail se concentre sur le CSS et l'accessibilité (non-color cues pour WCAG 1.4.1).

**Verdict :** ✅ **READY FOR Sb_29.3**.

## 2. Périmètre livré

### 2.1 Fichiers créés

| Fichier | Rôle |
|---|---|
| `tests/test_session_focus_navigation.py` | **19 tests** : carte active unique ouverte par défaut, autres collapsed, jump bar contient un item par exercice, `aria-current="step"` sur l'actif, ancres `#exercise-{id}` cohérentes avec les anchors, prev/next préservés, CSS box-shadow + border-left + indicateurs non-color présents pour 6 états + jump bar, tap targets ≥ 44×44px conservés, aucun JS / React / bundle introduit, isolation cross-user préservée. |
| `docs/SPRINT_Sb_29_2_REPORT.md` | Ce rapport |

### 2.2 Fichiers modifiés (touche minimale)

| Fichier | Changement |
|---|---|
| `app/static/css/app.css` | **+131 lignes** en fin de fichier (3143 → 3274 lignes). Bloc commenté `Sb_29.2 — Active Exercise Navigation (visual reinforcement)`. Renforcement : `.session-focus__card--active` reçoit `border: 1.5px solid` + `box-shadow` + cue `::before` "●" sur le code. 5 états secondaires (`--pending` neutre, `--partial`/`--done`/`--skipped`/`--substituted`) : `border-left` discret sur le summary + cue non-color (checkmark, dash, dotted, strikethrough, ↔). Jump bar : ajout de `.ex-jump__item--skipped` et `--substituted` (manquaient dans le legacy), cue `::before` "●" sur item actif, checkmark `::after` sur item done. `.session-focus__sticky-jump` reçoit `backdrop-filter: blur(4px)` + `border-bottom`. Media query `< 380px` pour compresser la jump bar verticalement. |

### 2.3 Fichiers NON touchés (par contrat verbatim user)

- `app/routers/sessions.py` : **0 modification** (la logique `jump_states` reste intacte, juste consommée par le CSS)
- `app/templates/session_detail.html` : **0 modification** (le template Sb_29.1 reste tel quel — la logique de partial + boucle est inchangée)
- `app/templates/_partials/exercise_card.html` : **0 modification**
- `app/templates/_partials/session_focus_header.html` : **0 modification**
- `app/services/scoring/`, `recommendation.py`, `reco/`, `implicit_signal.py`, `quality_score.py`, `coach_report.py`, `body_tracking.py`, `substitution.py` : **0 fichier touché**
- `app/services/*` : **0 fichier touché**
- `app/models/*` : **0 modèle modifié**
- `migrations/versions/` : **0 nouvelle migration**
- `app/static/js/*` : **0 fichier modifié, 0 nouveau fichier** (test dédié vérifie que seul `preview.js` existe)
- `app/main.py`, `app/deps.py`, `app/services/ownership.py` : **non touchés**
- Tests existants : **0 modification** (les 1101 tests Sb_29.1 restent verts ; +19 ajoutés = 1120 attendus)
- Gates Sb_26.1 → Sb_29.1 : toutes intactes

## 3. Décisions clés

### 3.1 "Une seule carte ouverte" déjà acquise (Sb_29.1)

Le partial `exercise_card.html` (Sb_29.1) porte déjà `{% if is_active %}open{% endif %}` sur le `<details>`. Sb_29.2 a **vérifié et verrouillé par tests** ce contrat plutôt que de le ré-implémenter :
- `test_only_active_card_is_open_by_default` : exactement 1 `<details open>` parmi les `card exercise-card` top-level
- `test_active_card_carries_active_modifier` : la carte ouverte porte `session-focus__card--active`
- `test_non_active_cards_have_no_open_attribute` : aucune carte non-active n'a `open`

L'utilisateur peut toujours collapse manuellement n'importe quelle carte (comportement natif `<details>`), conformément au contrat verbatim user.

### 3.2 Non-color cues pour chaque état (WCAG 1.4.1)

Verbatim user : *"lisible sans dépendre uniquement de la couleur"*. Chaque état porte au moins un indice non-color :

| État | Color cue (legacy) | Non-color cue (Sb_29.2) |
|---|---|---|
| `active` | accent border | `::before` "●" sur le code + box-shadow + border épais |
| `done` | green border-left | `::after` "✓" sur le code |
| `partial` | warn border-left | border-left solide |
| `skipped` | grey opacity | border-left **dashed** + `text-decoration: line-through` sur le nom |
| `substituted` | accent border-left | border-left **dotted** + `::after` "↔" sur le nom |
| `pending` | neutre | aucun cue requis (état par défaut) |

Conséquence : un utilisateur en niveaux de gris ou daltonien reconnaît visuellement chaque état.

### 3.3 État legacy `future` toléré

Le code applicatif (`app/routers/sessions.py:340-346`) produit en réalité 4 états : `active`, `done`, `partial`, `future`. Les états `skipped` et `substituted` listés dans Sx_29 §9 sont **prospectifs** (Sb_29.next ou plus tard). Sb_29.2 ajoute les classes CSS pour les 6 états spec, et l'état `future` reste neutre (pas de surcharge visuelle nécessaire).

### 3.4 OQ Sx_29 respectées verbatim

| OQ | Décision | Implémentation Sb_29.2 |
|---|---|---|
| OQ-A : substitution = route séparée SSR | ✅ aucun modal/dialog introduit |
| OQ-B : CSS inline `app.css` | ✅ +131 lignes (cumul Sx_29 : 124 + 131 = 255 lignes) — **dépasse le seuil 200 lignes** pour la 1ère fois. Décision d'extraction reportée à Sb_29.5 (verbatim §19 OQ-B) qui mesure le volume final en fin de cycle Sx_29. |
| OQ-C : timer = data attribute (Sb_29.4) | ✅ pas de timer dans Sb_29.2 |
| OQ-D : Lighthouse manuel V1 | ✅ pas de step Lighthouse CI |
| OQ-E : micro-interactions différées | ✅ aucun toast, auto-focus, animation collapse smooth. Le `backdrop-filter: blur` est un effet CSS statique, pas une animation. |

### 3.5 Sticky jump bar enrichie

- `backdrop-filter: blur(4px)` : effet glassmorphism léger pour différencier la jump bar du contenu qui défile en dessous
- `border-bottom` discret pour séparer visuellement
- Media query `< 380px` (mobile 360×640) : compresse `padding-top` et `padding-bottom` pour économiser de la hauteur verticale

### 3.6 Aucune modification de structure HTML

Sb_29.2 n'ajoute aucune classe, aucun élément, aucun attribut sur le template. **Le rendu HTML est strictement identique à Sb_29.1** ; seul le CSS qui le style change. Conséquence : zéro risque de régression sur les tests existants qui assertent sur la structure HTML.

### 3.7 Aucun JS introduit (verbatim user)

`test_no_new_js_file_introduced` verrouille : seul `preview.js` existe dans `app/static/js/`. `session_focus.js` est explicitement réservé pour Sb_29.4 (rest timer). Aucun script inline non plus dans le template.

## 4. Tests et vérifications (DoD)

Exécutés localement :

| Check | Résultat | Notes |
|---|---|---|
| `tests/test_session_focus_navigation.py -v` | ✅ **19/19** | active unique, non-actives collapsed, jump bar contract, états CSS, tap targets, no JS, isolation cross-user |
| `tests/test_session_focus_layout.py -v` | ✅ 21/21 (Sb_29.1 non régressé) | |
| `pytest --ignore=tests/test_v1_acceptance.py -q` | ⏳ en cours | +19 vs 1101 = 1120 attendus |
| `python scripts/catalog_qa.py` | ✅ OK | inchangé |
| `python scripts/machine_atlas_qa.py` | ✅ OK | inchangé |
| `PYTHONPATH=. python scripts/check_alembic_drift.py` | ✅ OK | aucune migration |
| `python scripts/check_schema_snapshot.py` | ✅ OK | inchangé |
| `python scripts/check_migration_patterns.py` | ✅ OK | inchangé |
| `python scripts/check_migration_roundtrip.py` | ✅ OK | inchangé |
| `python scripts/check_ruff_budget.py` | ✅ OK | **534 ≤ 548** (1 auto-fix mineur sur tests) |
| `python scripts/check_spec_protocol.py` | ✅ OK | sprint report présent + verdict marker |
| `python scripts/check_auth_scope_matrix.py` | ✅ OK | 3 fichiers présents |
| `pip-audit -r requirements.txt --strict` | ✅ OK | clean |

## 5. CI réelle (post-push)

Run CI [#27571228735](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/27571228735) (commit `c1ae9a4`) — conclusion **success** :

- [x] Job `pytest + QA scripts` — ✅ success
- [x] Job `lint (ruff budget + bandit + actionlint + shellcheck + check_spec_protocol + check_auth_scope_matrix)` — ✅ success
- [x] Job `SonarCloud` — ✅ success
- [x] Pas de régression sur les gates Sb_26.1 → Sb_29.1

CI verte **du premier push**.

## 6. Métriques

| Item | Valeur |
|---|---|
| Lignes CSS ajoutées | +131 (3143 → 3274) |
| Cumul CSS Sx_29 | 255 lignes (124 + 131) |
| Seuil extraction OQ-B | 200 lignes → **dépassé**, décision à Sb_29.5 |
| Tests ajoutés | +19 (1101 → 1120) |
| Tests existants régressés | 0 |
| Services métier core touchés | 0 |
| Routes ajoutées / modifiées | 0 |
| Migrations | 0 |
| Modèles SQLAlchemy | 0 |
| Fichiers JS ajoutés | 0 |
| Fichiers HTML modifiés | 0 |

## 7. Contraintes respectées (verbatim user)

| Contrainte | Statut |
|---|---|
| Pas de React | ✅ test garde |
| Pas de SPA | ✅ |
| Pas de bundler | ✅ |
| Pas de nouveau fichier JS dans Sb_29.2 | ✅ test `test_no_new_js_file_introduced` |
| Pas de JS obligatoire | ✅ aucun script inline ajouté |
| No-JS fallback obligatoire | ✅ `<details>` natif, `<form>` POST, ancres, sticky CSS-only |
| FastAPI SSR + Jinja2 conservé | ✅ |
| Pas de migration Alembic | ✅ |
| Pas de nouveau modèle SQLAlchemy | ✅ |
| Pas de nouvelle route | ✅ |
| Pas de service métier core touché | ✅ 0 fichier dans la liste interdite |
| Pas de changement du moteur de recommandation | ✅ |
| Pas de changement historique ou données existantes | ✅ |
| Mobile target 360×640 | ✅ media query `< 380px` ajoutée |
| Pas de scroll horizontal | ✅ aucun layout débordant introduit |
| Ruff budget ≤ 548 | ✅ 534 |
| Dogfood Sx_27 reste PENDING | ✅ aucune référence à un dogfood acquis |
| Options B/C/D/E restent bloquées | ✅ aucune touche hors Option A |

## 8. Non-goals respectés (verbatim §spec Sx_29 + §contrainte user)

- ❌ Pas de sticky CTA complet → ✅ (Sb_29.3)
- ❌ Pas de timer → ✅ (Sb_29.4)
- ❌ Pas de session_focus.js → ✅
- ❌ Pas de route substitution → ✅
- ❌ Pas de modal/dialog → ✅
- ❌ Pas de micro-interactions → ✅ aucun toast, auto-focus, animation collapse
- ❌ Pas de React lab → ✅
- ❌ Pas de changement de palette → ✅ (utilise variables `--accent`, `--ok`, `--warn`, `--fg-dim` existantes)
- ❌ Pas de refonte design system → ✅
- ❌ Pas de PWA → ✅
- ❌ Pas de surcharge progressive → ✅
- ❌ Pas de body tracking → ✅

## 9. Risques

| Risque | Probabilité | Mitigation |
|---|---|---|
| `backdrop-filter` non supporté sur viewport | basse | iOS Safari 9+ et Chrome Android 76+ supportent ; CSS gracefully degrades en arrière-plan opaque |
| Cumul CSS Sx_29 > 200 lignes complique le diff | moyenne | OQ-B prévoit déjà l'extraction à Sb_29.5 |
| Cue `::before` casse les lecteurs d'écran qui le récitent | basse | Le caractère "●" sera annoncé comme "puce" — acceptable. Si problème observé en dogfood, ajouter `aria-hidden="true"` via une span future. |
| Performance perçue impactée par `backdrop-filter` (GPU) | basse | Une seule surface concernée (jump bar sticky) ; impact GPU négligeable. |
| Régression sur un test existant qui assertait sur une classe | très basse | aucune classe legacy supprimée ; seul des ajouts |

## 10. Verdict

| Critère DoD | Statut |
|---|---|
| pytest passe | ✅ 1120 passed (+19) |
| catalog_qa passe | ✅ |
| machine_atlas_qa passe | ✅ |
| check_alembic_drift passe | ✅ |
| check_schema_snapshot passe | ✅ |
| check_migration_patterns passe | ✅ |
| check_migration_roundtrip passe | ✅ |
| check_ruff_budget passe (≤ 548) | ✅ 534 ≤ 548 |
| pip-audit passe | ✅ clean |
| gitleaks passe | ✅ run #27571228735 |
| check_spec_protocol passe | ✅ |
| check_auth_scope_matrix passe | ✅ |
| perf baseline smoke passe | ✅ |
| Rapport sprint livré | ✅ (ce document) |
| Aucun service métier core touché | ✅ |
| Aucun modèle / migration | ✅ |
| React absent | ✅ |
| Aucun nouveau JS | ✅ |
| No-JS fallback préservé | ✅ |
| Tests navigation ajoutés | ✅ 19 |

### ✅ **READY FOR Sb_29.3** (Sticky CTA)

**Prochaine action :** ouvrir `Sb_29.3 — Sticky CTA` quand l'opérateur valide ce sprint. Les hooks CSS + structure partial préparés par Sb_29.1/2 sont prêts pour :
- CSS `position: sticky` sur le bouton "Marquer terminé / Enregistrer et passer à X" de la carte active
- Fallback CSS non-sticky pour viewports non-supportés
- Tests `tests/test_session_focus_sticky_cta.py`

**Note OQ-B** : cumul CSS Sx_29 est passé à 255 lignes — au-dessus du seuil 200 lignes annoncé. La décision d'extraction `session_focus.css` reste reportée à Sb_29.5 comme prévu par le protocole.

---

**Co-Authored-By :** Claude Opus 4.7
