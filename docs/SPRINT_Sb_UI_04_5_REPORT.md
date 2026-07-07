# Sprint Report — Sb_UI_04.5 Worked Area Visual Slot + Alternatives Surface + Hardening

**Sprint ID :** `Sb_UI_04.5_WORKED_AREA_VISUAL_SLOT_AND_ALTERNATIVES_SURFACE`
**Type :** BUILD UI — template structure + scoped CSS + tests + report
**Date :** 2026-07-07
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Verdict :** 🟢 **DELIVERED — pending CI + human review** · **clôture Sx_UI_04**

---

## 1. Objectif

Transformer le Worked Area Panel (V1 textuelle Sb_UI_04.3) en **surface biomécanique lisible et instrumentale**, et rendre les **alternatives** plus utiles pendant la séance — sans modèle, migration, pipeline média ni profil. Dernier build du cycle **Sx_UI_04 Focused Exercise Flow** avant closeout.

## 2. Rappel Sb_UI_04.4 accepted for continuation

Sb_UI_04.4 (Set Logging Console) a été **accepté pour continuation** : la console d'exécution est validée, mais le Body Representation System restait partiel. Sb_UI_04.5 complète le premier jalon (Worked Area) et la surface Alternatives, en clôture du cycle.

## 3. Fichiers changés (whitelist stricte respectée)

| Fichier | Nature |
|---|---|
| `app/templates/_partials/exercise_card.html` | Worked Area → visual slot clinique + Alternatives Surface autour de la substitution existante |
| `app/static/css/session_focus.css` | styles scoped Sb_UI_04.5 (body-slot, body-map CSS-only, zone chip, pattern, alternatives) |
| `tests/test_session_focus_worked_area.py` | **nouveau** — 30 tests worked area + alternatives + anti-médical + invariants |

**`session_detail.html` non touché**. **`overload_hint.html` non touché**. Aucun test existant modifié (le contrat label substitution « Remplacer cet exercice » a été **préservé** — voir §6).

## 4. Worked Area Visual Slot

Le panneau textuel devient une **surface clinique SSR/CSS** (`.session-focus__body-slot`) :
- **Zone chip** (`.session-focus__body-zone-chip`) : code zone atlas réel (ex. `pecs`), mono, teal weak. Rendu seulement si `family.zone` existe.
- **Body-map décoratif** (`.session-focus__body-map`) : forme clinique **100% CSS** (gradient rayé + shape en `border-radius`), `aria-hidden="true"`, **aucun asset / image / GIF / SVG**. Variantes de forme par zone (pecs/lats/delt_lat/quads…) — purement décoratives, jamais anatomiquement précises (donc jamais un claim).
- **Rows** primary / assistants / stabilisation (héritées Sb_UI_04.3).
- **Pattern moteur** (`.session-focus__worked-area-pattern`) : source réelle `family.description` tronquée à 90 car., fallback « Pattern moteur à qualifier ».
- **Note anti-médicale** : « Zones ciblées estimées — repère d'entraînement pédagogique, **non diagnostic médical**. »

## 5. Body Representation V1 (sources & prudence)

- **Zone principale** : source réelle `atlas_data[se.id].family.name` (ex. « Pectoraux — Développé »).
- **Zone code** : `family.zone` (ex. `pecs`).
- **Pattern** : `family.description` (repère de geste réel).
- **Assistants / Stabilisation** : fallback conservateur « à qualifier » — **aucun muscle spécifique inventé sans source** (le contrat `body_map_descriptor` §23.5 les qualifiera plus tard, hors scope).
- **Prudence** : aucune activation réelle prétendue, aucun diagnostic. Formulation « zones ciblées estimées ».

Le texte porte toute la sémantique ; le body-map est décoratif (`aria-hidden`). Fallback texte obligatoire respecté.

## 6. Alternatives Surface

La substitution existante (Sb_03 / Sb_07 / Sb_22a N1/N2/N3) est **rendue plus lisible** via un wrapper `.session-focus__alternatives` **sans changer le mécanisme** :
- Label primaire « **Adapter l'exercice** » + sous-label « **Remplacer cet exercice** » (contrat legacy préservé) + compteur d'alternatives.
- Rôle explicité : « alternative de **même zone / même pattern** avant la première série travail ».
- **Mécanisme intact** : mêmes radios `name="substituted_name"`, mêmes tiers N1/N2/N3, mêmes rationales/badges, **soumission via le form exercice existant** (aucune nouvelle route, aucun service appelé depuis le template).
- `substitute-picker--drawer` + `substitute-picker__count` conservés (contrat Sb_07).
- Drawer `<details>` replié par défaut (no-JS, clavier natif), summary tap 44×44.
- `aria-label` sur le summary pour un libellé combiné accessible.

**Aucune alternative inventée** : si `can_substitute` est faux, aucune liste n'est rendue (comportement existant).

## 7. Substitution CTA

Le CTA substitution **conserve son contrat** : summary `<details>` (drawer), radios inline dans le form exercice, aucune route/action modifiée. Le seul changement est le **libellé/framing** (amélioration autorisée par le brief), le sous-label « Remplacer cet exercice » restant présent pour la compat.

## 8. Hardening mobile / a11y / no-JS

- **Mobile 360×640** : body-map réduit (44px), pattern empilé, pas de mur de texte. La console de logging (Sb_UI_04.4) **reste prioritaire** visuellement.
- **Desktop** : surface équilibrée, non étirée.
- **Session completed** : le hero cockpit (donc le body-slot) ne s'affiche pas sur une séance terminée (pas d'exercice actif) — écran terminé intact.
- **Home / profile / progression / login / register** : inchangés (scope `.session-focus`).
- **No-JS** : aucun JS ajouté, `<details>` natifs, forms POST intacts.
- **WCAG 44×44**, focus visible, `prefers-reduced-motion** préservés (hérités, non touchés).
- **Progressive disclosure** : alternatives repliées, note prudente courte.

## 9. Tests exécutés

| Commande | Résultat |
|---|---|
| `check_ruff_budget.py` | ✅ **542 ≤ 548** |
| `check_spec_protocol.py` | ✅ pass |
| `pytest tests/test_session_focus_*.py tests/test_visual_baseline_*.py` | ✅ **347 passed** |
| `pytest test_mobile_polish::…subheaders + test_overload_placeholder` | ✅ **15 passed** |
| `pytest tests/test_machine_atlas_surface.py` | ✅ **3 passed** (label substitution préservé) |
| broad sweep `-k "substitut or session or exercise or worked or console or mobile or atlas"` | ✅ **576 passed, 0 failed** |
| `tests/test_session_focus_worked_area.py` (nouveau) | ✅ **30 passed** |

Tests worked area couvrent : body-slot + body-map + `aria-hidden` · zone chip · rows primary/secondary/stabilizer · pattern row · fallbacks « à qualifier » · note anti-médicale · absence de claim diagnostic/activation · **absence d'asset externe** (template + CSS `url()`) · alternatives wrapper + rôle · substitution mécanisme préservé (radios `substituted_name`, pas de nouvelle route) · console/active set/up-next/stepper/guidance intacts · input names · anchors · rest timer · no-JS/no-React · macros · CSS scoped.

## 10. Screenshots after (locaux, non commités)

Capture P0 locale (uvicorn 127.0.0.1:8001, runtime CLI Sb_UI_11.2) :
- **Done. ok=16 failed=0** (`var/visual-after/Sb_UI_04_5/`).
- **Anti-404 OK** : `session-detail-active/mobile-authenticated.png` = 230 934 B (page complète).
- **Delta 04.4 → 04.5** :
  - `session-detail-active/mobile` : 219 541 B → **230 934 B** (+11 393 B).
  - `session-detail-active/desktop` : 254 391 B → **264 379 B** (+9 988 B).
  - `session-detail-done/mobile` : identique (98 762 B) — attendu.
- Screenshots **gitignored** (`/var/`), non commités.

## 11. Invariants préservés

- ✅ FastAPI SSR + Jinja2 only — React interdit respecté.
- ✅ Aucun changement route / service / model / migration.
- ✅ Aucun JS touché (aucun fichier ajouté).
- ✅ Aucun macro modifié · rest timer non touché · `overload_hint.html` non touché · `session_focus_header.html` non touché · `app.css` non touché.
- ✅ Substitution : radios `substituted_name`, drawer, route/action **inchangés**.
- ✅ Input names logging inchangés.
- ✅ Aucun asset / image / GIF / SVG / package ajouté.
- ✅ Aucun calcul biomécanique réel, aucun moteur body map.
- ✅ Aucun rebrand SPIGNOS → Auren · aucun changement profil.
- ✅ Baseline P0 capturable : `ok=16`.

## 12. Limites

- **Assistants / Stabilisation** restent « à qualifier » (aucun muscle inventé sans source). Leur qualification nécessitera le contrat `body_map_descriptor` (§23.5) — donnée future, hors scope V1.
- **Body-map** est une forme abstraite décorative, non une silhouette anatomique (choix délibéré : pas d'asset, pas de claim).
- **Zone chip / pattern** ne s'affichent que si l'atlas family existe pour l'exercice ; sinon fallbacks sobres.

## 13. Risques

- **Faible.** Build additif, scoped, sans logique métier ; 576 tests verts sur le périmètre élargi. Substitution intacte (contrat radios/route préservé).
- Risque esthétique : densité du slot sur mobile — mitigé par media query (body-map réduit, pattern empilé) et priorité maintenue à la console de logging.
- Perception « couche biomécanique utile vs texte décoratif » à valider en revue humaine visuelle.

## 14. Recommandations futures

- **Sb_UI_04.next / cycle body map** : brancher le contrat `body_map_descriptor` (§23.5) pour qualifier assistants/stabilisation à partir de données réelles (sans modèle lourd : un mapping documentaire `exercise_code → zones` suffirait en V2).
- **Sx_UI_05 / profil** : réutiliser cette couche Worked Area sur le program preview et le profile body intelligence (surfaces B/C §23.2).
- **Consolidation** : le bloc legacy `.last-time` pourrait fusionner avec la référence console (Sb_UI_04.4) dans un futur polish.

## 15. Statut final Sx_UI_04

Avec Sb_UI_04.5, le cycle **Sx_UI_04 Focused Exercise Flow** a livré ses 5 sous-sprints :
- `Sb_UI_04.1` CSS Foundation ✅
- `Sb_UI_04.2` Header & Jump Bar ✅ (réserve visuelle)
- `Sb_UI_04.3` Active Exercise Cockpit Shell ✅ (accepted for continuation)
- `Sb_UI_04.4` Set Logging Console ✅ (accepted for continuation)
- `Sb_UI_04.5` Worked Area Visual Slot + Alternatives + Hardening 🟢 **DELIVERED — pending CI + human review**

**Sx_UI_04 : READY FOR FINAL CLOSEOUT REVIEW** après CI verte + human review de Sb_UI_04.5.

## 16. Références

- Spec : `docs/strategy/Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC.md` (§18/§20/§21/§22/§23)
- Sb_UI_04.4 acceptance : `docs/SPRINT_Sb_UI_04_4_HUMAN_REVIEW_REPORT.md`
- Baseline P0 : `docs/BASELINE_P0_CAPTURED_2026_07_04.md`
- Registry : `docs/strategy/SPEC_REGISTRY.md`
- Roadmap : `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`

## 17. Verdict

🟢 **Sb_UI_04.5 DELIVERED — pending CI + human review.**

**Sx_UI_04 : pending final review / closeout.**
**Sx_UI_05 : next candidate, not opened.**
**After-screenshots : captured locally 16/16, not committed. No release tag.**
