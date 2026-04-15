# Sprint Sx_02 FINAL Report — Mobile Exercise Entry UX (Final Spec)

**Date:** 2026-04-14
**Type:** Spec only — aucun build
**Prerequisite:** Sx_01 FINAL (signal verrouille)
**Suivi par :** Sx_03 substitution (sans rework composant exercice)

---

## Objectif

Produire le cahier des charges UI definitif du bloc exercice mobile, consolider Sb_02 + Sb_02.1 + Sx_01 FINAL, et proteger le composant contre tout rework par Sx_03.

---

## Travail effectue

### 1. Audit du flow reel

- 5 routes FastAPI mappees (create, read editable, read terminal, update session, update exercise card)
- 14 cles de contexte template cartographiees (session, stats, last_time, hints, exercise_summaries, deltas, active_exercise_id, substitution_data, jump_states, next_code_by_exercise...)
- 411 lignes de `session_detail.html` auditees, structure 6 niveaux documentee
- 2005 lignes de `app.css` analysees, classes pertinentes listees (ex-jump, exercise-card, set-list, card__actions, substitute-picker)

### 2. Flow cible mobile documente

- Diagramme textuel complet entree → save → next → terminal → reopen
- 4 chemins alternatifs (retour arriere, reouverture, acces direct, skip)

### 3. Composant "bloc exercice" cible

- Header compact : contenu autorise (code, name, progress, recap) + interdits (boutons, badges, icones decoratives, animation)
- Body visible : ordre vertical fige en 12 blocs numerotes
- Set row : 4 zones inline (label, weight, reps, done checkbox) + interdits (execution_quality, reps_target, sliders)

### 4. Regles de densite mobile

5 regles formalisees :
- Usage a une main (CTA bas, min 44x44px)
- Lisibilite rapide (couleur semantique 4 etats + mono)
- Peu de texte (libelles courts, pas de paragraphes)
- CTA clairs (un seul primary, libelle consequence)
- Pas de double validation (un POST par niveau)
- Pas d'empilement excessif (profondeur `<details>` max 2)

### 5. Etats UX explicites

- 4 etats progress (future / partial / done / active avec `active` ecrasant)
- 2 etats open/collapsed (native `<details>`)
- Composition active+expanded couples par defaut, decouplables manuellement
- Validation error : flow non-bloquant (NULL tolerants)
- Session completed : redirect obligatoire vers /done (Sb_R3)

### 6. Transitions

5 transitions documentees en detail (save set, next exercise, retour arriere, reouverture done, compat substitution future).

### 7. Integration Sx_01

Tableau explicite :
- Visible standard : weight, reps, completed, free_note, concentration, global_state, bodyweight
- Secondaire (`<details>` optionnel) : muscle_sensation
- Absent UI : success_score (derive), execution_quality (orphelin), reps_target (orphelin)
- Separation stricte set-level / exercise-level / session-level

### 8. Wireframes textuels

3 wireframes mobile-first :
- Page `/sessions/{id}` (in_progress) — rail + cards + feedback
- Page `/sessions/{id}/done` (terminal) — badge + resume + CTA
- Etats de carte exercice (future / partial / done / active)

### 9. Preparation Sx_03

Liste explicite :
- **5 contraintes Sx_03 ne doit pas toucher** : position picker, mecanisme lock, fallback summary, parsing server, structure data injectee
- **4 points d'extension natifs** : substitute-picker, substitute-badge, nouveau `substitution_reason` optionnel, attributs data-equivalence

---

## Livrables produits

| Fichier | Type | Contenu |
|---------|------|---------|
| `docs/strategy/SPIGNOS_MOBILE_EXERCISE_ENTRY_UX_SPEC_FINAL.md` | New | Spec FINAL 14 sections — audit, flow cible, composant cible, regles densite, etats UX, transitions, integration Sx_01, wireframes, cartographie ecrans, preparation Sx_03, recommandations P1-P5, DoD |
| `docs/SPRINT_Sx_02_FINAL_REPORT.md` | New | Ce rapport |

**Aucun fichier code modifie.** Spec only.

---

## Cartographie ecrans / etats / transitions (synthese)

### Ecrans

`/` → `/library` → `/library/{slug}` → POST `/sessions` → `/sessions/{id}` → `/sessions/{id}/done`

Plus : `/history`, `/exercise-history/{slug}/{code}`.

### Etats session

- `in_progress` → editable
- `completed` → terminal (redirect auto)

### Transitions critiques (5)

1. Save intermediaire E1 → E2 : POST exercise card, 303 avec `?active=`
2. Save dernier E7 → feedback : POST exercise card, 303 vers `#session-feedback`
3. Clic "Terminer la seance" : POST session action=end, 303 vers `/done`
4. Clic "Rouvrir" : POST session action=reopen, 303 vers editable
5. GET editable sur session completed : redirect 303 vers `/done`

---

## Wireframes mobile-first — recap

Fournis en section §9 du spec FINAL :
- Page session in_progress (header + jump bar + cards collapsed/active + feedback + rules)
- Page terminal /done (badge + resume + par exercice + CTA + reopen discret)
- Etats de carte (future dim / partial warn / done ok / active accent + box-shadow)

---

## Recommandations ordonnees pour le futur build

| Priorite | Action | Quand |
|----------|--------|-------|
| **P1** | Figer ce spec comme contrat Sx_03 — aucun rework composant exercice | Immediat |
| P2 | Audit visuel cross-device (iOS Safari sticky, Android Chrome, 320px, 430px) | Si remontee terrain |
| P3 | Accessibilite approfondie (ARIA, screen readers, contrast) | Si demande utilisateur specifique |
| P4 | Haptic feedback PWA | Differer V3 |
| P5 | Persistence brouillon cote client | Differer, pas de trigger actuel |

---

## Definition of Done

| Critere | Statut |
|---------|--------|
| Mode focus exercice defini clairement | ✓ (§3 + §4 + §9 wireframes) |
| Etats active / done / future documentes | ✓ (§6.1 + §9.3 recap visuel) |
| Flow save → next specifie precisement | ✓ (§7.1 + §10 transitions) |
| Champs visibles coherents avec Sx_01 | ✓ (§4.4 + §8 separation niveaux) |
| Composant reste SSR-friendly | ✓ (zero JS, `<details>` natif, CSS pur) |
| Place future substitution prevue | ✓ (§11 contraintes + extensions) |
| Aucun besoin de rework majeur laisse pour Sx_03 | ✓ (§11.2 + §11.4 points natifs) |

**Spec FINAL approuve. Pret pour Sx_03.**

---

## Bloqueurs pour Sx_03

**Aucun.** Le composant exercice est **fige** par ce spec. Sx_03 peut :
- Enrichir la source des substitutes (JSON → canonical entity sous triggers)
- Ajouter `substitution_reason` comme champ optionnel
- Raffiner les metadata (equivalence level, reason hint)

Sans jamais toucher :
- La structure du `<details>` exercice
- Le placement du picker
- Le mecanisme de lock
- Le parsing `substituted_name` cote server

---

## Synthese executive (4 lignes)

- Bloc exercice mobile SPIGNOS post-Sb_02.1 : stable, mature, en production
- Flow focus-exercice + jump bar 4 etats + CTA contextuel + footer sticky CSS = cahier des charges fige
- Taxonomie Sx_01 respectee (7 primaires + 1 derive + 2 orphelins preserves, 17 inputs max/exercice)
- Sx_03 peut commencer sur des bases propres — zero rework composant exercice anticipe
