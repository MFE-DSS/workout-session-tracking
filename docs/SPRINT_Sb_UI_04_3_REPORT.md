# Sprint Report — Sb_UI_04.3 Active Exercise Cockpit Shell

**Sprint ID :** `Sb_UI_04.3_ACTIVE_EXERCISE_COCKPIT_SHELL`
**Type :** BUILD UI — structural template + scoped CSS + tests + report
**Date :** 2026-07-05
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Verdict :** 🟢 **DELIVERED — pending CI + human review**

---

## 1. Objectif

Transformer l'écran séance d'une **liste verticale d'exercices** vers un **cockpit centré sur l'exercice actif**, premier build du recast `Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC` (accepté 2026-07-04). Le résultat doit être **visuellement perceptible immédiatement** : un reviewer doit pouvoir dire « ce n'est plus une liste verticale repeinte ; c'est un cockpit d'exercice actif ».

## 2. Rappel réserve Sb_UI_04.2

Sb_UI_04.2 (Header & Jump Bar Structure) a été **accepté avec réserve visuelle** : transformation trop proche d'un recolor / polish léger, cœur de la séance encore trop proche de l'existant. Cette réserve a été transférée à Sb_UI_04.3 comme charte d'ouverture : **profondeur visuelle réelle exigée, simple recolor / accordéon explicitement rejeté**.

## 3. Rappel recast accepté

Le recast `Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC` (HUMAN REVIEW ACCEPTED 2026-07-04, commit `51811fa`) a figé :
- **Active Exercise Cockpit** comme cœur d'écran (§18) ;
- **Live Exercise Expert Model** à 7 couches (orientation · intent · worked area · cues · logging console · alternatives · up next) ;
- **Body Representation System** transverse (§23) — Worked Area Panel = premier jalon dès Sb_UI_04.3 ;
- OQ-A → OQ-G tranchées ;
- redécoupage : **Sb_UI_04.3 = Active Exercise Cockpit Shell**.

## 4. Fichiers changés (whitelist stricte respectée)

| Fichier | Nature |
|---|---|
| `app/templates/session_detail.html` | cockpit wrapper + orientation + mini-stepper (remplace jump bar dense) |
| `app/templates/_partials/exercise_card.html` | hero cockpit sur carte active : intent + worked area + cues shell ; up-next enrichi (zone) |
| `app/static/css/session_focus.css` | styles scoped Sb_UI_04.3 (cockpit, orientation, stepper, hero, worked area, up-next, dominance active / secondary) |
| `tests/test_session_focus_layout.py` | 1 test patché (jump bar → stepper, OQ-B) |
| `tests/test_session_focus_cockpit.py` | **nouveau** — 34 tests cockpit |

**Header partial non touché** : l'orientation cockpit a été placée dans `session_detail.html` (pas de rework cosmétique gratuit du header, conformément au périmètre §3 du brief).

## 5. Active cockpit structure

Topologie recomposée (`session_detail.html`) : les exercice-cards sont désormais enveloppées dans `.session-focus__cockpit` avec, en tête :
1. **Orientation** (`.session-focus__orientation`) — compteur exercice courant / total (chiffre mono large teal) + N restants. Données issues de `jump_states` + `stats` déjà calculées côté router (aucune logique backend ajoutée).
2. **Mini-stepper** (`.session-focus__stepper`) — voir §6.
3. **Cartes exercice** — la carte active devient un **hero dominant** (bordure accent 3px, ombre `--shadow-md`, surface élevée) ; les cartes non-actives sont réduites à un **index secondaire compact** (fond en retrait, pas d'ombre, `opacity 0.92`) afin de ne plus ressembler à une liste ouverte. Elles **restent dans le DOM** (anchors + no-JS + réouverture OQ-E).

## 6. Mini-stepper

La jump bar dense (`.session-focus__jump`, pleine largeur) devient un **stepper compressé** (`.session-focus__stepper`) : chips 44×44 en bande scrollable horizontale (`scroll-snap-type: x`), code + progression compacts. C'est le levier principal qui casse la perception « barre de navigation large ».
- Ancres `#exercise-{id}` **préservées** sur chaque item.
- `aria-current="location"` **uniquement** sur l'item actif ; non-actifs **sans** `aria-current`.
- Item actif : fond `--color-accent-weak` + code `--color-accent-strong` ; non-color cue héritée des `::before` d'état.
- `session-focus__sticky-jump` conservé (sticky préservé). CSS legacy `.session-focus__jump` conservé (additif, non supprimé).

## 7. Worked Area Panel (premier jalon Body Representation System)

Rendu sur la carte active (`.session-focus__worked-area`) :
- **Zone principale** — source **réelle existante** : `atlas_data[se.id].family.name` (le champ `zone`/`name` est déjà présent dans `data/machine_atlas.json`, ex. « Pectoraux — Développé »). **Aucun modèle, aucune migration, aucun mapping fragile inventé.**
- **Assistants** / **Stabilisation** — libellés fallback conservateurs « à qualifier » (aucune body zone spécifique inventée sans source, conformément au brief §Worked Area V1).
- Non-color cue par rôle (puce carrée, intensité dégressive : accent / accent-weak bordé / transparent bordé).
- **Note anti-médicale** : « Zones ciblées estimées — repère d'entraînement, pas une mesure physiologique. » Aucun diagnostic, aucune activation réelle prétendue (§23.7).

Si aucune donnée atlas fiable n'existe (ex. exercices sans famille) → fallback « Zone principale à qualifier ».

## 8. Exercise Intent

Bloc court sur la carte active (`.session-focus__intent`) : rôle de l'exercice dans la séance. Si une famille atlas existe, expose « Bloc {famille} — exercice actif de la séance » ; sinon formulation neutre conservatrice (« Exercice actif de la séance — reste concentré sur l'exécution »). **Aucune justification biomécanique précise inventée** (§Exercise Intent V1).

## 9. Technical Cues

Shell `.session-focus__cues` sur la carte active : **max 3 cues visibles**. Source réelle = `atlas_data[se.id].machine.execution_cues[:3]`. Fallback sobre si absent (« Exécution contrôlée, amplitude complète, tempo maîtrisé ») — aucun cue inventé (§Technical Cues V1).

## 10. Up-next

Surface `.session-focus__up-next` (réutilise `peek_for_active`, promue depuis le `card-peek` Sb_11a) : nom + rôle court (scheme) + **zone principale** du prochain exercice (`atlas_data[next].family.name` si disponible). **Pas de charge complète** (OQ-F respecté : aucun input `set_*`/`weight_kg` dans le bloc). Visible uniquement quand un prochain exercice avec rep scheme existe (`peek_for_active` truthy — comportement existant préservé).

## 11. No-JS / a11y

- **No-JS fallback intact** : aucun JS ajouté, cockpit 100% SSR/CSS. Exercices non-actifs restent des `<details>` navigables ; anchors adressables sans script.
- **Anchors `#exercise-N`** préservés (stepper + cartes).
- **`#session-feedback`** préservé.
- **Inputs logging** `set_*_weight_kg` / `set_*_reps` préservés.
- **Contrats `data-*` rest timer** inchangés (`data-rest-display` etc.).
- **WCAG 44×44** préservé (stepper items min 44×44, tap-targets conservés).
- **Focus visible universel** et **`prefers-reduced-motion`** préservés (hérités Sb_UI_04.1, non touchés).
- **Macros Jinja** (`segmented`, `field_group`) non modifiées.

## 12. Tests exécutés

| Commande | Résultat |
|---|---|
| `check_ruff_budget.py` | ✅ **542 ≤ 548** |
| `check_spec_protocol.py` | ✅ pass |
| `pytest tests/test_session_focus_*.py tests/test_visual_baseline_*.py` | ✅ **285 passed** |
| `pytest -k "session or exercise or cockpit"` | ✅ **444 passed, 0 failed** |
| `tests/test_session_focus_cockpit.py` (nouveau) | ✅ **34 passed** |

Tests cockpit couvrent : cockpit wrapper · orientation · mini-stepper + anchors · worked area (3 rôles + fallback + note anti-médicale) · intent · cues · up-next (structure + OQ-F no-load) · aria-current unique · logging inputs · rest timer data-* · no-JS / no-React · macros · CSS scoped.

## 13. Screenshots after (locaux, non commités)

Capture P0 locale (uvicorn 127.0.0.1:8001, runtime CLI Sb_UI_11.2) :
- **Done. ok=16 failed=0** (16/16 PNG dans `var/visual-after/Sb_UI_04_3/`).
- **Anti-404 OK** : `session-detail-active/mobile-authenticated.png` = 209 662 B (page complète, pas un stub Not Found).
- **Delta visuel confirmé** (byte-size proxy) :
  - `session-detail-active/mobile` : 164 613 B (04.2) → **209 662 B (04.3)** (+27 %)
  - `session-detail-active/desktop` : 193 602 B → **245 853 B** (+27 %)
  - `session-detail-done/mobile` : identique (98 762 B) — attendu : une séance terminée n'a pas d'exercice actif, donc pas de hero cockpit.
- Screenshots **gitignored** (`/var/`), non commités.

## 14. Invariants préservés

- ✅ FastAPI SSR + Jinja2 only — React interdit respecté (aucun marqueur SPA).
- ✅ Aucun changement route / service / model / migration.
- ✅ Aucun JS touché (aucun fichier ajouté ; `preview.js` + `session_focus.js` inchangés).
- ✅ Aucun macro Jinja modifié.
- ✅ Rest timer non touché (partial + contrats `data-*`).
- ✅ `app.css` non touché (CSS scoped `session_focus.css` uniquement).
- ✅ Aucun asset / font / package / PNG ajouté.
- ✅ Aucun rebrand SPIGNOS → Auren dans le code.
- ✅ Baseline P0 capturable après build : `ok=16`.

## 15. Limites

- **Worked Area** : seule la **zone principale** est issue d'une donnée réelle (atlas family). Assistants / stabilisation sont des fallbacks « à qualifier » — Sb_UI_04.5 enrichira via le contrat `exercise_code → body_map_descriptor` (§23.5), hors scope ici.
- **Exercise intent** : formulation dérivée de la famille atlas, volontairement générique (pas de justification biomécanique fine sans source).
- **Up-next** : dépend de `peek_for_active` (rep scheme du prochain exercice requis) ; absent si le prochain slot n'a pas de scheme — comportement existant conservé, pas régressé.
- **session-detail-done** : le cockpit hero ne s'affiche pas (pas d'exercice actif sur une séance terminée) — cohérent, non bloquant.

## 16. Risques

- **Faible.** Build additif, scoped, sans logique métier. Le principal risque est esthétique (densité du hero sur mobile 360×640) — mitigé par la media query `@max-width: 380px` (compaction orientation + hero + worked-area).
- Perception « cockpit vs liste » à valider en revue humaine visuelle (critère d'acceptation §Critère visuel du brief).
- Aucun risque de régression fonctionnelle : 444 tests verts, forms/anchors/inputs/timer préservés.

## 17. Prochaine étape candidate

**`Sb_UI_04.4 Set Logging Console + Progression Guidance`** (bloqué jusqu'à delivery + review de Sb_UI_04.3) : saisie des sets instrumentale, previous performance, target range, présentation du hint overload.

## 18. Références

- Spec : `docs/strategy/Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC.md` (§18/§19/§20/§21/§22/§23)
- Recast acceptance : `docs/SPRINT_Sx_UI_04_FOCUSED_EXERCISE_FLOW_HUMAN_REVIEW_REPORT.md`
- Réserve source : `docs/SPRINT_Sb_UI_04_2_HUMAN_REVIEW_REPORT.md`
- Baseline P0 : `docs/BASELINE_P0_CAPTURED_2026_07_04.md`
- Registry : `docs/strategy/SPEC_REGISTRY.md`
- Roadmap : `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`

## 19. Verdict

🟢 **Sb_UI_04.3 DELIVERED — pending CI + human review.**

**Sb_UI_04.4 : next candidate, not opened.**
**After-screenshots : captured locally 16/16, not committed.**
**No release tag.**
